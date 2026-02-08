from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
import os
from langchain_huggingface import HuggingFaceEmbeddings

def clear_screen() -> str:
    """Clear the terminal screen; returns empty string for print()."""
    os.system("cls" if os.name == "nt" else "clear")
    return ""

_project_root = os.path.dirname(os.path.abspath(__file__))
data_folder = os.environ.get("DATA_FOLDER", os.path.join(_project_root, "data"))
if not data_folder.endswith(os.sep):
    data_folder = data_folder + os.sep
persist_directory = os.environ.get("CHROMA_PERSIST_DIR", os.path.join(_project_root, "chroma_db"))
documents = []
i = 0

print(clear_screen())

pdf_files = sorted([f for f in os.listdir(data_folder) if f.lower().endswith(".pdf")])
ingested_pdf_names = []
ingested_path = os.path.join(data_folder, "ingested.txt")

already_ingested = set()

if os.path.exists(ingested_path):
    with open(ingested_path, "r", encoding="utf-8") as f:
        already_ingested = {line.strip() for line in f.read().splitlines() if line.strip()}

if len(pdf_files) == len(already_ingested):
    print("All PDFs already ingested")
    exit()

pdf_count = 0

for file in pdf_files:

    if file in already_ingested:

        continue

    pdf_count += 1

    ingested_pdf_names.append(file)

    loader = PyPDFLoader(os.path.join(data_folder, file))

    iterable = loader.lazy_load()

    for doc in iterable:
        i += 1
        doc.metadata["book_name"] = os.path.splitext(file)[0]
        documents.append(doc)

        print(
            f"Loaded {i} pages | PDFs {pdf_count}/{len(pdf_files)} | {file}",
            end="\r",
            flush=True,
        )

print(f"Loaded {i} pages from {pdf_count} PDFs, skipped {len(pdf_files) - pdf_count} PDFs already ingested.".ljust(120), flush=True)

if ingested_pdf_names:

    with open(ingested_path, "a", encoding="utf-8") as f:
        for name in ingested_pdf_names:
            f.write(name + "\n")

splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=50)
all_chunks = []
for doc in documents:
    chunks = splitter.split_documents([doc])
    all_chunks.extend(chunks)

embedding_model = None

if (len(all_chunks) > 0):

    print("Generating embeddings...")

    # Use BAAI/bge-small-en-v1.5 (avoids 404 on additional_chat_templates with recent transformers).
    embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

else:
    print("No data found")

if (embedding_model is not None):

    print("Populating chroma database...")

    vectorstore = Chroma.from_documents(
        documents=all_chunks,
        embedding=embedding_model,
        persist_directory=persist_directory,
    )

    print("Chroma database populated successfully")
else:
    print("No embeddings found")

