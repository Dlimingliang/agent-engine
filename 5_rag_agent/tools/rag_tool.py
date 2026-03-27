"""
@generated-by AI: matthewmli
@generated-date 2026-03-27
"""
from typing import Dict, Any, List, Optional
from .base import BaseTool
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval.retriever import Retriever
from retrieval.embedder import Embedder
from retrieval.vector_store import VectorStore


class KnowledgeSearchTool(BaseTool):
    """知识库检索工具"""

    def __init__(self, retriever: Retriever):
        """
        初始化知识库检索工具

        Args:
            retriever: 检索器实例
        """
        self.retriever = retriever

    @property
    def name(self) -> str:
        return "knowledge_search"

    @property
    def description(self) -> str:
        return "从知识库中检索相关文档。当用户询问与技术、配置、API、教程等相关的问题时，使用此工具获取准确的文档信息。"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "检索查询，用于在知识库中查找相关文档"
                },
                "top_k": {
                    "type": "integer",
                    "description": "返回结果数量，默认为 5",
                    "default": 5
                },
                "score_threshold": {
                    "type": "number",
                    "description": "相似度阈值（0-1），只返回高于此阈值的结果，默认为 0.3",
                    "default": 0.3
                }
            },
            "required": ["query"]
        }

    def execute(self, query: str, top_k: int = 5, score_threshold: float = 0.3) -> Dict[str, Any]:
        """
        执行知识库检索

        Args:
            query: 检索查询
            top_k: 返回结果数量
            score_threshold: 相似度阈值

        Returns:
            检索结果
        """
        try:
            # 执行检索
            results = self.retriever.retrieve(
                query=query,
                top_k=top_k,
                score_threshold=score_threshold
            )

            if not results:
                return {
                    "success": True,
                    "found": False,
                    "message": "未找到相关文档",
                    "results": []
                }

            # 格式化结果
            formatted_results = []
            citation_list = []

            for i, result in enumerate(results, 1):
                source = result.get("source", "unknown")
                chunk_id = result.get("chunk_id", 0)
                score = result.get("score", 0.0)
                text = result.get("text", "")

                # 添加到结果列表
                formatted_results.append({
                    "id": i,  # 添加编号
                    "source": source,
                    "chunk_id": chunk_id,
                    "score": score,
                    "text": text,
                    "char_count": result.get("char_count", 0)
                })

                # 生成引用格式
                citation_list.append(f"[{i}] {source} (片段 {chunk_id}, 相似度 {score:.2f})")

            return {
                "success": True,
                "found": True,
                "message": f"找到 {len(results)} 个相关文档",
                "results": formatted_results,
                "query": query,
                # 添加引用信息，供 LLM 使用
                "citation_list": citation_list,
                "citation_hint": "回答时请在相关内容后标注引用编号，如 [1], [2] 等，并在回答最后列出完整的引用来源。"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "检索失败"
            }


class CheckRelevanceTool(BaseTool):
    """检查相关性工具"""

    def __init__(self, retriever: Retriever):
        """
        初始化检查相关性工具

        Args:
            retriever: 检索器实例
        """
        self.retriever = retriever

    @property
    def name(self) -> str:
        return "check_relevance"

    @property
    def description(self) -> str:
        return "检查知识库中是否有与查询相关的文档。用于判断是否需要降级处理（如提示用户知识库中没有相关信息）。"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "要检查的查询"
                },
                "min_score": {
                    "type": "number",
                    "description": "最小相似度阈值，默认为 0.5",
                    "default": 0.5
                }
            },
            "required": ["query"]
        }

    def execute(self, query: str, min_score: float = 0.5) -> Dict[str, Any]:
        """
        执行相关性检查

        Args:
            query: 查询文本
            min_score: 最小相似度阈值

        Returns:
            检查结果
        """
        try:
            # 检查是否有相关文档
            has_relevant = self.retriever.has_relevant_docs(
                query=query,
                min_score=min_score
            )

            return {
                "success": True,
                "has_relevant_docs": has_relevant,
                "message": "存在相关文档" if has_relevant else "未找到相关文档",
                "query": query,
                "min_score": min_score
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "检查失败"
            }


class GetContextTool(BaseTool):
    """获取上下文工具"""

    def __init__(self, retriever: Retriever):
        """
        初始化获取上下文工具

        Args:
            retriever: 检索器实例
        """
        self.retriever = retriever

    @property
    def name(self) -> str:
        return "get_context"

    @property
    def description(self) -> str:
        return "获取与查询相关的上下文文本，用于直接注入到提示词中。"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "查询文本"
                },
                "top_k": {
                    "type": "integer",
                    "description": "检索文档数量，默认为 3",
                    "default": 3
                },
                "max_length": {
                    "type": "integer",
                    "description": "最大上下文长度（字符数），默认为 2000",
                    "default": 2000
                }
            },
            "required": ["query"]
        }

    def execute(self, query: str, top_k: int = 3, max_length: int = 2000) -> Dict[str, Any]:
        """
        执行获取上下文

        Args:
            query: 查询文本
            top_k: 检索文档数量
            max_length: 最大上下文长度

        Returns:
            上下文结果
        """
        try:
            # 获取上下文
            context = self.retriever.get_relevant_context(
                query=query,
                top_k=top_k,
                max_length=max_length
            )

            if not context:
                return {
                    "success": True,
                    "found": False,
                    "message": "未找到相关上下文",
                    "context": ""
                }

            return {
                "success": True,
                "found": True,
                "message": f"获取到 {len(context)} 字符的上下文",
                "context": context,
                "length": len(context)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "获取上下文失败"
            }
