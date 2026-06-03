"""
============================================
AI 行业脉搏 - 数据模型
============================================

支持 SQLite（本地开发）和 PostgreSQL（生产环境）
"""

import uuid
import json
from datetime import datetime
from typing import Optional, List, Any
from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, ForeignKey, UniqueConstraint, Index, JSON, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database import Base


# JSON 类型兼容 SQLite
class JSONEncoded(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    phone: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    vip_expire_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    daily_ai_usage: Mapped[int] = mapped_column(Integer, default=0)
    daily_article_usage: Mapped[int] = mapped_column(Integer, default=0)
    last_usage_reset: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    @property
    def is_vip(self) -> bool:
        if self.vip_expire_at is None:
            return False
        return self.vip_expire_at > datetime.now(self.vip_expire_at.tzinfo if self.vip_expire_at.tzinfo else None)


class Article(Base):
    """文章表"""
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
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
    ai_concepts: Mapped[Optional[List[str]]] = mapped_column(JSONEncoded, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Concept(Base):
    """概念表"""
    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    definition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hot_score: Mapped[float] = mapped_column(Float, default=0.0)
    hot: Mapped[bool] = mapped_column(Boolean, default=False)
    recommended: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    baseline_aligned: Mapped[bool] = mapped_column(Boolean, default=False)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSONEncoded, nullable=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="active")
    source_articles: Mapped[Optional[List[int]]] = mapped_column(JSONEncoded, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserFavorite(Base):
    """用户收藏表"""
    __tablename__ = "user_favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    target_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    is_saved: Mapped[bool] = mapped_column(Boolean, default=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "target_type", "target_id", name="uq_user_target"),
        Index("ix_user_target", "user_id", "target_type", "target_id"),
    )


class VerificationCode(Base):
    """验证码表"""
    __tablename__ = "verification_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserFeedback(Base):
    """用户反馈表"""
    __tablename__ = "user_feedbacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    user_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    feedback_type: Mapped[str] = mapped_column(String(20), default="general")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    related_concept_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    admin_reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
