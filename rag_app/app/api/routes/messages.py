
from fastapi import APIRouter, FastAPI, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List
# from app.core.database import get_db
# from app.models.conversation import Conversation
# from app.models.message import Message
# from app.schemas.conversation import (
#     ConversationCreate,
#     ConversationResponse,
#     ConversationWithMessages
# )
import openai
from app.schemas.document import UploadResponse
from app.schemas.message import *
from app.services.rag_service import SimpleRAGService
import os

# vector_store = VectorStoreService()
# doc_processor = DocumentProcessor()
from app.services.vector_service import vector_store

rag_service = SimpleRAGService()




router = APIRouter(prefix="/api/v1/message", tags=["message"])
@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Send a query and get an AI-generated answer based on uploaded documents
    
    Request body:
    {
        "query": "What is the main topic?",
        "conversation_history": [],  // Optional
        "top_k": 3  // Optional, number of chunks to retrieve
    }
    """
    try:
        # Step 1: Retrieve relevant context
        context_chunks = await rag_service.retrieve_context(
            request.query, 
            top_k=request.top_k
        )
        
        print('retrieved chunks', context_chunks)
        # Step 2: Generate answer with LLM
        answer = await rag_service.generate_answer(
            query=request.query,
            context_chunks=context_chunks,
            conversation_history=request.conversation_history or []
        )
        print("VECTOR STORE ID: query endpoint", id(vector_store))
        
        # Step 3: Return response
        return QueryResponse(
            answer=answer,
            sources=[
                Source(
                    content=chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"],
                    score=chunk["score"],
                    chunk_id=chunk["chunk_id"],
                    page_number=chunk.get("page_number")
                )
                for chunk in context_chunks
            ],
            query=request.query
        )
        
    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

