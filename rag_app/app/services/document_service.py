import PyPDF2
from typing import List, Optional
import io, os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()


client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ========== Document Processing Service ==========
class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
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
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > self.chunk_size * 0.5:
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - self.chunk_overlap
        
        return [c for c in chunks if c]
    
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
            model="text-embedding-3-small",
            input=texts
        )
        return [item.embedding for item in response.data]