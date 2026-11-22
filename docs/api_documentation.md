# MindBridge AI: REST API Documentation

Base URL: `http://127.0.0.1:8000/api/v1`

---

## 1. System Health

### `GET /health`
Returns application and database connectivity status.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "app_name": "MindBridge AI",
  "version": "1.0.0",
  "environment": "development",
  "database": {
    "status": "healthy",
    "engine": "mysql"
  },
  "gemini_configured": true,
  "timestamp": "2026-11-20T09:00:20.558092"
}
```

---

## 2. Conversational Chat Endpoints

### `POST /chat/message`
Processes natural language text queries with multi-turn context retention and optional RAG.

**Request Body (JSON):**
```json
{
  "session_id": "session_user_001",
  "message": "Can you help me organize my thoughts?",
  "enable_rag": true,
  "enable_tts": false,
  "image_url": null
}
```

**Response (200 OK):**
```json
{
  "session_id": "session_user_001",
  "conversation_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "message_id": "c9284920-5dfc-423c-9a40-e2b26002f2ec",
  "role": "assistant",
  "reply": "I would be glad to help you organize your thoughts...",
  "modality": "text",
  "audio_base64": null,
  "citations": [],
  "crisis_detected": false,
  "created_at": "2026-11-20T09:05:00Z"
}
```

---

### `POST /chat/multimodal`
Unified endpoint accepting text, image, and audio in a single multipart request.

**Form Data:**
- `session_id` (string, required)
- `message` (string, optional)
- `image` (file: JPG, PNG, WEBP, optional)
- `audio` (file: WAV, MP3, optional)
- `enable_rag` (boolean, default: true)
- `enable_tts` (boolean, default: false)

**cURL Example:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/chat/multimodal \
  -F "session_id=session_001" \
  -F "message=What does this diagram show?" \
  -F "image=@diagram.png"
```

---

### `GET /chat/history/{session_id}`
Retrieves conversation history for a given session.

**Response (200 OK):**
```json
{
  "session_id": "session_001",
  "conversation_id": "9b1deb4d-...",
  "title": "New Conversation",
  "messages": [
    {
      "id": "...",
      "role": "user",
      "content": "Hello",
      "modality": "text",
      "created_at": "2026-11-20T09:00:00Z"
    }
  ]
}
```

---

### `DELETE /chat/history/{session_id}`
Clears all conversation records for the given session.

---

### `POST /chat/feedback`
Submits user rating (1-5) and feedback on an assistant message.

**Request Body (JSON):**
```json
{
  "session_id": "session_001",
  "message_id": "msg_uuid_here",
  "rating": 5,
  "feedback_text": "Very empathetic and grounded answer."
}
```

---

## 3. Knowledge Document RAG Endpoints

### `POST /documents/upload`
Uploads and processes a PDF, DOCX, or TXT file into the session RAG vector index.

**Form Data:**
- `file` (binary document, required)
- `session_id` (string, required)

**cURL Example:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents/upload \
  -F "session_id=session_001" \
  -F "file=@notes.pdf"
```

**Response (200 OK):**
```json
{
  "document_id": "doc_uuid_here",
  "session_id": "session_001",
  "filename": "notes.pdf",
  "file_type": "pdf",
  "file_size": 24890,
  "chunks_created": 6,
  "processing_status": "processed",
  "created_at": "2026-11-20T09:10:00Z"
}
```

---

### `GET /documents?session_id={session_id}`
Lists all ingested documents for the session.

---

### `DELETE /documents/{document_id}`
Deletes an ingested document and cascades deletion of its vector chunks.

---

## 4. Audio Endpoints

### `POST /audio/transcribe`
Converts uploaded audio recording (WAV, MP3, M4A, OGG) to text.

---

### `POST /audio/synthesize`
Generates base64-encoded MP3 audio from text for speech playback.

**Request Body:**
```json
{
  "text": "Welcome to MindBridge AI."
}
```
