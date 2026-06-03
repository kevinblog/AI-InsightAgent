"""
============================================
AI 行业脉搏 - 概念服务模块
============================================

提供概念匹配和管理功能：
1. 概念去重检查
2. 新概念入库（待审状态）
3. 热度值更新
"""

import uuid
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from models import Concept, Article


class ConceptService:
    """
    概念服务类

    负责概念库的管理和匹配
    """

    def __init__(self, db: AsyncSession):
        """
        初始化概念服务

        Args:
            db: 数据库会话
        """
        self.db = db

    async def get_all_concepts(self) -> List[Concept]:
        """
        获取所有活跃概念

        Returns:
            Concept 列表
        """
        result = await self.db.execute(
            select(Concept).where(Concept.status == "active")
        )
        return list(result.scalars().all())

    async def get_concept_names(self) -> List[str]:
        """
        获取所有活跃概念的名称列表

        Returns:
            概念名称列表
        """
        result = await self.db.execute(
            select(Concept.name).where(Concept.status == "active")
        )
        return [row[0] for row in result.fetchall()]

    async def check_concept_exists(self, concept_name: str) -> Tuple[bool, Optional[Concept]]:
        """
        检查概念是否已存在

        Args:
            concept_name: 概念名称

        Returns:
            (是否存在, 概念对象)
        """
        # 精确匹配
        result = await self.db.execute(
            select(Concept).where(Concept.name == concept_name)
        )
        concept = result.scalar_one_or_none()
        if concept:
            return True, concept

        # 模糊匹配
        result = await self.db.execute(
            select(Concept).where(
                Concept.name.ilike(f"%{concept_name}%")
            )
        )
        concept = result.scalar_one_or_none()
        if concept:
            return True, concept

        return False, None

    async def increment_hot_score(self, concept_id: int, increment: float = 1.0) -> bool:
        """
        增加概念热度值

        Args:
            concept_id: 概念 ID
            increment: 增量

        Returns:
            是否成功
        """
        try:
            await self.db.execute(
                update(Concept)
                .where(Concept.id == concept_id)
                .values(
                    hot_score=Concept.hot_score + increment,
                    updated_at=datetime.now(timezone.utc)
                )
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"❌ 更新热度失败: {e}")
            return False

    async def create_pending_concept(
        self,
        name: str,
        source_article_id: int,
        confidence: float = 1.0,
        category: str = "待分类"
    ) -> Optional[Concept]:
        """
        创建待审概念

        Args:
            name: 概念名称
            source_article_id: 来源文章 ID
            confidence: 置信度
            category: 分类

        Returns:
            新创建的概念对象
        """
        # 检查是否已存在（防止重复）
        exists, _ = await self.check_concept_exists(name)
        if exists:
            return None

        concept = Concept(
            name=name,
            category=category,
            definition=f"待审核 - 来源文章 ID: {source_article_id}",
            status="pending",  # 待审状态
            confidence=confidence,
            hot_score=0.5,  # 初始热度
            baseline_aligned=False,
            tags=[]
        )

        self.db.add(concept)
        await self.db.commit()
        await self.db.refresh(concept)

        print(f"✅ 创建待审概念: {name}")
        return concept

    async def approve_concept(self, concept_id: int) -> bool:
        """
        审核通过概念

        Args:
            concept_id: 概念 ID

        Returns:
            是否成功
        """
        try:
            await self.db.execute(
                update(Concept)
                .where(Concept.id == concept_id)
                .values(
                    status="active",
                    baseline_aligned=True,
                    updated_at=datetime.now(timezone.utc)
                )
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"❌ 审核通过失败: {e}")
            return False

    async def reject_concept(self, concept_id: int) -> bool:
        """
        审核拒绝概念

        Args:
            concept_id: 概念 ID

        Returns:
            是否成功
        """
        try:
            await self.db.execute(
                update(Concept)
                .where(Concept.id == concept_id)
                .values(
                    status="rejected",
                    updated_at=datetime.now(timezone.utc)
                )
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"❌ 审核拒绝失败: {e}")
            return False

    async def get_pending_concepts(self) -> List[Concept]:
        """
        获取所有待审概念

        Returns:
            待审概念列表
        """
        result = await self.db.execute(
            select(Concept)
            .where(Concept.status == "pending")
            .order_by(Concept.created_at.desc())
        )
        return list(result.scalars().all())

    async def link_concept_to_article(
        self,
        concept_id: int,
        article_id: int
    ) -> bool:
        """
        将概念关联到文章

        Args:
            concept_id: 概念 ID
            article_id: 文章 ID

        Returns:
            是否成功
        """
        try:
            # 更新概念关联的文章
            result = await self.db.execute(
                select(Concept).where(Concept.id == concept_id)
            )
            concept = result.scalar_one_or_none()
            if not concept:
                return False

            # 追加文章 ID
            source_articles = concept.source_articles or []
            if article_id not in source_articles:
                source_articles.append(article_id)
                await self.db.execute(
                    update(Concept)
                    .where(Concept.id == concept_id)
                    .values(source_articles=source_articles)
                )
                await self.db.commit()

            return True
        except Exception as e:
            print(f"❌ 关联概念失败: {e}")
            return False


class DeduplicationService:
    """
    去重服务

    基于 URL + 标题哈希进行去重
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._seen_hashes: set = set()

    async def load_existing_hashes(self):
        """加载已存在的文章哈希"""
        result = await self.db.execute(
            select(Article.content_hash)
        )
        self._seen_hashes = {row[0] for row in result.fetchall()}
        print(f"📦 已加载 {len(self._seen_hashes)} 个已存文章哈希")

    def generate_hash(self, url: str, title: str) -> str:
        """生成内容哈希"""
        content = f"{url}|{title}"
        return hashlib.sha256(content.encode()).hexdigest()

    def is_duplicate(self, article_hash: str) -> bool:
        """检查是否重复"""
        return article_hash in self._seen_hashes

    async def save_hash(self, article_hash: str):
        """保存新哈希"""
        self._seen_hashes.add(article_hash)
