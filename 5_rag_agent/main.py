#!/usr/bin/env python3
"""
@generated-by AI: matthewmli
@generated-date 2026-03-27
"""
"""RAG Agent CLI 主程序"""
import sys
import os
import signal
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from retrieval.embedder import Embedder
from retrieval.vector_store import VectorStore
from retrieval.retriever import Retriever
from tools.tool_registry import ToolRegistry
from tools.rag_tool import KnowledgeSearchTool, CheckRelevanceTool, GetContextTool
from agent.agent import RAGAgent


class RAGAgentCLI:
    """RAG Agent 命令行界面"""

    def __init__(self):
        """初始化 CLI"""
        self.agent = None
        self.vector_store = None
        self.running = True

        # 设置信号处理（Ctrl+C 优雅退出）
        signal.signal(signal.SIGINT, self._handle_interrupt)

    def _handle_interrupt(self, signum, frame):
        """处理中断信号"""
        print("\n\n👋 正在退出...")
        self.running = False
        sys.exit(0)

    def initialize(self):
        """初始化 Agent 和组件"""
        print("=" * 60)
        print("🤖 RAG Agent 初始化中...")
        print("=" * 60)

        try:
            # 1. 初始化检索组件
            print("\n📦 加载 Embedding 模型...")
            embedder = Embedder()

            print("📦 连接向量数据库...")
            vector_store = VectorStore()
            self.vector_store = vector_store

            print("📦 初始化检索器...")
            retriever = Retriever(
                embedder=embedder,
                vector_store=vector_store,
                default_top_k=3
            )

            # 2. 注册工具
            print("\n🔧 注册工具...")
            tool_registry = ToolRegistry()
            tool_registry.register(KnowledgeSearchTool(retriever))
            tool_registry.register(CheckRelevanceTool(retriever))
            tool_registry.register(GetContextTool(retriever))

            # 3. 系统提示词
            system_prompt = """你是一个智能助手，具有访问知识库的能力。

当用户询问问题时：
1. 首先使用 knowledge_search 工具检索相关文档
2. 仔细阅读检索到的文档内容
3. 基于文档内容准确回答问题，不要编造信息
4. 在回答中标注引用编号：在引用的内容后标注来源编号，如 [1]、[2] 等
5. 在回答最后列出引用来源：使用工具返回的 citation_list 信息
6. 如果没有找到相关文档，诚实告知用户知识库中暂无相关信息

示例格式：
```
根据文档，数据库配置需要以下步骤：
1. 设置连接参数（参考配置文件）[1]
2. 配置连接池提升性能 [2]

📚 引用来源:
[1] database_config.md (片段 0, 相似度 0.88)
[2] database_config.md (片段 1, 相似度 0.82)
```

注意：citation_list 字段包含了完整的引用列表，请直接使用。"""

            # 4. 创建 Agent
            print("🤖 创建 RAG Agent...")
            self.agent = RAGAgent(
                system_prompt=system_prompt,
                retriever=retriever,
                tool_registry=tool_registry,
                citation_style="numbered"
            )

            print("\n✅ 初始化完成！")
            self._show_welcome()

        except Exception as e:
            print(f"\n❌ 初始化失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def _show_welcome(self):
        """显示欢迎信息"""
        print("\n" + "=" * 60)
        print("🎉 欢迎使用 RAG Agent")
        print("=" * 60)
        print("\n使用说明:")
        print("  - 直接输入问题进行问答")
        print("  - 输入 'stats' 查看知识库统计")
        print("  - 输入 'help' 查看帮助")
        print("  - 输入 'exit' 或 'quit' 退出程序")
        print("\n" + "=" * 60)

    def _show_stats(self):
        """显示统计信息"""
        print("\n" + "=" * 60)
        print("[知识库统计]")
        print("=" * 60)

        try:
            # 获取向量库信息
            info = self.vector_store.get_collection_info()

            if info:
                print(f"集合名称: {info['collection_name']}")
                print(f"向量数量: {info['points_count']}")
                print(f"向量维度: {info.get('vector_size', 'unknown')}")
                print(f"距离度量: {info.get('distance', 'unknown')}")
                print(f"状态: {info['status']}")
            else:
                print("⚠️  无法获取知识库信息")

            # 获取来源统计
            if self.agent:
                stats = self.agent.get_source_statistics()
                print(f"\n[本次会话统计]")
                print(f"查询次数: {stats['total_queries']}")
                print(f"来源引用次数: {stats['total_sources']}")
                print(f"唯一来源数: {stats['unique_sources']}")

                if stats['most_used']:
                    print("\n最常用来源 TOP 5:")
                    for item in stats['most_used']:
                        print(f"  - {item['source']} (被引用 {item['count']} 次)")

        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")

        print("=" * 60)

    def _show_help(self):
        """显示帮助信息"""
        print("\n" + "=" * 60)
        print("帮助信息")
        print("=" * 60)
        print("\n可用命令:")
        print("  <问题>    - 向 Agent 提问，获取基于知识库的回答")
        print("  stats     - 查看知识库统计信息")
        print("  help      - 显示此帮助信息")
        print("  exit/quit - 退出程序")
        print("\n功能说明:")
        print("  - Agent 会自动检索知识库中的相关文档")
        print("  - 回答会包含引用来源，方便溯源")
        print("  - 如果知识库中没有相关信息，Agent 会诚实告知")
        print("=" * 60)

    def process_input(self, user_input: str):
        """
        处理用户输入

        Args:
            user_input: 用户输入
        """
        user_input = user_input.strip()

        # 空输入
        if not user_input:
            return

        # 命令处理
        if user_input.lower() in ['exit', 'quit']:
            print("\n👋 感谢使用，再见！")
            self.running = False
            return

        if user_input.lower() == 'stats':
            self._show_stats()
            return

        if user_input.lower() == 'help':
            self._show_help()
            return

        # 正常问答
        try:
            print("\n" + "-" * 60)
            response = self.agent.chat(user_input)
            print(f"\n{response}")
            print("-" * 60)
        except Exception as e:
            print(f"\n❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()

    def run(self):
        """运行 CLI"""
        self.initialize()

        print("\n开始对话（输入 'help' 查看帮助）:\n")

        while self.running:
            try:
                # 获取用户输入
                user_input = input("你: ").strip()

                if user_input:
                    self.process_input(user_input)

            except EOFError:
                # 处理 Ctrl+D
                print("\n\n👋 感谢使用，再见！")
                break
            except KeyboardInterrupt:
                # 处理 Ctrl+C
                continue
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")
                import traceback
                traceback.print_exc()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("RAG Agent - 基于知识库的智能问答助手")
    print("=" * 60)

    # 检查环境变量
    from dotenv import load_dotenv
    load_dotenv()

    required_vars = ["LLM_MODEL_ID", "LLM_API_KEY", "LLM_BASE_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"\n❌ 缺少环境变量: {', '.join(missing_vars)}")
        print("请在 .env 文件中配置以下环境变量:")
        print("  LLM_MODEL_ID=your_model")
        print("  LLM_API_KEY=your_api_key")
        print("  LLM_BASE_URL=your_base_url")
        sys.exit(1)

    # 创建并运行 CLI
    cli = RAGAgentCLI()
    cli.run()


if __name__ == "__main__":
    main()
