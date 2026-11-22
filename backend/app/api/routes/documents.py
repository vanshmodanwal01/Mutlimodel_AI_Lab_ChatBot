from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.services.document_service import DocumentService
from backend.app.repositories.document_repo import DocumentRepository
from backend.app.schemas.document import (
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentItem,
    DocumentDeleteResponse
)

router = APIRouter(prefix="/documents", tags=["Documents"])
doc_service = DocumentService()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """Uploads and ingests a document (PDF, DOCX, TXT) into the session RAG vector index."""
    try:
        file_bytes = await file.read()
        doc_record = doc_service.process_and_ingest_document(
            db,
            session_id=session_id,
            filename=file.filename or "uploaded_document.txt",
            file_bytes=file_bytes
        )
        chunk_count = len(doc_record.chunks) if doc_record.chunks else 0

        return DocumentUploadResponse(
            document_id=doc_record.id,
            session_id=doc_record.session_id,
            filename=doc_record.filename,
            file_type=doc_record.file_type,
            file_size=doc_record.file_size,
            chunks_created=chunk_count,
            processing_status=doc_record.processing_status,
            created_at=doc_record.created_at
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(exc)}"
        )


@router.get("", response_model=DocumentListResponse)
def list_documents(session_id: str, db: Session = Depends(get_db)):
    """Lists all uploaded documents for a session."""
    docs = DocumentRepository.get_documents_by_session(db, session_id=session_id)
    items = [
        DocumentItem(
            id=d.id,
            session_id=d.session_id,
            filename=d.filename,
            file_type=d.file_type,
            file_size=d.file_size,
            processing_status=d.processing_status,
            chunk_count=len(d.chunks) if d.chunks else 0,
            created_at=d.created_at
        )
        for d in docs
    ]
    return DocumentListResponse(session_id=session_id, documents=items)


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Deletes an uploaded document and its embedded chunks from the vector store."""
    success = DocumentRepository.delete_document(db, document_id=document_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return DocumentDeleteResponse(
        document_id=document_id,
        success=True,
        message="Document and vector chunks deleted successfully."
    )
