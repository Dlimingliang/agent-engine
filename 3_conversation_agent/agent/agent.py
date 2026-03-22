"""
极简 Agent 类
"""
import os
from dotenv import load_dotenv
from .message import Message, MessageRole
from openai import OpenAI
from typing import Any

# 加载 .env 文件中的环境变量
load_dotenv()


def get_messages(messages: list[Message]) -> list[dict[str, Any]]:
    res = []
    for message in messages:
        res.append(message.to_openai_dict())
    return res


class Agent:
    """
    极简 Agent 类：只做最基础的 LLM 调用
    
    职责：
        - 接收用户消息
        - 调用 LLM
        - 返回回复
    """
    
    def __init__(self):
        """
        初始化 Agent
        
        TODO: 实现初始化逻辑
        - 初始化 OpenAI 客户端
        - 从环境变量读取 API Key
        - 设置模型名称（如 gpt-3.5-turbo）
        """
        self.model = os.getenv("LLM_MODEL_ID")
        apiKey = os.getenv("LLM_API_KEY")
        baseUrl = os.getenv("LLM_BASE_URL")
        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=60)
    
    def chat(self, user_input: str, messages: list[Message]) -> str:
        """
        调用 LLM 生成回复
        
        TODO: 实现对话逻辑
        1. 将 Message 列表转换为 OpenAI API 格式
        2. 添加当前用户输入到消息列表
        3. 调用 OpenAI API
        4. 提取回复内容
        5. 返回回复字符串
        
        参数：
            user_input: str - 用户输入
            messages: List[Message] - 历史消息列表
            
        返回：
            str - Agent 的回复
        """
        user_message = Message(role = MessageRole.USER, content=user_input)
        message_history = get_messages(messages)
        message_history.append(user_message.to_openai_dict())
        params = {
            "model": self.model,
            "messages": message_history,
            "temperature": 0,
            "stream": False,
        }
        try:
            response = self.client.chat.completions.create(**params)
            print("✅ 大语言模型响应成功:")
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            return ""
