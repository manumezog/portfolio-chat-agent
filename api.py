import os
import time
import uuid
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()

# ---------------------------------------------------------------------------
# Security config — tune these to balance usability vs. abuse protection
# ---------------------------------------------------------------------------
MAX_MESSAGE_CHARS = 500          # hard cap on input length
MAX_TURNS_PER_SESSION = 20       # session dies after this many exchanges
MAX_REQUESTS_PER_IP_PER_MIN = 10 # per-IP rate limit
ALLOWED_ORIGINS = os.getenv(     # restrict CORS in production
    "ALLOWED_ORIGINS", "*"
).split(",")

# ---------------------------------------------------------------------------
# In-memory rate limiter: {ip: [timestamps]}
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
# Global app state
# ---------------------------------------------------------------------------
app_state: dict = {}

def format_docs(docs) -> str:
    return "\n\n".join(
        f"[Source: {d.metadata.get('source','?')}]\n{d.page_content}" for d in docs
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    api_key = os.getenv("GOOGLE_API_KEY")

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.2,
        max_output_tokens=512,   # cap LLM output tokens → caps cost per call
    )

    contextualize_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Given the chat history and the latest user question, "
         "rewrite it as a standalone question. "
         "Do NOT answer, only reformulate if needed, otherwise return as-is."),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    contextualize_chain = contextualize_prompt | llm | StrOutputParser()

    def contextualize_question(inputs: dict) -> str:
        if inputs.get("chat_history"):
            return contextualize_chain.invoke(inputs)
        return inputs["input"]

    answer_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a helpful assistant on Manuel Mezo's portfolio website. "
         "Answer questions about his education, experience, skills, and projects. "
         "Use ONLY the context below. Be concise and professional.\n\nContext:\n{context}"),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    rag_chain = (
        RunnablePassthrough.assign(
            context=RunnableLambda(contextualize_question) | retriever | format_docs
        )
        | answer_prompt
        | llm
        | StrOutputParser()
    )

    session_store: dict = {}

    def get_session_history(session_id: str) -> ChatMessageHistory:
        if session_id not in session_store:
            session_store[session_id] = ChatMessageHistory()
        return session_store[session_id]

    app_state["chain"] = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    app_state["sessions"] = session_store
    print("Chat agent ready.")
    yield


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="Portfolio Chat Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schemas with input validation
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

    @field_validator("message")
    @classmethod
    def message_not_empty_or_too_long(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("message cannot be empty")
        if len(v) > MAX_MESSAGE_CHARS:
            raise ValueError(f"message exceeds {MAX_MESSAGE_CHARS} characters")
        return v

    @field_validator("session_id")
    @classmethod
    def session_id_safe(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 64:
            raise ValueError("invalid session_id")
        return v


class ChatResponse(BaseModel):
    answer: str
    session_id: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "chain_loaded": "chain" in app_state}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):
    # 1. Rate limit by IP
    client_ip = http_request.client.host if http_request.client else "unknown"
    if is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")

    # 2. Resolve or create session
    session_id = request.session_id or str(uuid.uuid4())

    # 3. Enforce max turns per session to prevent history bloat
    sessions = app_state.get("sessions", {})
    if session_id in sessions:
        turns = len(sessions[session_id].messages) // 2
        if turns >= MAX_TURNS_PER_SESSION:
            raise HTTPException(
                status_code=400,
                detail="Session limit reached. Please refresh to start a new conversation."
            )

    # 4. Invoke chain with retry on transient Google 500s
    last_err = None
    for attempt in range(3):
        try:
            answer = app_state["chain"].invoke(
                {"input": request.message},
                config={"configurable": {"session_id": session_id}},
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
