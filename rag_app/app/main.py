# main.py
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from openai import AsyncOpenAI
import os
import io
from app.api.routes import document, messages
from app.api.routes.document import doc_router, stats_router


app = FastAPI(title="Simple RAG API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(document.router)
app.include_router(messages.router)
# app.include_router(stats.router)
app.include_router(doc_router)
app.include_router(stats_router)

# ========== Routes ==========
@app.get("/")
async def root():
    return {
        "message": "Simple RAG API",
        "endpoints": {
            "POST /upload": "Upload and process a PDF file",
            "POST /query": "Send a question and get an answer",
            "GET /stats": "Get vector store statistics"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "openai_configured": bool(os.getenv("OPENAI_API_KEY"))}
