# Cirix

Chat with PDFs, websites, and YouTube videos from one place.

A RAG (Retrieval-Augmented Generation) system built on LangChain's LCEL (LangChain Expression Language), with a hand-written ingestion and chunking layer feeding into a composed, runnable chain, wrapped in a clean, terminal-minimal, mobile-responsive UI.

**Live:** [cirix.vercel.app](https://cirix.vercel.app)

---

## What it does

Upload a PDF, paste a website URL, or drop a YouTube link, and Cirix extracts the content, breaks it into chunks, embeds them, and stores them in a vector database. Ask a question in plain English, and Cirix retrieves the most relevant chunks across all your sources at once and asks an LLM to answer using only that material, citing exactly which source and location (page number, URL, or timestamp) each claim came from.

Three completely different content types, a PDF, a webpage, a video transcript, all flow through one identical ingestion pipeline and land in one composed LCEL chain for retrieval and generation. That convergence is the core architectural idea behind this project.

A session starts with a clean slate: landing on the app shows a short walkthrough of how it works, and starting a session clears any previous sources before you upload anything new, so every demo run is isolated and predictable.

---

## Architecture

### Ingestion (hand-written adapters, shared chunking)

```
Raw Input (PDF / URL / YouTube link)
        │
        ▼
Adapter extracts raw text + metadata   (pdf.py / website.py / youtube.py)
        │
        ▼
Chunker (shared, sentence-aware)       (chunker.py, PDF & website only)
        │
        ▼
LangChain Chroma vector store          (vector_store.py, embeds + stores in one step)
```

Every source type reduces to the same shape, `{ source_id, chunks: [str], metadatas: [dict] }`, the moment it leaves its adapter. From there, `vector_store.add_chunks()` hands raw text straight to a `langchain_chroma.Chroma` instance, which embeds and stores it internally using a shared Gemini embeddings model. YouTube's adapter groups transcript snippets differently than the shared sentence-chunker (captions arrive as many small pre-timestamped fragments, not one continuous block of text) so that each chunk keeps an accurate timestamp. This is the one deliberate deviation from the shared chunking path.

### Retrieval + generation (LCEL chain)

```
Question
   │
   ▼
Retriever (Chroma .as_retriever(), top-k similarity search)
   │
   ▼
Context blocks + citation labels built from retrieved chunks
   │
   ▼
LCEL chain:  ChatPromptTemplate | ChatGoogleGenerativeAI | StrOutputParser
   │           (wrapped in RunnableWithMessageHistory for per-session memory)
   ▼
Cited answer + citations list
```

This is the "runnables and chains" part of the project: `app/rag/chain.py` composes a prompt template, the Gemini chat model, and an output parser into a single LCEL pipeline using the `|` operator, then wraps it with `RunnableWithMessageHistory` so each `session_id` automatically gets its own conversation memory, with no manual history-passing required at the call site.

---

## Tech stack

### Frontend
- Next.js 15 (App Router) + TypeScript
- Tailwind CSS v4, mobile-responsive layout (slide-out drawers for sources/citations on small screens)
- Axios

### Backend
- FastAPI + Uvicorn + Pydantic

### AI / RAG (LangChain)
- **Orchestration:** LangChain (LCEL), `langchain`, `langchain-core`
- **LLM:** Gemini 2.5 Flash via `langchain-google-genai` (`ChatGoogleGenerativeAI`), free tier
- **Embeddings:** Gemini's embedding API via `langchain-google-genai`'s `GoogleGenerativeAIEmbeddings` (`gemini-embedding-001`, 768 dimensions), free tier, no local model loaded
- **Vector store:** `langchain-chroma`, LangChain's official wrapper around ChromaDB, embedding and storage handled in one step
- **Memory:** `RunnableWithMessageHistory` with a custom TTL-pruned, in-memory chat history store (per `session_id`, auto-expires after 1 hour of inactivity)

### Document processing (hand-written, framework-free)
- **PDF:** PyMuPDF (`fitz`)
- **Website:** Trafilatura (primary) with a BeautifulSoup4 fallback if Trafilatura returns nothing
- **YouTube:** `youtube-transcript-api`, captions only, no audio transcription. Videos without captions return a clean "no captions available" error rather than failing silently.

### Deployment
- **Backend:** Render (free tier), kept awake via a scheduled GitHub Actions workflow pinging `/health` every 10 minutes
- **Frontend:** Vercel

**Everything above is free.** No paid APIs, no paid hosting required to run or demo this project.

---

## Why these specific choices

- **LCEL over manual prompt-building:** composing `prompt | llm | output_parser` with the `|` operator gives a declarative, inspectable pipeline instead of imperative glue code, and `RunnableWithMessageHistory` handles per-session memory without hand-rolling a history dictionary.
- **Gemini embeddings over a locally-loaded HuggingFace model:** the project originally used a local `sentence-transformers` model (`bge-small-en-v1.5`), which works well on a laptop but requires `torch` and pulls in several hundred MB of dependencies, too heavy for a 512MB free-tier deployment container. Switching to Gemini's own embedding API keeps everything free while removing the local-model memory footprint entirely, at the cost of no longer being fully offline.
- **Gemini 2.5 Flash over Gemini Pro:** Pro models moved to a paid-only tier in April 2026; Flash remains free with a reasonable rate limit and is more than capable of answering from retrieved context rather than doing deep multi-step reasoning.
- **ChromaDB (via `langchain-chroma`) over a hosted vector DB:** file-based and zero-config, so the entire project runs without an external database dependency.
- **Hand-written ingestion adapters, not LangChain's document loaders:** PDF/website/YouTube extraction is simple enough to own directly, keeping the ingestion layer fully transparent while still getting LangChain's benefit where it matters most, composing the retrieval-and-generation chain.
- **Sentence-aware chunking over naive character splitting:** a hand-written recursive chunker that tries to avoid cutting mid-sentence, used for PDF and website content.
- **GitHub Actions keep-alive over a third-party pinger:** Render's free tier spins down after 15 minutes of inactivity; a scheduled workflow living in the same repo keeps the backend awake without an external account, and doubles as a small piece of deployment automation worth explaining on its own.

---

## Project structure

```
cirix/
├── .github/
│   └── workflows/
│       └── keep-alive.yml    # scheduled ping to keep the Render backend awake
├── backend/
│   ├── app/
│   │   ├── api/            # upload.py, chat.py, sources.py - FastAPI routes
│   │   ├── ingestion/       # pdf.py, website.py, youtube.py, chunker.py
│   │   ├── embeddings/      # embedder.py, vector_store.py (LangChain-backed)
│   │   ├── rag/             # retriever.py, prompt.py, chain.py (LCEL)
│   │   ├── models/          # Pydantic schemas
│   │   ├── main.py
│   │   └── config.py
│   ├── uploads/              # temp storage for uploaded PDFs
│   ├── chroma_db/            # ChromaDB persistent storage
│   └── requirements.txt
│
└── frontend/
    ├── app/                  # page.tsx, layout.tsx, globals.css
    ├── components/           # SourceSidebar, ChatPanel, CitationPanel, WelcomeModal, etc.
    ├── hooks/                 # useSources.ts, useChat.ts
    ├── services/              # api.ts
    └── types/
```

---

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/upload/pdf` | Upload and ingest a PDF |
| POST | `/upload/website` | Add and ingest a website URL |
| POST | `/upload/youtube` | Add and ingest a YouTube URL |
| POST | `/chat` | Ask a question, get a cited answer (LCEL chain, session-aware) |
| GET | `/sources` | List all ingested sources |
| DELETE | `/sources/{id}` | Remove one source and its chunks |
| DELETE | `/sources` | Clear all sources, used for "start new session" |
| GET | `/health` | Health check, also used to keep the deployed backend awake |

---

## Design decisions worth calling out

**Session memory is intentionally simple.** `session_id` is a client-generated UUID with no authentication behind it. It exists purely to give `RunnableWithMessageHistory` a key to look up each conversation's history, not as a security boundary. History is capped at the last 5 exchanges per session and auto-expires after an hour of inactivity, so idle sessions don't accumulate in server memory indefinitely. All memory is lost on server restart; there is no database-backed persistence in v1, by design.

**Every upload gets a fresh `source_id`, with no deduplication.** Uploading the same file twice creates two separate entries. A "start new session" flow, shown as a welcome screen on first load and also available mid-app, clears all sources at once before a fresh batch of uploads, rather than deduplicating automatically.

**No user isolation, by design.** There is no concept of separate users; all uploaded sources and all chat sessions share one global ChromaDB collection, and the welcome screen's reset clears state globally. This makes the app effectively single-user at a time, which is an accepted, explicit tradeoff for a public demo, not something that would be appropriate for a real multi-user deployment without adding real session/user scoping first.

**Embeddings moved from local to API-based partway through the project.** The switch from a locally-loaded HuggingFace model to Gemini's embedding API was driven directly by deployment constraints (Render's free tier caps memory at 512MB, torch-based local models routinely exceed that even before handling a request), not a change in local development experience. Both approaches are valid; this project favors the one that actually fits the target hosting environment.

---

## Local setup

### Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:
```
GEMINI_API_KEY=your_key_here
```
Get a free key from [Google AI Studio](https://aistudio.google.com/apikey). This key is required for both the chat model and the embeddings API.

Run it:
```powershell
uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`. The backend must be running on port 8000 for the frontend to work.

---

## Known limitations / future work

Explicitly out of scope for v1, listed here rather than built:

- **Reranking** (e.g. `bge-reranker-base`): retrieval currently relies on raw embedding similarity only
- **Hybrid search** (BM25 + semantic): semantic-only retrieval for now
- **Auth / multi-user support:** single shared global state, no login
- **Persistent chat history across sessions:** in-memory only, cleared on server restart
- **Content-hash deduplication on upload:** re-uploading the same file creates a duplicate entry rather than being detected and skipped
- **Streaming token-by-token responses:** answers currently return as a single completed response
- **Real YouTube video titles:** currently uses a placeholder label (`YouTube video (video_id)`) rather than fetching the actual title, to avoid requiring a YouTube Data API key
- **Migrating off `RunnableWithMessageHistory`:** it works correctly today but is deprecated as of LangChain 1.3.3 in favor of LangGraph's built-in persistence; not urgent since it isn't removed until LangChain 2.0.0
- **Fully offline embeddings:** the current Gemini-based embeddings require network access and a valid API key; a local, memory-light embedding runtime (e.g. `fastembed`) would restore offline capability if a larger deployment memory budget isn't available