"""
@generated-by AI: matthewmli
@generated-date 2026-03-24
"""
from enum import Enum
from datetime import datetime
from typing import Any, Optional


class MessageRole(str, Enum):
    """
    消息角色枚举
    """
    SYSTEM = "system"      # 系统提示词
    USER = "user"          # 用户输入
    ASSISTANT = "assistant"  # 助手回复
    TOOL = "tool"          # 工具执行结果


class Message:
    """消息模型"""
    
    role: MessageRole
    content: Optional[str]
    timestamp: Optional[datetime]
    tool_calls: Optional[list[dict[str, Any]]]
    tool_call_id: Optional[str]
    
    def __init__(
        self,
        role: MessageRole,
        content: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        tool_calls: Optional[list[dict[str, Any]]] = None,
        tool_call_id: Optional[str] = None
    ):
        """
        初始化消息
        
        Args:
            role: 消息角色 (user/assistant/system/tool)
            content: 消息内容
            timestamp: 时间戳
            tool_calls: 工具调用列表
            tool_call_id: 工具调用ID
        """
        self.role = role
        self.content = content
        self.timestamp = timestamp
        self.tool_calls = tool_calls
        self.tool_call_id = tool_call_id
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        msg: dict[str, Any] = {"role": self.role.value}

        if self.content is not None:
            msg["content"] = self.content

        if self.tool_calls:
            msg["tool_calls"] = [
                {
                    "id": tc["id"],
                    "type": tc["type"],
                    "function": tc["function"]
                }
                for tc in self.tool_calls
            ]

        if self.tool_call_id:
            msg["tool_call_id"] = self.tool_call_id

        if self.timestamp:
            msg["timestamp"] = self.timestamp.isoformat()

        return msg
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Message":
        """从字典创建消息"""
        timestamp = None
        if "timestamp" in data and data["timestamp"]:
            timestamp = datetime.fromisoformat(str(data["timestamp"]))
        
        tool_calls = None
        if "tool_calls" in data and data["tool_calls"]:
            tool_calls = data["tool_calls"]
        
        return cls(
            role=MessageRole(data["role"]),
            content=data.get("content"),
            timestamp=timestamp,
            tool_calls=tool_calls,
            tool_call_id=data.get("tool_call_id")
        )
    
    def __repr__(self) -> str:
        content_preview = (self.content[:50] if self.content else "")
        return f"Message(role={self.role}, content={content_preview}...)"
