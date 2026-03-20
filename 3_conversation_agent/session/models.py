"""
会话数据模型
"""
from datetime import datetime
from typing import List, Dict, Any
from .session_status import SessionStatus
from agent.message import Message


class Session:
    """
    会话类：表示一个完整的对话会话
    
    字段：
        session_id: str - 会话唯一标识
        user_id: str - 用户标识
        messages: List[Message] - 消息历史
        status: SessionStatus - 当前状态
        created_at: datetime - 创建时间
        updated_at: datetime - 更新时间
        title: str - 会话标题
    """
    
    def __init__(
        self,
        session_id: str,
        user_id: str,
        messages: List[Message] = None,
        status: SessionStatus = SessionStatus.COMPLETED,
        created_at: datetime = None,
        updated_at: datetime = None,
        title: str = ""
    ):
        """
        初始化会话
        
        TODO: 实现初始化逻辑
        - 设置所有字段
        - messages 默认为空列表
        - created_at 和 updated_at 默认使用当前时间
        - title 可以是空字符串
        """
        pass
    
    def add_message(self, role: str, content: str) -> Message:
        """
        添加消息到会话
        
        TODO: 实现添加逻辑
        1. 创建 Message 对象
        2. 添加到 messages 列表
        3. 更新 updated_at
        4. 返回创建的 Message 对象
        """
        pass
    
    def update_status(self, status: SessionStatus):
        """
        更新会话状态
        
        TODO: 实现更新逻辑
        1. 设置新状态
        2. 更新 updated_at
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        TODO: 实现转换逻辑
        - 将 Session 对象转换为字典
        - messages 需要转换为字典列表
        - status 需要转换为字符串
        - datetime 需要转换为 ISO 格式字符串
        
        返回格式：
        {
            "session_id": "session_abc123",
            "user_id": "user_001",
            "messages": [...],
            "status": "completed",
            "created_at": "2026-03-20T10:00:00",
            "updated_at": "2026-03-20T10:00:05",
            "title": "聊天对话"
        }
        """
        pass
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """
        从字典创建会话对象
        
        TODO: 实现创建逻辑
        1. 从字典中提取数据
        2. messages 需要从字典列表转换为 Message 对象列表
        3. status 需要从字符串转换为 SessionStatus 枚举
        4. datetime 需要从字符串解析
        5. 返回 Session 对象
        """
        pass
    
    def __repr__(self) -> str:
        """字符串表示"""
        pass
