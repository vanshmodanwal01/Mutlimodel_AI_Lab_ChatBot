import io
import uuid
from PIL import Image
from backend.app.services.vision_service import VisionService
from backend.app.services.audio_service import AudioService
from backend.app.db.session import get_session
from backend.app.services.chat_service import ChatService
from backend.app.schemas.chat import ChatMessageRequest


def test_speech_synthesis():
    audio_service = AudioService()
    text = "Hello! This is a test of speech synthesis in MindBridge AI."
    audio_b64 = audio_service.synthesize_speech(text)
    assert audio_b64 is not None
    assert len(audio_b64) > 100  # Base64 string for MP3


def test_audio_transcription():
    audio_service = AudioService()
    fake_audio_bytes = b"RIFF....WAVEfmt ...."
    text = audio_service.transcribe_audio("test_voice.wav", fake_audio_bytes)
    assert text is not None
    assert "test_voice.wav" in text or len(text) > 0


def test_vision_image_analysis():
    vision_service = VisionService()

    # Create a small valid test PNG in memory
    img = Image.new("RGB", (64, 64), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    analysis, saved_path = vision_service.process_and_analyze_image(
        filename="test_image.png",
        file_bytes=img_bytes,
        user_query="What color is this square?"
    )
    assert analysis is not None
    assert saved_path is not None
    assert "test_image.png" in saved_path


def test_chat_message_with_tts_generation():
    db = get_session()
    chat_service = ChatService()
    test_session = f"tts_session_{uuid.uuid4().hex[:8]}"

    req = ChatMessageRequest(
        session_id=test_session,
        message="Please give me a brief calm thought.",
        enable_rag=False,
        enable_tts=True
    )
    res = chat_service.process_chat_message(db, req)
    assert res.reply is not None

    # Clean up
    chat_service.delete_history(db, test_session)
