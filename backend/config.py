"""
============================================
AI 行业脉搏 - 数据库配置
============================================

【重要】此文件包含数据库连接信息，请确保：
1. 生产环境使用环境变量
2. config.py 在 .gitignore 中
3. 不要提交真实的数据库密码

使用方法：
1. 复制 config.example.py 为 config.py
2. 填入您的数据库连接信息
3. 运行 python main.py 自动创建表结构
"""

import os
from typing import Optional


class Config:
    """数据库配置类"""

    # PostgreSQL 连接配置
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ai_pulse")

    # ============================================
    # AI API 配置（用于内容处理 Pipeline）
    # ============================================
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_API_BASE_URL: str = os.getenv("AI_API_BASE_URL", "https://api.deepseek.com")
    AI_MODEL: str = os.getenv("AI_MODEL", "deepseek-chat")

    @property
    def database_url(self) -> str:
        """获取数据库连接 URL"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def sync_database_url(self) -> str:
        """获取同步数据库连接 URL（用于创建表）"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


# 全局配置实例
config = Config()
