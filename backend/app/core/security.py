import os
import re
import uuid
from pathlib import Path
from typing import Tuple
from backend.app.core.config import settings


class SecurityValidator:
    """Validates files, paths, and enforces boundary security on uploads."""

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Generates a secure, collision-resistant filename preventing directory traversal."""
        # Remove directory paths if present
        clean_name = os.path.basename(filename)
        # Strip non-alphanumeric chars except period, hyphen, underscore
        clean_name = re.sub(r"[^\w\.\-]", "_", clean_name)
        # Add UUID prefix
        unique_prefix = uuid.uuid4().hex[:12]
        return f"{unique_prefix}_{clean_name}"

    @staticmethod
    def validate_file(filename: str, file_size: int, allowed_extensions: set) -> Tuple[bool, str]:
        """Validates file extension and size constraints."""
        ext = Path(filename).suffix.lower()
        if not ext:
            return False, "File must have a valid extension."

        if ext not in allowed_extensions:
            return False, f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(sorted(allowed_extensions))}"

        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            return False, f"File size exceeds the maximum limit of {settings.MAX_UPLOAD_SIZE_MB}MB."

        return True, ""

    @staticmethod
    def get_safe_destination_path(filename: str) -> Path:
        """Resolves target storage path ensuring it remains inside settings.UPLOAD_DIR."""
        safe_filename = SecurityValidator.sanitize_filename(filename)
        destination = (settings.UPLOAD_DIR / safe_filename).resolve()
        
        # Verify destination path is strictly within UPLOAD_DIR
        if not str(destination).startswith(str(settings.UPLOAD_DIR.resolve())):
            raise ValueError("Potential path traversal attempt detected.")
            
        return destination
