"""
============================================
AI 行业脉搏 - AI 服务模块
============================================

提供大模型 API 调用功能：
1. 文章摘要生成
2. 概念提取
3. 语义匹配
"""

import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

import requests


@dataclass
class ArticleSummary:
    """AI 生成的摘要"""
    summary: str  # 200字中文摘要
    key_points: List[str]  # 关键点
    sentiment: str  # 情感: positive/neutral/negative


@dataclass
class ExtractedConcept:
    """提取的概念"""
    name: str  # 概念名称
    confidence: float  # 置信度 0-1
    definition: Optional[str] = None  # 概念定义


class AIService:
    """
    AI 服务类

    支持 DeepSeek、硅基流动 等兼容 OpenAI 格式的 API
    """

    def __init__(
        self,
        api_key: str,
        api_base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-chat",
        timeout: int = 60
    ):
        """
        初始化 AI 服务

        Args:
            api_key: API 密钥
            api_base_url: API 基础 URL
            model: 模型名称
            timeout: 请求超时（秒）
        """
        self.api_key = api_key
        self.api_base_url = api_base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._session = requests.Session()

    def _call_api(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """
        调用 AI API

        Args:
            messages: 消息列表
            temperature: 温度参数

        Returns:
            AI 回复内容
        """
        url = f"{self.api_base_url}/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2000
        }

        try:
            response = self._session.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.RequestException as e:
            print(f"❌ AI API 调用失败: {e}")
            raise

    def summarize_article(self, article_content: str, title: str = "") -> ArticleSummary:
        """
        生成文章摘要

        Args:
            article_content: 文章内容
            title: 文章标题

        Returns:
            ArticleSummary 对象
        """
        system_prompt = """你是一位专业的 AI 行业分析师。请为以下英文文章生成：

1. 一段约 200 字的中文行业摘要
2. 3 个关键要点
3. 情感倾向 (positive/neutral/negative)

输出格式（必须是有效的 JSON）：
{
    "summary": "中文摘要内容...",
    "key_points": ["要点1...", "要点2...", "要点3..."],
    "sentiment": "neutral"
}"""

        user_prompt = f"文章标题：{title}\n\n文章内容：\n{article_content[:3000]}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            response = self._call_api(messages, temperature=0.5)
            # 解析 JSON 响应
            return self._parse_summary_response(response)
        except Exception as e:
            print(f"⚠️ 摘要生成失败: {e}")
            return ArticleSummary(
                summary="AI 摘要生成失败",
                key_points=[],
                sentiment="neutral"
            )

    def extract_concepts(self, article_content: str, title: str = "") -> List[ExtractedConcept]:
        """
        从文章中提取 AI 行业新概念

        Args:
            article_content: 文章内容
            title: 文章标题

        Returns:
            ExtractedConcept 列表
        """
        system_prompt = """你是一位 AI 行业专家。请从以下文章中提取 3 个前沿 AI 概念。

要求：
1. 每个概念不超过 5 个中文字符
2. 必须是行业通用术语或新兴概念
3. 如：Agentic、Test-Time Compute、MoE、RAG、思维链 等
4. 优先提取最新的、革命性的概念

输出格式（必须是有效的 JSON）：
{
    "concepts": [
        {"name": "概念名", "confidence": 0.95},
        {"name": "概念名", "confidence": 0.85},
        {"name": "概念名", "confidence": 0.75}
    ]
}"""

        user_prompt = f"文章标题：{title}\n\n文章内容：\n{article_content[:3000]}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            response = self._call_api(messages, temperature=0.8)
            return self._parse_concepts_response(response)
        except Exception as e:
            print(f"⚠️ 概念提取失败: {e}")
            return []

    def check_concept_match(
        self,
        concept_name: str,
        existing_concepts: List[str]
    ) -> tuple[bool, Optional[str]]:
        """
        检查概念是否已存在

        Args:
            concept_name: 要检查的概念
            existing_concepts: 已存在的概念列表

        Returns:
            (是否匹配, 匹配的概念名)
        """
        concept_lower = concept_name.lower()
        for existing in existing_concepts:
            if concept_lower == existing.lower():
                return True, existing
            # 模糊匹配（包含关系）
            if concept_lower in existing.lower() or existing.lower() in concept_lower:
                return True, existing

        return False, None

    def _parse_summary_response(self, response: str) -> ArticleSummary:
        """解析摘要响应"""
        try:
            # 提取 JSON
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return ArticleSummary(
                    summary=data.get("summary", ""),
                    key_points=data.get("key_points", []),
                    sentiment=data.get("sentiment", "neutral")
                )
        except json.JSONDecodeError:
            pass

        # 降级处理：返回原始响应
        return ArticleSummary(
            summary=response[:200],
            key_points=[],
            sentiment="neutral"
        )

    def _parse_concepts_response(self, response: str) -> List[ExtractedConcept]:
        """解析概念提取响应"""
        concepts = []

        try:
            # 提取 JSON
            json_match = re.search(r'\{[^{}]*"concepts"[^{}]*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                for item in data.get("concepts", []):
                    concepts.append(ExtractedConcept(
                        name=item.get("name", ""),
                        confidence=item.get("confidence", 0.5)
                    ))
        except json.JSONDecodeError:
            pass

        return concepts[:3]  # 最多返回 3 个
