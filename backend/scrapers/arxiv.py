"""
============================================
Arxiv 机器学习论文爬虫
============================================

通过 RSS 抓取 Arxiv CS.AI 类别最新论文
"""

from typing import List
from datetime import datetime
import re

from .base_scraper import BaseScraper, Article


class ArxivScraper(BaseScraper):
    """Arxiv CS.AI 论文爬虫"""

    FEED_URL = "https://export.arxiv.org/rss/cs.AI"
    SOURCE_NAME = "Arxiv"
    SOURCE_FEED = "arxiv_csai"

    def __init__(self):
        super().__init__(request_interval=2.0, timeout=30)

    @property
    def source_name(self) -> str:
        return self.SOURCE_NAME

    @property
    def feed_url(self) -> str:
        return self.FEED_URL

    def scrape(self) -> List[Article]:
        """抓取 Arxiv CS.AI 最新论文"""
        import feedparser

        articles = []
        feed = feedparser.parse(self.fetch(self.FEED_URL))

        if not feed.entries:
            print(f"⚠️ [{self.SOURCE_NAME}] 未获取到内容")
            return articles

        for entry in feed.entries[:15]:
            try:
                article = self._parse_paper(entry)
                articles.append(article)
            except Exception as e:
                print(f"⚠️ [{self.SOURCE_NAME}] 解析论文失败: {e}")
                continue

        print(f"✅ [{self.SOURCE_NAME}] 抓取到 {len(articles)} 篇论文")
        return articles

    def _parse_paper(self, entry) -> Article:
        """解析论文条目"""
        # 提取 Arxiv ID
        arxiv_id = self._extract_arxiv_id(entry.get("id", ""))

        # 解析作者
        authors = []
        if hasattr(entry, 'authors'):
            authors = [author.get("name", "") for author in entry.authors]
        author_str = ", ".join(authors[:3]) if authors else ""

        # 提取摘要
        summary = self.clean_text(entry.get("summary", ""))
        if len(summary) > 1000:
            summary = summary[:1000] + "..."

        # 生成论文标签
        tags = self._extract_tags(entry.get("title", ""), summary)

        return Article(
            title=self._clean_paper_title(entry.get("title", "")),
            url=entry.get("link", f"https://arxiv.org/abs/{arxiv_id}"),
            original_title=None,
            source=self.SOURCE_NAME,
            source_feed=self.SOURCE_FEED,
            content=summary,
            author=author_str,
            published_at=self.parse_date(entry.get("published", "")),
            category="学术论文",
            tags=tags,
            arxiv_id=arxiv_id
        )

    def _extract_arxiv_id(self, url: str) -> str:
        """从 URL 提取 Arxiv ID"""
        match = re.search(r'(\d+\.\d+)', url)
        return match.group(1) if match else ""

    def _clean_paper_title(self, title: str) -> str:
        """清理论文标题"""
        # 移除 . 结尾
        title = title.strip()
        if title.endswith('.'):
            title = title[:-1]
        return title

    def _extract_tags(self, title: str, summary: str) -> List[str]:
        """提取论文相关标签"""
        tags = ["Arxiv", "学术"]

        # 常见 ML/DL 关键词
        keywords = {
            "Transformer": "Transformer",
            "BERT": "BERT",
            "GPT": "GPT",
            "RLHF": "RLHF",
            "RAG": "RAG",
            "Diffusion": "Diffusion",
            "GAN": "GAN",
            "LSTM": "LSTM",
            "CNN": "CNN",
            "Reinforcement": "强化学习",
            "Multimodal": "多模态",
            "Vision": "计算机视觉",
        }

        text = (title + " " + summary).lower()
        for keyword, tag in keywords.items():
            if keyword.lower() in text:
                tags.append(tag)

        return tags[:5]  # 最多 5 个标签
