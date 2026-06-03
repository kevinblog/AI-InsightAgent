"""
============================================
Hacker News 爬虫
============================================

抓取 Hacker News AI 相关热门讨论
"""

from typing import List
from datetime import datetime
import time

from .base_scraper import BaseScraper, Article


class HackerNewsScraper(BaseScraper):
    """Hacker News 爬虫"""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    SOURCE_NAME = "Hacker News"
    SOURCE_FEED = "hackernews"

    # AI 相关关键词
    AI_KEYWORDS = ["AI", "artificial intelligence", "machine learning", "GPT", "LLM",
                   "neural network", "deep learning", "OpenAI", "Anthropic", "Agent"]

    def __init__(self):
        super().__init__(request_interval=0.5, timeout=30)

    @property
    def source_name(self) -> str:
        return self.SOURCE_NAME

    @property
    def feed_url(self) -> str:
        return f"{self.BASE_URL}/topstories.json"

    def scrape(self) -> List[Article]:
        """抓取 Hacker News AI 相关内容"""
        articles = []

        try:
            # 获取热门故事 IDs
            response = self.fetch(f"{self.BASE_URL}/topstories.json")
            if not response:
                return articles

            story_ids = eval(response)[:50]  # 获取前 50 个

            for story_id in story_ids:
                # 获取故事详情
                story = self._fetch_story(story_id)
                if story and self._is_ai_related(story):
                    article = self._parse_story(story)
                    if article:
                        articles.append(article)

                # 限制抓取数量
                if len(articles) >= 10:
                    break

                time.sleep(0.3)  # 避免请求过快

        except Exception as e:
            print(f"❌ [{self.SOURCE_NAME}] 抓取失败: {e}")

        print(f"✅ [{self.SOURCE_NAME}] 抓取到 {len(articles)} 篇 AI 相关文章")
        return articles

    def _fetch_story(self, story_id: int) -> dict:
        """获取故事详情"""
        response = self.fetch(f"{self.BASE_URL}/item/{story_id}.json")
        if response:
            try:
                return eval(response)
            except:
                pass
        return {}

    def _is_ai_related(self, story: dict) -> bool:
        """检查是否 AI 相关"""
        title = story.get("title", "").lower()
        text = story.get("text", "").lower()

        for keyword in self.AI_KEYWORDS:
            if keyword.lower() in title or keyword.lower() in text:
                return True
        return False

    def _parse_story(self, story: dict) -> Article:
        """解析故事为 Article 对象"""
        url = story.get("url") or f"https://news.ycombinator.com/item?id={story.get('id')}"

        return Article(
            title=self.clean_text(story.get("title", "")),
            url=url,
            original_title=None,
            source=self.SOURCE_NAME,
            source_feed=self.SOURCE_FEED,
            content=self.clean_text(story.get("text", "")),
            author=story.get("by", ""),
            published_at=datetime.fromtimestamp(story.get("time", 0)) if story.get("time") else None,
            category="AI 社区",
            tags=["HN", "AI", "讨论"],
            score=story.get("score", 0)
        )
