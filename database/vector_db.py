import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from .vector_db_config import VectorDBConfig
import os
import json

class VectorDB:
    def __init__(self):
        print("Initializing VectorDB...")
        self.index_path = VectorDBConfig.FAISS_INDEX_PATH
        self.documents_path = self.index_path.replace('.bin', '_documents.json')
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer(VectorDBConfig.EMBEDDING_MODEL)
        print("Embedding model loaded.")
        
        print("Loading FAISS index...")
        self.index = self._load_index()
        print("FAISS index loaded.")

        print("Loading documents...")
        self.documents = self._load_documents()
        print("Documents loaded.")
        print("VectorDB Initialized.")

    def _load_index(self):
        try:
            print(f"Reading FAISS index from {self.index_path}")
            return faiss.read_index(self.index_path)
        except RuntimeError:
            print("FAISS index not found. Creating a new one.")
            # If the index file doesn't exist, create a new one
            # The dimension of the embeddings is 384 for all-MiniLM-L6-v2
            return faiss.IndexFlatL2(384)

    def _load_documents(self):
        try:
            print(f"Loading documents from {self.documents_path}")
            with open(self.documents_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Documents file not found or empty. Returning empty list.")
            return []

    def _save_documents(self):
        print(f"Saving documents to {self.documents_path}")
        with open(self.documents_path, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)

    def add_documents(self, documents: list[str]):
        print("Adding documents to VectorDB...")
        embeddings = self.embedding_model.encode(documents, convert_to_tensor=False)
        self.index.add(np.array(embeddings, dtype=np.float32))
        
        # Store documents
        self.documents.extend(documents)
        self._save_documents()
        print(f"Saving FAISS index to {self.index_path}")
        faiss.write_index(self.index, self.index_path)
        print("Documents added.")

    def search(self, query: str, k: int = 5):
        print(f"Searching for: {query}")
        if not self.documents:
            print("No documents in DB.")
            return []
            
        query_embedding = self.embedding_model.encode([query], convert_to_tensor=False)
        distances, indices = self.index.search(np.array(query_embedding, dtype=np.float32), k)
        
        # Return actual document content
        results = []
        for idx in indices[0]:
            if idx < len(self.documents):
                results.append(self.documents[idx])
        
        print(f"Found {len(results)} results.")
        return results

print("Creating VectorDB instance...")
vector_db = VectorDB()
print("VectorDB instance created.")