"""
============================================
VentureBeat AI 爬虫
============================================

抓取 VentureBeat AI 行业分析
"""

from typing import List
from datetime import datetime

from .base_scraper import BaseScraper, Article


class VentureBeatScraper(BaseScraper):
    """VentureBeat AI 新闻爬虫"""

    FEED_URL = "https://venturebeat.com/category/ai/feed/"
    SOURCE_NAME = "VentureBeat"
    SOURCE_FEED = "venturebeat"

    def __init__(self):
        super().__init__(request_interval=3.0, timeout=30)

    @property
    def source_name(self) -> str:
        return self.SOURCE_NAME

    @property
    def feed_url(self) -> str:
        return self.FEED_URL

    def scrape(self) -> List[Article]:
        """抓取 VentureBeat AI 新闻"""
        import feedparser

        articles = []
        feed = feedparser.parse(self.fetch(self.FEED_URL))

        if not feed.entries:
            print(f"⚠️ [{self.SOURCE_NAME}] 未获取到内容")
            return articles

        for entry in feed.entries[:15]:
            try:
                article = self._parse_article(entry)
                articles.append(article)
            except Exception as e:
                print(f"⚠️ [{self.SOURCE_NAME}] 解析文章失败: {e}")
                continue

        print(f"✅ [{self.SOURCE_NAME}] 抓取到 {len(articles)} 篇行业分析")
        return articles

    def _parse_article(self, entry) -> Article:
        """解析文章条目"""
        # 提取分类
        category = self._extract_category(entry)

        return Article(
            title=self.clean_text(entry.get("title", "")),
            url=entry.get("link", ""),
            original_title=None,
            source=self.SOURCE_NAME,
            source_feed=self.SOURCE_FEED,
            content=self.clean_text(entry.get("summary", "")),
            author=entry.get("author", ""),
            published_at=self.parse_date(entry.get("published", "")),
            category=category,
            tags=["VB", "AI", "行业"],
            image=self._extract_image(entry)
        )

    def _extract_category(self, entry) -> str:
        """提取分类"""
        # 尝试从 DC.subject 获取
        if hasattr(entry, 'dc') and hasattr(entry.dc, 'subject'):
            subjects = entry.dc.subject
            if isinstance(subjects, list) and subjects:
                return subjects[0]
            elif isinstance(subjects, str):
                return subjects

        return "行业分析"

    def _extract_image(self, entry) -> str:
        """提取文章图片"""
        # 尝试从 media_content 获取
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if 'url' in media:
                    return media['url']

        # 尝试从 enclosures 获取
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                if enclosure.get('type', '').startswith('image/'):
                    return enclosure['url']

        return ""
