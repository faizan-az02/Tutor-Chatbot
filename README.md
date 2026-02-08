# AI Tutor

An **AI-powered teaching chatbot** that turns your PDFs into an interactive Q&A experience. It ingests study materials, builds a vector database i.e Chroma, retrieves relevant passages, and answers questions **grounded in your documents** via an OpenAI LLM.

---

## System overview

- **RAG:** PDFs → chunks → HuggingFace Embeddings → Chroma. Queries retrieve top-k chunks and the LLM answers from that context only.
- **Web app:** Flask serves the frontend and API. Upload PDFs in the UI, run Ingest, then chat.


---

## File structure

```
Tutor-Chatbot/
├── api.py           # Flask app: serves frontend + /api/greeting, /api/chat, upload, ingest
├── qa.py            # RAG: Chroma + HuggingFace embeddings + LLM (answer_query, get_greeting)
├── db_setup.py      # PDF ingestion → chunks → Chroma (run as subprocess by API)
├── requirements.txt # Python dependencies
├── Dockerfile       # Image: Python 3.12 + deps + app; CMD python api.py
├── .env             # GITHUB_MODEL_KEY (required); optional LANGCHAIN_* (not in repo)
├── data/            # PDFs + ingested.txt (writable)
├── chroma_db/       # Chroma vector DB (writable, created by db_setup)
└── frontend/        # Static HTML, CSS, JS (served by Flask)
```

---

## Quickstart

1. **Env:** Copy `.env.example` to `.env` and set `GITHUB_MODEL_KEY=your_key`.
2. **Deps:** `pip install -r requirements.txt`
3. **Ingest:** Put PDFs in `data/`, run `python db_setup.py`.
4. **Run:** `python api.py` → open **http://127.0.0.1:5000**

Upload PDFs in the UI and run Ingest to build/update the vector DB; then ask questions.

---

## Docker

**Build:**

```bash
docker build -t tutor-chatbot .
```

**Run (use your `.env`; port 5000 → container 8080):**

```bash
docker run -p 5000:8080 --env-file .env tutor-chatbot
```

**Run with persistent data (volumes):**

```bash
docker run -p 5000:8080 --env-file .env -v tutor-data:/app/data -v tutor-chroma:/app/chroma_db tutor-chatbot
```

- The image does **not** include your PDFs or Chroma DB (they’re in `.dockerignore` or created at runtime).
- Data lives in the container unless you use `-v`; with the volumes above, it persists across container restarts.
- See **[DOCKER-SETUP.md](DOCKER-SETUP.md)** for install and details.


## Environment variables

| Variable             | Required | Description                                  |
|----------------------|----------|----------------------------------------------|
| `GITHUB_MODEL_KEY`   | Yes      | API key for the OpenAI-compatible LLM       |
| `PORT`               | No       | Port the app listens on (default 5000; 8080 in Docker) |
| `DATA_FOLDER`       | No       | Path for PDFs and `ingested.txt` (default: project `data/`) |
| `CHROMA_PERSIST_DIR`| No       | Path for Chroma DB (default: project `chroma_db/`) |
| `LANGCHAIN_*`       | No       | LangSmith tracing (optional)                |

---

## Optional: LangSmith

To enable tracing, set in `.env`: `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`, and optionally `LANGCHAIN_ENDPOINT=https://eu.api.smith.langchain.com`. Omit these to run without tracing.

---

## Notes

- **Re-ingesting PDFs:** Clear `data/ingested.txt` if you want to re-run ingestion on the same PDFs.

