#!/bin/bash
# ============================================
# AI 行业脉搏 - 前端启动脚本
# ============================================

echo "🚀 正在启动前端服务..."
echo "   前端地址: http://localhost:3000"
echo "   后端地址: http://localhost:8000"
echo ""

cd "$(dirname "$0")"
python3 -m http.server 3000
