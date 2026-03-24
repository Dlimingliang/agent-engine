"""
@generated-by AI: matthewmli
@generated-date 2026-03-23
"""
from datetime import datetime
from typing import Any, Dict, Optional

from .base import BaseMemory


class ShortTermMemory(BaseMemory):
    """
    短期记忆

    存储当前会话的意图和状态跟踪
    生命周期：会话级，会话结束清除
    """

    def __init__(self):
        """初始化短期记忆"""
        self.current_intent: str | None = None
        self.intent_context: dict[str, Any] | None = None
        self.recent_topics: list[str] = []
        self.last_updated: datetime | None = None

    def update_intent(self, intent: str, context: Optional[dict[str, Any]] = None):
        """
        更新意图

        Args:
            intent: 意图名称
            context: 意图上下文
        """
        self.current_intent = intent
        self.intent_context = context
        self.last_updated = datetime.now()

    def add_topic(self, topic: str):
        """
        添加话题

        Args:
            topic: 话题名称
        """
        self.recent_topics.append(topic)
        if len(self.recent_topics) > 5:
            self.recent_topics = self.recent_topics[-5:]
        self.last_updated = datetime.now()

    def clear_intent(self):
        """清除当前意图"""
        self.current_intent = None
        self.intent_context = None
        self.last_updated = datetime.now()

    def get_context_summary(self) -> str:
        """
        获取上下文摘要

        Returns:
            上下文摘要字符串
        """
        parts = []
        if self.current_intent:
            parts.append(f"当前意图: {self.current_intent}")
        if self.intent_context:
            parts.append(f"意图上下文: {self.intent_context}")
        if self.recent_topics:
            parts.append(f"最近话题: {', '.join(self.recent_topics)}")
        return "\n".join(parts) if parts else "暂无上下文信息"

    # === 基类方法实现 ===

    def update(self, data: dict[str, Any]):
        """
        更新记忆

        Args:
            data: 包含更新数据的字典
        """
        if "current_intent" in data:
            self.current_intent = data["current_intent"]
        if "intent_context" in data:
            self.intent_context = data["intent_context"]
        if "recent_topics" in data:
            self.recent_topics = data["recent_topics"]
        if "last_updated" in data:
            last_updated = data["last_updated"]
            if isinstance(last_updated, str):
                self.last_updated = datetime.fromisoformat(last_updated)
            else:
                self.last_updated = last_updated
        self.last_updated = datetime.now()

    def get(self) -> Dict[str, Any]:
        """获取记忆内容"""
        return self.to_dict()

    def clear(self):
        """清除记忆"""
        self.current_intent = None
        self.intent_context = None
        self.recent_topics = []
        self.last_updated = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "current_intent": self.current_intent,
            "intent_context": self.intent_context,
            "recent_topics": self.recent_topics,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShortTermMemory":
        """
        从字典创建

        Args:
            data: 包含记忆数据的字典

        Returns:
            ShortTermMemory 实例
        """
        memory = cls()
        memory.current_intent = data.get("current_intent")
        memory.intent_context = data.get("intent_context")
        memory.recent_topics = data.get("recent_topics", [])
        if data.get("last_updated"):
            memory.last_updated = datetime.fromisoformat(data["last_updated"])
        return memory
