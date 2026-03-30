import sys
import re
from pathlib import Path
from typing import Any
import requests

# 添加项目根目录到 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .tool_registry import Tool


class WebSearchTool(Tool):
    """
    网页搜索工具
    
    功能：搜索网页内容
    
    参数：
    - query: 搜索关键词
    
    注意：这是一个模拟工具，实际应用需要接入真实搜索 API
    """
    
    def __init__(self):
        """
        初始化网页搜索工具
        """
        super().__init__(
            name="web_search",
            description="搜索网页内容（模拟工具）。返回与搜索关键词相关的结果。",
            parameters_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回结果数量，默认为5",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        )
    
    def execute(self, query: str, top_k: int = 5, **kwargs) -> dict:
        """
        执行搜索
        
        Args:
            query: 搜索关键词
            top_k: 返回结果数量
            **kwargs: 其他参数
            
        Returns:
            dict: 搜索结果
        """
        try:
            # 使用模拟搜索结果
            results = self._mock_search(query, top_k)
            
            return {
                "success": True,
                "results": results,
                "query": query,
                "total": len(results)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def _mock_search(self, query: str, top_k: int) -> list[dict]:
        """
        模拟搜索结果
        
        Args:
            query: 搜索关键词
            top_k: 结果数量
            
        Returns:
            list[dict]: 模拟的搜索结果
        """
        # 模拟的搜索结果
        mock_results = [
            {
                "title": f"关于 {query} 的详细介绍",
                "url": f"https://example.com/article/1?q={query}",
                "snippet": f"这是一篇关于 {query} 的详细文章，包含基础知识、应用场景和最佳实践..."
            },
            {
                "title": f"{query} 完整教程",
                "url": f"https://example.com/tutorial/2?q={query}",
                "snippet": f"从零开始学习 {query}，包含示例代码和实战案例..."
            },
            {
                "title": f"{query} 最佳实践指南",
                "url": f"https://example.com/guide/3?q={query}",
                "snippet": f"深入探讨 {query} 的最佳实践，包括常见问题和解决方案..."
            },
            {
                "title": f"{query} 常见问题解答",
                "url": f"https://example.com/faq/4?q={query}",
                "snippet": f"关于 {query} 的常见问题和详细解答..."
            },
            {
                "title": f"{query} 实战案例分享",
                "url": f"https://example.com/case/5?q={query}",
                "snippet": f"真实项目中使用 {query} 的案例分析和经验分享..."
            }
        ]
        
        return mock_results[:top_k]


class WebFetchTool(Tool):
    """
    网页抓取工具
    
    功能：抓取网页内容
    
    参数：
    - url: 网页 URL
    """
    
    def __init__(self):
        """
        初始化网页抓取工具
        """
        super().__init__(
            name="web_fetch",
            description="抓取指定网页的内容。返回网页的文本内容。",
            parameters_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "要抓取的网页URL"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "超时时间（秒），默认30秒",
                        "default": 30
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "最大内容长度，默认5000字符",
                        "default": 5000
                    }
                },
                "required": ["url"]
            }
        )
    
    def execute(self, url: str, timeout: int = 30, max_length: int = 5000, **kwargs) -> dict:
        """
        抓取网页
        
        Args:
            url: 网页 URL
            timeout: 超时时间（秒）
            max_length: 最大内容长度
            **kwargs: 其他参数
            
        Returns:
            dict: 抓取结果
        """
        try:
            # 验证 URL
            if not self._validate_url(url):
                return {
                    "success": False,
                    "error": f"无效的URL格式: {url}",
                    "url": url
                }
            
            # 发送 HTTP 请求
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=timeout, headers=headers)
            
            # 检查响应状态
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"HTTP错误: {response.status_code}",
                    "url": url,
                    "status_code": response.status_code
                }
            
            # 提取文本内容
            html = response.text
            text = self._extract_text(html)
            
            # 清理内容
            cleaned_text = self._clean_content(text, max_length)
            
            return {
                "success": True,
                "url": url,
                "content": cleaned_text,
                "status_code": response.status_code,
                "content_length": len(cleaned_text)
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": f"请求超时（{timeout}秒）",
                "url": url
            }
        except requests.exceptions.ConnectionError as e:
            return {
                "success": False,
                "error": f"连接错误: {str(e)}",
                "url": url
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
    
    def _extract_text(self, html: str) -> str:
        """
        从 HTML 中提取文本
        
        Args:
            html: HTML 内容
            
        Returns:
            str: 纯文本内容
        """
        # 移除 script 和 style 标签及其内容
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # 移除注释
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        
        # 移除所有 HTML 标签
        html = re.sub(r'<[^>]+>', ' ', html)
        
        # 移除多余的空白字符
        html = re.sub(r'\s+', ' ', html)
        
        return html.strip()
    
    def _validate_url(self, url: str) -> bool:
        """
        验证 URL 是否有效
        
        Args:
            url: URL 字符串
            
        Returns:
            bool: 是否有效
        """
        # 检查 URL 格式
        pattern = re.compile(
            r'^https?://'  # http:// 或 https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 域名
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP 地址
            r'(?::\d+)?'  # 端口
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(pattern.match(url))
    
    def _clean_content(self, content: str, max_length: int = 5000) -> str:
        """
        清理内容
        
        Args:
            content: 原始内容
            max_length: 最大长度
            
        Returns:
            str: 清理后的内容
        """
        # 移除多余的空白字符
        content = re.sub(r'\s+', ' ', content)
        
        # 如果内容过长，截断
        if len(content) > max_length:
            content = content[:max_length] + "...(内容已截断)"
        
        return content.strip()
