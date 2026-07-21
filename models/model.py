from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime, timezone
from enum import Enum
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import DateTime, Column
from sqlalchemy.dialects.postgresql import JSONB


class MemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    VIEWER = "viewer"


class MessageRole(str, Enum):
    ASSISTANT = "assistant"
    USER = "user"
    SYSTEM = "system"


class Organization(SQLModel, table=True):
    __tablename__ = "organizations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )

    org_members: List["OrgMember"] = Relationship(back_populates="organization")
    host_devices: List["HostDevice"] = Relationship(back_populates="organization")
    auth_tokens: List["AuthToken"] = Relationship(back_populates="organization")
    chat_sessions: List["ChatSession"] = Relationship(back_populates="organization")


class OrgMember(SQLModel, table=True):
    __tablename__ = "org_members"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    org_id: UUID = Field(foreign_key="organizations.id", ondelete="CASCADE")
    user_id: UUID
    role: MemberRole = Field(default=MemberRole.VIEWER)
    joined_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )

    organization: Organization = Relationship(back_populates="org_members")


class HostDevice(SQLModel, table=True):
    __tablename__ = "host_devices"

    id: Optional[int] = Field(default=None, primary_key=True)
    host_id: str = Field(unique=True, index=True)
    org_id: UUID = Field(foreign_key="organizations.id", ondelete="CASCADE")
    name: str
    is_online: bool = Field(default=False)
    last_seen: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )

    organization: Organization = Relationship(back_populates="host_devices")


class AuthToken(SQLModel, table=True):
    __tablename__ = "auth_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    org_id: UUID = Field(foreign_key="organizations.id", ondelete="CASCADE")
    name: str
    token: str = Field(unique=True, index=True)
    created_by: UUID
    is_active: bool = Field(default=True)
    expires_at: Optional[datetime] = Field(
        default=None, sa_type=DateTime(timezone=True)
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        sa_type=DateTime(timezone=True),
    )

    organization: Organization = Relationship(back_populates="auth_tokens")


class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    org_id: UUID = Field(foreign_key="organizations.id", ondelete="CASCADE")
    created_by: UUID
    title: str = Field(default="New Chat")
    is_private: bool = Field(default=False)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        sa_type=DateTime(timezone=True),
    )

    messages: List["ChatMessage"] = Relationship(back_populates="session")
    organization: Organization = Relationship(back_populates="chat_sessions")


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: UUID = Field(foreign_key="chat_sessions.id", ondelete="CASCADE")
    sender_id: Optional[UUID] = Field(default=None)
    role: MessageRole
    content: str
    tokens: Optional[int] = Field(default=None)
    metadata_: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSONB))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )

    session: ChatSession = Relationship(back_populates="messages")
