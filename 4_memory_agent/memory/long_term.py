"""
@generated-by AI: matthewmli
@generated-date 2026-03-23
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .base import BaseMemory


class LongTermMemory(BaseMemory):
    """
    长期记忆

    存储用户偏好、重要事实、关键决策
    生命周期：永久持久化，跨会话复用
    """

    def __init__(self, storage_path: str = "data/long_term_memory.json"):
        """
        初始化长期记忆

        Args:
            storage_path: 存储文件路径
        """
        self.user_preferences: dict[str, Any] = {}
        self.important_facts: list[dict[str, Any]] = []
        self.key_decisions: list[dict[str, Any]] = []
        self.storage_path = storage_path

    def add_preference(self, key: str, value: Any):
        """
        添加用户偏好

        Args:
            key: 偏好键
            value: 偏好值
        """
        self.user_preferences[key] = value

    def add_fact(self, content: str, metadata: Optional[dict[str, Any]] = None):
        """
        添加重要事实

        Args:
            content: 事实内容
            metadata: 元数据
        """
        self.important_facts.append(
            {
                "content": content,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
            }
        )

    def add_decision(self, decision: str, reason: str):
        """
        添加关键决策

        Args:
            decision: 决策内容
            reason: 决策原因
        """
        self.key_decisions.append(
            {
                "decision": decision,
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def get_relevant(self, query: str) -> dict[str, Any]:
        """
        检索相关记忆

        Args:
            query: 查询字符串

        Returns:
            相关记忆数据
        """
        result: dict[str, Any] = {
            "preferences": {},
            "facts": [],
            "decisions": [],
        }

        # 检索偏好
        for key, value in self.user_preferences.items():
            if query.lower() in key.lower():
                result["preferences"][key] = value

        # 检索事实
        for fact in self.important_facts:
            if query.lower() in fact.get("content", "").lower():
                result["facts"].append(fact)

        # 检索决策
        for decision in self.key_decisions:
            if query.lower() in decision.get("decision", "").lower():
                result["decisions"].append(decision)

        return result

    def save(self):
        """保存到文件"""
        path = Path(self.storage_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    def load(self):
        """从文件加载"""
        path = Path(self.storage_path)
        if not path.exists():
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.user_preferences = data.get("user_preferences", {})
        self.important_facts = data.get("important_facts", [])
        self.key_decisions = data.get("key_decisions", [])

    # === 基类方法实现 ===

    def update(self, data: dict[str, Any]):
        """
        更新记忆

        Args:
            data: 包含更新数据的字典
        """
        if "user_preferences" in data:
            self.user_preferences.update(data["user_preferences"])
        if "important_facts" in data:
            self.important_facts.extend(data["important_facts"])
        if "key_decisions" in data:
            self.key_decisions.extend(data["key_decisions"])

    def get(self) -> dict[str, Any]:
        """获取记忆内容"""
        return self.to_dict()

    def clear(self):
        """清除记忆"""
        self.user_preferences = {}
        self.important_facts = []
        self.key_decisions = []

    def to_dict(self) -> dict[str, Any]:
        """序列化为字典"""
        return {
            "user_preferences": self.user_preferences,
            "important_facts": self.important_facts,
            "key_decisions": self.key_decisions,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LongTermMemory":
        """
        从字典创建

        Args:
            data: 包含记忆数据的字典

        Returns:
            LongTermMemory 实例
        """
        memory = cls()
        memory.user_preferences = data.get("user_preferences", {})
        memory.important_facts = data.get("important_facts", [])
        memory.key_decisions = data.get("key_decisions", [])
        return memory
