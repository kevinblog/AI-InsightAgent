#!/bin/bash

# AI 行业脉搏 - Vercel 部署准备脚本

echo "🔧 准备 Vercel 部署..."

# 创建 public 目录
mkdir -p public

# 复制前端文件
echo "📄 复制前端文件..."
cp index.html public/
cp admin.html public/
cp config.example.js public/config.js

# 创建 .gitignore 补充（可选）
if [ ! -f ".gitignore" ]; then
    touch .gitignore
fi

echo ""
echo "✅ Vercel 部署准备完成！"
echo ""
echo "🚀 下一步操作："
echo "1. 安装 Vercel CLI: npm i -g vercel"
echo "2. 登录: vercel login"
echo "3. 部署: vercel"
echo ""
echo "💡 提示：对于全栈部署，建议使用 Render（见 DEPLOYMENT.md）"
