import os
from pathlib import Path
from typing import List, Tuple
from sqlalchemy.orm import Session
from pypdf import PdfReader
from docx import Document as DocxDocument

from backend.app.core.logging import logger
from backend.app.core.security import SecurityValidator
from backend.app.core.config import settings
from backend.app.utils.text_chunker import TextChunker
from backend.app.repositories.document_repo import DocumentRepository
from backend.app.ai.gemini_provider import GeminiProvider
from backend.app.models.document import Document


class DocumentService:
    """Manages document text extraction, preprocessing, chunking, and vector embedding persistence."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.repo = DocumentRepository()
        self.ai_provider = GeminiProvider()

    def extract_text(self, file_path: str, file_type: str) -> str:
        """Extracts plain text content from PDF, DOCX, or TXT file."""
        path = Path(file_path)
        ext = path.suffix.lower()

        try:
            if ext == ".pdf":
                reader = PdfReader(str(path))
                text_parts = [page.extract_text() or "" for page in reader.pages]
                return "\n\n".join(text_parts)

            elif ext == ".docx":
                doc = DocxDocument(str(path))
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                return "\n\n".join(paragraphs)

            elif ext == ".txt":
                # Try UTF-8 first, fallback to latin-1
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        return f.read()
                except UnicodeDecodeError:
                    with open(path, "r", encoding="latin-1") as f:
                        return f.read()

            else:
                raise ValueError(f"Unsupported file format: {ext}")
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            raise

    def process_and_ingest_document(
        self,
        db: Session,
        session_id: str,
        filename: str,
        file_bytes: bytes
    ) -> Document:
        """Full pipeline: validates file, saves to filesystem, extracts text, chunks, embeds, and persists."""
        # 1. Validate file
        is_valid, msg = SecurityValidator.validate_file(
            filename=filename,
            file_size=len(file_bytes),
            allowed_extensions=settings.ALLOWED_DOCUMENT_EXTENSIONS
        )
        if not is_valid:
            raise ValueError(msg)

        # 2. Save file safely
        dest_path = SecurityValidator.get_safe_destination_path(filename)
        with open(dest_path, "wb") as f:
            f.write(file_bytes)

        file_type = dest_path.suffix.lstrip(".").lower()

        # 3. Create document record
        doc_record = self.repo.create_document(
            db,
            session_id=session_id,
            filename=filename,
            file_type=file_type,
            file_path=str(dest_path),
            file_size=len(file_bytes),
            status="pending"
        )

        try:
            # 4. Extract and chunk text
            raw_text = self.extract_text(str(dest_path), file_type)
            chunks = self.chunker.split_text(raw_text)

            if not chunks:
                chunks = ["Document contains no readable text content."]

            # 5. Generate embeddings
            embeddings = self.ai_provider.generate_embeddings_batch(chunks)

            # 6. Prepare chunk database objects
            chunks_data = [
                {
                    "chunk_index": idx,
                    "chunk_text": chunk_text,
                    "embedding": emb,
                    "token_count": len(chunk_text.split()),
                    "meta_info": {"char_count": len(chunk_text)}
                }
                for idx, (chunk_text, emb) in enumerate(zip(chunks, embeddings))
            ]

            # 7. Persist chunks in MySQL
            self.repo.add_chunks_batch(db, document_id=doc_record.id, chunks_data=chunks_data)
            self.repo.update_document_status(db, document_id=doc_record.id, status="processed")
            logger.info(f"Successfully processed document '{filename}' with {len(chunks)} chunks.")
            return doc_record

        except Exception as e:
            self.repo.update_document_status(db, document_id=doc_record.id, status="failed")
            logger.error(f"Failed to process document {doc_record.id}: {e}", exc_info=True)
            raise
