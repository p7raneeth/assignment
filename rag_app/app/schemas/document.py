from pydantic import BaseModel

class UploadResponse(BaseModel):
    filename: str
    total_chunks: int
    status: str
    message: str