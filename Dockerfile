# Python 3.12 (matches project recommendation)
FROM python:3.12-slim

WORKDIR /app

# Dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code and frontend
COPY api.py qa.py db_setup.py .
COPY frontend ./frontend

# data/ and chroma_db/ next to app
RUN mkdir -p /app/data /app/chroma_db

ENV PORT=8080
EXPOSE 8080

CMD ["python", "api.py"]
