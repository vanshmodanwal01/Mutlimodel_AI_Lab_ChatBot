from typing import List, Tuple, Optional
from sqlalchemy.orm import Session

from backend.app.core.logging import logger
from backend.app.repositories.document_repo import DocumentRepository
from backend.app.ai.gemini_provider import GeminiProvider
from backend.app.utils.vector_math import top_k_similar
from backend.app.schemas.chat import Citation
from backend.app.models.document import Document


class RAGService:
    """Orchestrates semantic retrieval, similarity ranking, and grounded context construction."""

    def __init__(self, top_k: int = 4, similarity_threshold: float = 0.25):
        self.repo = DocumentRepository()
        self.ai_provider = GeminiProvider()
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold

    def retrieve_context(
        self,
        db: Session,
        session_id: str,
        query: str
    ) -> Tuple[Optional[str], List[Citation]]:
        """Finds top relevant chunks from uploaded documents in the session.
        
        Returns:
            (assembled_context_string, list_of_citations)
        """
        # Fetch all chunks for this session
        chunks = self.repo.get_chunks_for_session(db, session_id=session_id)
        if not chunks:
            return None, []

        # Extract embeddings
        candidate_embeddings = [chunk.embedding for chunk in chunks]

        # Generate query vector
        query_vector = self.ai_provider.generate_embedding(query)

        # Rank candidates using cosine similarity
        ranked_matches = top_k_similar(
            query_vector=query_vector,
            candidate_vectors=candidate_embeddings,
            top_k=self.top_k,
            threshold=self.similarity_threshold
        )

        if not ranked_matches:
            return None, []

        citations: List[Citation] = []
        context_blocks: List[str] = []

        # Map document_ids to filenames for citation badges
        doc_cache = {}

        for idx, score in ranked_matches:
            chunk = chunks[idx]
            doc_id = chunk.document_id
            
            if doc_id not in doc_cache:
                doc = db.query(Document).filter(Document.id == doc_id).first()
                doc_cache[doc_id] = doc.filename if doc else "Document"

            filename = doc_cache[doc_id]
            snippet = chunk.chunk_text[:160] + "..." if len(chunk.chunk_text) > 160 else chunk.chunk_text

            citations.append(
                Citation(
                    document_id=doc_id,
                    filename=filename,
                    chunk_index=chunk.chunk_index,
                    snippet=snippet,
                    score=round(score, 3)
                )
            )

            context_blocks.append(
                f"[Source: {filename} | Chunk {chunk.chunk_index + 1}]\n{chunk.chunk_text}"
            )

        assembled_context = "\n\n---\n\n".join(context_blocks)
        return assembled_context, citations
