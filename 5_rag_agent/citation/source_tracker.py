"""
@generated-by AI: matthewmli
@generated-date 2026-03-27
"""
from typing import List, Dict, Any, Optional
from collections import defaultdict
import os


class SourceTracker:
    """来源追踪器 - 记录和统计文档来源信息"""
    
    def __init__(self):
        """初始化来源追踪器"""
        self.sources = []  # 所有来源记录
        self.source_counts = defaultdict(int)  # 来源计数
        self.queries = []  # 查询历史
    
    def track(
        self,
        query: str,
        sources: List[Dict[str, Any]]
    ) -> None:
        """
        记录一次查询和其来源
        
        Args:
            query: 查询文本
            sources: 检索到的来源列表
        """
        # 记录查询
        self.queries.append({
            "query": query,
            "sources": sources,
            "source_count": len(sources)
        })
        
        # 记录来源
        for source in sources:
            source_file = source.get("source", "unknown")
            self.sources.append({
                "query": query,
                "source": source_file,
                "chunk_id": source.get("chunk_id"),
                "score": source.get("score", 0.0)
            })
            
            # 更新计数
            self.source_counts[source_file] += 1
    
    def get_most_used_sources(
        self,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取最常用的来源
        
        Args:
            top_n: 返回前 N 个
            
        Returns:
            来源列表，格式: [
                {"source": "doc.md", "count": 10},
                ...
            ]
        """
        sorted_sources = sorted(
            self.source_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {"source": source, "count": count}
            for source, count in sorted_sources[:top_n]
        ]
    
    def get_source_statistics(self) -> Dict[str, Any]:
        """
        获取来源统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "total_queries": len(self.queries),
            "total_sources": len(self.sources),
            "unique_sources": len(self.source_counts),
            "avg_sources_per_query": len(self.sources) / len(self.queries) if self.queries else 0,
            "most_used": self.get_most_used_sources(5)
        }
    
    def get_sources_by_query(
        self,
        query: str
    ) -> List[Dict[str, Any]]:
        """
        获取特定查询的来源
        
        Args:
            query: 查询文本
            
        Returns:
            来源列表
        """
        return [
            s for s in self.sources
            if s["query"] == query
        ]
    
    def get_queries_by_source(
        self,
        source: str
    ) -> List[str]:
        """
        获取使用特定来源的所有查询
        
        Args:
            source: 来源文件名
            
        Returns:
            查询列表
        """
        return [
            s["query"] for s in self.sources
            if s["source"] == source
        ]
    
    def clear(self) -> None:
        """清空所有记录"""
        self.sources = []
        self.source_counts = defaultdict(int)
        self.queries = []
    
    def export_history(self) -> Dict[str, Any]:
        """
        导出历史记录
        
        Returns:
            历史记录字典
        """
        return {
            "queries": self.queries,
            "sources": self.sources,
            "source_counts": dict(self.source_counts)
        }
    
    def get_summary_report(self) -> str:
        """
        生成摘要报告
        
        Returns:
            格式化的摘要报告
        """
        stats = self.get_source_statistics()
        
        lines = [
            "=" * 50,
            "📊 来源追踪报告",
            "=" * 50,
            f"总查询次数: {stats['total_queries']}",
            f"总来源引用次数: {stats['total_sources']}",
            f"唯一来源数: {stats['unique_sources']}",
            f"平均每次查询引用来源数: {stats['avg_sources_per_query']:.2f}",
            "",
            "🏆 最常用来源 TOP 5:",
        ]
        
        for i, item in enumerate(stats['most_used'], 1):
            lines.append(f"  {i}. {item['source']} (被引用 {item['count']} 次)")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)


if __name__ == "__main__":
    # 测试代码
    print("=" * 50)
    print("测试 SourceTracker 模块")
    print("=" * 50)
    
    # 创建追踪器
    tracker = SourceTracker()
    
    # 模拟检索结果
    query1_sources = [
        {"source": "database_config.md", "chunk_id": 0, "score": 0.88},
        {"source": "database_config.md", "chunk_id": 1, "score": 0.82},
        {"source": "python_basics.md", "chunk_id": 5, "score": 0.75}
    ]
    
    query2_sources = [
        {"source": "python_basics.md", "chunk_id": 0, "score": 0.90},
        {"source": "python_basics.md", "chunk_id": 1, "score": 0.85}
    ]
    
    query3_sources = [
        {"source": "database_config.md", "chunk_id": 2, "score": 0.80}
    ]
    
    # ========== 测试 1: 记录查询 ==========
    print("\n📝 测试 1: 记录查询")
    
    tracker.track("如何配置数据库？", query1_sources)
    tracker.track("Python 如何定义函数？", query2_sources)
    tracker.track("数据库连接池配置", query3_sources)
    
    print("已记录 3 次查询")
    
    # ========== 测试 2: 获取统计信息 ==========
    print("\n📊 测试 2: 获取统计信息")
    
    stats = tracker.get_source_statistics()
    print(f"总查询次数: {stats['total_queries']}")
    print(f"总来源引用次数: {stats['total_sources']}")
    print(f"唯一来源数: {stats['unique_sources']}")
    print(f"平均每次查询引用来源数: {stats['avg_sources_per_query']:.2f}")
    
    # ========== 测试 3: 最常用来源 ==========
    print("\n🏆 测试 3: 最常用来源")
    
    most_used = tracker.get_most_used_sources(top_n=5)
    for i, item in enumerate(most_used, 1):
        print(f"  {i}. {item['source']} (被引用 {item['count']} 次)")
    
    # ========== 测试 4: 按查询获取来源 ==========
    print("\n🔍 测试 4: 按查询获取来源")
    
    sources = tracker.get_sources_by_query("如何配置数据库？")
    print(f"查询: 如何配置数据库？")
    print(f"来源数量: {len(sources)}")
    for src in sources:
        print(f"  - {src['source']} (片段 {src['chunk_id']}, 相似度 {src['score']:.2f})")
    
    # ========== 测试 5: 按来源获取查询 ==========
    print("\n🔎 测试 5: 按来源获取查询")
    
    queries = tracker.get_queries_by_source("python_basics.md")
    print(f"来源: python_basics.md")
    print(f"被以下查询引用:")
    for q in queries:
        print(f"  - {q}")
    
    # ========== 测试 6: 导出历史 ==========
    print("\n💾 测试 6: 导出历史记录")
    
    history = tracker.export_history()
    print(f"查询历史数量: {len(history['queries'])}")
    print(f"来源记录数量: {len(history['sources'])}")
    print(f"来源计数: {history['source_counts']}")
    
    # ========== 测试 7: 生成报告 ==========
    print("\n📄 测试 7: 生成摘要报告")
    
    report = tracker.get_summary_report()
    print(report)
    
    # ========== 测试 8: 清空记录 ==========
    print("\n🗑️  测试 8: 清空记录")
    
    tracker.clear()
    print(f"清空后查询数量: {len(tracker.queries)}")
    print(f"清空后来源数量: {len(tracker.sources)}")
    
    print("\n✅ 所有测试完成！")
