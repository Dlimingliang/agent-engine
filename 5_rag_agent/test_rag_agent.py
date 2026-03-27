#!/usr/bin/env python3
"""
@generated-by AI: matthewmli
@generated-date 2026-03-27
"""
"""测试 RAG Agent"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from retrieval.embedder import Embedder
from retrieval.vector_store import VectorStore
from retrieval.retriever import Retriever
from tools.tool_registry import ToolRegistry
from tools.rag_tool import KnowledgeSearchTool, CheckRelevanceTool, GetContextTool
from agent.agent import RAGAgent


def main():
    print("=" * 60)
    print("测试 RAG Agent")
    print("=" * 60)

    # ========== 1. 初始化组件 ==========
    print("\n📦 初始化组件...")

    # 检索组件
    embedder = Embedder()
    vector_store = VectorStore()
    retriever = Retriever(embedder=embedder, vector_store=vector_store, default_top_k=3)

    # 工具注册
    tool_registry = ToolRegistry()
    tool_registry.register(KnowledgeSearchTool(retriever))
    tool_registry.register(CheckRelevanceTool(retriever))
    tool_registry.register(GetContextTool(retriever))

    # 系统提示词
    system_prompt = """你是一个智能助手，具有访问知识库的能力。

当用户询问问题时：
1. 首先使用 knowledge_search 工具检索相关文档
2. 基于检索到的内容回答问题
3. 准确标注引用来源
4. 如果没有找到相关文档，诚实告知用户"""

    # 创建 Agent
    agent = RAGAgent(
        system_prompt=system_prompt,
        retriever=retriever,
        tool_registry=tool_registry,
        citation_style="numbered"
    )

    print("✅ Agent 初始化完成")

    # ========== 2. 测试对话 ==========
    print("\n" + "=" * 60)
    print("测试对话")
    print("=" * 60)

    test_questions = [
        "如何配置数据库？",
        "Python 如何定义函数？",
        "什么是机器学习？"  # 知识库中没有的内容
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n[测试 {i}] 用户: {question}")
        print("-" * 60)

        try:
            response = agent.chat(question)
            print(f"Agent: {response}")
        except Exception as e:
            print(f"❌ 错误: {e}")

    # ========== 3. 查看统计信息 ==========
    print("\n" + "=" * 60)
    print("来源统计")
    print("=" * 60)

    stats = agent.get_source_statistics()
    print(f"总查询次数: {stats['total_queries']}")
    print(f"总来源引用次数: {stats['total_sources']}")
    print(f"唯一来源数: {stats['unique_sources']}")

    if stats['most_used']:
        print("\n最常用来源 TOP 5:")
        for item in stats['most_used']:
            print(f"  - {item['source']} (被引用 {item['count']} 次)")

    print("\n✅ 测试完成！")


if __name__ == "__main__":
    main()
