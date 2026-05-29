---
title: Portfolio Chat Agent
emoji: 💬
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Portfolio Chat Agent

A RAG (Retrieval-Augmented Generation) chat agent embedded in my personal portfolio. Visitors can ask questions about my education, professional experience, and projects — the agent answers based on carefully curated knowledge documents, not LLM memory.

Live at: [cv.manuelmezo.com](https://www.cv.manuelmezo.com)  
API: [manumezog-portfolio-chat-agent.hf.space](https://manumezog-portfolio-chat-agent.hf.space) · [Interactive API docs](https://manumezog-portfolio-chat-agent.hf.space/docs)  
HF Space: [huggingface.co/spaces/manumezog/portfolio-chat-agent](https://huggingface.co/spaces/manumezog/portfolio-chat-agent)  
Portfolio page: [portfolio-chat-agent-project.html](https://www.cv.manuelmezo.com/portfolio-chat-agent-project.html)

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
  "Find 8 most relevant knowledge chunks"
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
| Embeddings | `BAAI/bge-small-en-v1.5` (local, no API — ~25% better retrieval than MiniLM) |
| Vector store | ChromaDB (persisted to disk) |
| RAG framework | LangChain (LCEL chains) |
| Chat memory | `RunnableWithMessageHistory` + in-memory session store |
| API | FastAPI + uvicorn |
| Frontend | Vanilla JS widget injected into static HTML portfolio |

---

## Knowledge base design

The agent's quality depends entirely on the quality of the indexed content. After an initial version that gave poor answers (built from presentation slides only), the knowledge base was redesigned from scratch.

### Input documents (`data - copia/`)

| File | Type | Purpose |
|---|---|---|
| `professional_experience_stories.md` | Synthetic | 17 professional STAR stories in clean prose, with metadata headers (Company, Year, Skills). Replaces a raw interview-prep DOCX. |
| `professional_summary.md` | Synthetic | ~600-word narrative bio — career arc, what he brings, target roles. |
| `technical_skills.md` | Synthetic | Structured skills taxonomy with evidence per skill. |
| `personality_and_approach.md` | Synthetic | 7 sections on working style and soft skills, each backed by a real story. |
| `side_projects.md` | Synthetic | Descriptions of all 15+ portfolio projects. |
| CV PDFs | Source | Two CV variants (Applied AI, Physical AI). |
| Thesis PDFs | Source | Full thesis reports (MSc, two BSc). Full documents, not just slides. |

> **Source PDFs and DOCX are gitignored** — they contain personal data and are large. `knowledge_base.json` is the pre-processed artifact used for deployment.

### Why this matters: the "garbage in, garbage out" problem

The original version indexed presentation slides (PDFs of PPTs). These are bullet-point fragments with almost no prose — they produce incoherent retrieval chunks. The original STAR interview-prep document was also in rough notes format with no structure. The 500-character blind chunker would cut mid-story, producing chunks with no company, no context, and no result.

**Result:** questions like *"Tell me about a time you dealt with a difficult stakeholder"* returned fragments like *"Additionally he handled with 'brio' this cross-functional project..."* — useless without context.

**Fix:** hand-authored documents designed for retrieval:
- Each STAR story is a self-contained prose unit with company/skills metadata embedded
- Synthetic summaries answer cross-cutting questions ("What is Manuel's working style?") that no single CV chunk can answer
- Story-level chunking preserves narrative coherence instead of splitting mid-sentence

### Chunking strategy

```
prepare_knowledge_base.py
  ├── Markdown files → split on "---" story separators (semantic chunking)
  │     Each story/section stays as one chunk (max 1800 chars)
  │     Falls back to RecursiveCharacterTextSplitter only if section is too long
  └── PDF files → RecursiveCharacterTextSplitter(chunk_size=1200, overlap=150)
        Larger than typical (was 500) — narrative text needs more context per chunk
```

Result: **1,042 chunks** from 10 source files. Story chunks carry structured metadata (`title`, `company`, `skills`, `year`) for potential filtered retrieval.

---

## Project structure

```
portfolio-chat-agent/
├── data - copia/                   # Knowledge source documents
│   ├── professional_experience_stories.md   # 17 STAR stories
│   ├── professional_summary.md              # Narrative bio
│   ├── technical_skills.md                  # Skills taxonomy
│   ├── personality_and_approach.md          # Working style
│   └── side_projects.md                     # Portfolio projects
├── prepare_knowledge_base.py       # Builds knowledge_base.json from data - copia/
├── build_db.py                     # Builds chroma_db from knowledge_base.json (Docker)
├── portfolio_rag_pipeline.ipynb    # Step-by-step learning notebook
├── api.py                          # FastAPI backend
├── chat-widget.js                  # Drop-in portfolio chat widget
├── chat-widget.css                 # Widget styles (dark theme)
├── Dockerfile                      # HF Spaces Docker deployment
├── requirements.txt
└── .env.example                    # GOOGLE_API_KEY template
```

---

## Updating the knowledge base

### 1. Edit source documents

Add or edit files in `data - copia/`. The markdown files are the primary knowledge source — edit them directly.

- For new professional stories: follow the `## Title` + `**Company/Year/Skills**` + S/T/A/R prose format in `professional_experience_stories.md`, separated by `---`
- For new projects: add a `---`-delimited section to `side_projects.md`

### 2. Rebuild `knowledge_base.json`

```bash
python prepare_knowledge_base.py
```

This loads all `.md` and `.pdf` files from `data - copia/`, applies smart chunking, strips personal contact info from PDF chunks, and writes `knowledge_base.json`.

### 3. Deploy to HF Spaces

`knowledge_base.json` is gitignored on GitHub (contains document text). Push to HF separately via the `hf-deploy` orphan branch:

```bash
git checkout hf-deploy
git add -f knowledge_base.json        # force-add the gitignored file
git add api.py build_db.py Dockerfile requirements.txt prepare_knowledge_base.py \
        "data - copia/professional_experience_stories.md" \
        "data - copia/professional_summary.md" \
        "data - copia/technical_skills.md" \
        "data - copia/personality_and_approach.md" \
        "data - copia/side_projects.md"
git commit -m "Deploy: update knowledge base"
git push hf hf-deploy:main --force    # HF builds from main, not master
git checkout master
```

HF Spaces rebuilds the Docker image automatically, running `build_db.py` to reconstruct ChromaDB from the JSON.

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

### 3. Build the knowledge base and vector store

```bash
python prepare_knowledge_base.py   # generates knowledge_base.json
python build_db.py                 # builds chroma_db/ from the JSON
```

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

The Docker image builds ChromaDB from `knowledge_base.json` at image build time — no binary files needed in git. HF Spaces builds from the `main` branch (not `master`).

To deploy your own fork:
1. Create a new Space on [huggingface.co](https://huggingface.co) with SDK = Docker
2. Add `GOOGLE_API_KEY` as a Space secret (Settings → Variables and secrets)
3. Add a remote: `git remote add hf https://huggingface.co/spaces/YOUR_USER/YOUR_SPACE`
4. Push: `git push hf YOUR_BRANCH:main`

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
| Personal data exposure | Phone/email stripped from CV chunks; source PDFs gitignored |

---

## Learning notebook

`portfolio_rag_pipeline.ipynb` is a step-by-step Jupyter notebook that builds the full pipeline interactively.

| Section | What you learn |
|---|---|
| 1. Setup | Loading env vars, importing LangChain |
| 2. Document loading | `PyPDFLoader`, `TextLoader`, the `Document` object |
| 3. Text splitting | `RecursiveCharacterTextSplitter`, chunk size vs. overlap trade-offs |
| 4. Embeddings | What a vector is, how `embed_query` works |
| 5. Vector store | Building and persisting ChromaDB |
| 6. Retriever | Similarity search, inspecting retrieved chunks |
| 7. RAG chain | LCEL pipe operator, `RunnablePassthrough`, `StrOutputParser` |
| 8. Q&A | Testing the full pipeline end to end |
| 10. Chat history | `RunnableWithMessageHistory`, contextualize → retrieve → answer pattern |

```bash
jupyter notebook portfolio_rag_pipeline.ipynb
```

---

## LangChain concepts covered

- **Document loaders** — `PyPDFLoader`, `TextLoader`
- **Text splitting** — `RecursiveCharacterTextSplitter`, semantic story-level splitting
- **Embeddings** — local HuggingFace sentence-transformers
- **Vector store** — ChromaDB with similarity search and metadata
- **LCEL chains** — `RunnablePassthrough.assign`, pipe operator
- **Chat history** — `RunnableWithMessageHistory`, `ChatMessageHistory`
- **Conversational RAG** — contextualize question → retrieve → answer pattern
- **Knowledge base design** — synthetic documents, chunking strategy, metadata enrichment
