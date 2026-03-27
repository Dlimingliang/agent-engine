"""
@generated-by AI: matthewmli
@generated-date 2026-03-27
"""
from typing import List, Dict, Any
import os


class CitationHandler:
    """引用处理器 - 在回答中插入引用标记，格式化引用列表"""
    
    def __init__(self, style: str = "numbered"):
        """
        初始化引用处理器
        
        Args:
            style: 引用风格
                - "numbered": 数字编号 [1], [2]
                - "bracket": 方括号 [来源: file.md]
                - "footnote": 脚注样式
        """
        self.style = style
    
    def format_answer_with_citations(
        self,
        answer: str,
        sources: List[Dict[str, Any]]
    ) -> str:
        """
        格式化带引用的回答
        
        Args:
            answer: 原始回答文本
            sources: 来源列表，格式: [
                {
                    "source": "doc.md",
                    "chunk_id": 0,
                    "score": 0.85,
                    "text": "文档片段"
                },
                ...
            ]
            
        Returns:
            格式化后的回答，包含引用列表
        """
        if not sources:
            return f"{answer}\n\n⚠️ 注意：未找到明确的引用来源。"
        
        # 格式化引用列表
        citation_list = self.format_citation_list(sources)
        
        return f"{answer}\n\n{citation_list}"
    
    def format_citation_list(self, sources: List[Dict[str, Any]]) -> str:
        """
        格式化引用列表
        
        Args:
            sources: 来源列表
            
        Returns:
            格式化的引用列表文本
        """
        if not sources:
            return ""
        
        # 去重（按来源文件）
        unique_sources = self._deduplicate_sources(sources)
        
        lines = ["📚 引用来源:"]
        
        for i, source in enumerate(unique_sources, 1):
            citation = self._format_single_citation(source, i)
            lines.append(citation)
        
        return "\n".join(lines)
    
    def _format_single_citation(
        self,
        source: Dict[str, Any],
        index: int
    ) -> str:
        """
        格式化单个引用
        
        Args:
            source: 来源信息
            index: 引用编号
            
        Returns:
            格式化的引用文本
        """
        source_file = source.get("source", "unknown")
        chunk_id = source.get("chunk_id", "?")
        score = source.get("score", 0.0)
        
        if self.style == "numbered":
            return f"[{index}] {source_file} (片段 {chunk_id}, 相似度 {score:.2f})"
        elif self.style == "bracket":
            return f"[来源: {source_file}#{chunk_id}] (相似度: {score:.2f})"
        elif self.style == "footnote":
            return f"[{index}] {source_file}, 片段 {chunk_id}, 相似度 {score:.2f}"
        else:
            return f"[{index}] {source_file} (片段 {chunk_id}, 相似度 {score:.2f})"
    
    def _deduplicate_sources(
        self,
        sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        去重来源（按文件名去重，保留相似度最高的）
        
        Args:
            sources: 来源列表
            
        Returns:
            去重后的来源列表
        """
        seen = {}
        for source in sources:
            source_file = source.get("source", "")
            if source_file not in seen:
                seen[source_file] = source
            else:
                # 保留相似度更高的
                if source.get("score", 0) > seen[source_file].get("score", 0):
                    seen[source_file] = source
        
        return list(seen.values())
    
    def format_inline_citation(
        self,
        text: str,
        source: Dict[str, Any],
        index: int
    ) -> str:
        """
        插入行内引用
        
        Args:
            text: 文本内容
            source: 来源信息
            index: 引用编号
            
        Returns:
            带行内引用的文本
        """
        source_file = source.get("source", "unknown")
        
        if self.style == "numbered":
            return f"{text} [{index}]"
        elif self.style == "bracket":
            return f"{text} [来源: {source_file}]"
        else:
            return f"{text} [{index}]"
    
    def format_source_reference(
        self,
        sources: List[Dict[str, Any]]
    ) -> str:
        """
        格式化来源参考（用于上下文注入）
        
        Args:
            sources: 来源列表
            
        Returns:
            格式化的来源参考文本
        """
        if not sources:
            return ""
        
        lines = ["=== 相关文档片段 ===\n"]
        
        for i, source in enumerate(sources, 1):
            source_file = source.get("source", "unknown")
            text = source.get("text", "")
            score = source.get("score", 0.0)
            
            lines.append(f"[文档 {i}] 来源: {source_file} (相似度: {score:.2f})")
            lines.append(f"{text}\n")
        
        lines.append("=== 以上是相关文档片段 ===")
        
        return "\n".join(lines)
    
    def get_source_summary(
        self,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        获取来源统计摘要
        
        Args:
            sources: 来源列表
            
        Returns:
            统计摘要，格式: {
                "total_count": 总数量,
                "unique_sources": 唯一来源数,
                "avg_score": 平均相似度,
                "source_files": [文件列表],
                "top_source": "最相关来源"
            }
        """
        if not sources:
            return {
                "total_count": 0,
                "unique_sources": 0,
                "avg_score": 0.0,
                "source_files": [],
                "top_source": None
            }
        
        # 统计
        unique_files = set()
        total_score = 0.0
        top_source = None
        top_score = 0.0
        
        for source in sources:
            source_file = source.get("source", "")
            score = source.get("score", 0.0)
            
            unique_files.add(source_file)
            total_score += score
            
            if score > top_score:
                top_score = score
                top_source = source_file
        
        return {
            "total_count": len(sources),
            "unique_sources": len(unique_files),
            "avg_score": total_score / len(sources),
            "source_files": list(unique_files),
            "top_source": top_source
        }


if __name__ == "__main__":
    # 测试代码
    print("=" * 50)
    print("测试 CitationHandler 模块")
    print("=" * 50)
    
    # 创建引用处理器
    handler = CitationHandler(style="numbered")
    
    # 模拟检索结果
    test_sources = [
        {
            "source": "database_config.md",
            "chunk_id": 0,
            "score": 0.88,
            "text": "数据库配置需要设置连接参数..."
        },
        {
            "source": "database_config.md",
            "chunk_id": 1,
            "score": 0.82,
            "text": "连接池配置可以提高性能..."
        },
        {
            "source": "python_basics.md",
            "chunk_id": 5,
            "score": 0.75,
            "text": "Python 连接数据库的方法..."
        }
    ]
    
    # ========== 测试 1: 格式化引用列表 ==========
    print("\n📋 测试 1: 格式化引用列表")
    
    citation_list = handler.format_citation_list(test_sources)
    print(citation_list)
    
    # ========== 测试 2: 格式化完整回答 ==========
    print("\n📄 测试 2: 格式化完整回答")
    
    answer = "根据文档，数据库配置需要以下步骤：\n1. 设置连接参数\n2. 配置连接池\n3. 测试连接"
    
    formatted = handler.format_answer_with_citations(answer, test_sources)
    print(formatted)
    
    # ========== 测试 3: 去重测试 ==========
    print("\n🔍 测试 3: 来源去重")
    
    # 添加重复来源
    duplicate_sources = test_sources + [
        {
            "source": "database_config.md",
            "chunk_id": 2,
            "score": 0.90,  # 更高的相似度
            "text": "另一个数据库配置片段..."
        }
    ]
    
    unique = handler._deduplicate_sources(duplicate_sources)
    print(f"原始数量: {len(duplicate_sources)}")
    print(f"去重后数量: {len(unique)}")
    print("去重后的来源:")
    for src in unique:
        print(f"  - {src['source']} (片段 {src['chunk_id']}, 相似度 {src['score']:.2f})")
    
    # ========== 测试 4: 来源统计 ==========
    print("\n📊 测试 4: 来源统计")
    
    summary = handler.get_source_summary(test_sources)
    print(f"总数量: {summary['total_count']}")
    print(f"唯一来源数: {summary['unique_sources']}")
    print(f"平均相似度: {summary['avg_score']:.2f}")
    print(f"来源文件: {summary['source_files']}")
    print(f"最相关来源: {summary['top_source']}")
    
    # ========== 测试 5: 来源参考格式 ==========
    print("\n📝 测试 5: 来源参考格式")
    
    reference = handler.format_source_reference(test_sources[:2])
    print(reference)
    
    # ========== 测试 6: 不同引用风格 ==========
    print("\n🎨 测试 6: 不同引用风格")
    
    styles = ["numbered", "bracket", "footnote"]
    
    for style in styles:
        print(f"\n--- 风格: {style} ---")
        h = CitationHandler(style=style)
        print(h.format_citation_list(test_sources[:1]))
    
    print("\n✅ 所有测试完成！")
