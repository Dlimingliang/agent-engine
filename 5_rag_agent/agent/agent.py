"""
@generated-by AI: matthewmli
@generated-date 2026-03-27
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from typing import List, Dict, Any, Optional
from common.message import Message, MessageRole
from session.conversation_manager import ConversationManager
from tools.tool_registry import ToolRegistry
from retrieval.retriever import Retriever
from citation.citation_handler import CitationHandler
from citation.source_tracker import SourceTracker

# 加载 .env 文件中的环境变量
load_dotenv()


class RAGAgent:
    """RAG Agent - 带知识库检索能力的智能助手"""

    def __init__(
        self,
        system_prompt: str,
        retriever: Retriever,
        conversation_manager: Optional[ConversationManager] = None,
        tool_registry: Optional[ToolRegistry] = None,
        citation_style: str = "numbered"
    ):
        """
        初始化 RAG Agent

        Args:
            system_prompt: 系统提示词
            retriever: 检索器实例
            conversation_manager: 会话管理器（可选）
            tool_registry: 工具注册器（可选）
            citation_style: 引用风格
        """
        self.system_prompt = system_prompt
        self.retriever = retriever
        self.conversation_manager = conversation_manager or ConversationManager()
        self.tool_registry = tool_registry or ToolRegistry()

        # 引用处理
        self.citation_handler = CitationHandler(style=citation_style)
        self.source_tracker = SourceTracker()

        # LLM 配置
        self.model = os.getenv("LLM_MODEL_ID")
        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("LLM_BASE_URL")
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=60)

    def chat(self, user_input: str) -> str:
        """
        处理用户输入

        Args:
            user_input: 用户输入

        Returns:
            Agent 回复
        """
        # 获取或创建会话
        session = self.conversation_manager.get_current_session()
        if session is None:
            session = self.conversation_manager.create_session()

        # 添加用户消息
        self.conversation_manager.add_message(
            session.session_id,
            MessageRole.USER,
            user_input
        )

        # 构建上下文
        messages = self._build_context(user_input)

        # 调用 LLM（支持工具调用循环）
        response_text = self._chat_loop(messages)

        return response_text

    def _chat_loop(self, messages: List[Dict[str, str]]) -> str:
        """
        对话循环（处理工具调用）

        Args:
            messages: 消息列表

        Returns:
            最终回复
        """
        session = self.conversation_manager.get_current_session()

        while True:
            # 调用 LLM
            response = self._call_llm(messages)
            message = response.choices[0].message

            # 检查是否有工具调用
            if message.tool_calls:
                # 添加 assistant 消息（包含 tool_calls）
                tool_calls_data = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
                self.conversation_manager.add_message(
                    session.session_id,
                    MessageRole.ASSISTANT,
                    content=message.content,
                    tool_calls=tool_calls_data
                )

                # 处理每个工具调用
                for tool_call in message.tool_calls:
                    tool_id = tool_call.id
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # 执行工具
                    tool_result = self.tool_registry.execute_tool(tool_name, tool_args)

                    # 添加工具响应消息
                    self.conversation_manager.add_message(
                        session.session_id,
                        MessageRole.TOOL,
                        content=json.dumps(tool_result, ensure_ascii=False),
                        tool_call_id=tool_id
                    )

                    # 如果是检索工具，追踪来源
                    if tool_name == "knowledge_search" and tool_result.get("success"):
                        sources = tool_result.get("results", [])
                        if sources:
                            # 获取查询参数
                            query = tool_args.get("query", "")
                            self.source_tracker.track(query, sources)

                # 重新构建上下文并继续循环
                messages = self._build_context("")
            else:
                # 没有工具调用，获取最终回复
                final_response = message.content or ""

                # 添加 assistant 消息
                self.conversation_manager.add_message(
                    session.session_id,
                    MessageRole.ASSISTANT,
                    content=final_response
                )

                return final_response

    def _build_context(self, user_input: str) -> List[Dict[str, str]]:
        """
        构建上下文

        Args:
            user_input: 用户输入

        Returns:
            上下文消息列表
        """
        messages = []

        # 1. System Prompt
        messages.append({
            "role": MessageRole.SYSTEM,
            "content": self.system_prompt
        })

        # 2. 会话历史
        session = self.conversation_manager.get_current_session()
        if session:
            messages.extend([msg.to_dict() for msg in session.messages])

        return messages

    def _call_llm(self, messages: List[Dict[str, str]]):
        """
        调用 LLM

        Args:
            messages: 消息列表

        Returns:
            LLM 响应对象
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tool_registry.get_openai_tools(),
                temperature=0,
                stream=False
            )
            return response
        except Exception as e:
            print(f"❌ 调用 LLM 失败: {e}")
            raise

    def get_source_statistics(self) -> Dict[str, Any]:
        """
        获取来源统计信息

        Returns:
            统计信息
        """
        return self.source_tracker.get_source_statistics()

    def get_source_report(self) -> str:
        """
        获取来源追踪报告

        Returns:
            报告文本
        """
        return self.source_tracker.get_summary_report()
