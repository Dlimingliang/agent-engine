"""
@generated-by AI: matthewmli
@generated-date 2026-03-27
"""
from typing import List, Dict, Any, Optional
from .embedder import Embedder
from .vector_store import VectorStore


class Retriever:
    """检索器 - 协调 Embedder 和 VectorStore，提供完整检索流程"""
    
    def __init__(
        self,
        embedder: Embedder,
        vector_store: VectorStore,
        default_top_k: int = 5,
        score_threshold: Optional[float] = None
    ):
        """
        初始化检索器
        
        Args:
            embedder: Embedding 模型实例
            vector_store: 向量存储实例
            default_top_k: 默认返回结果数量
            score_threshold: 默认相似度阈值（可选）
        """
        self.embedder = embedder
        self.vector_store = vector_store
        self.default_top_k = default_top_k
        self.score_threshold = score_threshold
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
        query_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            top_k: 返回结果数量（可选，使用默认值）
            score_threshold: 相似度阈值（可选）
            query_filter: 过滤条件（可选）
                例如: {"source": "config.md"} 按文件名过滤
                例如: {"topic": "python"} 按主题过滤
            
        Returns:
            检索结果列表，格式: [
                {
                    "id": 1,
                    "score": 0.85,
                    "text": "文档内容",
                    "source": "doc.md",
                    "chunk_id": 0,
                    ...其他元数据
                },
                ...
            ]
        """
        # 使用默认值
        if top_k is None:
            top_k = self.default_top_k
        if score_threshold is None:
            score_threshold = self.score_threshold
        
        # 1. 查询向量化
        query_vector = self.embedder.encode_single(query)
        
        # 2. 向量检索
        results = self.vector_store.search(
            query_vector=query_vector.tolist(),
            top_k=top_k,
            score_threshold=score_threshold,
            query_filter=query_filter
        )
        
        return results
    
    def retrieve_by_topic(
        self,
        query: str,
        topic: str,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        按主题过滤检索
        
        Args:
            query: 查询文本
            topic: 主题标签
            top_k: 返回结果数量（可选）
            
        Returns:
            检索结果列表
        """
        return self.retrieve(
            query=query,
            top_k=top_k,
            query_filter={"topic": topic}
        )
    
    def retrieve_by_source(
        self,
        query: str,
        source: str,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        按文件来源过滤检索
        
        Args:
            query: 查询文本
            source: 文件名
            top_k: 返回结果数量（可选）
            
        Returns:
            检索结果列表
        """
        return self.retrieve(
            query=query,
            top_k=top_k,
            query_filter={"source": source}
        )
    
    def retrieve_batch(
        self,
        queries: List[str],
        top_k: Optional[int] = None
    ) -> List[List[Dict[str, Any]]]:
        """
        批量检索
        
        Args:
            queries: 查询文本列表
            top_k: 每个查询返回结果数量（可选）
            
        Returns:
            每个查询的检索结果列表
        """
        # 批量向量化
        query_vectors = self.embedder.encode(queries)
        
        # 批量检索
        all_results = []
        for query_vector in query_vectors:
            results = self.vector_store.search(
                query_vector=query_vector.tolist(),
                top_k=top_k or self.default_top_k,
                score_threshold=self.score_threshold
            )
            all_results.append(results)
        
        return all_results
    
    def get_relevant_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        max_length: Optional[int] = None
    ) -> str:
        """
        获取相关上下文（用于 RAG）
        
        Args:
            query: 查询文本
            top_k: 返回结果数量（可选）
            max_length: 最大上下文长度（字符数，可选）
            
        Returns:
            拼接后的上下文文本
        """
        results = self.retrieve(query, top_k=top_k)
        
        # 拼接文本
        context_parts = []
        current_length = 0
        
        for result in results:
            text = result.get("text", "")
            
            # 检查长度限制
            if max_length and current_length + len(text) > max_length:
                break
            
            context_parts.append(text)
            current_length += len(text)
        
        return "\n\n".join(context_parts)
    
    def has_relevant_docs(
        self,
        query: str,
        min_score: float = 0.5
    ) -> bool:
        """
        检查是否有相关文档
        
        Args:
            query: 查询文本
            min_score: 最小相似度阈值
            
        Returns:
            是否存在相关文档
        """
        results = self.retrieve(query, top_k=1, score_threshold=min_score)
        return len(results) > 0


if __name__ == "__main__":
    # 测试代码
    print("=" * 50)
    print("测试 Retriever 模块")
    print("=" * 50)
    
    # 导入依赖
    from .embedder import Embedder
    from .vector_store import VectorStore
    
    # 初始化组件
    print("\n📦 初始化组件...")
    embedder = Embedder()
    vector_store = VectorStore()  # 使用默认集合 knowledge_base
    
    # 创建检索器
    retriever = Retriever(
        embedder=embedder,
        vector_store=vector_store,
        default_top_k=3
    )
    
    # ========== 测试 1: 基础检索 ==========
    print("\n🔍 测试 1: 基础检索")
    
    query = "如何配置数据库？"
    results = retriever.retrieve(query)
    
    print(f"查询: {query}")
    print(f"检索到 {len(results)} 个结果:")
    for i, result in enumerate(results, 1):
        print(f"  [{i}] {result['text'][:50]}... (来源: {result.get('source', 'unknown')}, 相似度: {result['score']:.4f})")
    
    # ========== 测试 2: 按主题过滤 ==========
    print("\n🔎 测试 2: 按主题过滤检索")
    
    results = retriever.retrieve_by_topic(query, topic="python")
    print(f"过滤条件: topic = python")
    print(f"检索到 {len(results)} 个结果:")
    for i, result in enumerate(results, 1):
        print(f"  [{i}] {result['text'][:50]}... (主题: {result.get('topic', 'unknown')}, 相似度: {result['score']:.4f})")
    
    # ========== 测试 3: 获取上下文 ==========
    print("\n📄 测试 3: 获取相关上下文")
    
    context = retriever.get_relevant_context(query, max_length=500)
    print(f"上下文长度: {len(context)} 字符")
    print(f"上下文内容:\n{context[:200]}...")
    
    # ========== 测试 4: 检查相关性 ==========
    print("\n✅ 测试 4: 检查是否有相关文档")
    
    has_docs = retriever.has_relevant_docs(query, min_score=0.3)
    print(f"查询: {query}")
    print(f"是否存在相关文档: {has_docs}")
    
    # 测试一个不太可能存在的查询
    has_docs_rare = retriever.has_relevant_docs("量子计算机的工作原理", min_score=0.7)
    print(f"查询: 量子计算机的工作原理")
    print(f"是否存在相关文档: {has_docs_rare}")
    
    print("\n✅ 所有测试完成！")
