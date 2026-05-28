FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached layer — only rebuilds when requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code and pre-built vector store
COPY api.py .
COPY chroma_db/ ./chroma_db/

# HF Spaces runs containers as a non-root user — make files accessible
RUN chmod -R 755 /app

# HF Spaces always exposes port 7860
EXPOSE 7860

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
