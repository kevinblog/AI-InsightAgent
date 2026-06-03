"""
============================================
AI 行业脉搏 - 配置文件
============================================

本地开发版本配置
"""

import os

# ============================================
# 数据库配置
# ============================================
# True = 使用 SQLite（本地开发，无需安装数据库）
# False = 使用 PostgreSQL（生产环境）
USE_SQLITE = True

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "ai_pulse")

@property
def database_url(self) -> str:
    return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

# ============================================
# AI API 配置
# ============================================
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_API_BASE_URL = os.getenv("AI_API_BASE_URL", "https://api.deepseek.com")
AI_MODEL = os.getenv("AI_MODEL", "deepseek-chat")

# ============================================
# 邮件服务配置（可选）
# ============================================
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "")

# ============================================
# JWT 配置
# ============================================
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 小时

# ============================================
# 验证码配置
# ============================================
VERIFICATION_CODE_EXPIRE_MINUTES = 5
VERIFICATION_CODE_LENGTH = 6


class Config:
    """配置类"""
    USE_SQLITE = USE_SQLITE
    AI_API_KEY = AI_API_KEY
    AI_API_BASE_URL = AI_API_BASE_URL
    AI_MODEL = AI_MODEL
    SMTP_HOST = SMTP_HOST
    SMTP_PORT = SMTP_PORT
    SMTP_USER = SMTP_USER
    SMTP_PASSWORD = SMTP_PASSWORD
    SMTP_FROM = SMTP_FROM or SMTP_USER
    JWT_SECRET_KEY = JWT_SECRET_KEY
    JWT_ALGORITHM = JWT_ALGORITHM
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    VERIFICATION_CODE_EXPIRE_MINUTES = VERIFICATION_CODE_EXPIRE_MINUTES
    VERIFICATION_CODE_LENGTH = VERIFICATION_CODE_LENGTH

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


# 全局配置实例
config = Config()
