"""
@generated-by AI: matthewmli
@generated-date 2026-03-23
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from typing import List, Dict, Any, Optional
from common.message import Message, MessageRole
from session.conversation_manager import ConversationManager
from memory.writer import MemoryWriter
from memory.reader import MemoryReader
from tools.tool_registry import ToolRegistry

# 加载 .env 文件中的环境变量
load_dotenv()

class Agent:
    """Agent 主类，协调记忆、工具、会话"""
    
    def __init__(self, system_prompt:str,conversation_manager:ConversationManager,
                 memory_reader: MemoryReader,
                 memory_writer: MemoryWriter,
                 tool_registry: ToolRegistry, ):
        """
        初始化 Agent
        
        Args:
            conversation_manager: 会话管理器
            memory_reader: 记忆读取器
            memory_writer: 记忆写入器
            tool_registry: 工具注册器
        """
        # TODO: 实现初始化逻辑
        self.system_prompt = system_prompt
        self.conversation_manager = conversation_manager
        self.memory_reader = memory_reader
        self.memory_writer = memory_writer
        self.tool_registry = tool_registry
        self.model = os.getenv("LLM_MODEL_ID")
        apiKey = os.getenv("LLM_API_KEY")
        baseUrl = os.getenv("LLM_BASE_URL")
        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=60)
    
    def chat(self, user_input: str) -> str:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入
        
        Returns:
            Agent 回复
        """
        # TODO: 实现对话处理流程
        # 1. 获取当前会话
        # 2. 读取记忆
        # 3. 组装上下文
        # 4. 调用 LLM
        # 5. 处理工具调用（如有）
        # 6. 更新记忆
        # 7. 返回回复
        session = self.conversation_manager.get_current_session()
        if session is None:
            session = self.conversation_manager.create_session()

        self.conversation_manager.add_message(session.session_id, MessageRole.USER, user_input)

        # 构建上下文给模型
        messages = self._build_context(user_input)

        while True:
            response = self._call_llm(messages)
            message = response.choices[0].message
            if message.tool_calls:
                # 添加 assistant 消息到会话
                # 构造 tool_calls 格式
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
                    tool_res = self.tool_registry.execute_tool(tool_name, tool_args)
                    
                    # 添加工具响应消息
                    self.conversation_manager.add_message(
                        session.session_id,
                        MessageRole.TOOL,
                        content=str(tool_res),
                        tool_call_id=tool_id
                    )
                
                # 重新构建上下文并继续循环
                messages = self._build_context(user_input)
            else:
                # 添加最终回复到会话
                self.conversation_manager.add_message(
                    session.session_id,
                    MessageRole.ASSISTANT,
                    content=message.content
                )
                
                # 更新记忆
                self._update_memories(user_input, message.content)
                
                return message.content

    
    def _build_context(self, user_input: str) -> List[Dict[str, str]]:
        """
        组装上下文
        
        Args:
            user_input: 用户输入
        
        Returns:
            上下文消息列表
        """
        # 1. System Prompt
        res = []
        res.append({
            "role": MessageRole.SYSTEM,
            "content": self.system_prompt,
        })

        # 2. 记忆上下文（长期 -> 工作 -> 短期）
        memory_content = self.memory_reader.build_memory_context(user_input)
        if memory_content:
            res.append({
                "role": MessageRole.SYSTEM,
                "content": f"[记忆上下文]\n{memory_content}",
            })

        # 3. 会话历史
        session = self.conversation_manager.get_current_session()
        if session:
            res.extend([message.to_dict() for message in session.messages])

        return res



    
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
            print("✅ 大语言模型响应成功")
            return response
        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            raise
    
    def _update_memories(self, user_input: str, assistant_response: str):
        """
        更新记忆
        
        Args:
            user_input: 用户输入
            assistant_response: Agent 回复
        """
        # TODO: 实现记忆更新逻辑
        # 调用 memory_writer 判断并更新
        self.memory_writer.process_update(user_input, assistant_response)
