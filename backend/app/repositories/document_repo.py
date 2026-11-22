from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.document import Document, DocumentChunk


class DocumentRepository:
    """Database repository for document records and chunk vector persistence."""

    @staticmethod
    def create_document(
        db: Session,
        session_id: str,
        filename: str,
        file_type: str,
        file_path: str,
        file_size: int,
        status: str = "pending"
    ) -> Document:
        """Inserts a new document record."""
        doc = Document(
            session_id=session_id,
            filename=filename,
            file_type=file_type,
            file_path=file_path,
            file_size=file_size,
            processing_status=status
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    def add_chunks_batch(
        db: Session,
        document_id: str,
        chunks_data: List[dict]
    ) -> List[DocumentChunk]:
        """Inserts a batch of document chunks with their dense vector embeddings."""
        chunk_objects = []
        for item in chunks_data:
            chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=item["chunk_index"],
                chunk_text=item["chunk_text"],
                embedding=item["embedding"],
                token_count=item.get("token_count", len(item["chunk_text"].split())),
                meta_info=item.get("meta_info", {})
            )
            chunk_objects.append(chunk)

        db.bulk_save_objects(chunk_objects)
        db.commit()
        return chunk_objects

    @staticmethod
    def update_document_status(db: Session, document_id: str, status: str) -> Optional[Document]:
        """Updates the processing status of a document."""
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.processing_status = status
            db.commit()
            db.refresh(doc)
        return doc

    @staticmethod
    def get_documents_by_session(db: Session, session_id: str) -> List[Document]:
        """Lists all uploaded documents for a session."""
        return db.query(Document).filter(Document.session_id == session_id).order_by(Document.created_at.desc()).all()

    @staticmethod
    def get_chunks_for_session(db: Session, session_id: str) -> List[DocumentChunk]:
        """Fetches all chunk records and embeddings belonging to documents in a session."""
        return (
            db.query(DocumentChunk)
            .join(Document, DocumentChunk.document_id == Document.id)
            .filter(Document.session_id == session_id, Document.processing_status == "processed")
            .all()
        )

    @staticmethod
    def delete_document(db: Session, document_id: str) -> bool:
        """Deletes a document and its cascading chunks."""
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return False
        db.delete(doc)
        db.commit()
        return True
