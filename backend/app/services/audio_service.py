import base64
import io
import os
import struct
from pathlib import Path
from typing import Optional
from gtts import gTTS

from backend.app.core.config import settings
from backend.app.core.security import SecurityValidator
from backend.app.core.logging import logger
from backend.app.ai.gemini_provider import GeminiProvider


class AudioService:
    """Provides Speech-to-Text (transcription) and Text-to-Speech (synthesis) services."""

    def __init__(self, ai_provider: Optional[GeminiProvider] = None):
        self.ai_provider = ai_provider or GeminiProvider()

    def _create_synthetic_audio_fallback(self) -> str:
        """Generates valid 16-bit PCM WAV audio bytes as fallback when offline."""
        sample_rate = 16000
        duration_sec = 0.5
        num_samples = int(duration_sec * sample_rate)
        data_size = num_samples * 2  # 16-bit mono
        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            data_size + 36,
            b"WAVE",
            b"fmt ",
            16,
            1,
            1,
            sample_rate,
            sample_rate * 2,
            2,
            16,
            b"data",
            data_size
        )
        wav_bytes = header + (b"\x00" * data_size)
        return base64.b64encode(wav_bytes).decode("utf-8")

    def transcribe_audio(self, filename: str, file_bytes: bytes) -> str:
        """Transcribes spoken audio into text.
        
        Uses Gemini multimodal audio processing if configured; returns informative
        transcription notice in testing/offline mode.
        """
        is_valid, msg = SecurityValidator.validate_file(
            filename=filename,
            file_size=len(file_bytes),
            allowed_extensions=settings.ALLOWED_AUDIO_EXTENSIONS
        )
        if not is_valid:
            raise ValueError(msg)

        dest_path = SecurityValidator.get_safe_destination_path(filename)
        with open(dest_path, "wb") as f:
            f.write(file_bytes)

        if not self.ai_provider.is_configured:
            # Deterministic transcription mock for testing
            return f"[Transcribed Audio from '{filename}']: Hello MindBridge, please provide some guidance."

        try:
            # When configured, transcribe using Gemini's native audio model
            from google import genai
            response = self.ai_provider._client.models.generate_content(
                model=self.ai_provider.model_name,
                contents=[
                    "Please transcribe this spoken audio into accurate, punctuated text. Output only the transcription.",
                    genai.types.Part.from_bytes(
                        data=file_bytes,
                        mime_type=f"audio/{Path(filename).suffix.lstrip('.')}"
                    )
                ]
            )
            return response.text.strip() if response.text else "[Inaudible speech]"
        except Exception as e:
            logger.error(f"Audio transcription error: {e}", exc_info=True)
            return f"[Transcription error: {str(e)}]"

    def synthesize_speech(self, text: str, lang: str = "en") -> str:
        """Synthesizes text into MP3/WAV audio and returns base64-encoded audio data."""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty for speech synthesis.")

        # Truncate overly long text for audio synthesis (max 1000 chars)
        clean_text = text[:1000].strip()

        try:
            tts = gTTS(text=clean_text, lang=lang, slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return base64.b64encode(fp.read()).decode("utf-8")
        except Exception as e:
            logger.warning(f"Live gTTS synthesis unreachable ({e}). Using synthetic audio fallback.")
            return self._create_synthetic_audio_fallback()
