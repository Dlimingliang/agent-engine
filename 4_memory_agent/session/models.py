"""
@generated-by AI: matthewmli
@generated-date 2026-03-23
"""
import uuid
from datetime import datetime
from typing import  Any, Optional
from .session_status import SessionStatus
from ..agent.message import Message, MessageRole


class Session:
    """会话数据模型"""
    
    def __init__(
        self,
        session_id: Optional[str] = None,
        user_id: str = "default_user",
        title: Optional[str] = None
    ):
        """
        初始化会话
        
        Args:
            session_id: 会话ID（可选，自动生成）
            user_id: 用户ID
            title: 会话标题
        """
        self.session_id: str = session_id or str(uuid.uuid4())
        self.user_id: str = user_id
        self.messages: list[Message] = []
        self.status: SessionStatus = SessionStatus.COMPLETED
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()
        self.title: str = title or ""
        self.short_term_memory: dict[str, Any] = {}
        self.working_memory: dict[str, Any] = {}

    def add_message(self, role: MessageRole, content: str):
        """
        添加消息
        
        Args:
            role: 消息角色
            content: 消息内容
        """
        message = Message(role=role, content=content)
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def update_status(self, status: SessionStatus):
        """
        更新状态
        
        Args:
            status: 新状态
        """
        self.status = status
        self.updated_at = datetime.now()
    
    def update_short_term_memory(self, data: dict[str, Any]):
        """
        更新短期记忆
        
        Args:
            data: 短期记忆数据
        """
        self.short_term_memory.update(data)
        self.updated_at = datetime.now()
    
    def update_working_memory(self, data: dict[str, Any]):
        """
        更新工作记忆
        
        Args:
            data: 工作记忆数据
        """
        self.working_memory.update(data)
        self.updated_at = datetime.now()
    
    def get_short_term_memory(self) -> dict[str, Any]:
        """获取短期记忆"""
        return self.short_term_memory
    
    def get_working_memory(self) -> dict[str, Any]:
        """获取工作记忆"""
        return self.working_memory
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "messages": [msg.to_dict() for msg in self.messages] if self.messages else [],
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "title": self.title,
            "short_term_memory": self.short_term_memory,
            "working_memory": self.working_memory,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Session":
        """从字典创建"""
        session = cls(
            session_id=data.get("session_id"),
            user_id=data.get("user_id", "default_user"),
            title=data.get("title", "")
        )
        
        # 恢复消息
        if "messages" in data and data["messages"]:
            session.messages = [Message.from_dict(msg) for msg in data["messages"]]
        
        # 恢复状态
        if "status" in data:
            session.status = SessionStatus(data["status"])
        
        # 恢复时间
        if data.get("created_at"):
            session.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            session.updated_at = datetime.fromisoformat(data["updated_at"])
        
        # 恢复记忆
        if "short_term_memory" in data:
            session.short_term_memory = data["short_term_memory"]
        if "working_memory" in data:
            session.working_memory = data["working_memory"]
        
        return session
