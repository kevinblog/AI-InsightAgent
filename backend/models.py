"""
============================================
AI 行业脉搏 - 数据模型
============================================

定义所有数据库表结构：
- User: 用户表
- Article: 文章表
- Concept: 核心概念表
- UserFavorite: 用户收藏表
"""

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    vip_expire_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    daily_ai_usage: Mapped[int] = mapped_column(Integer, default=0)
    daily_article_usage: Mapped[int] = mapped_column(Integer, default=0)
    last_usage_reset: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    favorites: Mapped[List["UserFavorite"]] = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")

    @property
    def is_vip(self) -> bool:
        if self.vip_expire_at is None:
            return False
        return self.vip_expire_at > datetime.now(self.vip_expire_at.tzinfo)


class Article(Base):
    """文章表"""
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    original_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    translated_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    hot: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    image: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_feed: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    original_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ai_concepts: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    favorites: Mapped[List["UserFavorite"]] = relationship("UserFavorite", back_populates="article", cascade="all, delete-orphan")


class Concept(Base):
    """概念表"""
    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    definition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hot_score: Mapped[float] = mapped_column(Float, default=0.0)
    hot: Mapped[bool] = mapped_column(Boolean, default=False)
    recommended: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    baseline_aligned: Mapped[bool] = mapped_column(Boolean, default=False)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="active")  # pending | active | rejected
    source_articles: Mapped[Optional[List[int]]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    favorites: Mapped[List["UserFavorite"]] = relationship("UserFavorite", back_populates="concept", cascade="all, delete-orphan")


class UserFavorite(Base):
    """用户收藏表"""
    __tablename__ = "user_favorites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    target_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    is_saved: Mapped[bool] = mapped_column(Boolean, default=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="favorites")

    __table_args__ = (
        UniqueConstraint("user_id", "target_type", "target_id", name="uq_user_target"),
        Index("ix_user_target", "user_id", "target_type", "target_id"),
    )


class VerificationCode(Base):
    """验证码表"""
    __tablename__ = "verification_codes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserFeedback(Base):
    """用户反馈表"""
    __tablename__ = "user_feedbacks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    feedback_type: Mapped[str] = mapped_column(String(20), default="general")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    related_concept_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    admin_reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
