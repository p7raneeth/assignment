# RAG QA Chatbot Backend

A FastAPI-based backend for a RAG (Retrieval-Augmented Generation) Question Answering chatbot. Upload PDF documents and ask questions about them using AI.

## Features

- 📄 **PDF Document Processing** - Upload and process PDF files
- 🔍 **Vector Search** - FAISS-based semantic search
- 🤖 **AI-Powered Answers** - OpenAI GPT-4 integration
- 💬 **Conversation History** - Contextual multi-turn conversations
- 📊 **Source Citations** - Track which document chunks were used

## Tech Stack

- **Framework**: FastAPI
- **Package Manager**: UV
- **Vector Store**: FAISS
- **Embeddings**: OpenAI text-embedding-3-small
- **LLM**: OpenAI GPT-4 Turbo
- **PDF Processing**: PyPDF2

## Prerequisites

- Python 3.11 or higher
- UV package manager
- OpenAI API key

## Installation

### 1. Install UV

If you don't have UV installed, install it first:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Or using pip:**
```bash
pip install uv
```

Verify installation:
```bash
uv --version
```

### 2. Clone the Repository

```bash
git clone https://github.com/p7raneeth/assignment.git
cd assignment
```

### 3. Sync Dependencies with UV

UV can automatically create a virtual environment and install all dependencies in one command:

```bash
uv sync
```

This will:
- ✅ Create a `.venv` directory (if it doesn't exist)
- ✅ Install all dependencies from `pyproject.toml` or `requirements.txt`
- ✅ Lock dependency versions for reproducibility

**Note:** If you don't have a `pyproject.toml`, UV will use `requirements.txt` automatically.

**Alternative (Manual approach):**

If you prefer manual control:

```bash
# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

You can get an OpenAI API key from: https://platform.openai.com/api-keys

### 5. Run the Application

Start the development server:

```bash
uv run uvicorn app.main:app --reload
```

Or with Python directly:
```bash
python -m uvicorn app.main:app --reload
```

The API will be available at: **http://localhost:8000**


## Using the API with Swagger UI

The easiest way to interact with the API is through the **Swagger UI** - an interactive API documentation interface.

### 1. Access Swagger UI

Open your browser and visit: **http://localhost:8000/docs**

You'll see an interactive interface with all available endpoints organized by tags.

### 2. Upload a PDF Document

**Step 1:** Locate the **documents** section and click on `POST /documents/upload`

**Step 2:** Click the **"Try it out"** button on the right

**Step 3:** Click **"Choose File"** and select a PDF from your computer

**Step 4:** Click the blue **"Execute"** button

**Step 5:** View the response below showing:
```json
{
  "filename": "your-document.pdf",
  "total_chunks": 42,
  "status": "success",
  "message": "Successfully processed 42 chunks from your-document.pdf"
}
```

![Upload Document](https://i.imgur.com/example-upload.png)

### 3. Query Your Documents

**Step 1:** Scroll down to the **chat** section and click on `POST /chat/query`

**Step 2:** Click **"Try it out"**

**Step 3:** Edit the request body in the text box:
```json
{
  "query": "What is the main topic of the document?",
  "conversation_history": [],
  "top_k": 5
}
```

**Step 4:** Click **"Execute"**

**Step 5:** View the AI-generated answer with source citations:
```json
{
  "answer": "Based on the document (Page 3), the main topic is...",
  "sources": [
    {
      "content": "The document discusses...",
      "score": 0.89,
      "chunk_id": "abc-123",
      "page_number": 3
    }
  ],
  "query": "What is the main topic of the document?"
}
```


### 5. Check Document Statistics

**Step 1:** Click on `GET /documents/stats`

**Step 2:** Click **"Try it out"** then **"Execute"**

**Step 3:** View how many document chunks are indexed:
```json
{
  "total_chunks": 42,
  "indexed_vectors": 42
}
```

### Tips for Using Swagger UI

- 💡 **Auto-completion**: Swagger validates your input and shows required fields
- 🔍 **Schema Browser**: Click "Schema" to see the expected request/response format
- 📋 **Copy as cURL**: Click the "Copy" icon to get curl commands for terminal use
- 🎨 **Response Codes**: Green (200s) = success, Red (400s/500s) = error
- 🔄 **Try Multiple Queries**: You can execute requests multiple times to test different scenarios

## API Endpoints

### Document Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/documents/upload` | Upload a PDF document |

### message/query

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/messages/query` | Ask questions about uploaded documents |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |

## Project Structure

```
rag-qa-chatbot/
├── app/
│   ├── main.py                      # FastAPI application
│   ├── api/
│   │   └── routes/
│   │       ├── document.py            # Document upload routes
│   │       └── messages.py              # Chat/query routes
│   ├── schemas/
│   │   ├── document.py                # Upload schemas
│   │   └── messages.py                  # Chat schemas
│   services/
│   ├── doc_service.py          # to create an object of the class DocumentService
│   ├── document_service.py     # PDF text extraction & chunking logic
│   ├── embedding_service.py    # OpenAI embedding generation
│   ├── vector_service.py       # to create an object of the class VectorStoreService
│   └── rag_service.py          # Orchestrates all services together
│   └── core/
│       └── config.py                # Configuration
├── .env                             # Environment variables (create this)
├── requirements.txt                 # Dependencies
├── pyproject.toml                   # UV project config (optional)
└── README.md                        # This file
```




```

## Configuration

Configuration can be modified in `.env` or `app/core/config.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API key (required) |
| `CHUNK_SIZE` | 1000 | Size of text chunks |
| `CHUNK_OVERLAP` | 200 | Overlap between chunks |
| `MAX_FILE_SIZE_MB` | 10 | Maximum PDF file size |
| `TOP_K_RETRIEVAL` | 3 | Number of chunks to retrieve |
| `LLM_MODEL` | gpt-4-turbo-preview | OpenAI model to use |
| `EMBEDDING_MODEL` | text-embedding-3-small | Embedding model |

```


