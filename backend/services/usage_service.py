"""
============================================
AI 行业脉搏 - 使用统计与配额管理
============================================

管理用户每日 AI 讨论和深度文章查看次数
"""

from datetime import datetime, timezone, timedelta
from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from models import User


class UsageService:
    """使用统计服务"""

    # 免费用户每日配额
    FREE_DAILY_AI_LIMIT = 3
    FREE_DAILY_ARTICLE_LIMIT = 5

    @staticmethod
    def _need_reset(user: User) -> bool:
        """判断是否需要重置今日使用统计"""
        if not user.last_usage_reset:
            return True
        today = datetime.now(timezone.utc).date()
        reset_date = user.last_usage_reset.date()
        return today > reset_date

    @staticmethod
    async def _reset_daily_usage(db: AsyncSession, user: User) -> None:
        """重置今日使用统计"""
        user.daily_ai_usage = 0
        user.daily_article_usage = 0
        user.last_usage_reset = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(user)

    @staticmethod
    async def get_quota(db: AsyncSession, user: User) -> dict:
        """获取用户剩余配额"""
        if UsageService._need_reset(user):
            await UsageService._reset_daily_usage(db, user)

        if user.is_vip:
            return {
                "is_vip": True,
                "ai_used": 0,
                "ai_limit": -1,  # -1 表示无限
                "article_used": 0,
                "article_limit": -1,
                "vip_expire_at": user.vip_expire_at
            }
        else:
            return {
                "is_vip": False,
                "ai_used": user.daily_ai_usage,
                "ai_limit": UsageService.FREE_DAILY_AI_LIMIT,
                "article_used": user.daily_article_usage,
                "article_limit": UsageService.FREE_DAILY_ARTICLE_LIMIT,
                "vip_expire_at": None
            }

    @staticmethod
    async def check_ai_usage(db: AsyncSession, user: User) -> Tuple[bool, str]:
        """检查是否可以进行 AI 讨论"""
        if user.is_vip:
            return True, ""

        if UsageService._need_reset(user):
            await UsageService._reset_daily_usage(db, user)

        if user.daily_ai_usage >= UsageService.FREE_DAILY_AI_LIMIT:
            return False, f"今日 AI 讨论次数已达上限 ({UsageService.FREE_DAILY_AI_LIMIT}次)，升级 VIP 解锁无限次数"

        return True, ""

    @staticmethod
    async def increment_ai_usage(db: AsyncSession, user: User) -> int:
        """增加 AI 使用次数"""
        if UsageService._need_reset(user):
            await UsageService._reset_daily_usage(db, user)

        user.daily_ai_usage += 1
        await db.commit()
        await db.refresh(user)
        return user.daily_ai_usage

    @staticmethod
    async def check_article_usage(db: AsyncSession, user: User) -> Tuple[bool, str]:
        """检查是否可以查看深度文章"""
        if user.is_vip:
            return True, ""

        if UsageService._need_reset(user):
            await UsageService._reset_daily_usage(db, user)

        if user.daily_article_usage >= UsageService.FREE_DAILY_ARTICLE_LIMIT:
            return False, f"今日深度文章查看次数已达上限 ({UsageService.FREE_DAILY_ARTICLE_LIMIT}篇)，升级 VIP 解锁无限查看"

        return True, ""

    @staticmethod
    async def increment_article_usage(db: AsyncSession, user: User) -> int:
        """增加文章查看次数"""
        if UsageService._need_reset(user):
            await UsageService._reset_daily_usage(db, user)

        user.daily_article_usage += 1
        await db.commit()
        await db.refresh(user)
        return user.daily_article_usage


class VIPService:
    """VIP 管理服务"""

    @staticmethod
    async def grant_vip(
        db: AsyncSession,
        user_email: str,
        duration_days: int = 30
    ) -> Tuple[User, bool]:
        """授予 VIP 权限"""
        result = await db.execute(select(User).where(User.phone == user_email))
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"用户不存在: {user_email}")

        now = datetime.now(timezone.utc)
        
        # 如果用户已是 VIP，延长时间
        if user.is_vip and user.vip_expire_at:
            new_expire_at = user.vip_expire_at + timedelta(days=duration_days)
        else:
            new_expire_at = now + timedelta(days=duration_days)

        user.vip_expire_at = new_expire_at
        await db.commit()
        await db.refresh(user)

        return user, True

    @staticmethod
    async def revoke_vip(db: AsyncSession, user_email: str) -> User:
        """取消 VIP 权限"""
        result = await db.execute(select(User).where(User.phone == user_email))
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"用户不存在: {user_email}")

        user.vip_expire_at = None
        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def get_vip_status(db: AsyncSession, user_email: str) -> dict:
        """查询 VIP 状态"""
        result = await db.execute(select(User).where(User.phone == user_email))
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"用户不存在: {user_email}")

        return {
            "user_id": user.id,
            "email": user.phone,
            "is_vip": user.is_vip,
            "vip_expire_at": user.vip_expire_at
        }
