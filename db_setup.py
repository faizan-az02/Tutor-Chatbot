from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import os
from langchain_huggingface import HuggingFaceEmbeddings


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
print()

splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=50)
all_chunks = []
for doc in documents:
    chunks = splitter.split_documents([doc])
    all_chunks.extend(chunks)

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vectorstore = Chroma.from_documents(
    documents=all_chunks,
    embedding=embedding_model,
    persist_directory="./chroma_db"
)
vectorstore.persist()