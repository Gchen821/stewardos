from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base_mixins import SoftDeleteMixin, TimestampMixin


class Agent(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "agents"
    __table_args__ = (Index("ix_agents_owner_user_id", "owner_user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    type: Mapped[str] = mapped_column(String(64), default="default", nullable=False)
    runtime_status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    manifest_version: Mapped[str] = mapped_column(String(32), default="1.0.0", nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    chat_selectable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    owner = relationship("User", back_populates="agents")


class Skill(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "skills"
    __table_args__ = (Index("ix_skills_owner_user_id", "owner_user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="general", nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    manifest_version: Mapped[str] = mapped_column(String(32), default="1.0.0", nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    owner = relationship("User", back_populates="skills")


class Tool(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "tools"
    __table_args__ = (Index("ix_tools_owner_user_id", "owner_user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="general", nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    manifest_version: Mapped[str] = mapped_column(String(32), default="1.0.0", nullable=False)
    risk_level: Mapped[str] = mapped_column(String(32), default="low", nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    owner = relationship("User", back_populates="tools")
