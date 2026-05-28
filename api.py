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

import os
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
# BaseModel: Pydantic base class. Any class inheriting it gets automatic JSON
# parsing, type coercion, and validation — FastAPI uses it for request/response bodies.
# field_validator: decorator to add custom validation logic to a single field.
from pydantic import BaseModel, field_validator

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
MAX_REQUESTS_PER_DAY = 200       # global daily cap across all users — protects against billing surprises
RETRIEVER_K = 8                  # chunks retrieved per query (more = better answers, slightly more tokens)
ALLOWED_ORIGINS = os.getenv(     # set ALLOWED_ORIGINS env var in HF Space to restrict to your domain
    "ALLOWED_ORIGINS", "*"       # default "*" is fine locally; in prod: "https://www.cv.manuelmezo.com"
).split(",")

# ---------------------------------------------------------------------------
# In-memory rate limiter (per IP, sliding 60-second window)
# ---------------------------------------------------------------------------
_rate_store: dict = defaultdict(list)

def is_rate_limited(ip: str) -> bool:
    now = time.time()
    window = [t for t in _rate_store[ip] if now - t < 60]
    _rate_store[ip] = window
    if len(window) >= MAX_REQUESTS_PER_IP_PER_MIN:
        return True
    _rate_store[ip].append(now)
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
    # all-MiniLM-L6-v2 is small (80 MB) and fast while still being accurate.
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

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
        max_output_tokens=512,  # hard ceiling on output — protects against runaway responses
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
         "Use ONLY the context below. Be concise and professional.\n\nContext:\n{context}"),
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

    print("Chat agent ready.")
    yield  # server runs here — everything after yield is teardown (nothing needed)


# ---------------------------------------------------------------------------
# App instantiation
#
# FastAPI() creates the ASGI application. The lifespan parameter tells it
# which function to call on startup/shutdown.
# ---------------------------------------------------------------------------
app = FastAPI(title="Portfolio Chat Agent", lifespan=lifespan)

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

    # 5. Invoke the RAG chain with retry on transient Google 500s
    # The session_id is passed via config["configurable"] — RunnableWithMessageHistory
    # uses it to look up the right ChatMessageHistory from the session store.
    last_err = None
    for attempt in range(3):
        try:
            answer = app_state["chain"].invoke(
                {"input": request.message},
                config={"configurable": {"session_id": session_id}},
            )
            return ChatResponse(answer=answer, session_id=session_id)
        except HTTPException:
            raise  # don't swallow our own intentional errors
        except Exception as e:
            last_err = e
            if "500" in str(e) or "INTERNAL" in str(e):
                # Exponential backoff: 1s, 2s, 4s before giving up
                time.sleep(2 ** attempt)
                continue
            raise  # non-500 errors are not transient — fail immediately
    raise last_err   # all 3 attempts failed
