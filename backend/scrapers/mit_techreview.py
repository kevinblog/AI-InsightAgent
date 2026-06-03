"""
============================================
MIT Technology Review 爬虫
============================================

抓取 MIT Technology Review AI 相关深度报道
"""

from typing import List
from datetime import datetime

from .base_scraper import BaseScraper, Article


class MITTechReviewScraper(BaseScraper):
    """MIT Technology Review AI 新闻爬虫"""

    FEED_URL = "https://www.technologyreview.com/topic/artificial-intelligence/feed"
    SOURCE_NAME = "MIT Tech Review"
    SOURCE_FEED = "mit_techreview"

    def __init__(self):
        super().__init__(request_interval=3.0, timeout=30)

    @property
    def source_name(self) -> str:
        return self.SOURCE_NAME

    @property
    def feed_url(self) -> str:
        return self.FEED_URL

    def scrape(self) -> List[Article]:
        """抓取 MIT Technology Review AI 新闻"""
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

        print(f"✅ [{self.SOURCE_NAME}] 抓取到 {len(articles)} 篇深度报道")
        return articles

    def _parse_article(self, entry) -> Article:
        """解析文章条目"""
        # 提取图片
        image = self._extract_image(entry)

        return Article(
            title=self.clean_text(entry.get("title", "")),
            url=entry.get("link", ""),
            original_title=None,
            source=self.SOURCE_NAME,
            source_feed=self.SOURCE_FEED,
            content=self.clean_text(entry.get("summary", "")),
            author=self._extract_author(entry),
            published_at=self.parse_date(entry.get("published", "")),
            category="深度报道",
            image=image,
            tags=["MIT", "AI", "深度分析"]
        )

    def _extract_image(self, entry) -> str:
        """提取文章图片"""
        # 尝试从 media_content 获取
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if 'url' in media and any(img_type in media.get('type', '') for img_type in ['image']):
                    return media['url']

        # 尝试从 enclosures 获取
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                if enclosure.get('type', '').startswith('image/'):
                    return enclosure['url']

        return ""

    def _extract_author(self, entry) -> str:
        """提取作者"""
        if hasattr(entry, 'author'):
            return entry.author
        if hasattr(entry, 'authors') and entry.authors:
            return entry.authors[0].get("name", "")
        return ""
