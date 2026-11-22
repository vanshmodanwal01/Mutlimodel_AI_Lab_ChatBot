from typing import Optional
from pydantic import BaseModel, Field


class FeedbackCreateRequest(BaseModel):
    session_id: str
    message_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 (poor) to 5 (excellent)")
    feedback_text: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: str
    message_id: str
    rating: int
    status: str = "success"
