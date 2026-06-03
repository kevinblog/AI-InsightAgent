# Issue 006: 管理员数据看板

**状态**: 待开发
**优先级**: High
**创建时间**: 2026-06-03
**负责人**: 待指定

---

## 背景

为方便管理员监控运营数据和审核 AI 提取的概念，需要开发一个专属的数据看板。

---

## 需求

### 1. 核心指标展示

| 指标 | 说明 |
|------|------|
| 今日新增用户 | 当天注册的用户数量 |
| 今日抓取文章 | Pipeline 当天采集的文章数 |
| 待处理反馈 | 用户提交的悬浮球反馈数量 |
| VIP 用户数 | 当前 VIP 用户总数 |
| 概念总数 | 概念库总数量 |

### 2. 概念三态审核

概念具有三种状态：

| 状态 | 说明 | 操作 |
|------|------|------|
| pending | 待审核 | 通过 / 拒绝 |
| active | 已通过 | 可设为 Baseline |
| baseline | Baseline 对齐 | 对齐行业等效产品 |

#### Baseline 对齐功能

将国际 AI 概念对齐到国内等效产品：

| 国际概念 | 国内对齐 |
|----------|----------|
| OpenAI GPT-4 | 百度文心一言 / 阿里通义千问 |
| Claude | 字节豆包 / 智谱 GLM |
| Midjourney | 阿里通义万相 / 百度文心一格 |
| Agentic Workflow | 钉钉 AI Agent / 飞书 AI |

### 3. 用户反馈管理

- 查看用户反馈列表
- 标记已处理
- 回复用户

---

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/admin/dashboard/stats` | GET | 获取核心统计数据 |
| `/api/admin/concepts/pending` | GET | 获取待审概念列表 |
| `/api/admin/concepts/{id}/approve` | POST | 通过概念 |
| `/api/admin/concepts/{id}/reject` | POST | 拒绝概念 |
| `/api/admin/concepts/{id}/baseline` | POST | 设置为 Baseline |
| `/api/admin/concepts/{id}/align` | POST | 对齐国内产品 |
| `/api/admin/feedbacks` | GET | 获取用户反馈列表 |
| `/api/admin/feedbacks/{id}/resolve` | POST | 标记反馈已处理 |

---

## 页面设计

### 布局
- 顶部：核心指标卡片（4-5 个）
- 中部：概念审核列表（Tab 切换）
- 底部：用户反馈列表

### 操作
- 一键通过/拒绝/对齐
- 批量操作支持

---

## 进度

- [x] Issue 创建
- [ ] 后端数据模型
- [ ] 管理员服务
- [ ] 管理接口
- [ ] 前端页面

---

## 备注

- 管理页面独立于主站
- 需要管理员认证
- 考虑添加导出功能
