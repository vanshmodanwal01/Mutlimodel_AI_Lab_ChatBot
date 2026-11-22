import os
from typing import Dict, Any, List, Optional
import httpx

FASTAPI_BASE_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000/api/v1")


class APIClient:
    """HTTP Client handling all network communication from Streamlit to FastAPI backend."""

    def __init__(self, base_url: str = FASTAPI_BASE_URL, timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def check_health(self) -> Dict[str, Any]:
        """Queries backend health check endpoint."""
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(f"{self.base_url}/health")
                if res.status_code == 200:
                    return res.json()
                return {"status": "unhealthy", "error": f"HTTP {res.status_code}"}
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}

    def send_chat_message(
        self,
        session_id: str,
        message: str,
        enable_rag: bool = True,
        enable_tts: bool = False,
        image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Dispatches text-based conversational message."""
        payload = {
            "session_id": session_id,
            "message": message,
            "enable_rag": enable_rag,
            "enable_tts": enable_tts,
            "image_url": image_url
        }
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(f"{self.base_url}/chat/message", json=payload)
            res.raise_for_status()
            return res.json()

    def send_multimodal_message(
        self,
        session_id: str,
        message: Optional[str] = None,
        image_file: Optional[Any] = None,
        audio_file: Optional[Any] = None,
        enable_rag: bool = True,
        enable_tts: bool = False
    ) -> Dict[str, Any]:
        """Dispatches multimodal message with optional image and audio files."""
        data = {
            "session_id": session_id,
            "message": message or "",
            "enable_rag": str(enable_rag).lower(),
            "enable_tts": str(enable_tts).lower()
        }
        files = {}
        if image_file:
            files["image"] = (image_file.name, image_file.getvalue(), image_file.type)
        if audio_file:
            files["audio"] = (audio_file.name, audio_file.getvalue(), audio_file.type)

        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(f"{self.base_url}/chat/multimodal", data=data, files=files if files else None)
            res.raise_for_status()
            return res.json()

    def get_conversation_history(self, session_id: str) -> Dict[str, Any]:
        """Retrieves conversational messages for a session."""
        with httpx.Client(timeout=self.timeout) as client:
            res = client.get(f"{self.base_url}/chat/history/{session_id}")
            res.raise_for_status()
            return res.json()

    def clear_conversation_history(self, session_id: str) -> Dict[str, Any]:
        """Clears all conversation messages for a session."""
        with httpx.Client(timeout=self.timeout) as client:
            res = client.delete(f"{self.base_url}/chat/history/{session_id}")
            res.raise_for_status()
            return res.json()

    def upload_document(self, session_id: str, uploaded_file: Any) -> Dict[str, Any]:
        """Uploads a document (PDF, DOCX, TXT) to the backend for RAG processing."""
        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
        }
        data = {"session_id": session_id}
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(f"{self.base_url}/documents/upload", data=data, files=files)
            res.raise_for_status()
            return res.json()

    def list_documents(self, session_id: str) -> Dict[str, Any]:
        """Lists uploaded documents for the active session."""
        with httpx.Client(timeout=self.timeout) as client:
            res = client.get(f"{self.base_url}/documents", params={"session_id": session_id})
            res.raise_for_status()
            return res.json()

    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Deletes a document and its chunks from the database."""
        with httpx.Client(timeout=self.timeout) as client:
            res = client.delete(f"{self.base_url}/documents/{document_id}")
            res.raise_for_status()
            return res.json()

    def submit_feedback(self, session_id: str, message_id: str, rating: int, feedback_text: Optional[str] = None) -> Dict[str, Any]:
        """Submits message rating and feedback."""
        payload = {
            "session_id": session_id,
            "message_id": message_id,
            "rating": rating,
            "feedback_text": feedback_text
        }
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(f"{self.base_url}/chat/feedback", json=payload)
            res.raise_for_status()
            return res.json()
