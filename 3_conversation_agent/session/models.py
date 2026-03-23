"""
会话数据模型
"""
from datetime import datetime
from typing import Any
from .session_status import SessionStatus
from agent.message import Message, MessageRole


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
        messages: list[Message] | None = None,
        status: SessionStatus = SessionStatus.COMPLETED,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        title: str = ""
    ):
        """
        初始化会话
        """
        self.session_id: str = session_id
        self.user_id: str = user_id
        self.messages: list[Message] = messages if messages is not None else []
        self.status: SessionStatus = status
        self.created_at: datetime = created_at if created_at is not None else datetime.now()
        self.updated_at: datetime = updated_at if updated_at is not None else datetime.now()
        self.title: str = title

    def add_message(self, role: MessageRole, content: str) -> Message:
        """
        添加消息到会话
        """
        message = Message(role = role, content = content)
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def update_status(self, status: SessionStatus):
        """
        更新会话状态
        """
        self.status = status
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict[str, Any]:
        """
        转换为字典格式
        
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
        # === AI Generated Code Start matthewmli===
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "messages": [msg.to_dict() for msg in self.messages] if self.messages else [],
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "title": self.title,
        }
        # === AI Generated Code End matthewmli===
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Session':
        """
        从字典创建会话对象
        
        1. 从字典中提取数据
        2. messages 需要从字典列表转换为 Message 对象列表
        3. status 需要从字符串转换为 SessionStatus 枚举
        4. datetime 需要从字符串解析
        5. 返回 Session 对象
        """
        # === AI Generated Code Start matthewmli===
        # 转换 messages
        messages = None
        if "messages" in data and data["messages"]:
            messages = [Message.from_dict(msg) for msg in data["messages"]]
        
        # 转换 status
        status = SessionStatus(data["status"])
        
        # 解析 datetime
        created_at = datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        updated_at = datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        
        return cls(
            session_id=data["session_id"],
            user_id=data["user_id"],
            messages=messages,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            title=data.get("title", "")
        )
        # === AI Generated Code End matthewmli===
