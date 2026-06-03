"""
============================================
AI 行业脉搏 - 数据库配置示例
============================================

使用方法：
1. 复制此文件为 config.py
2. 填入您的数据库连接信息
3. 不要提交 config.py 到 GitHub
"""

import os

# 数据库配置（使用环境变量或直接填写）
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "ai_pulse")
