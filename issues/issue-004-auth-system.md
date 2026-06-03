# Issue 004: 用户登录与鉴权系统

**状态**: 待开发
**优先级**: High
**创建时间**: 2026-06-03
**负责人**: 待指定

---

## 背景

为了实现用户个性化服务（收藏、VIP 会员管理等），需要开发用户登录与鉴权模块。

---

## 目标

1. 实现邮箱验证码登录
2. 使用 JWT 进行身份认证
3. 支持 VIP 身份识别
4. 验证码有效期管理
5. 安全的密码管理（无需密码）

---

## 技术方案

### 1. 登录流程

```
┌─────────────┐
│   用户输入   │
│   邮箱地址   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  后端验证邮箱格式   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  生成 6 位验证码    │
│  存入 Redis/DB      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  smtplib 发送邮件   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  用户输入验证码     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  后端验证验证码     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  创建/获取用户     │
│  发放 JWT Token    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  前端存储 Token    │
│  识别 VIP 身份     │
└─────────────────────┘
```

### 2. JWT Token 结构

```json
{
    "sub": "user-uuid",
    "email": "user@example.com",
    "is_vip": false,
    "exp": 1717502400,
    "iat": 1717416000
}
```

### 3. 数据库扩展

#### 验证码表 (VerificationCode)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键 |
| email | VARCHAR(255) | 邮箱 |
| code | VARCHAR(6) | 验证码 |
| expires_at | TIMESTAMP | 过期时间 |
| verified | BOOLEAN | 是否已验证 |

---

## API 接口设计

### 1. 发送验证码

```
POST /api/auth/send-code

Request:
{
    "email": "user@example.com"
}

Response (200):
{
    "success": true,
    "message": "验证码已发送"
}
```

### 2. 登录

```
POST /api/auth/login

Request:
{
    "email": "user@example.com",
    "code": "123456"
}

Response (200):
{
    "success": true,
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
        "id": "uuid",
        "email": "user@example.com",
        "is_vip": false,
        "vip_expire_at": null
    }
}
```

### 3. 获取当前用户

```
GET /api/auth/me
Authorization: Bearer <token>

Response (200):
{
    "id": "uuid",
    "email": "user@example.com",
    "is_vip": false,
    "vip_expire_at": null
}
```

### 4. 刷新 Token

```
POST /api/auth/refresh
Authorization: Bearer <token>

Response (200):
{
    "access_token": "...",
    "token_type": "bearer",
    "expires_in": 86400
}
```

---

## 安全要求

| 要求 | 实现方案 |
|------|----------|
| 验证码有效期 | 5 分钟 |
| 发送限流 | 同一邮箱 60 秒内只能发 1 次 |
| 登录失败限制 | 5 次失败后锁定 10 分钟 |
| JWT 有效期 | 24 小时 |
| 密码 | 无需密码，邮箱验证 |
| HTTPS | 生产环境强制 |

---

## 实现计划

- [x] Issue 创建
- [ ] 邮箱服务模块
- [ ] JWT 认证服务
- [ ] 数据库模型
- [ ] API 接口
- [ ] 前端集成

---

## 备注

1. 可使用免费 SMTP 服务（如 QQ 邮箱、163 邮箱、SendGrid）
2. 生产环境建议使用 Redis 存储验证码
3. 可考虑集成邮箱白名单功能（防止滥用）
