from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class Citation(BaseModel):
    document_id: str
    filename: str
    chunk_index: int
    snippet: str
    score: float


class ChatMessageRequest(BaseModel):
    session_id: str = Field(..., description="Unique user session identifier")
    message: str = Field(..., min_length=1, max_length=10000, description="User text query")
    enable_rag: bool = Field(True, description="Whether to retrieve relevant context from uploaded documents")
    enable_tts: bool = Field(False, description="Whether to synthesize speech for the reply")
    image_url: Optional[str] = Field(None, description="Path or URL of an attached image")


class ChatMessageResponse(BaseModel):
    session_id: str
    conversation_id: str
    message_id: str
    role: str = "assistant"
    reply: str
    modality: str = "text"
    audio_base64: Optional[str] = None
    audio_url: Optional[str] = None
    citations: List[Citation] = []
    crisis_detected: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MessageHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: str
    content: str
    modality: str
    media_url: Optional[str] = None
    created_at: datetime


class ConversationHistoryResponse(BaseModel):
    session_id: str
    conversation_id: Optional[str] = None
    title: Optional[str] = "Conversation History"
    messages: List[MessageHistoryItem] = []
