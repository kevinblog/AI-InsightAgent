# Issue 003: AI 内容自动采集与智能处理 Pipeline

**状态**: 待开发
**优先级**: High
**创建时间**: 2026-06-03
**负责人**: 待指定

---

## 背景

当前系统使用静态 Mock 数据，无法持续获取最新的 AI 行业动态。需要实现一个自动化 Pipeline，持续从海外权威来源抓取内容，AI 智能处理后入库。

---

## 目标

1. 实现多源内容定时抓取
2. 文章去重处理
3. AI 自动生成高精摘要
4. 自动提取新概念
5. 智能匹配已有概念库
6. 新概念待审状态管理

---

## 数据来源

### 爬取目标

| 来源 | URL | 类型 | 抓取频率 |
|------|-----|------|----------|
| TechCrunch AI | techcrunch.com/category/artificial-intelligence | 新闻 | 每 2 小时 |
| Hacker News | news.ycombinator.com | 社区讨论 | 每 1 小时 |
| Arxiv ML | export.arxiv.org/rss/cs.AI | 学术论文 | 每 6 小时 |
| MIT Technology Review | technologyreview.com/topic/artificial-intelligence | 深度报道 | 每 4 小时 |
| VentureBeat AI | venturebeat.com/category/ai | 行业分析 | 每 3 小时 |

---

## 核心流程

```
┌─────────────────────────────────────────────────────────────────┐
│                     自动 Pipeline 流程                           │
└─────────────────────────────────────────────────────────────────┘

1. 【定时触发】APScheduler 每小时检查一次
         │
         ▼
2. 【多源抓取】并行抓取 5 个数据源
         │
         ▼
3. 【去重检查】基于 URL + 标题哈希去重
         │
         ▼ (新文章)
4. 【AI 处理】调用大模型 API
    ├─ 生成 200 字行业高精摘要
    └─ 提取 3 个前沿新概念
         │
         ▼
5. 【概念匹配】
    ├─ 查询现有概念库
    ├─ 命中的概念：hot_score += 1
    └─ 未命中的概念：pending 状态入库
         │
         ▼
6. 【文章入库】完整文章 + AI 摘要 + 概念标签
```

---

## AI 处理规范

### 摘要生成

```
系统提示词：
你是一位专业的 AI 行业分析师。请为以下英文文章生成：
1. 一段 200 字的中文行业摘要
2. 包含：核心事件、技术突破、市场影响、关键人物/公司

输出格式：
{
  "summary": "...",
  "key_points": ["...", "...", "..."],
  "sentiment": "positive/neutral/negative"
}
```

### 概念提取

```
系统提示词：
从以下文章中提取 3 个 AI 行业前沿新概念。

要求：
- 每个概念不超过 5 个字
- 必须是行业通用术语或新兴概念
- 如：Agentic Workflow, Test-Time Compute, MoE, RAG 等

输出格式：
{
  "concepts": [
    {"name": "概念名", "confidence": 0.95},
    {"name": "概念名", "confidence": 0.85},
    {"name": "概念名", "confidence": 0.75}
  ]
}
```

---

## 概念匹配算法

### 匹配规则

| 匹配方式 | 描述 | 阈值 |
|----------|------|------|
| 精确匹配 | 概念名称完全一致 | 100% |
| 模糊匹配 | 包含/被包含关系 | 80% |
| 语义匹配 | 大模型语义相似度 | 70% |

### 热度更新

- 命中现有概念：`hot_score += 1`
- 文章阅读量 > 1000：`hot_score += 2`
- 概念被多次提取：`hot_score += 0.5`

---

## 数据库字段扩展

### Article 表新增字段

```sql
ALTER TABLE articles ADD COLUMN ai_concepts JSONB;
ALTER TABLE articles ADD COLUMN source_feed VARCHAR(50);
ALTER TABLE articles ADD COLUMN original_title VARCHAR(500);
```

### Concept 表新增字段

```sql
ALTER TABLE concepts ADD COLUMN status VARCHAR(20) DEFAULT 'active';
-- status: 'active' | 'pending' | 'rejected'
ALTER TABLE concepts ADD COLUMN source_articles JSONB;
ALTER TABLE concepts ADD COLUMN confidence FLOAT DEFAULT 1.0;
```

---

## 技术实现

### 技术栈

- **定时任务**: APScheduler
- **爬虫**: requests + BeautifulSoup4
- **RSS 解析**: feedparser
- **AI API**: DeepSeek / 硅基流动（兼容 OpenAI 格式）
- **去重**: 基于 SHA256(URL + title) 的 Redis Set

### 文件结构

```
backend/
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py     # 爬虫基类
│   ├── techcrunch.py       # TechCrunch 爬虫
│   ├── hackernews.py       # Hacker News 爬虫
│   ├── arxiv.py            # Arxiv RSS 爬虫
│   ├── mit_techreview.py   # MIT Tech Review 爬虫
│   └── venturebeat.py      # VentureBeat 爬虫
├── services/
│   ├── __init__.py
│   ├── ai_service.py       # AI API 调用服务
│   └── concept_service.py  # 概念匹配服务
├── scheduler.py            # 定时任务主脚本
└── requirements.txt
```

---

## 定时任务配置

```python
# 每小时执行一次全量检查
@scheduled_job('interval', hours=1)
def run_pipeline():
    ...

# 学术论文每 6 小时单独抓取
@scheduled_job('interval', hours=6)
def fetch_arxiv():
    ...
```

---

## 监控与告警

- [ ] 统计每日抓取文章数量
- [ ] 记录 AI API 调用失败次数
- [ ] 新概念入库通知（可选钉钉/飞书 webhook）
- [ ] 异常错误邮件告警

---

## API 接口（可选）

- `POST /api/admin/pipeline/run` - 手动触发 Pipeline
- `GET /api/admin/concepts/pending` - 获取待审核概念
- `POST /api/admin/concepts/{id}/approve` - 审核通过
- `POST /api/admin/concepts/{id}/reject` - 审核拒绝

---

## 进度追踪

- [x] Issue 创建
- [ ] 爬虫模块开发
- [ ] AI 服务开发
- [ ] 概念匹配服务
- [ ] 定时任务集成
- [ ] 管理后台接口
- [ ] 监控告警

---

## 备注

1. 爬虫需遵守各网站的 robots.txt
2. 建议添加请求间隔（每源 2-5 秒）
3. AI API 需控制调用频率，避免超出限额
4. 考虑添加代理池应对反爬
