@echo off
REM ============================================
REM AI 行业脉搏 - Windows 启动脚本
REM ============================================

echo 正在启动 AI 行业脉搏...

cd /d %~dp0

REM 创建虚拟环境（如果没有）
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖...
pip install -q -r requirements.txt

REM 启动后端服务
echo.
echo 启动后端服务...
echo    API 地址: http://localhost:8000
echo    API 文档: http://localhost:8000/docs
echo.

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
