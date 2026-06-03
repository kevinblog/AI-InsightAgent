"""
============================================
AI 行业脉搏 - FastAPI 主入口
============================================

提供 RESTful API 接口

启动方式：
1. 安装依赖：pip install -r requirements.txt
2. 配置数据库：设置环境变量或修改 config.py
3. 启动服务：python main.py
4. 访问 API 文档：http://localhost:8000/docs
"""

import uuid
from datetime import datetime
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db, init_database, async_session_maker
from models import User, Article, Concept, UserFavorite, VerificationCode
from config import config
from fastapi import Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# ============================================
# Pydantic 请求/响应模型
# ============================================

class ArticleResponse(BaseModel):
    """文章响应模型"""
    id: int
    title: str
    original_url: Optional[str] = None
    translated_content: Optional[str] = None
    ai_summary: Optional[str] = None
    category: Optional[str] = None
    views: int = 0
    hot: bool = False
    published_at: Optional[datetime] = None
    image: Optional[str] = None
    source: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConceptResponse(BaseModel):
    """概念响应模型"""
    id: int
    name: str
    category: Optional[str] = None
    definition: Optional[str] = None
    hot_score: float = 0.0
    hot: bool = False
    recommended: bool = False
    ai_analysis: Optional[str] = None
    baseline_aligned: bool = False
    icon: Optional[str] = None
    tags: Optional[List[str]] = None
    views: int = 0
    likes: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class FavoriteRequest(BaseModel):
    """收藏请求模型"""
    user_id: uuid.UUID
    target_type: str = Field(..., pattern="^(article|concept)$")
    target_id: int
    is_saved: bool = True
    feedback: Optional[str] = None


class FavoriteResponse(BaseModel):
    """收藏响应模型"""
    id: int
    user_id: uuid.UUID
    target_type: str
    target_id: int
    is_saved: bool
    feedback: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# 认证相关模型
# ============================================

class SendCodeRequest(BaseModel):
    """发送验证码请求"""
    email: str = Field(..., min_length=5, max_length=255)


class SendCodeResponse(BaseModel):
    """发送验证码响应"""
    success: bool
    message: str


class LoginRequest(BaseModel):
    """登录请求"""
    email: str = Field(..., min_length=5, max_length=255)
    code: str = Field(..., min_length=4, max_length=10)


class UserResponse(BaseModel):
    """用户响应模型"""
    id: uuid.UUID
    email: str
    is_vip: bool
    vip_expire_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """登录响应"""
    success: bool
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenRefreshRequest(BaseModel):
    """Token 刷新请求（可选）"""
    pass


# ============================================
# 初始化服务
# ============================================

from services.email_service import EmailService, DummyEmailService
from services.auth_service import JWTService, AuthService

# 初始化 JWT 服务
jwt_service = JWTService(config)

# 选择邮件服务（开发环境使用假服务，生产使用真实 SMTP）
if config.SMTP_USER and config.SMTP_PASSWORD:
    email_service = EmailService(config)
    print("📧 使用真实邮件服务")
else:
    email_service = DummyEmailService(config)
    print("📧 使用假邮件服务（验证码打印在控制台）")

# HTTP Bearer 认证
security = HTTPBearer()


# ============================================
# FastAPI 应用
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    print("🚀 启动 AI 行业脉搏 API 服务...")
    await init_database()
    yield
    # 关闭时清理资源
    print("👋 关闭服务...")


app = FastAPI(
    title="AI 行业脉搏 API",
    description="AI 行业动态与概念库的 RESTful API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# API 路由
# ============================================

@app.get("/")
async def root():
    """API 根路径"""
    return {
        "name": "AI 行业脉搏 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# ----------------------------------------
# 文章接口
# ----------------------------------------

@app.get("/api/articles", response_model=List[ArticleResponse])
async def get_articles(
    category: Optional[str] = None,
    hot: Optional[bool] = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    获取文章列表

    - **category**: 按分类筛选
    - **hot**: 筛选热门文章
    - **skip**: 跳过记录数（分页）
    - **limit**: 返回记录数
    """
    query = select(Article)

    if category:
        query = query.where(Article.category == category)
    if hot is not None:
        query = query.where(Article.hot == hot)

    query = query.order_by(Article.published_at.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    articles = result.scalars().all()
    return articles


@app.get("/api/articles/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取文章详情"""
    result = await db.execute(
        select(Article).where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )

    # 增加阅读量
    article.views += 1
    await db.commit()

    return article


@app.get("/api/articles/{article_id}/content")
async def get_article_content(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取文章完整内容（翻译 + AI 摘要）"""
    result = await db.execute(
        select(Article).where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )

    return {
        "title": article.title,
        "content": article.translated_content,
        "summary": article.ai_summary,
        "source": article.source,
        "category": article.category,
        "published_at": article.published_at
    }


# ----------------------------------------
# 概念接口
# ----------------------------------------

@app.get("/api/concepts", response_model=List[ConceptResponse])
async def get_concepts(
    category: Optional[str] = None,
    hot: Optional[bool] = None,
    recommended: Optional[bool] = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    获取概念列表

    - **category**: 按分类筛选
    - **hot**: 筛选热门概念
    - **recommended**: 筛选推荐概念
    - **skip**: 跳过记录数（分页）
    - **limit**: 返回记录数
    """
    query = select(Concept)

    if category:
        query = query.where(Concept.category == category)
    if hot is not None:
        query = query.where(Concept.hot == hot)
    if recommended is not None:
        query = query.where(Concept.recommended == recommended)

    query = query.order_by(Concept.hot_score.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    concepts = result.scalars().all()
    return concepts


@app.get("/api/concepts/{concept_id}", response_model=ConceptResponse)
async def get_concept(
    concept_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取概念详情"""
    result = await db.execute(
        select(Concept).where(Concept.id == concept_id)
    )
    concept = result.scalar_one_or_none()

    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="概念不存在"
        )

    # 增加浏览量
    concept.views += 1
    await db.commit()

    return concept


# ----------------------------------------
# 收藏接口
# ----------------------------------------

@app.post("/api/favorites", response_model=FavoriteResponse)
async def create_favorite(
    favorite: FavoriteRequest,
    db: AsyncSession = Depends(get_db)
):
    """添加收藏"""
    # 检查是否已存在
    result = await db.execute(
        select(UserFavorite).where(
            and_(
                UserFavorite.user_id == favorite.user_id,
                UserFavorite.target_type == favorite.target_type,
                UserFavorite.target_id == favorite.target_id
            )
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # 更新现有记录
        existing.is_saved = favorite.is_saved
        existing.feedback = favorite.feedback
        await db.commit()
        await db.refresh(existing)
        return existing

    # 创建新收藏
    new_favorite = UserFavorite(
        user_id=favorite.user_id,
        target_type=favorite.target_type,
        target_id=favorite.target_id,
        is_saved=favorite.is_saved,
        feedback=favorite.feedback
    )
    db.add(new_favorite)
    await db.commit()
    await db.refresh(new_favorite)

    return new_favorite


@app.delete("/api/favorites/{favorite_id}")
async def delete_favorite(
    favorite_id: int,
    db: AsyncSession = Depends(get_db)
):
    """取消收藏"""
    result = await db.execute(
        delete(UserFavorite).where(UserFavorite.id == favorite_id)
    )
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏不存在"
        )

    return {"message": "取消收藏成功"}


@app.get("/api/favorites/{user_id}", response_model=List[FavoriteResponse])
async def get_user_favorites(
    user_id: uuid.UUID,
    target_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取用户的所有收藏"""
    query = select(UserFavorite).where(UserFavorite.user_id == user_id)

    if target_type:
        query = query.where(UserFavorite.target_type == target_type)

    result = await db.execute(query)
    favorites = result.scalars().all()
    return favorites


# ----------------------------------------
# 认证接口
# ----------------------------------------

@app.post("/api/auth/send-code", response_model=SendCodeResponse)
async def send_verification_code(
    request: SendCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """发送验证码到邮箱"""
    from services.auth_service import VerificationCodeService
    
    try:
        # 创建验证码服务
        code_service = VerificationCodeService(config, db)
        
        # 生成并保存验证码
        code = await code_service.create_verification_code(request.email)
        
        # 发送邮件
        success = await email_service.send_verification_code(request.email, code)
        
        if success:
            return SendCodeResponse(
                success=True,
                message="验证码已发送，请查收邮件"
            )
        else:
            return SendCodeResponse(
                success=False,
                message="发送失败，请稍后重试（可能发送太频繁）"
            )
            
    except Exception as e:
        print(f"发送验证码失败: {e}")
        return SendCodeResponse(
            success=False,
            message="发送失败，请稍后重试"
        )


@app.post("/api/auth/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """邮箱验证码登录"""
    from services.auth_service import AuthService
    
    try:
        auth_service = AuthService(db, jwt_service, config)
        
        result = await auth_service.login(request.email, request.code)
        
        if result.success and result.user:
            return LoginResponse(
                success=True,
                access_token=result.access_token,
                token_type=result.token_type,
                expires_in=result.expires_in,
                user=UserResponse(
                    id=result.user.id,
                    email=result.user.phone,
                    is_vip=result.user.is_vip,
                    vip_expire_at=result.user.vip_expire_at,
                    created_at=result.user.created_at
                )
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.error or "验证码无效"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"登录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试"
        )


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """获取当前登录用户信息"""
    from services.auth_service import AuthService
    
    auth_service = AuthService(db, jwt_service, config)
    
    user = await auth_service.get_current_user(credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期"
        )
    
    return UserResponse(
        id=user.id,
        email=user.phone,
        is_vip=user.is_vip,
        vip_expire_at=user.vip_expire_at,
        created_at=user.created_at
    )


@app.post("/api/auth/refresh")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """刷新访问 Token（可选实现）"""
    # 验证并刷新 Token
    user_id = jwt_service.get_user_id_from_token(credentials.credentials)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效"
        )
    
    # 简单实现：直接查询用户并返回新 Token
    # 实际项目可以添加 Refresh Token 机制
    from sqlalchemy import select
    from database import async_session_maker
    
    async with async_session_maker() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
        
        new_token = jwt_service.create_access_token(user)
        
        return {
            "access_token": new_token,
            "token_type": "bearer",
            "expires_in": config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }


# ----------------------------------------
# 用户接口（简化版）
# ----------------------------------------

@app.get("/api/users/{user_id}/stats")
async def get_user_stats(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """获取用户统计信息"""
    # 统计收藏数量
    result = await db.execute(
        select(func.count(UserFavorite.id)).where(
            and_(
                UserFavorite.user_id == user_id,
                UserFavorite.is_saved == True
            )
        )
    )
    favorites_count = result.scalar()

    # 统计文章点赞数量
    result = await db.execute(
        select(func.count(UserFavorite.id)).where(
            and_(
                UserFavorite.user_id == user_id,
                UserFavorite.target_type == "article",
                UserFavorite.is_saved == False
            )
        )
    )
    article_likes = result.scalar()

    return {
        "user_id": user_id,
        "favorites_count": favorites_count,
        "article_likes": article_likes
    }


# ============================================
# 启动服务
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
