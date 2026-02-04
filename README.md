### Neural Networks Learning Bot

A **AI-powered PDF Q&A bot** designed to help learners understand **Neural Networks end-to-end**, with a focus on **Artificial Neural Networks (ANNs)**. It ingests your study PDFs, builds a local vector database, retrieves the most relevant passages, and answers questions **grounded in your documents**.

### Project Milestones
- **Learning-first**: turn dense NN/ANN PDFs into an interactive study experience.
- **Retrieval-Augmented Generation (RAG)**: answers are generated from retrieved context, not guesses.
- **Practical LLM engineering**: demonstrates document ingestion, chunking, embeddings, vector search, and chat completion orchestration using LangChain.

### Key features
- **PDF ingestion** from **PDFs**
- **Chunking**
- **Embeddings** via **HuggingFaceEmbeddings**
- **Vector search** with **Chroma**
- **Interactive QA loop**
- **Tracing via LangSmith**

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

Run the Q&A bot:

```bash
python qa.py
```

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
- The embedding model may download from HuggingFace on first run; ensure your network/DNS allows access to `huggingface.co`.
- Answers are intended to be **document-grounded**—if the context doesn’t contain the answer, the bot should say it doesn’t know.