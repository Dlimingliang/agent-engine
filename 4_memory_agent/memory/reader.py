"""
@generated-by AI: matthewmli
@generated-date 2026-03-23
"""
from typing import Any, Optional

from .long_term import LongTermMemory
from .short_term import ShortTermMemory
from .working import WorkingMemory


class MemoryReader:
    """
    记忆读取器

    按类型读取记忆，组装到上下文
    """

    def __init__(
        self,
        short_term_memory: ShortTermMemory,
        long_term_memory: LongTermMemory,
        working_memory: WorkingMemory,
    ):
        """
        初始化记忆读取器

        Args:
            short_term_memory: 短期记忆实例
            long_term_memory: 长期记忆实例
            working_memory: 工作记忆实例
        """
        self.short_term_memory = short_term_memory
        self.long_term_memory = long_term_memory
        self.working_memory = working_memory

    def read_short_term(self) -> Optional[dict[str, Any]]:
        """
        读取短期记忆

        Returns:
            短期记忆数据
        """
        data = self.short_term_memory.get()
        if data and any(data.values()):
            return data
        return None

    def read_long_term(self, query: str) -> Optional[dict[str, Any]]:
        """
        读取相关长期记忆

        Args:
            query: 查询字符串

        Returns:
            相关长期记忆
        """
        data = self.long_term_memory.get_relevant(query)
        if data and any(
            [data.get("preferences"), data.get("facts"), data.get("decisions")]
        ):
            return data
        return None

    def read_working(self) -> Optional[dict[str, Any]]:
        """
        读取工作记忆

        Returns:
            工作记忆数据
        """
        data = self.working_memory.get()
        if data and data.get("current_task"):
            return data
        return None

    def build_memory_context(self, query: str) -> str:
        """
        组装记忆上下文

        Args:
            query: 用户查询

        Returns:
            记忆上下文字符串
        """
        context: list[str] = []

        # 长期记忆（用户偏好、相关事实）
        long_term = self.read_long_term(query)
        if long_term:
            preferences = long_term.get("preferences", {})
            if preferences:
                prefs_str = ", ".join(f"{k}={v}" for k, v in preferences.items())
                context.append(f"[用户偏好] {prefs_str}")

            facts = long_term.get("facts", [])
            if facts:
                facts_str = "; ".join(f.get("content", "") for f in facts)
                context.append(f"[相关事实] {facts_str}")

            decisions = long_term.get("decisions", [])
            if decisions:
                decisions_str = "; ".join(
                    d.get("decision", "") for d in decisions[:3]
                )
                context.append(f"[关键决策] {decisions_str}")

        # 工作记忆（当前任务状态）
        working = self.read_working()
        if working:
            task = working.get("current_task", {})
            if task:
                task_name = task.get("name", "未知任务")
                task_status = task.get("status", "unknown")
                context.append(f"[当前任务] {task_name} ({task_status})")

        # 短期记忆（当前意图）
        short_term = self.read_short_term()
        if short_term:
            intent = short_term.get("current_intent")
            if intent:
                context.append(f"[当前意图] {intent}")
            topics = short_term.get("recent_topics", [])
            if topics:
                context.append(f"[最近话题] {', '.join(topics)}")

        return "\n".join(context) if context else ""

    def get_all_memories(self) -> dict[str, Any]:
        """
        获取所有记忆（用于调试/展示）

        Returns:
            所有记忆数据
        """
        return {
            "short_term": self.short_term_memory.get(),
            "long_term": self.long_term_memory.get(),
            "working": self.working_memory.get(),
        }
