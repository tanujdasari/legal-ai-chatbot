
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="New Conversation",
    )

    jurisdiction: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        default="US",
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="other",
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

    documents: Mapped[list["Document"]] = relationship(
        back_populates="conversation",
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    conversation_id: Mapped[str] = mapped_column(
        ForeignKey(
            "conversations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    sources: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    disclaimer: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    conversation: Mapped["Conversation"] = relationship(
        back_populates="messages",
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    jurisdiction: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
    )

    storage_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
    )

    conversation_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "conversations.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    conversation: Mapped["Conversation | None"] = relationship(
        back_populates="documents",
    )


Index(
    "ix_messages_conversation_created",
    Message.conversation_id,
    Message.created_at,
)

Index(
    "ix_documents_conversation",
    Document.conversation_id,
)
