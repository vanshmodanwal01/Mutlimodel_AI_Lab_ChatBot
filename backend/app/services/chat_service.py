import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.core.logging import logger
from backend.app.repositories.conversation_repo import ConversationRepository
from backend.app.services.emotional_support_service import EmotionalSupportService
from backend.app.services.rag_service import RAGService
from backend.app.ai.gemini_provider import GeminiProvider
from backend.app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    Citation,
    ConversationHistoryResponse,
    MessageHistoryItem
)


class ChatService:
    """Orchestrates end-to-end conversation flow, safety validation, RAG context, and LLM generation."""

    def __init__(self, llm_provider: Optional[GeminiProvider] = None):
        self.repo = ConversationRepository()
        self.emotional_support = EmotionalSupportService()
        self.rag_service = RAGService()
        self.llm = llm_provider or GeminiProvider()

    def process_chat_message(
        self,
        db: Session,
        request: ChatMessageRequest
    ) -> ChatMessageResponse:
        """Processes a chat query with full safety checks, multi-turn memory, RAG retrieval, and persistent history."""
        session_id = request.session_id
        user_message = request.message.strip()

        # Step 1: Ensure conversation exists
        conversation = self.repo.get_or_create_conversation(db, session_id=session_id)

        # Step 2: Record incoming user message
        user_msg_record = self.repo.add_message(
            db,
            conversation_id=conversation.id,
            role="user",
            content=user_message,
            modality="text",
            media_url=request.image_url
        )

        # Step 3: Safety & Crisis Evaluation
        is_crisis, crisis_reply = self.emotional_support.evaluate_safety_and_crisis(user_message)
        if is_crisis and crisis_reply:
            assistant_msg_record = self.repo.add_message(
                db,
                conversation_id=conversation.id,
                role="assistant",
                content=crisis_reply,
                modality="text"
            )
            return ChatMessageResponse(
                session_id=session_id,
                conversation_id=conversation.id,
                message_id=assistant_msg_record.id,
                reply=crisis_reply,
                crisis_detected=True,
                citations=[]
            )

        # Step 4: Prompt Injection Protection
        is_injection, injection_reply = self.emotional_support.detect_prompt_injection(user_message)
        if is_injection and injection_reply:
            assistant_msg_record = self.repo.add_message(
                db,
                conversation_id=conversation.id,
                role="assistant",
                content=injection_reply,
                modality="text"
            )
            return ChatMessageResponse(
                session_id=session_id,
                conversation_id=conversation.id,
                message_id=assistant_msg_record.id,
                reply=injection_reply,
                crisis_detected=False,
                citations=[]
            )

        # Step 5: Perform RAG retrieval if enabled
        rag_context = None
        citations: List[Citation] = []
        if request.enable_rag:
            rag_context, citations = self.rag_service.retrieve_context(
                db,
                session_id=session_id,
                query=user_message
            )

        # Step 6: Retrieve multi-turn history for context
        history_records = self.repo.get_conversation_history(db, session_id=session_id, limit=10)
        formatted_history: List[Dict[str, str]] = [
            {"role": rec.role, "content": rec.content}
            for rec in history_records[:-1]  # Exclude current query just added
        ]

        # Step 7: Assemble grounded system instructions
        system_instruction = self.emotional_support.get_system_instruction(rag_context=rag_context)

        # Step 8: Generate LLM response
        reply_text = self.llm.generate_response(
            prompt=user_message,
            system_instruction=system_instruction,
            chat_history=formatted_history
        )

        # Step 9: Persist assistant message
        assistant_msg_record = self.repo.add_message(
            db,
            conversation_id=conversation.id,
            role="assistant",
            content=reply_text,
            modality="text"
        )

        return ChatMessageResponse(
            session_id=session_id,
            conversation_id=conversation.id,
            message_id=assistant_msg_record.id,
            reply=reply_text,
            crisis_detected=False,
            citations=citations
        )

    def get_history(self, db: Session, session_id: str) -> ConversationHistoryResponse:
        """Retrieves formatted conversation history for a session."""
        conv = self.repo.get_or_create_conversation(db, session_id=session_id)
        records = self.repo.get_conversation_history(db, session_id=session_id)
        items = [
            MessageHistoryItem(
                id=rec.id,
                role=rec.role,
                content=rec.content,
                modality=rec.modality,
                media_url=rec.media_url,
                created_at=rec.created_at
            )
            for rec in records
        ]
        return ConversationHistoryResponse(
            session_id=session_id,
            conversation_id=conv.id,
            title=conv.title,
            messages=items
        )

    def delete_history(self, db: Session, session_id: str) -> bool:
        """Deletes all messages and conversation history for a session."""
        return self.repo.delete_conversation_history(db, session_id)
