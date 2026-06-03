FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy knowledge base (plain JSON) and build script
COPY knowledge_base.json .
COPY build_db.py .

# Build ChromaDB from JSON during image build — no binary files in git
RUN python build_db.py

# Copy API and voice sample for TTS proxy
COPY api.py .
COPY voice_sample.mp4 .

# HF Spaces requires port 7860
EXPOSE 7860

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
