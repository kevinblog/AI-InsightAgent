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
    """
    用户表

    存储用户基本信息，支持 VIP 会员管理
    """
    __tablename__ = "users"

    # 主键：UUID 类型
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # 手机号（唯一）
    phone: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )

    # VIP 到期时间（NULL 表示非 VIP）
    vip_expire_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # ============================================
    # Pipeline 新增字段
    # ============================================
    # 状态：active | pending | rejected
    status: Mapped[str] = mapped_column(String(20), default="active")

    # 来源文章 ID 列表（JSON 数组）
    source_articles: Mapped[Optional[List[int]]] = mapped_column(JSON, nullable=True)

    # 置信度
    confidence: Mapped[float] = mapped_column(Float, default=1.0)

    # 关系
    favorites: Mapped[List["UserFavorite"]] = relationship(
        "UserFavorite",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    @property
    def is_vip(self) -> bool:
        """检查用户是否为 VIP"""
        if self.vip_expire_at is None:
            return False
        return self.vip_expire_at > datetime.now(self.vip_expire_at.tzinfo)

    def __repr__(self):
        return f"<User(id={self.id}, phone={self.phone[:3]}***)>"


class Article(Base):
    """
    文章表

    存储 AI 行业资讯文章
    """
    __tablename__ = "articles"

    # 主键：自增 ID
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 标题
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)

    # 原文链接
    original_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # 翻译内容
    translated_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # AI 摘要
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 分类
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # 阅读量
    views: Mapped[int] = mapped_column(Integer, default=0)

    # 是否热门
    hot: Mapped[bool] = mapped_column(Boolean, default=False)

    # 发布时间
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # 封面图片
    image: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # 来源
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # 来源标识（techcrunch_ai, hackernews, arxiv_csai 等）
    source_feed: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)

    # 英文原文标题
    original_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # AI 提取的概念（JSON 数组）
    ai_concepts: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # 关系
    favorites: Mapped[List["UserFavorite"]] = relationship(
        "UserFavorite",
        back_populates="article",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title[:30]}...)>"


class Concept(Base):
    """
    核心概念表

    存储 AI 领域核心概念
    """
    __tablename__ = "concepts"

    # 主键：自增 ID
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 概念名称
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # 分类
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # 概念定义
    definition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 热度趋势值
    hot_score: Mapped[float] = mapped_column(Float, default=0.0)

    # 是否热门
    hot: Mapped[bool] = mapped_column(Boolean, default=False)

    # 是否推荐
    recommended: Mapped[bool] = mapped_column(Boolean, default=False)

    # AI 解析内容
    ai_analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Baseline 对齐状态
    baseline_aligned: Mapped[bool] = mapped_column(Boolean, default=False)

    # 图标名称
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # 标签数组（JSON 格式存储）
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # 浏览量
    views: Mapped[int] = mapped_column(Integer, default=0)

    # 点赞数
    likes: Mapped[int] = mapped_column(Integer, default=0)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # 关系
    favorites: Mapped[List["UserFavorite"]] = relationship(
        "UserFavorite",
        back_populates="concept",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Concept(id={self.id}, name={self.name})>"


class UserFavorite(Base):
    """
    用户收藏与反馈表

    存储用户对文章和概念的收藏/点赞记录
    """
    __tablename__ = "user_favorites"

    # 主键：自增 ID
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 用户 ID（外键）
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # 目标类型：article / concept
    target_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # 目标 ID（关联文章或概念的 ID）
    target_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # 是否收藏（False 可表示点赞）
    is_saved: Mapped[bool] = mapped_column(Boolean, default=True)

    # 用户反馈内容
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="favorites")
    article: Mapped[Optional["Article"]] = relationship(
        "Article",
        back_populates="favorites",
        foreign_keys=[target_id],
        primaryjoin="and_(UserFavorite.target_type=='article', UserFavorite.target_id==Article.id)"
    )
    concept: Mapped[Optional["Concept"]] = relationship(
        "Concept",
        back_populates="favorites",
        foreign_keys=[target_id],
        primaryjoin="and_(UserFavorite.target_type=='concept', UserFavorite.target_id==Concept.id)"
    )

    # 唯一约束：防止重复收藏
    __table_args__ = (
        UniqueConstraint("user_id", "target_type", "target_id", name="uq_user_target"),
        Index("ix_user_target", "user_id", "target_type", "target_id"),
    )

    def __repr__(self):
        return f"<UserFavorite(user_id={self.user_id}, type={self.target_type}, id={self.target_id})>"
