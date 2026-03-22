"""
消息模型
"""
from enum import Enum
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

class MessageRole(str, Enum):
    """
    消息角色枚举
    """
    SYSTEM = "system"      # 系统提示词
    USER = "user"          # 用户输入
    ASSISTANT = "assistant"  # 助手回复
    TOOL = "tool"          # 工具执行结果


class Message(BaseModel):
    """
    消息类：表示对话中的一条消息
    
    字段：
        role: str - 消息角色（user / assistant / system）
        content: str - 消息内容
        timestamp: datetime - 时间戳
    """
    role: MessageRole = Field(..., description="消息角色")
    content: str|None = Field(None, description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")

    def to_openai_dict(self) -> dict[str, Any]:
        """
        转换为 OpenAI API 所需的格式

        Returns:
            符合 OpenAI messages 格式的字典
        """
        msg = {"role": self.role.value}

        if self.content is not None:
            msg["content"] = self.content

        return msg
    
    def to_dict(self) -> dict[str, Any]:
        """
        转换为字典格式
        
        返回格式：
        {
            "role": "user",
            "content": "消息内容",
            "timestamp": "2026-03-20T10:00:00"
        }
        """
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Message':
        """
        从字典创建消息对象
        
        参数：
            data: dict - 消息字典数据
            
        返回：
            Message - 消息对象
        """
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )
