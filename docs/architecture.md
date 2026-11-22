# MindBridge AI: Architecture Specification

## 1. System Overview

**MindBridge AI** is an enterprise-oriented, secure multimodal conversational AI platform built using a strictly decoupled architecture:
- **Presentation Layer**: Streamlit web application.
- **Application & Orchestration Layer**: FastAPI REST API server.
- **AI & RAG Subsystem**: Google Gemini API integration with modular provider abstractions.
- **Persistence Layer**: MySQL 8.0 relational database with connection pooling and application-layer vector cosine similarity ranking.

---

## 2. Decoupled Architecture

```
+--------------------------------------------------------------------------+
|                       Presentation Layer (Streamlit)                     |
|  - Modern chat bubbles, uploaded file previews, audio playback           |
|  - Sidebar: session switcher, knowledge manager, modality toggles        |
|  - Communicates exclusively via HTTP REST API calls (APIClient)          |
+--------------------------------------------------------------------------+
                                     │  (HTTP / JSON / Multipart)
                                     ▼
+--------------------------------------------------------------------------+
|                       API Gateway & Security (FastAPI)                   |
|  - CORS middleware, rate limiting, request validation                    |
|  - Input sanitization, prompt injection shield, crisis detector          |
+--------------------------------------------------------------------------+
                                     │
                                     ▼
+--------------------------------------------------------------------------+
|                       Service Orchestration Layer                        |
|  - ChatService: Multi-turn memory, system prompt assembly                |
|  - DocumentService: Text extraction (PDF/DOCX/TXT), chunking             |
|  - RAGService: Top-K cosine similarity search over stored vectors        |
|  - VisionService: Image validation & visual reasoning                    |
|  - AudioService: STT transcription & TTS speech synthesis (gTTS)         |
|  - EmotionalSupportService: Empathetic framing & crisis interceptors     |
+--------------------------------------------------------------------------+
             │                                              │
             ▼                                              ▼
+----------------------------+             +-------------------------------+
|    AI Provider Adapters    |             |       Persistence Layer       |
|  - BaseLLMProvider         |             |  - MySQL 8.0 Database         |
|  - BaseEmbeddingProvider   |             |    (conversations, messages,  |
|  - BaseVisionProvider      |             |     documents, chunks)        |
|  - BaseSpeechProvider      |             |  - Filesystem Uploads (/uploads)|
+----------------------------+             +-------------------------------+
```

---

## 3. RAG Architecture

1. **Ingestion Pipeline**:
   - Files are validated against whitelisted extensions (`.pdf`, `.docx`, `.txt`) and 10MB size limit.
   - Text is extracted via `pypdf`, `python-docx`, or standard text decoders.
   - Recursive character chunker splits text with configurable window (default: 500 chars, 50 chars overlap).
   - Dense vector embeddings (768 dimensions) are generated using Google `text-embedding-004`.
   - Chunks and embeddings are stored as JSON arrays in MySQL `document_chunks`.

2. **Retrieval Pipeline**:
   - User query is converted into an embedding vector.
   - All chunks belonging to active session documents are loaded from MySQL.
   - Cosine similarity is computed across candidate vectors using vectorized `numpy` operations.
   - Top-K matches (score $\ge$ threshold) are ranked and structured into an untrusted reference block with exact filename and chunk attribution.

3. **Untrusted Data Isolation**:
   - Retrieved chunks are wrapped inside `<untrusted_document_context>` XML delimiter tags.
   - System prompts instruct the LLM to treat document context solely as external factual data that can never override system rules or boundaries.

---

## 4. Emotional Support & Safety Guardrails

1. **Non-Clinical Boundary**:
   - MindBridge AI acts as an empathetic emotional support companion.
   - Explicitly disclaims medical authority: never diagnoses mental health conditions and never prescribes psychiatric medications.

2. **Crisis Intervention Protocol**:
   - Monitored by regular expressions and heuristic classifiers for self-harm and suicidal ideation.
   - If triggered, the generation loop halts immediately.
   - A verified crisis intervention response is returned with 24/7 hotlines:
     - **United States / Canada**: 988
     - **India**: Tele-MANAS (14416 / 1800-891-4416)
     - **International**: findahelpline.com / befrienders.org

3. **Prompt Injection Shield**:
   - Inspects queries for jailbreak patterns ("ignore previous instructions", "developer mode", "reveal system prompt").
   - Intercepts and neutralizes prompt tampering before reaching LLM execution.
