from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    # DATABASE_URL: str
    
    # OpenAI
    OPENAI_API_KEY: str
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_MODEL_DIM: int = 1536
    LLM_MODEL: str = "gpt-4o"
    TEMPERATURE : float = 0.1
    MAX_TOKENS: int = 200
    
    # RAG Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RETRIEVAL: int = 5
    
    # Conversation
    MAX_HISTORY_MESSAGES: int = 1  # Include 1 previous message
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    FAISS_INDEX_DIR: str = "./faiss_index"
    MAX_FILE_SIZE: int = 20 * 1024 * 1024  # 10MB
    FILE_TYPE: str = '.pdf'
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()