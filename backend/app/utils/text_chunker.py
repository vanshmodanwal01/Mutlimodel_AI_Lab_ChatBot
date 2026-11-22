import re
from typing import List


class TextChunker:
    """Splits raw text recursively into semantic chunks with configurable overlap."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def clean_text(self, text: str) -> str:
        """Cleans and normalizes extracted text."""
        if not text:
            return ""
        # Normalize carriage returns and tabs
        text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")
        # Collapse multiple whitespace characters
        text = re.sub(r"[ \t]+", " ", text)
        # Collapse excessive newlines (max 2 consecutive)
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
        return text.strip()

    def split_text(self, text: str) -> List[str]:
        """Splits text recursively using paragraphs, sentences, and words as separators."""
        cleaned = self.clean_text(text)
        if not cleaned:
            return []

        if len(cleaned) <= self.chunk_size:
            return [cleaned]

        chunks = []
        start = 0
        text_length = len(cleaned)

        while start < text_length:
            end = start + self.chunk_size

            # If we are not at the end of text, attempt to find a natural break
            if end < text_length:
                # Look for paragraph break, newline, or sentence punctuation near the boundary
                boundary = cleaned.rfind("\n\n", start, end)
                if boundary == -1:
                    boundary = cleaned.rfind(". ", start, end)
                if boundary == -1:
                    boundary = cleaned.rfind("\n", start, end)
                if boundary == -1:
                    boundary = cleaned.rfind(" ", start, end)

                # Only split at boundary if it's past halfway through the chunk
                if boundary != -1 and boundary > start + (self.chunk_size // 2):
                    end = boundary + (1 if cleaned[boundary] != "." else 2)

            chunk = cleaned[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move window forward by chunk_size - overlap
            advance = max(1, (end - start) - self.chunk_overlap)
            start += advance

        return chunks
