from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.conversation import Conversation, Message
from backend.app.models.feedback import Feedback


class ConversationRepository:
    """Data access repository for conversations, messages, and feedback."""

    @staticmethod
    def get_or_create_conversation(db: Session, session_id: str, title: str = "New Conversation") -> Conversation:
        """Finds active conversation by session_id or creates a new one."""
        conv = db.query(Conversation).filter(Conversation.session_id == session_id).first()
        if not conv:
            conv = Conversation(session_id=session_id, title=title)
            db.add(conv)
            db.commit()
            db.refresh(conv)
        return conv

    @staticmethod
    def add_message(
        db: Session,
        conversation_id: str,
        role: str,
        content: str,
        modality: str = "text",
        media_url: Optional[str] = None
    ) -> Message:
        """Adds a message record to the conversation."""
        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            modality=modality,
            media_url=media_url
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg

    @staticmethod
    def get_conversation_history(db: Session, session_id: str, limit: int = 30) -> List[Message]:
        """Retrieves recent conversation messages for the given session."""
        conv = db.query(Conversation).filter(Conversation.session_id == session_id).first()
        if not conv:
            return []
        return db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at.asc()).limit(limit).all()

    @staticmethod
    def delete_conversation_history(db: Session, session_id: str) -> bool:
        """Deletes conversation and associated messages for a session."""
        conv = db.query(Conversation).filter(Conversation.session_id == session_id).first()
        if not conv:
            return False
        db.delete(conv)
        db.commit()
        return True

    @staticmethod
    def add_feedback(db: Session, conversation_id: str, message_id: str, rating: int, feedback_text: Optional[str] = None) -> Feedback:
        """Records user feedback for a generated message."""
        feedback = Feedback(
            conversation_id=conversation_id,
            message_id=message_id,
            rating=rating,
            feedback_text=feedback_text
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback
