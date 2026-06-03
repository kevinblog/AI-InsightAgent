"""
============================================
AI 行业脉搏 - JWT 认证服务
============================================

提供 JWT Token 生成、验证和用户鉴权功能
"""

import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from dataclasses import dataclass

from jose import jwt
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, VerificationCode

logger = logging.getLogger(__name__)


@dataclass
class LoginResult:
    """登录结果"""
    success: bool
    user: Optional[User] = None
    access_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = 86400
    error: Optional[str] = None


class JWTService:
    """JWT 服务类"""

    def __init__(self, config):
        """初始化 JWT 服务"""
        self.config = config
        self.secret_key = config.JWT_SECRET_KEY
        self.algorithm = config.JWT_ALGORITHM
        self.access_token_expire_minutes = config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES

    def create_access_token(self, user: User) -> str:
        """创建访问令牌"""
        to_encode = {
            "sub": str(user.id),
            "email": user.phone,  # phone 字段存储邮箱
            "is_vip": user.is_vip,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证 Token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token 已过期")
            return None
        except jwt.PyJWTError as e:
            logger.warning(f"Token 无效: {e}")
            return None

    def get_user_id_from_token(self, token: str) -> Optional[uuid.UUID]:
        """从 Token 获取用户 ID"""
        payload = self.verify_token(token)
        if payload:
            return uuid.UUID(payload.get("sub"))
        return None


class VerificationCodeService:
    """验证码服务类"""

    def __init__(self, config, db_session: AsyncSession):
        """初始化验证码服务"""
        self.config = config
        self.db = db_session
        self.code_length = config.VERIFICATION_CODE_LENGTH
        self.code_expire_minutes = config.VERIFICATION_CODE_EXPIRE_MINUTES

    async def create_verification_code(self, email: str) -> str:
        """创建验证码"""
        # 先生成随机码
        import random
        digits = "0123456789"
        code = "".join(random.choice(digits) for _ in range(self.code_length))

        # 计算过期时间
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=self.code_expire_minutes)

        # 保存到数据库
        verification_code = VerificationCode(
            email=email,
            code=code,
            expires_at=expires_at,
            verified=False
        )
        self.db.add(verification_code)
        await self.db.commit()

        return code

    async def verify_code(self, email: str, code: str) -> tuple[bool, Optional[VerificationCode]]:
        """验证验证码"""
        # 查询未过期且未验证的验证码
        stmt = select(VerificationCode).where(
            VerificationCode.email == email,
            VerificationCode.code == code,
            VerificationCode.verified == False,
            VerificationCode.expires_at > datetime.now(timezone.utc)
        )
        result = await self.db.execute(stmt)
        verification_code = result.scalar_one_or_none()

        if verification_code:
            # 标记为已验证
            verification_code.verified = True
            await self.db.commit()
            return True, verification_code

        return False, None


class AuthService:
    """认证服务类"""

    def __init__(self, db: AsyncSession, jwt_service: JWTService, config):
        self.db = db
        self.jwt_service = jwt_service
        self.verification_service = VerificationCodeService(config, db)
        self.config = config

    async def login(self, email: str, code: str) -> LoginResult:
        """登录流程"""
        # 1. 验证验证码
        verified, _ = await self.verification_service.verify_code(email, code)
        if not verified:
            return LoginResult(success=False, error="验证码无效或已过期")

        # 2. 查询或创建用户
        user = await self._get_or_create_user(email)

        # 3. 创建 Token
        access_token = self.jwt_service.create_access_token(user)

        return LoginResult(
            success=True,
            user=user,
            access_token=access_token,
            expires_in=self.config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    async def get_current_user(self, token: str) -> Optional[User]:
        """获取当前登录用户"""
        user_id = self.jwt_service.get_user_id_from_token(token)
        if not user_id:
            return None

        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def _get_or_create_user(self, email: str) -> User:
        """获取或创建用户"""
        result = await self.db.execute(select(User).where(User.phone == email))
        user = result.scalar_one_or_none()

        if user:
            return user

        # 创建新用户
        user = User(
            id=uuid.uuid4(),
            phone=email,  # phone 字段存储邮箱
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"新用户注册: {email}")
        return user
