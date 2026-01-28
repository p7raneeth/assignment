import PyPDF2
from typing import List, Optional
import io, os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
load_dotenv()

# In app/services/document_service.py
from app.core.config import get_settings

settings = get_settings()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ========== Document Processing Service ==========
class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        # Initialize LangChain's RecursiveCharacterTextSplitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],  # Try to split on paragraphs, then sentences, then words
            is_separator_regex=False,
        )

    def extract_text_from_pdf(self, pdf_content: bytes) -> List[tuple]:
        """Extract text from PDF with page numbers"""
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        texts = []
        
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            text = page.extract_text()
            if text.strip():
                texts.append((text, page_num))
        
        return texts
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks using LangChain's RecursiveCharacterTextSplitter
        
        This splitter tries to keep semantically related text together by:
        1. First trying to split on double newlines (paragraphs)
        2. Then single newlines
        3. Then sentences (periods followed by space)
        4. Then words (spaces)
        5. Finally individual characters as last resort
        """
        chunks = self.text_splitter.split_text(text)
        return chunks
    
    async def process_pdf(self, pdf_content: bytes, filename: str) -> dict:
        """Process PDF: extract, chunk, embed"""
        # Extract text
        page_texts = self.extract_text_from_pdf(pdf_content)
        
        # Chunk each page
        all_chunks = []
        metadata = []
        
        for page_text, page_num in page_texts:
            chunks = self.chunk_text(page_text)
            for chunk in chunks:
                all_chunks.append(chunk)
                metadata.append({
                    "page_number": page_num,
                    "filename": filename
                })
        
        if not all_chunks:
            raise ValueError("No text extracted from PDF")
        
        # Generate embeddings
        embeddings = await self.embed_batch(all_chunks)
        
        return {
            "chunks": all_chunks,
            "embeddings": embeddings,
            "metadata": metadata
        }
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        response = await client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=texts
        )
        return [item.embedding for item in response.data]