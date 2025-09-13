# rag.py
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

class RAGPipeline:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.create_collection(
            name="docs",
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")
        )

    def add_document(self, text, doc_id: str = None):
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        self.collection.add(documents=chunks, ids=ids)

    def answer(self, query: str, k: int = 3):
        results = self.collection.query(query_texts=[query], n_results=k)
        docs = results.get("documents", [[]])[0]
        if docs:
            return {"found_in_docs": True, "passages": docs, "source": "docs", "answer": f"Based on your docs: {docs[0]}"}
        else:
            return {"found_in_docs": False, "passages": [], "source": "fallback", "answer": "Answer not found in your documents."}
