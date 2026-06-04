"""
============================================
AI 行业脉搏 - 数据库连接模块
============================================

提供异步数据库连接和会话管理
支持 SQLite（本地开发）和 PostgreSQL（生产环境）
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool
from typing import AsyncGenerator

from config import config


# 检测数据库类型
USE_SQLITE = config.USE_SQLITE

if USE_SQLITE:
    # SQLite 本地开发模式
    engine = create_async_engine(
        "sqlite+aiosqlite:///./ai_pulse.db",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
else:
    # PostgreSQL 生产模式
    engine = create_async_engine(
        config.database_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# 创建会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


class Base(DeclarativeBase):
    """SQLAlchemy 基类"""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖注入函数
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """
    创建所有表结构
    """
    # 导入所有模型以触发 SQLAlchemy 注册
    from models import User, Article, Concept, UserFavorite, VerificationCode, UserFeedback

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ 数据库表创建成功！")


async def init_database():
    """初始化数据库"""
    print("🚀 正在初始化数据库...")

    # 创建表结构
    await create_tables()

    # 添加种子数据
    await seed_data()

    print("✅ 数据库初始化完成！")


async def seed_data():
    """添加种子数据"""
    from models import Article, Concept
    from sqlalchemy import select
    from datetime import datetime, timezone

    async with async_session_maker() as session:
        # 检查是否已有数据
        result = await session.execute(select(Article))
        if result.scalars().first():
            print("📦 种子数据已存在，跳过...")
            return

        # 添加示例文章
        articles = [
            Article(
                title="OpenAI 发布 GPT-4o：多模态实时交互新时代",
                original_url="https://example.com/gpt4o",
                translated_content="OpenAI 发布了 GPT-4o，这是首个原生多模态大模型，支持文本、音频、图像的实时交互...",
                ai_summary="GPT-4o 代表了多模态 AI 的重大突破，用户可以直接与 AI 进行语音对话...",
                category="大语言模型",
                views=1250,
                hot=True,
                published_at=datetime.now(timezone.utc),
                source="TechCrunch",
                source_feed="techcrunch_ai"
            ),
            Article(
                title="Anthropic Claude 3.5 引领 AI 安全新标准",
                original_url="https://example.com/claude35",
                translated_content="Anthropic 发布了 Claude 3.5 系列模型，在推理能力和安全性方面取得显著进步...",
                ai_summary="Claude 3.5 展示了 AI 安全性与能力并重的可能性...",
                category="AI 安全",
                views=890,
                hot=True,
                published_at=datetime.now(timezone.utc),
                source="MIT Tech Review",
                source_feed="mit_techreview"
            ),
        ]

        # 添加示例概念
        concepts = [
            Concept(
                name="Agentic Workflow",
                category="AI Agent",
                definition="AI Agent 能够自主规划、执行多步骤任务的工作流程",
                hot_score=95.5,
                hot=True,
                recommended=True,
                ai_analysis="Agentic Workflow 代表了 AI 从被动响应向主动执行的转变...",
                baseline_aligned=False,
                status="active",
                tags=["Agent", "自动化", "工作流"]
            ),
            Concept(
                name="RAG",
                category="检索增强生成",
                definition="Retrieval-Augmented Generation，结合检索和生成的技术",
                hot_score=88.0,
                hot=True,
                recommended=True,
                ai_analysis="RAG 通过结合外部知识库提高了生成内容的准确性...",
                baseline_aligned=True,
                status="baseline",
                tags=["RAG", "检索", "知识库"]
            ),
            Concept(
                name="MoE",
                category="混合专家",
                definition="Mixture of Experts，混合专家模型架构",
                hot_score=82.3,
                hot=False,
                recommended=False,
                ai_analysis="MoE 通过稀疏激活大幅降低了计算成本...",
                baseline_aligned=True,
                status="active",
                tags=["MoE", "稀疏激活", "架构"]
            ),
            Concept(
                name="Test-Time Compute",
                category="推理优化",
                definition="在推理阶段动态分配计算资源的技术",
                hot_score=78.0,
                hot=False,
                recommended=False,
                ai_analysis="Test-Time Compute 让模型在推理时可以根据任务难度自适应调整...",
                baseline_aligned=False,
                status="pending",
                tags=["推理", "计算分配"]
            ),
        ]

        for article in articles:
            session.add(article)
        for concept in concepts:
            session.add(concept)

        await session.commit()
        print("🌱 种子数据添加成功！")
