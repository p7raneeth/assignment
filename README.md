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


```
## Requirements to Productionize the solution

1. procure a compute instance. e.g. Azure web apps to deploy front end and backend seperately with multiple slots
   each for dev --> stage --> prod environments
2. setup Github actions CI/CD pipeline by configuring a .yaml script which triggers a deployement to the app service
   whenever a new changes is commited to a configured branch e.g.  main, it can be triggered to any branch
3. Docker file to create a docker image and deploy the docker image instead of publishing the whole code

```

```
## Design Requirements

1. As a vanilla solution, I have chosen to use RCTS (Recursive Character Text Splitter) for chunking the data which uses a series of delimeters like \n\n which chunks paragraphs, followed by sentences, words, characters and 
2. based on the similarity of the question which any of the chunked data and also basis the top-k parameter. semantically similar 
context would be fetched and sent to llm to generate the answer
3. choice of LLM 
  - LLM : gpt-4o
  - Embedding model : text-embedding-3-small
  - vector database : FAISS
  - prompt : few shot prompting
4. Engineering standards followed 
5. AI Tools used : ChatGPT for syntactical help
6. With more time, I would have 
  - productionalized the whole app on azure. made it scalable to atleast a throughput of 50 QPM with a p90 latenct of 3-4 seconds approx. 
  - implemented observability to monitor the metrics (application performance)
  - implemented a better Chunking mechanism (BPE)
  - experimented with better prompting techniques like chain-of-thoughts
  - prompt chaching to reduce token consumption
  - tried parallazation where function execution is not sequential, to increase the performance
  - user management, user login/authentication 
  - implemented alembic migration to track database changes
  - used an opensource llm and deployed it as a seperate micro-service

7. Architectural decisions, Tradeoffs

  Follow-up handling via LLM rewriting - Enables natural conversation
  RecursiveCharacterTextSplitter - Better chunk quality than manual splitting
  Dual-source answering - RAG + conversation = comprehensive responses
  In-memory FAISS - Fast prototyping, easy to migrate later
  Config-driven design - Production-ready PoV (parameterization)
  Stateless API - Scalable - client manages history
  No Database - Easy to start but no persistence - no user management
  vector db - FAISS - low latency, simple to setup - no persistance - lost on restart
  LLM choice - OpenAI due to high quality generated outputs  - vendor lock-in - requires internet to chat with docs even locally (as it is an API call)

```

```
High level Architecture
┌─────────────────────────────────────────────────────────────────┐
│                          USER / FRONTEND  (Streamlit)           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         FASTAPI BACKEND                         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    API ROUTES                            │   │
│  │  • POST /documents/upload  (Upload PDF)                  │   │
│  │  • POST /messages/query        (Ask Questions)           │   | 
│  └──────────────┬─────────────────────┬─────────────────────┘   │
│                 │                      │                        │
│                 ▼                      ▼                        │
│  ┌──────────────────────┐  ┌─────────────────────────────────   │
│  │  DOCUMENT SERVICE    │  │     RAG SERVICE                 │  │
│  │                      │  │                                 │  │
│  │  1. Extract PDF text │  │  1. Rewrite follow-up query     │  │
│  │  2. Chunk text       │  │  2. Search vector DB            │  │
│  │  3. Generate embed   │  │  3. Build prompt                │  │
│  │  4. Store in vector  │  │  4. Call LLM & Generates result │  │      
│  └──────────────────────┘  └──────────────────────────────────  │
│                 │                      │                        │
│                 ▼                      ▼                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              STORAGE & SERVICES LAYER                    │   │
│  │                                                          │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐   │   │
│  │  │ FAISS Index │  │ OpenAI API   │  │ In-Memory      │   │   │
│  │  │             │  │              │  │ Chunks Storage │   │   │
│  │  │ • Embeddings│  │ • Embeddings │  │                │   │   │
│  │  │ • Search    │  │ • GPT-4      │  │ • Text chunks  │   │   │
│  │  │             │  │              │  │ • Metadata     │   │   │
│  │  └─────────────┘  └──────────────┘  └────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

```
Engineering Standards followed: 

1. Code Organization & Architecture

 - Separation of Concerns - Routes, services, schemas, and config in separate layers
 - Single Responsibility Principle - Each service handles one domain (doc processing, embeddings, RAG)
 - Dependency Injection - Services use get_settings() for configuration
 - Modular Design - Easy to swap FAISS → Pinecone without touching routes

2. API Design Standards

 - RESTful conventions - Proper HTTP verbs (POST for creation, GET for retrieval)
 - Semantic status codes - HTTP_201_CREATED, HTTP_400_BAD_REQUEST instead of numbers
 - Consistent response formats - Pydantic schemas ensure uniform JSON structures
 - API versioning ready - Prefix structure allows /api/v1/ additions
 - Self-documenting - Auto-generated OpenAPI/Swagger docs

3. Type Safety & Validation

 - Type hints everywhere - All functions have input/output types
 - Pydantic validation - Request/response validation at API boundaries
 - Config validation - Settings validated on startup, fails fast if misconfigured
 - Runtime type checking - Pydantic catches type errors before they reach code

4. Error Handling

 - Graceful degradation - Specific exception handling for different error types
 - Client-friendly errors - Clear error messages ("File size exceeds 10MB" vs "Error 400")

5. Dependency Management

 - Lock file committed - uv.lock ensures reproducible builds
 - Modern tooling - UV for faster, more reliable dependency resolution

6. Documentation Standards

 - README with setup - Clear onboarding for new developers
 - API documentation - Auto-generated Swagger UI
 - Architecture diagrams - Visual overview of system

7. Git & Version Control

 - Meaningful commits - Descriptive commit messages
 - Branch strategy - Dev → Main workflow
 - .gitignore properly configured - No venv, secrets, or cache in repo
 - Lock files committed - Reproducible environments

```