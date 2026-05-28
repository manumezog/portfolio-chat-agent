"""
Builds chroma_db from knowledge_base.json at Docker image build time.
Run once during `docker build` — not at runtime.
"""
import json, uuid, os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

print("Building vector store from knowledge_base.json...")
with open("knowledge_base.json", encoding="utf-8") as f:
    chunks = json.load(f)

texts  = [c["text"]     for c in chunks]
metas  = [c["metadata"] for c in chunks]
ids    = [str(uuid.uuid4()) for _ in chunks]

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectors = embeddings.embed_documents(texts)

vs = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
vs._collection.add(documents=texts, embeddings=vectors, metadatas=metas, ids=ids)
print(f"Done. {vs._collection.count()} chunks indexed.")
