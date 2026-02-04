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

### Tech stack
- **Python**
- **LangChain**
- **ChromaDB**
- **HuggingFace - Transformers**
- **OpenAI-compatible chat endpoint**

### Quickstart

Add your API key in `.env`:

```bash
GITHUB_GPT5_KEY= your key here
```

Build the database:

```bash
python db_setup.py
```

Run the Q&A bot:

```bash
python qa.py
```

### Notes
- The embedding model may download from HuggingFace on first run; ensure your network/DNS allows access to `huggingface.co`.
- Answers are intended to be **document-grounded**—if the context doesn’t contain the answer, the bot should say it doesn’t know.