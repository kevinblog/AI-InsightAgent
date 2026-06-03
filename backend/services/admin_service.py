"""
============================================
AI 行业脉搏 - 管理员服务
============================================

提供数据看板和概念审核功能
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, Article, Concept, UserFeedback


class DashboardService:
    """数据看板服务"""

    @staticmethod
    async def get_stats(db: AsyncSession) -> Dict[str, Any]:
        """获取核心统计数据"""
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # 今日新增用户
        result = await db.execute(
            select(func.count(User.id)).where(User.created_at >= today_start)
        )
        today_new_users = result.scalar() or 0

        # 今日抓取文章
        result = await db.execute(
            select(func.count(Article.id)).where(Article.created_at >= today_start)
        )
        today_new_articles = result.scalar() or 0

        # 待处理反馈
        result = await db.execute(
            select(func.count(UserFeedback.id)).where(UserFeedback.status == "pending")
        )
        pending_feedbacks = result.scalar() or 0

        # VIP 用户数
        result = await db.execute(
            select(func.count(User.id)).where(User.vip_expire_at > now)
        )
        vip_users = result.scalar() or 0

        # 概念总数
        result = await db.execute(select(func.count(Concept.id)))
        total_concepts = result.scalar() or 0

        # 待审概念数
        result = await db.execute(
            select(func.count(Concept.id)).where(Concept.status == "pending")
        )
        pending_concepts = result.scalar() or 0

        # 用户总数
        result = await db.execute(select(func.count(User.id)))
        total_users = result.scalar() or 0

        return {
            "today_new_users": today_new_users,
            "today_new_articles": today_new_articles,
            "pending_feedbacks": pending_feedbacks,
            "vip_users": vip_users,
            "total_concepts": total_concepts,
            "pending_concepts": pending_concepts,
            "total_users": total_users
        }


class ConceptReviewService:
    """概念审核服务"""

    # Baseline 对齐映射表
    BASELINE_MAPPINGS = {
        "GPT-4": ["百度文心一言", "阿里通义千问", "智谱 GLM-4"],
        "Claude": ["字节豆包", "智谱 GLM", "百度文心"],
        "Midjourney": ["阿里通义万相", "百度文心一格", "腾讯混元"],
        "Agentic Workflow": ["钉钉 AI Agent", "飞书 AI", "百度 Agent"],
        "Test-Time Compute": ["智算推理", "思维链推理"],
        "MoE": ["阿里 Qwen-MoE", "百度 ERNIE-MoE"],
        "RAG": ["阿里云 RAG", "百度 RAG"],
    }

    @staticmethod
    async def get_concepts_by_status(
        db: AsyncSession,
        status: str,
        limit: int = 50
    ) -> List[Concept]:
        """获取指定状态的概念列表"""
        query = select(Concept).where(Concept.status == status)
        query = query.order_by(Concept.created_at.desc()).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_pending_concepts(db: AsyncSession, limit: int = 50) -> List[Concept]:
        """获取待审概念"""
        return await ConceptReviewService.get_concepts_by_status(db, "pending", limit)

    @staticmethod
    async def get_active_concepts(db: AsyncSession, limit: int = 50) -> List[Concept]:
        """获取已通过概念"""
        return await ConceptReviewService.get_concepts_by_status(db, "active", limit)

    @staticmethod
    async def get_baseline_concepts(db: AsyncSession, limit: int = 50) -> List[Concept]:
        """获取 Baseline 对齐概念"""
        return await ConceptReviewService.get_concepts_by_status(db, "baseline", limit)

    @staticmethod
    async def approve_concept(db: AsyncSession, concept_id: int) -> bool:
        """通过概念"""
        result = await db.execute(
            select(Concept).where(Concept.id == concept_id)
        )
        concept = result.scalar_one_or_none()
        if not concept:
            return False

        concept.status = "active"
        concept.baseline_aligned = False
        concept.updated_at = datetime.now(timezone.utc)
        await db.commit()
        return True

    @staticmethod
    async def reject_concept(db: AsyncSession, concept_id: int) -> bool:
        """拒绝概念"""
        result = await db.execute(
            select(Concept).where(Concept.id == concept_id)
        )
        concept = result.scalar_one_or_none()
        if not concept:
            return False

        concept.status = "rejected"
        concept.updated_at = datetime.now(timezone.utc)
        await db.commit()
        return True

    @staticmethod
    async def set_baseline(db: AsyncSession, concept_id: int) -> bool:
        """设置为 Baseline"""
        result = await db.execute(
            select(Concept).where(Concept.id == concept_id)
        )
        concept = result.scalar_one_or_none()
        if not concept:
            return False

        concept.status = "baseline"
        concept.baseline_aligned = True
        concept.updated_at = datetime.now(timezone.utc)
        await db.commit()
        return True

    @staticmethod
    async def align_concept(
        db: AsyncSession,
        concept_id: int,
        chinese_equivalent: str
    ) -> bool:
        """对齐国内等效产品"""
        result = await db.execute(
            select(Concept).where(Concept.id == concept_id)
        )
        concept = result.scalar_one_or_none()
        if not concept:
            return False

        concept.status = "baseline"
        concept.baseline_aligned = True
        concept.definition = f"{concept.name} 的国内等效产品：{chinese_equivalent}"
        concept.updated_at = datetime.now(timezone.utc)
        await db.commit()
        return True

    @staticmethod
    def get_suggested_alignment(concept_name: str) -> Optional[List[str]]:
        """获取建议的对齐产品"""
        for key, values in ConceptReviewService.BASELINE_MAPPINGS.items():
            if key.lower() in concept_name.lower():
                return values
        return None


class FeedbackService:
    """用户反馈服务"""

    @staticmethod
    async def get_pending_feedbacks(
        db: AsyncSession,
        limit: int = 50
    ) -> List[UserFeedback]:
        """获取待处理反馈"""
        query = select(UserFeedback).where(UserFeedback.status == "pending")
        query = query.order_by(UserFeedback.created_at.desc()).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_all_feedbacks(
        db: AsyncSession,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[UserFeedback]:
        """获取所有反馈"""
        query = select(UserFeedback)
        if status:
            query = query.where(UserFeedback.status == status)
        query = query.order_by(UserFeedback.created_at.desc()).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def resolve_feedback(db: AsyncSession, feedback_id: int) -> bool:
        """标记反馈已处理"""
        result = await db.execute(
            select(UserFeedback).where(UserFeedback.id == feedback_id)
        )
        feedback = result.scalar_one_or_none()
        if not feedback:
            return False

        feedback.status = "resolved"
        feedback.updated_at = datetime.now(timezone.utc)
        await db.commit()
        return True

    @staticmethod
    async def dismiss_feedback(db: AsyncSession, feedback_id: int) -> bool:
        """忽略反馈"""
        result = await db.execute(
            select(UserFeedback).where(UserFeedback.id == feedback_id)
        )
        feedback = result.scalar_one_or_none()
        if not feedback:
            return False

        feedback.status = "dismissed"
        feedback.updated_at = datetime.now(timezone.utc)
        await db.commit()
        return True

    @staticmethod
    async def reply_feedback(
        db: AsyncSession,
        feedback_id: int,
        reply: str
    ) -> bool:
        """回复反馈"""
        result = await db.execute(
            select(UserFeedback).where(UserFeedback.id == feedback_id)
        )
        feedback = result.scalar_one_or_none()
        if not feedback:
            return False

        feedback.admin_reply = reply
        feedback.status = "resolved"
        feedback.updated_at = datetime.now(timezone.utc)
        await db.commit()
        return True
