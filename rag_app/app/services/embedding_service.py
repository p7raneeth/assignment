from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import openai
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
import PyPDF2
import io
import uuid
import numpy as np
import faiss
import pickle
from app.core.config import get_settings
settings = get_settings()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ========== Vector Store Service ==========
class VectorStoreService:
    def __init__(self):
        self.dimension = settings.EMBEDDING_MODEL_DIM  # text-embedding-3-small dimension
        self.index = None
        self.chunks = []
        self.chunk_ids = []
        self.metadata = []
    
    def initialize_index(self):
        """Initialize FAISS index"""
        if self.index is None:
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
    
    def add_documents(self, chunks: List[str], embeddings: List[List[float]], metadata: List[dict]):
        """Add documents to the vector store"""
        self.initialize_index()
        
        # Convert to numpy array and normalize
        vectors = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(vectors)
        
        # Add to FAISS
        self.index.add(vectors)
        
        # Store chunks and metadata
        chunk_ids = [str(uuid.uuid4()) for _ in chunks]
        self.chunks.extend(chunks)
        self.chunk_ids.extend(chunk_ids)
        self.metadata.extend(metadata)
        
        return len(chunks)
    
    async def search(self, query: str, top_k: int = 3) -> List[dict]:
        """Search for similar chunks"""
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        response = await client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=query
        )
        query_embedding = response.data[0].embedding
        
        # Convert to numpy and normalize
        query_vector = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query_vector)
        
        # Search
        distances, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
        
        # Build results
        results = []
        for idx, score in zip(indices[0], distances[0]):
            if idx < len(self.chunks):
                results.append({
                    "content": self.chunks[idx],
                    "score": float(score),
                    "chunk_id": self.chunk_ids[idx],
                    "page_number": self.metadata[idx].get("page_number")
                })
        
        return results
    
    def get_stats(self) -> dict:
        """Get vector store statistics"""
        return {
            "total_chunks": len(self.chunks),
            "indexed_vectors": self.index.ntotal if self.index else 0
        }