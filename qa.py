import os
import sys
import itertools
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


def is_external_resource_request(user_query: str) -> bool:
    """
    Heuristic: detect when the user is asking for YouTube links / external resources.
    This is handled outside the "context-only" document QA flow.
    """
    q = (user_query or "").strip().lower()
    if not q:
        return False

    if "youtube" in q:
        return True

    # Catch common phrasing like "video links", "external resources", etc.
    triggers = (
        "video link",
        "video links",
        "youtube link",
        "youtube links",
        "external resource",
        "external resources",
        "resources",
        "links",
    )
    return any(t in q for t in triggers) and ("link" in q or "resource" in q or "video" in q)


def search_youtube_links(topic: str, max_results: int = 5):
    """
    Try to web-search YouTube links for a topic using DuckDuckGo.

    Returns:
      - list[dict] on success (each dict: title, href/url, body/snippet)
      - None if web search isn't available in this environment
    """
    try:
        # New package name (preferred).
        from ddgs import DDGS  # type: ignore[import-not-found]
    except Exception:
        try:
            # Backward-compatible fallback (older installs).
            from duckduckgo_search import DDGS  # type: ignore[import-not-found]  # optional dependency
        except Exception:
            return None

    q = f"site:youtube.com {topic}".strip()
    try:
        with DDGS() as ddgs:
            results_iter = ddgs.text(q, safesearch="moderate")
            return list(itertools.islice(results_iter, max_results))
    except Exception:
        # If DDG blocks or network fails, treat as unavailable.
        return None


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

print('\r\n', '='*50, '\r\n', 'Welcome to the AI-Powered Personal Tutor!', '\r\n', '='*50, '\r\n')

query = ""
initial_prompt = "Greet the user and ask what do they want to learn today using you, which is a teaching chatbot, dont mention the word chatbot or bot or anything like that."

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

    if is_external_resource_request(query):
        results = search_youtube_links(query, max_results=5)

        print("\n=== ANSWER ===")
        if results:
            lines = [
                "Here are some YouTube results you can start with:",
                "",
            ]
            for r in results:
                title = (r.get("title") or "YouTube result").strip()
                href = (r.get("href") or r.get("url") or "").strip()
                if href:
                    lines.append(f"- {title}\n  {href}")
                else:
                    lines.append(f"- {title}")

            lines.append("")
            lines.append("Want to ask a question from your PDFs on this topic?")
            safe_print("\n".join(lines) + "\n")
        else:
            # Be transparent: this script can't always browse the web, depending on environment/deps.
            safe_print(
                "I can’t fetch live YouTube links from this environment right now.\n\n"
                "Try searching YouTube with one of these queries:\n"
                f"- \"{query}\"\n"
                f"- \"{query} explained\"\n"
                f"- \"{query} tutorial\"\n\n"
                "If you want, ask a question from your PDFs and I’ll answer from the provided content.\n"
            )
        continue

    raw_docs = retriever.invoke(
        query,
        config={
            "run_name": "retrieve",
            "tags": ["docs-qa", "rag", "retrieval"],
            "metadata": {"k": 5, "query": query},
        },
    )
    docs = deduplicate_docs(raw_docs)

    # Build context for LLM

    context = "\n\n".join(
        f"[Source: {d.metadata.get('book_name', 'unknown')}]\n{d.page_content}"
        for d in docs
    )

    prompt = f"""
    You are a teaching chatbot. Help the user learn and understand the material.

    Rules:
    - Answer the question using ONLY the context below.
    - Do NOT use external knowledge.
    - If the answer is not present in the context, say you do not know - apologize only in this case.
    - Keep the conversation strictly study-related; if the user goes off-topic, redirect them back to studying.
    - If the user asks for YouTube links or any other external resources, you will search and provide links.

    Context:
    {context}

    Question:
    {query}

    Response style:
    - Be concise and clear.
    - After answering, ask if they want to learn more about the topic - like a teacher would.
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
