from pathlib import Path
from typing import Optional
from backend.app.core.security import SecurityValidator
from backend.app.core.config import settings
from backend.app.ai.gemini_provider import GeminiProvider


class VisionService:
    """Handles image verification, upload persistence, and visual comprehension."""

    def __init__(self, ai_provider: Optional[GeminiProvider] = None):
        self.ai_provider = ai_provider or GeminiProvider()

    def process_and_analyze_image(
        self,
        filename: str,
        file_bytes: bytes,
        user_query: str,
        system_instruction: Optional[str] = None
    ) -> tuple[str, str]:
        """Validates and analyzes an image.
        
        Returns:
            (analysis_response, saved_image_path)
        """
        # Validate image file
        is_valid, msg = SecurityValidator.validate_file(
            filename=filename,
            file_size=len(file_bytes),
            allowed_extensions=settings.ALLOWED_IMAGE_EXTENSIONS
        )
        if not is_valid:
            raise ValueError(msg)

        # Save image securely
        dest_path = SecurityValidator.get_safe_destination_path(filename)
        with open(dest_path, "wb") as f:
            f.write(file_bytes)

        # Analyze with Vision model
        analysis = self.ai_provider.analyze_image(
            image_path=str(dest_path),
            user_query=user_query,
            system_instruction=system_instruction
        )
        return analysis, str(dest_path)
