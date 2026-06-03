"""
api.py — Portfolio Chat Agent backend

FastAPI concepts you will see here:
- Lifespan: startup/shutdown hook to load heavy resources once
- Middleware: CORS so browsers can call this API from a different domain
- Pydantic models: automatic JSON validation on every request/response
- Dependency injection via function parameters (Request object)
- HTTPException: return structured error responses with HTTP status codes
- async def: non-blocking endpoint so the server handles other requests while waiting for Gemini
"""

import base64
import os
import re
import time
import uuid
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
# FastAPI: the web framework. Request gives us access to HTTP metadata (IP, headers).
# HTTPException lets us abort a request with a specific HTTP status code and message.
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
# BaseModel: Pydantic base class. Any class inheriting it gets automatic JSON
# parsing, type coercion, and validation — FastAPI uses it for request/response bodies.
# field_validator: decorator to add custom validation logic to a single field.
from pydantic import BaseModel, field_validator

try:
    # Langfuse v4: CallbackHandler takes no metadata args;
    # session/user context is set via propagate_attributes() context manager.
    from langfuse.langchain import CallbackHandler as LangfuseCallbackHandler
    from langfuse import propagate_attributes as _langfuse_propagate
    _LANGFUSE_AVAILABLE = True
except ImportError:
    _LANGFUSE_AVAILABLE = False

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Load GOOGLE_API_KEY from .env into os.environ so the rest of the code can read it
load_dotenv()

# ---------------------------------------------------------------------------
# Security config
# Centralised here so you can tune all limits in one place without touching
# the endpoint logic below.
# ---------------------------------------------------------------------------
MAX_MESSAGE_CHARS = 500          # reject inputs longer than this
MAX_TURNS_PER_SESSION = 20       # kill session after N exchanges to prevent history bloat
MAX_REQUESTS_PER_IP_PER_MIN = 10 # sliding-window rate limit per client IP
MAX_TTS_PER_IP_PER_MIN = 10      # TTS is GPU — same cap as chat
MAX_REQUESTS_PER_DAY = 200       # global daily cap across all users — protects against billing surprises
MAX_TTS_TEXT_CHARS = 1000        # cap TTS input to avoid runaway GPU time
RETRIEVER_K = 8                  # chunks retrieved per query (more = better answers, slightly more tokens)
ALLOWED_ORIGINS = os.getenv(     # set ALLOWED_ORIGINS env var in HF Space to restrict to your domain
    "ALLOWED_ORIGINS", "*"       # default "*" is fine locally; in prod: "https://www.cv.manuelmezo.com"
).split(",")

# ---------------------------------------------------------------------------
# In-memory rate limiter (per IP, sliding 60-second window)
# ---------------------------------------------------------------------------
_rate_store: dict = defaultdict(list)
_tts_rate_store: dict = defaultdict(list)

def is_rate_limited(ip: str) -> bool:
    now = time.time()
    window = [t for t in _rate_store[ip] if now - t < 60]
    _rate_store[ip] = window
    if len(window) >= MAX_REQUESTS_PER_IP_PER_MIN:
        return True
    _rate_store[ip].append(now)
    return False

def is_tts_rate_limited(ip: str) -> bool:
    now = time.time()
    window = [t for t in _tts_rate_store[ip] if now - t < 60]
    _tts_rate_store[ip] = window
    if len(window) >= MAX_TTS_PER_IP_PER_MIN:
        return True
    _tts_rate_store[ip].append(now)
    return False

# ---------------------------------------------------------------------------
# Daily global request counter
#
# Tracks total requests across ALL users today. Resets at midnight UTC.
# Prevents a single day of abuse from generating a surprise bill — even if
# the per-IP rate limit is bypassed via many different IPs.
# ---------------------------------------------------------------------------
_daily: dict = {"date": "", "count": 0}

def is_daily_budget_exceeded() -> bool:
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if _daily["date"] != today:
        # New day — reset counter
        _daily["date"] = today
        _daily["count"] = 0
    _daily["count"] += 1
    return _daily["count"] > MAX_REQUESTS_PER_DAY

# ---------------------------------------------------------------------------
# Global app state
#
# We store the loaded chain and session store here so the lifespan function
# can write to it and the endpoint functions can read from it.
# A plain dict works fine; for a larger app you'd use a proper dependency.
# ---------------------------------------------------------------------------
app_state: dict = {}


def format_docs(docs) -> str:
    """Turn a list of retrieved Document objects into a single context string."""
    return "\n\n".join(
        f"[Source: {d.metadata.get('source','?')}]\n{d.page_content}" for d in docs
    )


# ---------------------------------------------------------------------------
# Lifespan — runs ONCE at startup, then yields, then runs teardown at shutdown
#
# @asynccontextmanager turns this generator into a context manager.
# FastAPI calls it when the server starts (before accepting requests) and
# when it shuts down (after the last request).
#
# Why use lifespan instead of loading things inside the endpoint?
# Because loading the vectorstore and model on every request would be very
# slow (~2–3 seconds). Loading once at startup means the first request is
# fast too (after a brief startup delay).
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    api_key = os.getenv("GOOGLE_API_KEY")

    # Local embedding model — runs on CPU, no API calls, no rate limits.
    # bge-small-en-v1.5: same ~90MB size as MiniLM but significantly better
    # retrieval quality (MTEB retrieval ~51 vs ~40). Trained specifically for
    # retrieval tasks, not general sentence similarity.
    # MUST match the model used in build_db.py — changing one requires redeploying both.
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    # Load the pre-built ChromaDB vector store from disk.
    # persist_directory tells Chroma where the SQLite + binary index files are.
    vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)

    # as_retriever() wraps the store with a .invoke(query) interface that
    # returns the top-k most similar documents. k=4 is a good balance between
    # context richness and token cost.
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": RETRIEVER_K})

    # The LLM that generates answers. Only this call hits the Gemini API.
    # max_output_tokens caps the response length → directly caps cost per call.
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.2,        # low = more factual, less hallucination
        max_output_tokens=800,  # enough for a complete answer; prompt instructs model to summarize rather than truncate
    )

    # ── Step 1: Contextualize the question ───────────────────────────────
    # Problem: if the user asks "what tools did he use?" the retriever won't
    # find anything useful because "he" has no meaning without history.
    # Solution: ask the LLM to rewrite the question as standalone first.
    # This prompt only runs when there IS chat history (first message skips it).
    contextualize_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Given the chat history and the latest user question, "
         "rewrite it as a standalone question. "
         "Do NOT answer, only reformulate if needed, otherwise return as-is."),
        MessagesPlaceholder("chat_history"),  # previous turns are injected here
        ("human", "{input}"),
    ])
    # The | operator chains runnables: prompt → LLM → parse to plain string
    contextualize_chain = contextualize_prompt | llm | StrOutputParser()

    def contextualize_question(inputs: dict) -> str:
        """Rephrase the question if there's history; return it unchanged if not."""
        if inputs.get("chat_history"):
            return contextualize_chain.invoke(inputs)
        return inputs["input"]

    # ── Step 2: Answer with context ───────────────────────────────────────
    # The {context} placeholder is filled with the retrieved document chunks.
    # Telling the LLM to use ONLY the context prevents hallucination about
    # things not in the documents.
    answer_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a helpful assistant on Manuel Mezo's portfolio website. "
         "Answer questions about his education, experience, skills, and projects. "
         "Use ONLY the context below. Be concise and professional. "
         "Always write complete sentences and end with a proper conclusion — never stop mid-thought. "
         "If the answer would be very long, summarize the key points rather than listing everything.\n\nContext:\n{context}"),
        MessagesPlaceholder("chat_history"),  # history shown so LLM can refer back to it
        ("human", "{input}"),
    ])

    # ── Full RAG chain (LCEL) ─────────────────────────────────────────────
    # RunnablePassthrough.assign adds new keys to the input dict without
    # removing the existing ones.
    #
    # Flow:
    #   input dict {"input": "...", "chat_history": [...]}
    #     → assign "context": run contextualize_question → retriever → format_docs
    #     → dict now has {"input", "chat_history", "context"}
    #     → fill answer_prompt template
    #     → send to LLM
    #     → parse output to plain string
    rag_chain = (
        RunnablePassthrough.assign(
            context=RunnableLambda(contextualize_question) | retriever | format_docs
        )
        | answer_prompt
        | llm
        | StrOutputParser()
    )

    # ── Session store ─────────────────────────────────────────────────────
    # Maps session_id (UUID string) → ChatMessageHistory (list of messages).
    # Stored in memory — resets when the server restarts.
    # For production persistence, swap ChatMessageHistory for a Redis or DB store.
    session_store: dict = {}

    def get_session_history(session_id: str) -> ChatMessageHistory:
        """Return existing history for this session, or create a new one."""
        if session_id not in session_store:
            session_store[session_id] = ChatMessageHistory()
        return session_store[session_id]

    # RunnableWithMessageHistory wraps the chain and handles history bookkeeping:
    # before each invoke it loads history → after each invoke it saves the exchange.
    # input_messages_key: which input key is the user's text
    # history_messages_key: which key the chain expects for prior messages
    app_state["chain"] = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    app_state["sessions"] = session_store  # expose so the endpoint can inspect turn count

    # ── Langfuse observability (optional) ────────────────────────────────
    # LANGFUSE_BASE_URL is the HF Space secret name; the SDK expects LANGFUSE_HOST.
    if os.getenv("LANGFUSE_BASE_URL") and not os.getenv("LANGFUSE_HOST"):
        os.environ["LANGFUSE_HOST"] = os.environ["LANGFUSE_BASE_URL"]

    langfuse_enabled = (
        _LANGFUSE_AVAILABLE
        and bool(os.getenv("LANGFUSE_SECRET_KEY"))
        and bool(os.getenv("LANGFUSE_PUBLIC_KEY"))
    )
    app_state["langfuse_enabled"] = langfuse_enabled
    if langfuse_enabled:
        print("Langfuse tracing: ENABLED")
    else:
        print("Langfuse tracing: disabled (keys not set or langfuse not installed)")

    # ── TTS proxy: pre-load voice sample ─────────────────────────────────
    voice_path = os.path.join(os.path.dirname(__file__), "voice_sample.mp4")
    if os.path.exists(voice_path):
        app_state["tts_ref_audio_b64"] = base64.b64encode(
            open(voice_path, "rb").read()
        ).decode()
        print("Voice sample loaded for TTS proxy.")
    else:
        app_state["tts_ref_audio_b64"] = None
        print("WARNING: voice_sample.mp4 not found — /tts endpoint will be disabled.")

    print("Chat agent ready.")
    yield  # server runs here — everything after yield is teardown (nothing needed)


# ---------------------------------------------------------------------------
# App instantiation
#
# FastAPI() creates the ASGI application. The lifespan parameter tells it
# which function to call on startup/shutdown.
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Portfolio Chat Agent API",
    description="RAG-powered conversational agent for Manuel Mezo's portfolio. Built with LangChain, ChromaDB, and Gemini 2.5 Flash.",
    version="1.0.0",
    contact={
        "name": "Manuel Mezo",
        "url": "https://www.cv.manuelmezo.com",
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


_LANDING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Portfolio Chat Agent API — Manuel Mezo</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0f172a; --card: #1e293b; --border: #334155;
    --text: #f1f5f9; --muted: #94a3b8;
    --grad: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
    --accent: #0ea5e9;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }
  a { color: var(--accent); text-decoration: none; font-weight: 600; }
  a:hover { text-decoration: underline; }

  .hero {
    text-align: center; padding: 80px 40px 60px;
    border-bottom: 1px solid var(--border);
  }
  .badge {
    display: inline-block; background: var(--grad);
    color: #fff; font-size: 0.72rem; font-weight: 700;
    letter-spacing: 1.5px; text-transform: uppercase;
    padding: 5px 14px; border-radius: 20px; margin-bottom: 20px;
  }
  h1 { font-size: 2.8rem; font-weight: 800; letter-spacing: -1px; margin-bottom: 16px; }
  .grad-text { background: var(--grad); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; color: transparent; }
  .hero p { font-size: 1.1rem; color: var(--muted); max-width: 600px; margin: 0 auto 32px; }

  .links { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
  .btn {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 10px 22px; border-radius: 8px; font-size: 0.9rem; font-weight: 700;
    transition: opacity .15s; text-decoration: none;
  }
  .btn-primary { background: var(--grad); color: #fff; }
  .btn-secondary { background: var(--card); color: var(--text); border: 1px solid var(--border); }
  .btn:hover { opacity: .85; text-decoration: none; }

  .container { max-width: 900px; margin: 0 auto; padding: 0 40px; }

  .section { padding: 60px 0; border-bottom: 1px solid var(--border); }
  .section h2 { font-size: 1.3rem; font-weight: 800; margin-bottom: 24px; color: var(--text); }

  .flow {
    display: flex; gap: 0; margin: 0 0 32px; flex-wrap: wrap;
  }
  .flow-step {
    flex: 1; min-width: 90px;
    background: var(--card); border: 1px solid var(--border);
    padding: 14px 10px; text-align: center; position: relative;
  }
  .flow-step:first-child { border-radius: 8px 0 0 8px; }
  .flow-step:last-child  { border-radius: 0 8px 8px 0; }
  .flow-step:not(:last-child)::after {
    content: '→'; position: absolute; right: -13px; top: 50%; transform: translateY(-50%);
    color: var(--accent); font-weight: 700; z-index: 2;
  }
  .flow-step .icon { font-size: 1.3rem; margin-bottom: 4px; }
  .flow-step .label { font-size: 0.68rem; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }

  .endpoint-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; margin-bottom: 16px; overflow: hidden;
  }
  .endpoint-header {
    display: flex; align-items: center; gap: 12px;
    padding: 14px 20px; border-bottom: 1px solid var(--border);
  }
  .method {
    font-size: 0.75rem; font-weight: 800; padding: 3px 10px; border-radius: 5px;
  }
  .method.post { background: #065f46; color: #6ee7b7; }
  .method.get  { background: #1e3a5f; color: #7dd3fc; }
  .endpoint-path { font-family: monospace; font-size: 1rem; color: var(--text); font-weight: 700; }
  .endpoint-desc { color: var(--muted); font-size: 0.875rem; margin-left: auto; }
  .endpoint-body { padding: 18px 20px; }
  .endpoint-body p { color: var(--muted); font-size: 0.9rem; margin-bottom: 14px; }

  pre {
    background: #0f172a; border: 1px solid var(--border);
    border-radius: 8px; padding: 16px 18px;
    font-size: 0.82rem; overflow-x: auto; color: #e2e8f0; line-height: 1.6;
  }
  code { font-family: 'Courier New', monospace; }

  .pills { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 24px; }
  .pill {
    background: var(--card); border: 1px solid var(--border);
    color: var(--muted); font-size: 0.78rem; font-weight: 600;
    padding: 4px 12px; border-radius: 20px;
  }

  .security-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 16px; }
  .sec-item {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 8px; padding: 14px 16px;
  }
  .sec-item strong { display: block; font-size: 0.85rem; color: var(--text); margin-bottom: 4px; }
  .sec-item span { font-size: 0.82rem; color: var(--muted); }
  @media (max-width: 600px) { .security-grid { grid-template-columns: 1fr; } }

  footer {
    text-align: center; padding: 40px; color: var(--muted); font-size: 0.85rem;
    border-top: 1px solid var(--border);
  }
</style>
</head>
<body>

<div class="hero">
  <div class="badge">🤖 RAG · LangChain · FastAPI</div>
  <h1>Portfolio Chat Agent <span class="grad-text">API</span></h1>
  <p>
    A conversational AI agent that answers questions about
    <a href="https://www.cv.manuelmezo.com" target="_blank">Manuel Mezo's</a>
    education, professional experience, skills, and projects — grounded in his actual CV and documents.
  </p>
  <div class="links">
    <a class="btn btn-primary" href="/docs">📖 Interactive API Docs</a>
    <a class="btn btn-secondary" href="https://www.cv.manuelmezo.com/portfolio-chat-agent-project.html" target="_blank">🧠 How it was built</a>
    <a class="btn btn-secondary" href="https://github.com/manumezog/portfolio-chat-agent" target="_blank">💻 GitHub</a>
    <a class="btn btn-secondary" href="https://www.cv.manuelmezo.com" target="_blank">🌐 Portfolio</a>
  </div>
</div>

<div class="container">

  <div class="section">
    <h2>Architecture</h2>
    <div class="flow">
      <div class="flow-step"><div class="icon">💬</div><div class="label">Widget</div></div>
      <div class="flow-step"><div class="icon">🔐</div><div class="label">Rate limit</div></div>
      <div class="flow-step"><div class="icon">🔄</div><div class="label">Contextualize</div></div>
      <div class="flow-step"><div class="icon">🔍</div><div class="label">Retrieve</div></div>
      <div class="flow-step"><div class="icon">🧠</div><div class="label">Gemini LLM</div></div>
      <div class="flow-step"><div class="icon">✅</div><div class="label">Answer</div></div>
    </div>
    <p style="color: var(--muted); font-size: 0.9rem;">
      Built with <strong style="color:var(--text)">LangChain LCEL</strong> chains.
      Embeddings run locally (<code>all-MiniLM-L6-v2</code>) — no API calls for retrieval.
      The LLM (<strong style="color:var(--text)">Gemini 2.5 Flash</strong>) only runs at answer time.
      Conversation history is managed per <code>session_id</code> using
      <code>RunnableWithMessageHistory</code>.
    </p>
    <div class="pills">
      <span class="pill">LangChain 1.3</span>
      <span class="pill">ChromaDB</span>
      <span class="pill">Gemini 2.5 Flash</span>
      <span class="pill">sentence-transformers/all-MiniLM-L6-v2</span>
      <span class="pill">FastAPI</span>
      <span class="pill">Docker · HF Spaces</span>
    </div>
  </div>

  <div class="section">
    <h2>Endpoints</h2>

    <div class="endpoint-card">
      <div class="endpoint-header">
        <span class="method post">POST</span>
        <span class="endpoint-path">/chat</span>
        <span class="endpoint-desc">Send a message, get an answer</span>
      </div>
      <div class="endpoint-body">
        <p>
          Send a question about Manuel's background, experience, or projects.
          Include the <code>session_id</code> returned on the first call to maintain conversation history
          across follow-up questions.
        </p>
        <pre><code># First message — omit session_id
curl -X POST https://manumezog-portfolio-chat-agent.hf.space/chat \\
  -H "Content-Type: application/json" \\
  -d '{"message": "What did Manuel study?"}'

# Response
{
  "answer": "Manuel has a Master's in Aerospace Engineering from UC3M...",
  "session_id": "a3f8c2d1-..."
}

# Follow-up — send session_id to maintain history
curl -X POST https://manumezog-portfolio-chat-agent.hf.space/chat \\
  -H "Content-Type: application/json" \\
  -d '{"message": "What tools did he use?", "session_id": "a3f8c2d1-..."}'</code></pre>
      </div>
    </div>

    <div class="endpoint-card">
      <div class="endpoint-header">
        <span class="method get">GET</span>
        <span class="endpoint-path">/health</span>
        <span class="endpoint-desc">Liveness check</span>
      </div>
      <div class="endpoint-body">
        <p>Returns server status and whether the RAG chain loaded successfully at startup.</p>
        <pre><code>curl https://manumezog-portfolio-chat-agent.hf.space/health

{"status": "ok", "chain_loaded": true}</code></pre>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>Rate limits & security</h2>
    <div class="security-grid">
      <div class="sec-item"><strong>500 char input cap</strong><span>Prevents token-exhaustion on a single request</span></div>
      <div class="sec-item"><strong>512 token output cap</strong><span>Limits LLM cost per response</span></div>
      <div class="sec-item"><strong>10 req / min / IP</strong><span>Per-IP sliding window rate limit</span></div>
      <div class="sec-item"><strong>200 req / day global</strong><span>Hard daily ceiling across all users</span></div>
      <div class="sec-item"><strong>20 turns / session</strong><span>History cap prevents memory bloat</span></div>
      <div class="sec-item"><strong>CORS restricted</strong><span>Only portfolio domain allowed in production</span></div>
    </div>
  </div>

</div>

<footer>
  Built by <a href="https://www.cv.manuelmezo.com" target="_blank">Manuel Mezo</a> &nbsp;·&nbsp;
  <a href="https://github.com/manumezog/portfolio-chat-agent" target="_blank">GitHub</a> &nbsp;·&nbsp;
  <a href="/docs" target="_blank">Swagger UI</a> &nbsp;·&nbsp;
  <a href="/redoc" target="_blank">ReDoc</a>
</footer>

</body>
</html>"""


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def landing():
    """Custom landing page for the API — explains the project and links to docs."""
    return _LANDING_HTML

# ---------------------------------------------------------------------------
# CORS Middleware
#
# Browsers enforce the Same-Origin Policy: a script on domain A cannot call
# an API on domain B unless domain B explicitly says it's OK via CORS headers.
# This middleware adds those headers to every response.
#
# allow_origins=["*"] means "any domain can call this API".
# In production set this to ["https://www.cv.manuelmezo.com"] to block other sites.
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic schemas
#
# FastAPI automatically:
#   - Parses incoming JSON into these classes
#   - Returns HTTP 422 with a detailed error message if validation fails
#   - Generates OpenAPI docs (visible at /docs) from these definitions
# ---------------------------------------------------------------------------
def _strip_markdown(text: str) -> str:
    """Remove markdown so the TTS model reads clean prose, not symbols."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)   # bold
    text = re.sub(r"\*(.+?)\*", r"\1", text)         # italic
    text = re.sub(r"`(.+?)`", r"\1", text)            # inline code
    text = re.sub(r"^[\*\-]\s+", "", text, flags=re.MULTILINE)   # bullet points
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)    # numbered lists
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)        # links
    return text.strip()


class TtsRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def text_not_empty_or_too_long(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("text cannot be empty")
        if len(v) > MAX_TTS_TEXT_CHARS:
            v = v[:MAX_TTS_TEXT_CHARS]
        return v


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # None on first message; server generates one

    @field_validator("message")
    @classmethod
    def message_not_empty_or_too_long(cls, v: str) -> str:
        """Reject empty or oversized inputs before they reach the LLM."""
        v = v.strip()
        if not v:
            raise ValueError("message cannot be empty")
        if len(v) > MAX_MESSAGE_CHARS:
            raise ValueError(f"message exceeds {MAX_MESSAGE_CHARS} characters")
        return v

    @field_validator("session_id")
    @classmethod
    def session_id_safe(cls, v: Optional[str]) -> Optional[str]:
        """Prevent absurdly long session IDs that could be used for injection."""
        if v is not None and len(v) > 64:
            raise ValueError("invalid session_id")
        return v


class ChatResponse(BaseModel):
    answer: str
    session_id: str  # client must store this and send it back on follow-up messages


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    """Quick liveness check — useful for deployment platforms and monitoring."""
    return {"status": "ok", "chain_loaded": "chain" in app_state}


@app.post("/tts", include_in_schema=True)
async def tts(request: TtsRequest, http_request: Request):
    """
    TTS proxy — converts text to speech using the Modal F5-TTS GPU endpoint.
    The Modal API key never leaves the server; clients only call this endpoint.
    Returns audio/wav bytes ready for the browser to play.
    """
    import httpx

    f5_url = os.getenv("F5_SERVER_URL", "")
    f5_key = os.getenv("F5_API_KEY", "")
    f5_ref_text = os.getenv("F5_REF_TEXT", "")
    ref_audio_b64 = app_state.get("tts_ref_audio_b64")

    if not f5_url or not f5_key or not ref_audio_b64:
        raise HTTPException(status_code=503, detail="TTS service not configured.")

    client_ip = http_request.client.host if http_request.client else "unknown"
    if is_tts_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Too many TTS requests. Please slow down.")

    clean_text = _strip_markdown(request.text)

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f5_url,
                json={
                    "api_key": f5_key,
                    "ref_audio": ref_audio_b64,
                    "ref_text": f5_ref_text,
                    "gen_text": clean_text,
                },
            )
        resp.raise_for_status()
        return Response(content=resp.content, media_type="audio/wav")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"TTS backend error: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=502, detail="TTS service unavailable.")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):
    """
    Main chat endpoint.

    FastAPI injects two objects here:
    - request: our ChatRequest Pydantic model (already validated)
    - http_request: the raw Request object — we use it to read the client IP

    The function is `async def` so FastAPI runs it in an async event loop.
    The .invoke() calls on the chain are synchronous (blocking), which is fine
    for a low-traffic portfolio site. For high traffic you'd use .ainvoke().
    """

    # 1. Daily global budget — hard ceiling across all users, resets at midnight UTC
    if is_daily_budget_exceeded():
        raise HTTPException(status_code=429, detail="Daily request limit reached. Try again tomorrow.")

    # 2. Rate limiting — read client IP from the request and check the window
    client_ip = http_request.client.host if http_request.client else "unknown"
    if is_rate_limited(client_ip):
        # HTTP 429 = Too Many Requests — standard code for rate limiting
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")

    # 3. Resolve session — use provided ID or create a new UUID
    session_id = request.session_id or str(uuid.uuid4())

    # 4. Enforce turn cap — count pairs of (human, ai) messages in history
    sessions = app_state.get("sessions", {})
    if session_id in sessions:
        turns = len(sessions[session_id].messages) // 2  # each turn = 1 human + 1 AI message
        if turns >= MAX_TURNS_PER_SESSION:
            raise HTTPException(
                status_code=400,
                detail="Session limit reached. Please refresh to start a new conversation."
            )

    # 5. Invoke the RAG chain (with optional Langfuse tracing).
    #    Langfuse v4 API: CallbackHandler() takes no metadata args.
    #    Session/user context propagates via propagate_attributes() context manager.
    #    The entire Langfuse setup is in a try/except — if anything fails,
    #    the request still succeeds without tracing.
    from contextlib import nullcontext

    callbacks = []
    trace_ctx = nullcontext()
    if app_state.get("langfuse_enabled"):
        try:
            callbacks = [LangfuseCallbackHandler()]
            trace_ctx = _langfuse_propagate(
                session_id=session_id,
                user_id=client_ip,
            )
        except Exception:
            callbacks = []
            trace_ctx = nullcontext()

    last_err = None
    with trace_ctx:
        for attempt in range(3):
            try:
                answer = app_state["chain"].invoke(
                    {"input": request.message},
                    config={
                        "configurable": {"session_id": session_id},
                        "callbacks": callbacks,
                    },
                )
                return ChatResponse(answer=answer, session_id=session_id)
            except HTTPException:
                raise
            except Exception as e:
                last_err = e
                if "500" in str(e) or "INTERNAL" in str(e):
                    time.sleep(2 ** attempt)
                    continue
                raise
    raise last_err
