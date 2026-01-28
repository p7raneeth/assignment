
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
import os
from app.schemas.document import UploadResponse
from app.services.document_service import DocumentProcessor
from app.services.vector_service import vector_store
from app.services.doc_service import doc_process

# from app.services.embedding_service import VectorStoreService

# vector_store = VectorStoreService()

# print('vectorstore', vector_store)
# doc_processor = DocumentProcessor()

doc_router = APIRouter(prefix="/api/v1/document", tags=["document"])


@doc_router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file, extract text, chunk it, and create embeddings
    
    The file will be processed and added to the vector store for querying.
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read file content
        pdf_content = await file.read()
        # print(pdf_content)
        # Validate file size (max 10MB)
        if len(pdf_content) > 20 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        # Process PDF
        result = await doc_process.process_pdf(pdf_content, file.filename)
        
        # Add to vector store
        total_chunks = vector_store.add_documents(
            chunks=result["chunks"],
            embeddings=result["embeddings"],
            metadata=result["metadata"]
        )
        print("VECTOR STORE ID:", id(vector_store))

        return UploadResponse(
            filename=file.filename,
            total_chunks=total_chunks,
            status="success",
            message=f"Successfully processed {total_chunks} chunks from {file.filename}"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    
stats_router = APIRouter(prefix="/api/v1/statistics", tags=["statistics"])
@stats_router.get("/stats")
async def get_stats():
    """Get statistics about the vector store"""
    stats = vector_store.get_stats()
    return {
        "status": "healthy",
        "vector_store": stats,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }