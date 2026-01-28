from typing import List, Optional
import io, os
from openai import AsyncOpenAI
from app.services.vector_service import vector_store

# In-memory storage (replace with DB later)
VECTOR_STORE = {
    "index": None,  # FAISS index
    "chunks": [],   # List of text chunks
    "chunk_ids": [], # Chunk IDs
    "metadata": []   # Metadata (page numbers, etc.)
}

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# vector_store = VectorStoreService()

# ========== RAG Service ==========
class SimpleRAGService:
    async def retrieve_context(self, query: str, top_k: int = 6) -> List[dict]:
        """Retrieve relevant context using vector search"""
        return await vector_store.search(query, top_k)
    
    async def generate_answer(
        self, 
        query: str, 
        context_chunks: List[dict],
        conversation_history: List[dict]
    ) -> str:
        """Generate answer using LLM with retrieved context"""
        
        # Build context string
        context_text = "\n\n".join([
            f"[Source {i+1} - Page {chunk.get('page_number', 'N/A')}]\n{chunk['content']}" 
            for i, chunk in enumerate(context_chunks)
        ])
        
        # Build messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": """You are a helpful AI assistant. Answer the user's question based on the provided context from the documents.
If the answer cannot be found in the context, say so clearly.
Always cite the source number when referencing information from the context."""
            }
        ]
        
        # Add conversation history (if any)
        messages.extend(conversation_history)
        
        # Add current query with context
        if context_chunks:
            user_message = f"""Context from documents:
{context_text}

Question: {query}

Please answer based on the context provided above."""
        else:
            user_message = f"""No relevant context found in the documents.

Question: {query}

Please let the user know that you don't have information about this in the uploaded documents."""
        
        messages.append({"role": "user", "content": user_message})
        
        # Call OpenAI
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content