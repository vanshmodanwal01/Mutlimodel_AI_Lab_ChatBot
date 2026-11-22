from fastapi import APIRouter, UploadFile, File, HTTPException, status
from backend.app.services.audio_service import AudioService
from backend.app.schemas.audio import (
    AudioTranscribeResponse,
    AudioSynthesizeRequest,
    AudioSynthesizeResponse
)

router = APIRouter(prefix="/audio", tags=["Audio"])
audio_service = AudioService()


@router.post("/transcribe", response_model=AudioTranscribeResponse)
async def transcribe_audio_file(file: UploadFile = File(...)):
    """Transcribes an uploaded audio file (WAV, MP3, M4A, OGG) to text."""
    try:
        file_bytes = await file.read()
        transcription = audio_service.transcribe_audio(
            filename=file.filename or "audio.wav",
            file_bytes=file_bytes
        )
        return AudioTranscribeResponse(text=transcription, language="en")
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio transcription failed: {str(exc)}"
        )


@router.post("/synthesize", response_model=AudioSynthesizeResponse)
def synthesize_audio(request: AudioSynthesizeRequest):
    """Converts text into base64-encoded MP3 audio for in-browser playback."""
    try:
        audio_b64 = audio_service.synthesize_speech(text=request.text)
        return AudioSynthesizeResponse(audio_base64=audio_b64, mime_type="audio/mp3")
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech synthesis failed: {str(exc)}"
        )
