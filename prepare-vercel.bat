@echo off
REM AI 行业脉搏 - Vercel 部署准备脚本 (Windows)

echo 🔧 准备 Vercel 部署...

REM 创建 public 目录
if not exist public mkdir public

REM 复制前端文件
echo 📄 复制前端文件...
copy index.html public\index.html
copy admin.html public\admin.html
copy config.example.js public\config.js

echo.
echo ✅ Vercel 部署准备完成！
echo.
echo 🚀 下一步操作：
echo 1. 安装 Vercel CLI: npm i -g vercel
echo 2. 登录: vercel login
echo 3. 部署: vercel
echo.
echo 💡 提示：对于全栈部署，建议使用 Render（见 DEPLOYMENT.md）
pause
