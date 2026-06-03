"""
============================================
AI 行业脉搏 - 数据库连接模块
============================================

提供异步数据库连接和会话管理
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from config import config


# 创建异步引擎
engine = create_async_engine(
    config.database_url,
    echo=True,  # 开发环境显示 SQL 语句
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

    使用方式：
    @app.get("/items")
    async def get_items(db: AsyncSession = Depends(get_db)):
        ...
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

    自动导入所有模型类，确保表被创建
    """
    # 导入所有模型以触发 SQLAlchemy 注册
    from models import User, Article, Concept, UserFavorite

    async with engine.begin() as conn:
        # DROP TABLE 用于开发环境重建（生产环境请注释）
        # await conn.run_sync(Base.metadata.drop_all)

        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
        print("✅ 数据库表创建成功！")


async def init_database():
    """初始化数据库（创建表 + 种子数据）"""
    print("🚀 正在初始化数据库...")

    # 创建表结构
    await create_tables()

    # 可以在这里添加种子数据
    # await seed_data()

    print("✅ 数据库初始化完成！")
