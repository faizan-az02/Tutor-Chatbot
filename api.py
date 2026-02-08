"""
Flask API for the Tutor Chatbot. Serves the frontend and exposes /api/greeting, /api/chat, upload + ingest.
Run: python api.py
Then open http://127.0.0.1:5000 in a browser.
"""
import os
import re
import sys
import subprocess
import json
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Import after env is loaded (api.py is run from project root)
from qa import get_greeting, answer_query

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(PROJECT_ROOT, "data")
ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename):
    return filename and filename.lower().endswith(".pdf")


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)


@app.route("/api/greeting", methods=["GET"])
def greeting():
    try:
        text = get_greeting()
        return jsonify({"greeting": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    query = (data.get("query") or "").strip()
    if not query:
        return jsonify({"answer": "Please ask a question.", "youtube_links": None})
    try:
        result = answer_query(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({"answer": f"Error: {e}", "youtube_links": None}), 500


@app.route("/api/upload-pdfs", methods=["POST"])
def upload_pdfs():
    if "files" not in request.files and "file" not in request.files:
        return jsonify({"error": "No files", "saved": []}), 400
    files = request.files.getlist("files") if request.files.getlist("files") else [request.files["file"]]
    saved = []
    for f in files:
        if not f or f.filename == "":
            continue
        if not allowed_file(f.filename):
            continue
        name = secure_filename(f.filename)
        path = os.path.join(DATA_FOLDER, name)
        try:
            f.save(path)
            saved.append(name)
        except Exception as e:
            return jsonify({"error": str(e), "saved": saved}), 500
    return jsonify({"saved": saved})


def _strip_ansi(line: str) -> str:
    """Remove ANSI escape sequences (e.g. [3m, [0m)."""
    return re.sub(r"\x1b\[[0-9;]*m", "", line)


def _is_hf_noise(line: str) -> bool:
    """Skip Hugging Face warnings, load reports, Notes/UNEXPECTED, and progress bar noise."""
    s = _strip_ansi(line).strip()
    if not s:
        return True
    lower = s.lower()
    # HF Hub / token warnings
    if "hf_token" in lower or "hf hub" in lower or "unauthenticated requests" in lower:
        return True
    # Loading weights progress bar
    if "loading weights" in lower and ("%" in s or "it/s" in lower):
        return True
    # BertModel load report header/table
    if "bertmodel load report" in lower or "from: BAAI/" in lower:
        return True
    if lower.startswith("key ") and "|" in s and "status" in lower:
        return True
    if "----" in s and "|" in s:
        return True
    if set(s.replace(" ", "")) <= set("-+|") and len(s) > 10:
        return True
    if "| unexpected |" in lower or ("position_ids" in lower and "|" in s):
        return True
    # Notes / UNEXPECTED / "can be ignored" / ANSI junk
    if "notes:" in lower or "unexpected" in lower:
        return True
    if "can be ignored when" in lower or "identical arch" in lower:
        return True
    if "not ok if you expect" in lower:
        return True
    if re.search(r"\[\d+m", line):
        return True
    # Progress bar line (e.g. █████)
    if "█" in s and "%" in s:
        return True
    if "materializing param" in lower:
        return True
    return False


def _parse_page_progress(line: str):
    """If line is 'Loaded N pages | PDFs X/Y' return (N, None). If 'Loaded N pages from X PDFs' return (N, N). Else None."""
    s = _strip_ansi(line).strip()
    # "Loaded 36 pages | PDFs 1/5 | file.pdf" -> current only
    m = re.match(r"Loaded\s+(\d+)\s+pages\s+\|\s+PDFs", s, re.I)
    if m:
        return (int(m.group(1)), None)
    # "Loaded 36 pages from 1 PDFs, skipped 4 PDFs already ingested." -> current and total
    m = re.match(r"Loaded\s+(\d+)\s+pages\s+from\s+\d+\s+PDFs", s, re.I)
    if m:
        n = int(m.group(1))
        return (n, n)
    return None


def ingest_stream():
    yield f"data: {json.dumps({'stage': 'start', 'line': 'Starting ingestion...'})}\n\n"
    try:
        proc = subprocess.Popen(
            [sys.executable, os.path.join(PROJECT_ROOT, "db_setup.py")],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        for line in proc.stdout:
            line = line.rstrip()
            if line:
                # If line has \r (overwriting progress), show only the last segment
                if "\r" in line:
                    line = line.split("\r")[-1].strip()
                line = _strip_ansi(line).strip()
                if not line:
                    continue
                progress = _parse_page_progress(line)
                if progress is not None:
                    current, total = progress
                    payload = {"progress_pages": current}
                    if total is not None:
                        payload["total_pages"] = total
                    yield f"data: {json.dumps(payload)}\n\n"
                    if total is not None:
                        yield f"data: {json.dumps({'line': line})}\n\n"
                    continue
                if not _is_hf_noise(line):
                    yield f"data: {json.dumps({'line': line})}\n\n"
        proc.wait()
        if proc.returncode != 0:
            yield f"data: {json.dumps({'stage': 'error', 'line': f'Process exited with code {proc.returncode}'})}\n\n"
        else:
            yield f"data: {json.dumps({'stage': 'done', 'line': 'Chroma database updated.'})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'stage': 'error', 'line': str(e)})}\n\n"


@app.route("/api/ingest-stream", methods=["GET", "POST"])
def ingest_stream_route():
    return Response(
        stream_with_context(ingest_stream()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)
