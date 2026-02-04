import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


# Load environment variables

load_dotenv()
GITHUB_KEY = os.getenv("GITHUB_MODEL_KEY")


# Initialize LLM (GitHub GPT-5)

_BASE_URL = "https://models.inference.ai.azure.com"
_MODEL = "gpt-4o-mini"
llm = ChatOpenAI(model=_MODEL, temperature=0.2, api_key=GITHUB_KEY, base_url=_BASE_URL)


# Deduplication function

def deduplicate_docs(docs, preview_len=200):
    unique_docs = []
    seen = set()
    for d in docs:
        key = "".join(filter(str.isalnum, d.page_content.lower()))[:preview_len]
        if key not in seen:
            seen.add(key)
            unique_docs.append(d)
    return unique_docs


def safe_print(text: str) -> None:
    """Print without crashing on Windows console encodings (e.g., cp1252)."""
    s = text if isinstance(text, str) else str(text)
    try:
        print(s)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "utf-8"
        print(s.encode(enc, errors="replace").decode(enc, errors="replace"))


def clear_screen() -> str:
    """Clear the terminal screen; returns empty string for print()."""
    os.system("cls" if os.name == "nt" else "clear")
    return ""


# Load chroma database

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding_model
)

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

print(clear_screen())

print('\r\n', '='*50, '\r\n', 'Welcome to the AI-Powered Neural Networks Learning Bot!', '\r\n', '='*50, '\r\n')

query = ""
initial_prompt = "Greet the user and ask what do they want to learn about neural networks today using a chatbot which is an expert in neural networks and you are the chatbot, dont mention the word chatbot or bot or anything like that."

response = llm.invoke(
    [HumanMessage(content=initial_prompt)],
    config={
    "run_name": "generate_answer",
    "metadata": {"model": _MODEL},
    },
)
answer = response.content

safe_print(answer +'\n')

while (True):

    query = input("Enter your query, exit to quit: ")

    if query == "exit":
        break

    raw_docs = retriever.invoke(
        query,
        config={
            "run_name": "retrieve",
            "tags": ["docs-qa", "rag", "retrieval"],
            "metadata": {"k": 5, "query": query},
        },
    )
    docs = deduplicate_docs(raw_docs)

    print(f"Number of chunks: {len(docs)} obtained")


    # Build context for LLM

    context = "\n\n".join(
        f"[Source: {d.metadata.get('book_name', 'unknown')}]\n{d.page_content}"
        for d in docs
    )

    prompt = f"""
    You are an expert in neural networks. Answer the question strictly using the context below.
    Do NOT use any external knowledge. If the answer is not in the context, say you do not know.

    Context:
    {context}

    Question:
    {query}

    Answer concisely and clearly and ask if the user wants to know more about the topic, like a teacher would. Just apologize ONLY if you don't know the answer and ask if they want to learn something else about Neural Networks.
    """

    # Generate answer using the LLM

    response = llm.invoke(
        [HumanMessage(content=prompt)],
        config={
            "run_name": "generate_answer",
            "tags": ["docs-qa", "rag", "llm"],
            "metadata": {"model": _MODEL},
        },
    )
    answer = response.content

    print("\n=== ANSWER ===")
    safe_print(answer +'\n')
