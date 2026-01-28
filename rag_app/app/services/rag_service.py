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
    
    async def _resolve_followup_query(
        self, 
        query: str, 
        conversation_history: List[dict]
    ) -> str:
        """
        Use LLM to rewrite follow-up questions with context from conversation history.
        
        Examples:
        - "What about Mumbai?" → "What are important facts about Mumbai in the context of Indian cities?"
        - "Tell me more" → "Tell me more about [previous topic]"
        """
        if not conversation_history or len(conversation_history) == 0:
            # No history, return query as-is
            return query
        
        # Build conversation context
        history_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}" 
            for msg in conversation_history[-4:]  # Last 2 exchanges (4 messages)
        ])
        
        # Ask LLM to rewrite the query if it's a follow-up
        rewrite_prompt = f"""Given the conversation history below, determine if the current query is a follow-up question that needs context from the conversation.

Conversation History:
{history_text}

Current Query: {query}

Task:
1. If this is a standalone question (not referencing previous context), return it exactly as-is.
2. If this is a follow-up question (uses pronouns like "it", "that", "they" or references previous context), rewrite it to be self-contained by incorporating relevant context from the conversation history.

Return ONLY the query (original or rewritten), nothing else.

Rewritten Query:"""

        response = await client.chat.completions.create(
            model="gpt-4o",  # Use faster model for query rewriting
            messages=[{"role": "user", "content": rewrite_prompt}],
            temperature=0.3,
            max_tokens=200
        )
        
        rewritten_query = response.choices[0].message.content.strip()
        return rewritten_query
    
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