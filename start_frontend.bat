@echo off
REM ============================================
REM AI 行业脉搏 - 前端启动脚本
REM ============================================

echo 正在启动前端服务...
echo    前端地址: http://localhost:3000
echo    后端地址: http://localhost:8000
echo.

cd /d %~dp0
python -m http.server 3000
