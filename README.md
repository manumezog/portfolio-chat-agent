---
title: Portfolio Chat Agent
emoji: 💬
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Portfolio Chat Agent

A RAG (Retrieval-Augmented Generation) chat agent embedded in my personal portfolio. Visitors can ask questions about my education, professional experience, and projects — the agent answers based on my actual CV, thesis, and project documents.

Live at: [cv.manuelmezo.com](https://www.cv.manuelmezo.com)  
API: [manumezog-portfolio-chat-agent.hf.space](https://manumezog-portfolio-chat-agent.hf.space)  
HF Space: [huggingface.co/spaces/manumezog/portfolio-chat-agent](https://huggingface.co/spaces/manumezog/portfolio-chat-agent)

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
├── chroma_db/                   # Persisted vector store
├── portfolio_rag_pipeline.ipynb # Step-by-step learning notebook
├── api.py                       # FastAPI backend
├── chat-widget.js               # Drop-in portfolio chat widget
├── chat-widget.css              # Widget styles (dark theme)
├── Dockerfile                   # HF Spaces Docker deployment
├── requirements.txt
└── .env.example                 # GOOGLE_API_KEY template
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

## Setup (local)

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

Run sections 2–5 of the notebook, or use the rebuild script in the **Updating the knowledge base** section below.

### 4. Start the API

```bash
python -m uvicorn api:app --reload
```

API runs at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### 5. Add widget to portfolio

Copy `chat-widget.js` and `chat-widget.css` to your portfolio folder, then add before `</body>`:

```html
<link rel="stylesheet" href="chat-widget.css">
<script src="chat-widget.js"></script>
```

Update `API_URL` in `chat-widget.js` to your deployed API URL.

---

## Deployment (HF Spaces)

**Live deployment:** [huggingface.co/spaces/manumezog/portfolio-chat-agent](https://huggingface.co/spaces/manumezog/portfolio-chat-agent)  
**API endpoint:** `https://manumezog-portfolio-chat-agent.hf.space/chat`

The Docker image builds ChromaDB from `knowledge_base.json` at image build time — no binary files in git. On every push to the `hf-deploy` branch, HF Spaces automatically rebuilds and redeploys.

To deploy your own fork:
1. Create a new Space on [huggingface.co](https://huggingface.co) with SDK = Docker
2. Add `GOOGLE_API_KEY` as a Space secret (Settings → Variables and secrets)
3. Push this repo to the Space remote

The container exposes port 7860 as required by HF Spaces.

> **Note:** Free tier Spaces sleep after 48h of inactivity. The first request after sleep takes ~30s to cold-start.

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
| API key exposure | Key loaded from `.env` / HF Space secret, never committed |

---

## Updating the knowledge base

The agent answers from the documents in `data/`. To teach it new things:

### 1. Add your documents

Drop any `.pdf` or `.docx` files into the `data/` folder.

### 2. Stop the API (if running)

### 3. Rebuild the vector store

```python
import os, uuid, shutil
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

docs = []
for f in os.listdir("data"):
    p = os.path.join("data", f)
    if f.endswith(".pdf"):   docs.extend(PyPDFLoader(p).load())
    elif f.endswith(".docx"): docs.extend(Docx2txtLoader(p).load())

chunks = [c for c in RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=80
).split_documents(docs) if c.page_content.strip()]

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

### 4. Commit chroma_db and redeploy

```bash
git add chroma_db/
git commit -m "Update knowledge base"
git push
```

HF Spaces rebuilds the Docker image automatically on push.

---

## LangChain concepts covered

- **Document loaders** — `PyPDFLoader`, `Docx2txtLoader`
- **Text splitting** — `RecursiveCharacterTextSplitter`
- **Embeddings** — local HuggingFace sentence-transformers
- **Vector store** — ChromaDB with similarity search
- **LCEL chains** — `RunnablePassthrough.assign`, `RunnableLambda`, pipe operator
- **Chat history** — `RunnableWithMessageHistory`, `ChatMessageHistory`
- **Conversational RAG** — contextualize question → retrieve → answer pattern
