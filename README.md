### Teaching Chatbot

An **AI-powered teaching chatbot** that turns your PDFs into an interactive learning experience. It ingests your study materials, builds a local vector database, retrieves the most relevant passages, and answers questions **grounded in your documents**.

### Project Milestones
- **Learning-first**: turn dense course notes and textbooks into a guided Q&A experience.
- **Retrieval-Augmented Generation (RAG)**: answers are generated from retrieved context, not guesses.
- **Practical LLM engineering**: demonstrates document ingestion, chunking, embeddings, vector search, and chat completion orchestration using LangChain.

### Key features
- **PDF ingestion**
- **Chunking** for retrieval-friendly context
- **Embeddings** via **HuggingFaceEmbeddings**
- **Vector search** with **Chroma**
- **Interactive Q&A**
- **Optional tracing** via **LangSmith**

### Tech stack
- **Python**
- **LangSmith**
- **LangChain**
- **ChromaDB**
- **HuggingFace - Transformers**
- **OpenAI-compatible chat endpoint**

### Quickstart

Add your API key in `.env`:

```bash
GITHUB_MODEL_KEY=your_key_here
```

Build the database:

```bash
python db_setup.py
```

Add more PDFs anytime (grow the DB):
- Drop new `.pdf` files into the `data/` folder
- Re-run `python db_setup.py`

The script keeps `data/ingested.txt` (a simple list of already-ingested PDF filenames) so it **skips PDFs it has processed before** and only ingests the new ones.

Run the Q&A bot (terminal):

```bash
python qa.py
```

### Web frontend

To use the chat in the browser:

1. Install dependencies: `pip install -r requirements.txt`
2. Start the server: `python api.py`
3. Open **http://127.0.0.1:5000** in your browser.

The frontend is in `frontend/` (HTML, CSS, JS). The API serves it and exposes `/api/greeting`, `/api/chat`, upload, and ingest.

### Hosting (free)

To host this app on a **free** tier (Fly.io, Render, or Railway), see **[DEPLOY.md](DEPLOY.md)** for the system layout, env vars, and step-by-step instructions.

### LangSmith
LangSmith adds **tracing/observability** for your RAG pipeline (retrieval → prompt → model output). It helps you debug “why did it answer this?” by showing the retrieved chunks, prompt, latency, and errors.

To enable it:
- Create a LangSmith API key in the LangSmith UI: **Settings → API Keys → Create API Key**
- Copy `.env.example` to `.env` and fill in:

- `LANGCHAIN_API_KEY`
- `LANGCHAIN_PROJECT`

If you are using the EU LangSmith domain, set:

```bash
LANGCHAIN_ENDPOINT=https://eu.api.smith.langchain.com
```

Disable LangSmith (optional): you can comment out/remove the `LANGCHAIN_*` variables and the app will run normally; tracing will simply be off.

### Notes
- **Windows:** If you see `OSError: [WinError 1114] ... c10.dll` when running `python db_setup.py`, install [Microsoft Visual C++ Redistributable (x64)](https://aka.ms/vs/17/release/vc_redist.x64.exe), then try again.
- The embedding model may download from HuggingFace on first run; ensure your network/DNS allows access to `huggingface.co`.
- Answers are intended to be **document-grounded**—if the context doesn’t contain the answer, the bot should say it doesn’t know.
- **YouTube links:** To let the bot fetch YouTube links when asked, install `ddgs`: `pip install ddgs`.
- **Re-ingesting PDFs:** To re-run ingestion on the same PDFs, clear `data/ingested.txt` otherwise the system skips them.
