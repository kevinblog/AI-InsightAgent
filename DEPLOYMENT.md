# AI 行业脉搏 - 部署指南

## 项目结构
```
backend/
├── main.py          # FastAPI 主入口（已包含静态文件服务）
├── requirements.txt # Python 依赖
├── config.py        # 配置文件
├── database.py      # 数据库连接
├── models.py        # 数据模型
├── services/        # 业务服务
├── scrapers/        # 爬虫模块
├── static/          # 前端静态文件
│   ├── index.html   # 首页
│   ├── admin.html   # 管理后台
│   └── config.js    # 前端配置
├── render.yaml      # Render 部署配置
├── fly.toml         # Fly.io 部署配置
└── Dockerfile       # Docker 配置
```

## 免费部署方案

### 方案一：Vercel（前端静态文件部署）
**优点**：CDN 加速、部署速度快、完美支持前端静态文件

**注意**：Vercel 对 Python 后端的支持有限（主要适合 Serverless Functions），所以我们推荐以下方案：

**选项 A：只部署前端静态文件**
1. 注册 Vercel 账户：https://vercel.com/
2. 安装 Vercel CLI：`npm i -g vercel`
3. 在项目根目录创建一个 `public/` 文件夹
4. 将 `index.html`、`admin.html` 和 `config.example.js` 复制到 `public/` 目录
5. 运行 `vercel` 命令开始部署
6. 按照提示完成部署

**选项 B：前后端分离部署**
- 前端：部署在 Vercel（静态文件）
- 后端：部署在 Render/Fly.io（如其他方案所述）
- 修改前端 `config.js` 中的 API 地址为后端服务地址

---

### 方案二：Render（全栈推荐）
**优点**：简单易用，支持 Python 直接部署，免费额度充足

**步骤**：
1. 注册 Render 账户：https://render.com/
2. 创建新的 Web Service
3. 连接您的 GitHub 仓库
4. 设置：
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. 添加环境变量：
   - `USE_SQLITE`: `true`
   - `JWT_SECRET_KEY`: 生成一个随机密钥
6. 部署完成后会得到一个公开 URL

### 方案三：Fly.io
**优点**：全球边缘部署，性能好

**步骤**：
1. 安装 Fly CLI: https://fly.io/docs/hands-on/install-flyctl/
2. 登录: `fly auth login`
3. 部署: `fly launch`
4. 设置环境变量: `fly secrets set USE_SQLITE=true`

### 方案四：Replit
**优点**：在线开发环境，一键部署

**步骤**：
1. 注册 Replit: https://replit.com/
2. 创建新项目，选择 Python
3. 上传代码
4. 运行 `pip install -r requirements.txt`
5. 点击 "Run" 按钮
6. 获取公开 URL

## 部署后配置

1. **邮件服务**：如需真实发送邮件，配置 SMTP 环境变量：
   - `SMTP_HOST`
   - `SMTP_PORT`
   - `SMTP_USER`
   - `SMTP_PASSWORD`
   - `SMTP_FROM`

2. **AI API**：如需启用 AI 聊天功能，配置：
   - 在 `static/config.js` 中设置 `AI_API_KEY`

## 访问地址

- 首页: `https://your-domain.com/`
- 管理后台: `https://your-domain.com/admin`
- API 文档: `https://your-domain.com/docs`
- 健康检查: `https://your-domain.com/api/health`
