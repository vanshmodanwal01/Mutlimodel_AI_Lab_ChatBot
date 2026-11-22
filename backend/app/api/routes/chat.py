from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationHistoryResponse
)
from backend.app.schemas.feedback import FeedbackCreateRequest, FeedbackResponse
from backend.app.services.chat_service import ChatService
from backend.app.services.vision_service import VisionService
from backend.app.services.audio_service import AudioService
from backend.app.repositories.conversation_repo import ConversationRepository

router = APIRouter(prefix="/chat", tags=["Chat"])
chat_service = ChatService()
vision_service = VisionService()
audio_service = AudioService()


@router.post("/message", response_model=ChatMessageResponse)
def send_chat_message(request: ChatMessageRequest, db: Session = Depends(get_db)):
    """Receives user text query, checks safety/crisis boundaries, coordinates RAG, and returns reply."""
    try:
        response = chat_service.process_chat_message(db, request=request)
        if request.enable_tts and response.reply:
            try:
                response.audio_base64 = audio_service.synthesize_speech(response.reply[:500])
            except Exception:
                pass
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(exc)}"
        )


@router.post("/multimodal", response_model=ChatMessageResponse)
async def send_multimodal_message(
    session_id: str = Form(...),
    message: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    enable_rag: bool = Form(True),
    enable_tts: bool = Form(False),
    db: Session = Depends(get_db)
):
    """Processes multimodal inputs (text, image, audio) in a single unified conversation endpoint."""
    try:
        effective_text = (message or "").strip()
        saved_image_path = None

        # 1. Process audio transcription if audio was attached
        if audio is not None:
            audio_bytes = await audio.read()
            transcribed_text = audio_service.transcribe_audio(
                filename=audio.filename or "recording.wav",
                file_bytes=audio_bytes
            )
            effective_text = f"{effective_text} {transcribed_text}".strip() if effective_text else transcribed_text

        # 2. Process image vision if image was attached
        if image is not None:
            image_bytes = await image.read()
            vision_query = effective_text if effective_text else "Describe and analyze this image in detail."
            vision_analysis, saved_image_path = vision_service.process_and_analyze_image(
                filename=image.filename or "uploaded_image.png",
                file_bytes=image_bytes,
                user_query=vision_query
            )
            effective_text = f"{effective_text}\n[User attached an image. Image Analysis: {vision_analysis}]".strip()

        if not effective_text:
            raise HTTPException(status_code=400, detail="Must provide at least text message, image, or audio input.")

        # 3. Dispatch to chat conversational service
        req = ChatMessageRequest(
            session_id=session_id,
            message=effective_text,
            enable_rag=enable_rag,
            enable_tts=enable_tts,
            image_url=saved_image_path
        )
        response = chat_service.process_chat_message(db, request=req)

        # 4. Synthesize TTS if requested
        if enable_tts and response.reply:
            try:
                response.audio_base64 = audio_service.synthesize_speech(response.reply[:500])
            except Exception:
                pass

        return response

    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multimodal processing error: {str(exc)}"
        )


@router.get("/history/{session_id}", response_model=ConversationHistoryResponse)
def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """Fetches conversation history for a given session."""
    return chat_service.get_history(db, session_id=session_id)


@router.delete("/history/{session_id}")
def clear_chat_history(session_id: str, db: Session = Depends(get_db)):
    """Deletes all messages and active conversation for a session."""
    success = chat_service.delete_history(db, session_id=session_id)
    return {
        "session_id": session_id,
        "cleared": success,
        "message": "Conversation history cleared successfully." if success else "No conversation found to clear."
    }


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(request: FeedbackCreateRequest, db: Session = Depends(get_db)):
    """Submits rating and feedback for a message."""
    conv = ConversationRepository.get_or_create_conversation(db, session_id=request.session_id)
    feedback = ConversationRepository.add_feedback(
        db,
        conversation_id=conv.id,
        message_id=request.message_id,
        rating=request.rating,
        feedback_text=request.feedback_text
    )
    return FeedbackResponse(
        id=feedback.id,
        message_id=feedback.message_id,
        rating=feedback.rating,
        status="recorded"
    )
