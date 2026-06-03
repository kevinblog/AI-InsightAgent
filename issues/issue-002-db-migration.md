# Issue 002: 本地 Mock 数据迁移至 PostgreSQL

**状态**: 待处理
**优先级**: High
**创建时间**: 2026-06-03
**负责人**: 待指定

---

## 背景

当前系统使用本地 Mock 数据进行开发和测试。为了支持商用部署，需要将数据存储迁移至 PostgreSQL 数据库，实现数据的持久化存储、用户管理和内容管理。

---

## 目标

1. 设计并实现完整的 PostgreSQL 数据库 Schema
2. 支持用户体系（VIP 会员管理）
3. 支持文章内容管理
4. 支持 AI 概念库管理
5. 支持用户收藏和反馈功能
6. 提供 FastAPI 接口供前端调用

---

## 数据库设计

### 1. users（用户表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PRIMARY KEY | 用户唯一标识 |
| phone | VARCHAR(20) | UNIQUE, NOT NULL | 手机号 |
| vip_expire_at | TIMESTAMP | | VIP 到期时间（NULL 表示非 VIP） |
| created_at | TIMESTAMP | DEFAULT NOW() | 注册时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 最后更新时间 |

### 2. articles（文章表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | SERIAL | PRIMARY KEY | 文章 ID |
| title | VARCHAR(500) | NOT NULL | 标题 |
| original_url | VARCHAR(1000) | | 原文链接 |
| translated_content | TEXT | | 翻译内容 |
| ai_summary | TEXT | | AI 摘要 |
| category | VARCHAR(100) | | 分类 |
| views | INTEGER | DEFAULT 0 | 阅读量 |
| published_at | TIMESTAMP | | 发布时间 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

### 3. concepts（核心概念表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | SERIAL | PRIMARY KEY | 概念 ID |
| name | VARCHAR(200) | NOT NULL | 概念名称 |
| category | VARCHAR(100) | | 分类 |
| definition | TEXT | | 概念定义 |
| hot_score | FLOAT | DEFAULT 0 | 热度趋势值 |
| ai_analysis | TEXT | | AI 解析内容 |
| baseline_aligned | BOOLEAN | DEFAULT FALSE | Baseline 对齐状态 |
| icon | VARCHAR(50) | | 图标名称 |
| tags | JSON | | 标签数组 |
| views | INTEGER | DEFAULT 0 | 浏览量 |
| likes | INTEGER | DEFAULT 0 | 点赞数 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

### 4. user_favorites（用户收藏与反馈表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | SERIAL | PRIMARY KEY | 收藏 ID |
| user_id | UUID | FOREIGN KEY (users.id) | 用户 ID |
| target_type | VARCHAR(20) | NOT NULL | 目标类型：article/concept |
| target_id | INTEGER | NOT NULL | 目标 ID |
| is_saved | BOOLEAN | DEFAULT TRUE | 是否收藏（FALSE 可表示点赞） |
| feedback | TEXT | | 用户反馈内容 |
| created_at | TIMESTAMP | DEFAULT NOW() | 收藏时间 |

**索引**:
- UNIQUE(user_id, target_type, target_id) - 防止重复收藏

---

## 技术实现

### 1. 技术栈

- **数据库**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Web 框架**: FastAPI
- **异步支持**: asyncpg

### 2. 文件结构

```
backend/
├── config.py      # 配置文件
├── database.py    # 数据库连接
├── models.py      # 数据模型
├── main.py        # 主入口
└── requirements.txt
```

### 3. API 接口设计（待实现）

- [ ] GET /api/articles - 获取文章列表
- [ ] GET /api/articles/{id} - 获取文章详情
- [ ] GET /api/concepts - 获取概念列表
- [ ] GET /api/concepts/{id} - 获取概念详情
- [ ] POST /api/favorites - 添加收藏
- [ ] DELETE /api/favorites/{id} - 取消收藏
- [ ] GET /api/users/me - 获取当前用户信息

---

## 进度追踪

- [x] Issue 创建
- [ ] 数据库 Schema 设计
- [ ] FastAPI 模型编写
- [ ] 数据库连接测试
- [ ] API 接口开发
- [ ] 前端对接

---

## 备注

1. 数据库连接信息应存储在环境变量中
2. 需要实现数据迁移脚本将现有 Mock 数据导入
3. 考虑添加缓存层（Redis）提升查询性能
