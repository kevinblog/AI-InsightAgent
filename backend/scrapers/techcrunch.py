"""
============================================
TechCrunch AI 爬虫
============================================

抓取 TechCrunch 人工智能分类新闻
"""

from typing import List
from datetime import datetime

from .base_scraper import BaseScraper, Article


class TechCrunchScraper(BaseScraper):
    """TechCrunch AI 新闻爬虫"""

    FEED_URL = "https://techcrunch.com/category/artificial-intelligence/feed/"
    SOURCE_NAME = "TechCrunch"
    SOURCE_FEED = "techcrunch_ai"

    def __init__(self):
        super().__init__(request_interval=3.0, timeout=30)

    @property
    def source_name(self) -> str:
        return self.SOURCE_NAME

    @property
    def feed_url(self) -> str:
        return self.FEED_URL

    def scrape(self) -> List[Article]:
        """抓取 TechCrunch AI 新闻"""
        import feedparser

        articles = []
        feed = feedparser.parse(self.fetch(self.FEED_URL))

        if not feed.entries:
            print(f"⚠️ [{self.SOURCE_NAME}] 未获取到内容")
            return articles

        for entry in feed.entries[:15]:  # 限制数量
            try:
                article = Article(
                    title=self.clean_text(entry.get("title", "")),
                    url=entry.get("link", ""),
                    original_title=None,
                    source=self.SOURCE_NAME,
                    source_feed=self.SOURCE_FEED,
                    content=self.clean_text(entry.get("summary", "")),
                    author=entry.get("author", ""),
                    published_at=self.parse_date(entry.get("published", "")),
                    category="大语言模型",
                    image=self._extract_image(entry),
                    tags=["AI", "LLM", "Tech"]
                )
                articles.append(article)
            except Exception as e:
                print(f"⚠️ [{self.SOURCE_NAME}] 解析文章失败: {e}")
                continue

        print(f"✅ [{self.SOURCE_NAME}] 抓取到 {len(articles)} 篇文章")
        return articles

    def _extract_image(self, entry) -> str:
        """从条目中提取图片 URL"""
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
