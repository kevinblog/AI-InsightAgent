# AI 行业脉搏 - 快速启动指南

## 一键启动（推荐）

### macOS / Linux

```bash
# 终端 1：启动后端
cd backend
chmod +x start.sh
./start.sh

# 终端 2：启动前端
cd ..
chmod +x start_frontend.sh
./start_frontend.sh
```

### Windows

```batch
# CMD 1：启动后端
cd backend
start.bat

# CMD 2：启动前端
cd ..
start_frontend.bat
```

## 访问地址

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:3000 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |
| 管理后台 | http://localhost:3000/admin.html |

## 功能说明

### 前台 (index.html)
- AI 行业资讯浏览
- 核心概念库
- AI 智能讨论（需登录，有每日次数限制）
- 深度文章查看（需登录，有每日次数限制）

### 管理后台 (admin.html)
- 核心运营指标
- 概念三态审核
- 用户反馈管理
- VIP 管理

## 配置说明

### 后端配置
编辑 `backend/config.py`：
```python
USE_SQLITE = True  # True=本地 SQLite，False=PostgreSQL
AI_API_KEY = "your-api-key"  # DeepSeek API Key
```

### 前端配置
编辑 `config.js`：
```javascript
const API_CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    AI_API_KEY: 'your-api-key'
};
```

## 数据库

本地使用 SQLite，数据存储在 `backend/ai_pulse.db`

首次启动会自动：
1. 创建数据库表
2. 添加示例数据（文章、概念）

## 注意事项

1. **后端必须先启动**，前端才能正常访问 API
2. **不填 AI API Key** 时，AI 对话功能不可用，但可以浏览内容
3. **登录功能** 需要配置 SMTP 才能发送邮件验证码（可选）
