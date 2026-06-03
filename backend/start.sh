#!/bin/bash
# ============================================
# AI 行业脉搏 - 启动脚本
# ============================================

echo "🚀 正在启动 AI 行业脉搏..."

# 进入后端目录
cd "$(dirname "$0")"

# 创建虚拟环境（如果没有）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -q -r requirements.txt

# 启动后端服务
echo "🚀 启动后端服务..."
echo "   API 地址: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
