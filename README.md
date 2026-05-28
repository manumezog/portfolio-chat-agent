# Portfolio Chat Agent

A RAG (Retrieval-Augmented Generation) chat agent embedded in my personal portfolio. Visitors can ask questions about my education, professional experience, and projects — the agent answers based on my actual CV, thesis, and project documents.

Live at: [cv.manuelmezo.com](https://www.cv.manuelmezo.com)

---

## Architecture

```
Browser (chat widget)
        │  POST /chat  { message, session_id }
        ▼
FastAPI backend (api.py)
  ├── Rate limiter (10 req/min/IP)
  ├── Input validation (max 500 chars)
  ├── Session turn limit (max 20 turns)
        │
        ▼
  Contextualize chain (Gemini 2.5 Flash)
  "Rewrite question as standalone given chat history"
        │
        ▼
  Retriever → ChromaDB (local embeddings)
  "Find 4 most relevant document chunks"
        │
        ▼
  Answer chain (Gemini 2.5 Flash, max 512 tokens)
  "Answer using only retrieved context"
        │
        ▼
  { answer, session_id }
```

---

## Tech stack

| Layer | Technology |
|---|---|
| LLM | Google Gemini 2.5 Flash |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (local, no API) |
| Vector store | ChromaDB (persisted to disk) |
| RAG framework | LangChain (LCEL chains) |
| Chat memory | `RunnableWithMessageHistory` + in-memory session store |
| API | FastAPI + uvicorn |
| Frontend | Vanilla JS widget injected into static HTML portfolio |

---

## Project structure

```
portfolio-chat-agent/
├── data/                        # Source documents (CV, thesis, project examples)
├── chroma_db/                   # Persisted vector store (git-ignored)
├── portfolio_rag_pipeline.ipynb # Step-by-step learning notebook
├── api.py                       # FastAPI backend
├── chat-widget.js               # Drop-in portfolio chat widget
├── chat-widget.css              # Widget styles (dark theme)
├── requirements.txt
└── .env                         # GOOGLE_API_KEY (git-ignored)
```

---

## Learning notebook

`portfolio_rag_pipeline.ipynb` is a step-by-step Jupyter notebook that builds the full pipeline interactively. Run it before the API to understand each component in isolation.

| Section | What you learn |
|---|---|
| 1. Setup | Loading env vars, importing LangChain |
| 2. Document loading | `PyPDFLoader`, `Docx2txtLoader`, the `Document` object |
| 3. Text splitting | `RecursiveCharacterTextSplitter`, chunk size vs. overlap trade-offs |
| 4. Embeddings | What a vector is, how `embed_query` works |
| 5. Vector store | Building and persisting ChromaDB, skipping re-embedding on reload |
| 6. Retriever | Similarity search, inspecting retrieved chunks before adding the LLM |
| 7. RAG chain | LCEL pipe operator, `RunnablePassthrough.assign`, `StrOutputParser` |
| 8. Q&A | Testing the full pipeline end to end |
| 9. Next steps | — |
| 10. Chat history | `RunnableWithMessageHistory`, contextualize → retrieve → answer pattern |

To run it:
```bash
jupyter notebook portfolio_rag_pipeline.ipynb
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Add your GOOGLE_API_KEY to .env
```

### 3. Build the vector store

Run the notebook `portfolio_rag_pipeline.ipynb` cells 1–5, or run the build script:

```python
# From the notebook — sections 2, 3, 4, 5
# Uses local HuggingFace embeddings (no API key needed for this step)
```

The `chroma_db/` folder is created automatically.

### 4. Start the API

```bash
# Use your Anaconda/venv Python explicitly if needed
python -m uvicorn api:app --reload
```

API runs at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### 5. Add widget to portfolio

Copy `chat-widget.js` and `chat-widget.css` to your portfolio folder, then add before `</body>`:

```html
<link rel="stylesheet" href="chat-widget.css">
<script src="chat-widget.js"></script>
```

Update `API_URL` in `chat-widget.js` to your deployed API URL for production.

---

## API

### `POST /chat`

```json
// Request
{ "message": "What did Manuel study?", "session_id": null }

// Response
{ "answer": "Manuel studied...", "session_id": "uuid-..." }
```

Send the returned `session_id` on follow-up messages to maintain conversation history.

### `GET /health`

```json
{ "status": "ok", "chain_loaded": true }
```

---

## Security

| Threat | Protection |
|---|---|
| Token exhaustion (long inputs) | Input capped at 500 characters |
| Token exhaustion (long outputs) | LLM `max_output_tokens=512` |
| History bloat / unbounded sessions | Sessions capped at 20 turns |
| Scraping / abuse bots | Rate limit: 10 requests/min/IP (429 returned) |
| Cross-origin abuse | CORS restricted to configured origins |
| Prompt injection via session_id | session_id validated, max 64 chars |
| API key exposure | Key loaded from `.env`, never committed |

---

## LangChain concepts covered

- **Document loaders** — `PyPDFLoader`, `Docx2txtLoader`
- **Text splitting** — `RecursiveCharacterTextSplitter`
- **Embeddings** — local HuggingFace sentence-transformers
- **Vector store** — ChromaDB with similarity search
- **LCEL chains** — `RunnablePassthrough.assign`, `RunnableLambda`, pipe operator
- **Chat history** — `RunnableWithMessageHistory`, `ChatMessageHistory`
- **Conversational RAG** — contextualize question → retrieve → answer pattern

---

## Updating the knowledge base

The agent answers from the documents in `data/`. To teach it new things:

### 1. Add your documents

Drop any `.pdf` or `.docx` files into the `data/` folder. Examples:
- New CV version
- Project write-ups
- Course certificates
- Blog posts or articles (exported as PDF)

### 2. Stop the API (if running)

The ChromaDB files must not be open when you rebuild. Press `Ctrl+C` in the uvicorn terminal.

### 3. Rebuild the vector store

Run this Python script (or re-run sections 2–5 of the notebook):

```python
import os, uuid, shutil
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Load all documents from data/
docs = []
for f in os.listdir("data"):
    p = os.path.join("data", f)
    if f.endswith(".pdf"):   docs.extend(PyPDFLoader(p).load())
    elif f.endswith(".docx"): docs.extend(Docx2txtLoader(p).load())

# Split and filter empty chunks
chunks = [c for c in RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=80
).split_documents(docs) if c.page_content.strip()]
print(f"{len(chunks)} chunks")

# Embed locally and rebuild store
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
if os.path.exists("chroma_db"): shutil.rmtree("chroma_db")

texts  = [c.page_content for c in chunks]
metas  = [c.metadata     for c in chunks]
ids    = [str(uuid.uuid4()) for _ in chunks]
vectors = embeddings.embed_documents(texts)

vs = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
vs._collection.add(documents=texts, embeddings=vectors, metadatas=metas, ids=ids)
print(f"Done. {vs._collection.count()} chunks indexed.")
```

### 4. Restart the API

```bash
python -m uvicorn api:app --reload
```

That's it — the agent immediately answers from the new documents. No retraining, no model fine-tuning. This is the power of RAG: the knowledge lives in the vector store, not in the model weights.

---

## Deployment

The API is designed to run on any Python host. Recommended options for free-tier hosting:

- **Railway** — `railway up` from project root
- **Render** — connect GitHub repo, set `GOOGLE_API_KEY` env var
- **Google Cloud Run** — scales to zero, good for low traffic

After deploying, update `API_URL` in `chat-widget.js` and update `ALLOWED_ORIGINS` in `.env`.
