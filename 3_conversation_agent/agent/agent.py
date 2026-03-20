"""
极简 Agent 类
"""
from typing import List
from .message import Message


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
        pass
    
    def chat(self, user_input: str, messages: List[Message]) -> str:
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
        pass
