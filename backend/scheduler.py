"""
============================================
AI 行业脉搏 - 定时任务主脚本
============================================

自动采集 AI 行业内容并智能处理

功能：
1. 多源内容抓取
2. 文章去重
3. AI 摘要生成
4. 新概念提取
5. 概念库智能匹配

使用方法：
1. 配置环境变量或修改配置
2. 运行：python scheduler.py
3. 查看日志了解执行情况
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import List

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pipeline.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class ContentPipeline:
    """
    内容采集 Pipeline

    协调爬虫、AI 服务和数据库操作
    """

    def __init__(self):
        """初始化 Pipeline"""
        # 导入配置
        from config import config

        # 初始化 AI 服务
        self.ai_service = None
        if config.AI_API_KEY:
            from services.ai_service import AIService
            self.ai_service = AIService(
                api_key=config.AI_API_KEY,
                api_base_url=config.AI_API_BASE_URL,
                model=config.AI_MODEL
            )
            logger.info("✅ AI 服务初始化成功")
        else:
            logger.warning("⚠️ 未配置 AI API Key，跳过 AI 处理")

        # 爬虫列表
        from scrapers import (
            TechCrunchScraper,
            HackerNewsScraper,
            ArxivScraper,
            MITTechReviewScraper,
            VentureBeatScraper
        )

        self.scrapers = {
            "TechCrunch": TechCrunchScraper(),
            "Hacker News": HackerNewsScraper(),
            "Arxiv": ArxivScraper(),
            "MIT Tech Review": MITTechReviewScraper(),
            "VentureBeat": VentureBeatScraper()
        }

        # 统计信息
        self.stats = {
            "scraped": 0,
            "duplicates": 0,
            "processed": 0,
            "concepts_found": 0,
            "concepts_new": 0,
            "errors": 0
        }

    async def run_full_pipeline(self):
        """运行完整 Pipeline"""
        logger.info("=" * 50)
        logger.info("🚀 开始执行内容采集 Pipeline")
        logger.info(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 50)

        from database import async_session_maker
        from services.concept_service import ConceptService, DeduplicationService
        from models import Article, Concept

        async with async_session_maker() as db:
            concept_service = ConceptService(db)
            dedup_service = DeduplicationService(db)

            # 加载已存在的哈希
            await dedup_service.load_existing_hashes()

            # 加载现有概念
            existing_concepts = await concept_service.get_concept_names()
            logger.info(f"📚 现有概念库: {len(existing_concepts)} 个")

            # 遍历所有爬虫
            for source_name, scraper in self.scrapers.items():
                try:
                    await self._process_source(
                        scraper,
                        db,
                        concept_service,
                        dedup_service,
                        existing_concepts
                    )
                except Exception as e:
                    logger.error(f"❌ 处理 {source_name} 失败: {e}")
                    self.stats["errors"] += 1

        # 输出统计
        self._print_stats()

    async def _process_source(
        self,
        scraper,
        db,
        concept_service,
        dedup_service,
        existing_concepts: List[str]
    ):
        """处理单个数据源"""
        from scrapers.base_scraper import Article
        from services.concept_service import DeduplicationService

        logger.info(f"\n📡 正在抓取: {scraper.source_name}")

        # 抓取文章
        articles = scraper.scrape()
        self.stats["scraped"] += len(articles)

        # 处理每篇文章
        for article_data in articles:
            article_hash = dedup_service.generate_hash(
                article_data.url,
                article_data.title
            )

            # 去重检查
            if dedup_service.is_duplicate(article_hash):
                logger.info(f"⏭️ 跳过重复文章: {article_data.title[:30]}...")
                self.stats["duplicates"] += 1
                continue

            try:
                # AI 处理
                if self.ai_service:
                    await self._process_with_ai(
                        article_data,
                        db,
                        concept_service,
                        existing_concepts
                    )

                # 保存文章
                await self._save_article(article_data, db)

                # 标记哈希
                await dedup_service.save_hash(article_hash)

                self.stats["processed"] += 1

            except Exception as e:
                logger.error(f"❌ 处理文章失败: {e}")
                self.stats["errors"] += 1

        logger.info(f"✅ {scraper.source_name} 处理完成")

    async def _process_with_ai(
        self,
        article_data,
        db,
        concept_service,
        existing_concepts: List[str]
    ):
        """使用 AI 处理文章"""
        from services.ai_service import ExtractedConcept

        content = article_data.content or ""
        if not content:
            return

        # 生成摘要
        logger.info(f"🤖 生成摘要: {article_data.title[:30]}...")
        summary = self.ai_service.summarize_article(content, article_data.title)
        article_data.summary = summary.summary

        # 提取概念
        logger.info(f"🔍 提取概念...")
        concepts = self.ai_service.extract_concepts(content, article_data.title)

        # 保存提取的概念
        for concept in concepts:
            # 检查是否匹配现有概念
            matched, matched_name = self.ai_service.check_concept_match(
                concept.name,
                existing_concepts
            )

            if matched:
                # 现有概念：增加热度
                if matched_name:
                    logger.info(f"📈 命中共存概念: {matched_name}")
                    # TODO: 查询并更新热度
                self.stats["concepts_found"] += 1
            else:
                # 新概念：待审入库
                logger.info(f"🆕 发现新概念: {concept.name}")
                concept_obj = await concept_service.create_pending_concept(
                    name=concept.name,
                    source_article_id=0,  # 文章保存后再更新
                    confidence=concept.confidence,
                    category="AI 前沿"
                )
                if concept_obj:
                    self.stats["concepts_new"] += 1

    async def _save_article(self, article_data, db):
        """保存文章到数据库"""
        from models import Article as ArticleModel

        article = ArticleModel(
            title=article_data.title,
            original_title=article_data.original_title,
            original_url=article_data.url,
            translated_content=article_data.content,
            ai_summary=article_data.summary,
            category=article_data.category,
            source=article_data.source,
            source_feed=article_data.source_feed,
            published_at=article_data.published_at,
            image=article_data.image,
            views=0,
            hot=article_data.hot if hasattr(article_data, 'hot') else False
        )

        db.add(article)
        await db.commit()
        await db.refresh(article)

        logger.info(f"💾 保存文章: {article.title[:30]}... (ID: {article.id})")
        return article.id

    def _print_stats(self):
        """输出统计信息"""
        logger.info("\n" + "=" * 50)
        logger.info("📊 Pipeline 执行统计")
        logger.info("=" * 50)
        logger.info(f"  抓取文章: {self.stats['scraped']}")
        logger.info(f"  重复跳过: {self.stats['duplicates']}")
        logger.info(f"  处理成功: {self.stats['processed']}")
        logger.info(f"  命中共存概念: {self.stats['concepts_found']}")
        logger.info(f"  新增待审概念: {self.stats['concepts_new']}")
        logger.info(f"  处理错误: {self.stats['errors']}")
        logger.info("=" * 50)


def run_scheduler():
    """运行定时任务调度器"""
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.interval import IntervalTrigger

    pipeline = ContentPipeline()
    scheduler = AsyncIOScheduler()

    # 每小时执行一次
    scheduler.add_job(
        pipeline.run_full_pipeline,
        trigger=IntervalTrigger(hours=1),
        id="content_pipeline",
        name="AI 内容采集 Pipeline",
        replace_existing=True
    )

    # 学术论文每 6 小时单独抓取（可配置）
    # scheduler.add_job(...)

    scheduler.start()
    logger.info("✅ 定时任务调度器已启动")
    logger.info("📅 Pipeline 将每小时执行一次")

    # 保持运行
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 调度器已停止")


async def run_once():
    """只执行一次（用于测试）"""
    pipeline = ContentPipeline()
    await pipeline.run_full_pipeline()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI 内容采集 Pipeline")
    parser.add_argument("--once", action="store_true", help="只执行一次（不启动定时器）")
    parser.add_argument("--debug", action="store_true", help="调试模式")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.once:
        # 只执行一次
        asyncio.run(run_once())
    else:
        # 启动定时任务
        run_scheduler()
