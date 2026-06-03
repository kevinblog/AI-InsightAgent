"""
============================================
AI 行业脉搏 - 爬虫基类
============================================

定义爬虫通用接口和工具方法
"""

import hashlib
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


@dataclass
class Article:
    """文章数据结构"""
    title: str
    url: str
    original_title: Optional[str] = None  # 英文标题
    source: str = ""
    source_feed: str = ""  # 来源标识
    content: Optional[str] = None
    summary: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    image: Optional[str] = None

    @property
    def content_hash(self) -> str:
        """生成内容哈希用于去重"""
        content = f"{self.url}|{self.title}"
        return hashlib.sha256(content.encode()).hexdigest()


class BaseScraper(ABC):
    """
    爬虫基类

    所有具体爬虫应继承此类并实现 fetch 方法
    """

    # 默认请求头
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    def __init__(self, request_interval: float = 2.0, timeout: int = 30):
        """
        初始化爬虫

        Args:
            request_interval: 请求间隔（秒），避免触发反爬
            timeout: 请求超时时间（秒）
        """
        self.request_interval = request_interval
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
        self._last_request_time = 0

    def _wait_if_needed(self):
        """请求间隔控制"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.request_interval:
            time.sleep(self.request_interval - elapsed)
        self._last_request_time = time.time()

    def fetch(self, url: str) -> Optional[str]:
        """
        获取页面内容

        Args:
            url: 目标 URL

        Returns:
            HTML 内容，失败返回 None
        """
        self._wait_if_needed()

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'
            return response.text
        except requests.RequestException as e:
            print(f"❌ 请求失败 [{self.source_name}]: {url} - {e}")
            return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """解析 HTML"""
        return BeautifulSoup(html, 'html.parser')

    @abstractmethod
    def scrape(self) -> List[Article]:
        """
        抓取文章列表

        子类必须实现此方法

        Returns:
            文章列表
        """
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        """来源名称"""
        pass

    @property
    @abstractmethod
    def feed_url(self) -> str:
        """Feed/RSS URL"""
        pass

    def parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        解析日期字符串

        Args:
            date_str: 日期字符串

        Returns:
            datetime 对象，解析失败返回 None
        """
        if not date_str:
            return None

        formats = [
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        return None

    def clean_text(self, text: Optional[str]) -> str:
        """清理文本"""
        if not text:
            return ""
        # 移除多余空白
        text = " ".join(text.split())
        return text.strip()
