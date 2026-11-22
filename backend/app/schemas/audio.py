from typing import Optional
from pydantic import BaseModel, Field


class AudioTranscribeResponse(BaseModel):
    text: str
    language: Optional[str] = "en"
    duration_seconds: Optional[float] = None


class AudioSynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Text to synthesize to speech")
    voice: Optional[str] = None


class AudioSynthesizeResponse(BaseModel):
    audio_base64: str
    mime_type: str = "audio/mp3"
