# 🌉 MindBridge AI

**Production-Oriented MVP for a Secure Multimodal Conversational AI Platform with RAG & Responsible AI Guardrails**

---

## Overview

**MindBridge AI** is an intelligent conversational platform designed to combine:
1. **Multimodal Perception**: Text, image understanding, audio transcription (Speech-to-Text), and speech synthesis (Text-to-Speech).
2. **Retrieval-Augmented Generation (RAG)**: Ingestion of PDF, DOCX, and TXT documents, recursive text chunking, dense vector embeddings (`text-embedding-004`), MySQL vector persistence, and application-layer cosine similarity ranking with verified source citations.
3. **Empathetic Support & Safety Guardrails**: Active listening and compassionate dialogue bounded by safety guardrails (non-clinical disclaimer, prompt injection shield, and automatic crisis hotline dispatch for self-harm ideation).
4. **Decoupled Architecture**: Strict separation of concerns between presentation (Streamlit) and application logic/orchestration (FastAPI + Async Services + MySQL).

---

## Technology Stack

- **Backend Framework**: FastAPI, Pydantic v2, Uvicorn
- **Frontend Presentation**: Streamlit (responsive custom CSS)
- **Database**: MySQL 8.0+ (with connection pooling and automatic SQLite dev fallback)
- **AI Intelligence**: Google Gemini API (`gemini-2.5-flash`, `text-embedding-004`, Gemini Vision)
- **Audio Processing**: `gTTS` (Text-to-Speech) and Gemini audio transcription
- **Document Processing**: `pypdf`, `python-docx`, recursive character chunking
- **Testing**: `pytest` (16 automated tests covering all layers)

---

## Project Structure

```
mini_pro_AI_lab/
│
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entrypoint & middleware
│   │   ├── api/
│   │   │   ├── api.py                  # Master APIRouter
│   │   │   └── routes/                 # chat, documents, audio, health routes
│   │   ├── core/                       # config, security, safety guardrails, logging
│   │   ├── db/                         # SQLAlchemy session, engine, connection pool
│   │   ├── models/                     # conversations, messages, documents, chunks, feedback
│   │   ├── schemas/                    # Pydantic v2 validation schemas
│   │   ├── repositories/               # database data access objects
│   │   ├── services/                   # chat, rag, document, vision, audio services
│   │   ├── ai/                         # Gemini provider & abstract interfaces
│   │   └── utils/                      # text chunker, vector math
│   └── tests/                          # 16 unit & integration tests
│
├── frontend/
│   ├── app.py                          # Streamlit UI main entrypoint
│   ├── components/                     # chat view, file uploader, sidebar
│   ├── services/                       # HTTP API client communicating with FastAPI
│   └── assets/                         # custom styling
│
├── database/
│   └── schema.sql                      # Normalized MySQL 8.0 schema
│
├── docs/
│   ├── architecture.md                 # Deep architectural design
│   ├── api_documentation.md            # OpenAPI specification & cURL examples
│   └── setup_guide.md                  # Local installation & execution manual
│
├── requirements.txt                    # Project dependencies
├── .env.example                        # Template environment variables
├── app.py                              # All-in-one CLI runner (backend / frontend / test)
└── README.md                           # Master documentation
```

---

## Quickstart

### 1. Configure Environment
```bash
cp .env.example .env
# Edit .env and insert your GEMINI_API_KEY from https://aistudio.google.com/
```

### 2. Start Backend & Frontend
```bash
# Terminal 1: Backend
python app.py backend

# Terminal 2: Frontend
python app.py frontend
```

Access the UI at **`http://localhost:8501`** and the API docs at **`http://localhost:8000/docs`**.

---

## Running Tests

```bash
python app.py test
```
All 16 test suites will run across health checks, safety boundaries, prompt injection mitigation, chat history, document ingestion, vector cosine retrieval, and multimodal processing.
