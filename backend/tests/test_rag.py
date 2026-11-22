import uuid
from backend.app.db.session import get_session
from backend.app.utils.text_chunker import TextChunker
from backend.app.utils.vector_math import cosine_similarity, top_k_similar
from backend.app.services.document_service import DocumentService
from backend.app.services.rag_service import RAGService
from backend.app.services.chat_service import ChatService
from backend.app.schemas.chat import ChatMessageRequest
from backend.app.repositories.document_repo import DocumentRepository


def test_text_chunker():
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    sample_text = (
        "MindBridge AI is an intelligent conversational platform. "
        "It supports multimodal AI inputs including text, images, and audio. "
        "It also features a robust RAG architecture for grounding answers in documents."
    )
    chunks = chunker.split_text(sample_text)
    assert len(chunks) >= 2
    assert all(len(c) <= 120 for c in chunks)


def test_vector_cosine_similarity():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]
    v4 = [-1.0, 0.0, 0.0]

    assert round(cosine_similarity(v1, v2), 4) == 1.0
    assert round(cosine_similarity(v1, v3), 4) == 0.0
    assert round(cosine_similarity(v1, v4), 4) == -1.0


def test_top_k_ranking():
    query = [1.0, 0.0, 0.0]
    candidates = [
        [0.0, 1.0, 0.0],  # 0.0
        [0.8, 0.2, 0.0],  # ~0.97
        [0.5, 0.5, 0.0],  # ~0.71
    ]
    ranked = top_k_similar(query, candidates, top_k=2, threshold=0.1)
    assert len(ranked) == 2
    assert ranked[0][0] == 1  # candidate 1 is highest
    assert ranked[1][0] == 2  # candidate 2 is second


def test_document_ingestion_and_rag_retrieval():
    db = get_session()
    doc_service = DocumentService(chunk_size=150, chunk_overlap=20)
    rag_service = RAGService(top_k=3, similarity_threshold=0.1)
    chat_service = ChatService()
    test_session = f"rag_session_{uuid.uuid4().hex[:8]}"

    sample_doc_text = (
        "MindBridge Platform Architecture Guidelines:\n"
        "1. Always treat user data confidentially.\n"
        "2. Ground all facts in reliable reference material.\n"
        "3. MindBridge utilizes MySQL database for vector persistence."
    )

    # 1. Ingest document
    doc = doc_service.process_and_ingest_document(
        db,
        session_id=test_session,
        filename="guidelines.txt",
        file_bytes=sample_doc_text.encode("utf-8")
    )
    assert doc.id is not None
    assert doc.processing_status == "processed"

    # 2. Retrieve context via RAG
    context, citations = rag_service.retrieve_context(
        db,
        session_id=test_session,
        query="What database does MindBridge utilize for vector persistence?"
    )
    assert context is not None
    assert len(citations) > 0
    assert citations[0].filename == "guidelines.txt"

    # 3. Chat with RAG enabled
    chat_req = ChatMessageRequest(
        session_id=test_session,
        message="Explain the MindBridge database architecture guidelines.",
        enable_rag=True
    )
    chat_res = chat_service.process_chat_message(db, chat_req)
    assert len(chat_res.citations) > 0
    assert chat_res.citations[0].filename == "guidelines.txt"

    # 4. Cleanup
    DocumentRepository.delete_document(db, doc.id)
    chat_service.delete_history(db, test_session)
