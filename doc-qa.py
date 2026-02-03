from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings


data_folder = "data/"
documents = []
i = 0  # page counter across all PDFs

pdf_files = sorted([f for f in os.listdir(data_folder) if f.lower().endswith(".pdf")])
pdf_count = 0

for file in pdf_files:
    pdf_count += 1
    loader = PyPDFLoader(os.path.join(data_folder, file))

    # Prefer streaming pages for realtime progress when available.
    iterable = loader.lazy_load() if hasattr(loader, "lazy_load") else loader.load()

    for doc in iterable:
        i += 1
        doc.metadata["book_name"] = os.path.splitext(file)[0]
        documents.append(doc)

        print(
            f"Loaded {i} pages | PDFs {pdf_count}/{len(pdf_files)} | {file}",
            end="\r",
            flush=True,
        )

print(f"Loaded {i} pages from {pdf_count} PDFs".ljust(120), flush=True)
print(type(documents))