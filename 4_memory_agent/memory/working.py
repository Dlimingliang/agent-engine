"""
@generated-by AI: matthewmli
@generated-date 2026-03-23
"""
from datetime import datetime
from typing import Any, Optional

from .base import BaseMemory


class WorkingMemory(BaseMemory):
    """
    工作记忆

    存储任务执行过程中的计划、进度、中间结果
    生命周期：任务级，任务完成/取消后清除
    """

    def __init__(self):
        """初始化工作记忆"""
        self.current_task: dict[str, Any] = {}
        self.intermediate_results: dict[str, Any] = {}

    def init_task(self, task_id: str, name: str, steps: Optional[list[str]] = None):
        """
        初始化任务

        Args:
            task_id: 任务ID
            name: 任务名称
            steps: 任务步骤列表（可选）
        """
        self.current_task = {
            "task_id": task_id,
            "name": name,
            "status": "pending",
            "steps": [{"step": s, "status": "pending"} for s in (steps or [])],
            "created_at": datetime.now().isoformat(),
        }
        self.intermediate_results = {}

    def update_step(self, step_name: str, status: str):
        """
        更新步骤状态

        Args:
            step_name: 步骤名称
            status: 步骤状态 (pending/in_progress/completed/failed)
        """
        steps = self.current_task.get("steps", [])
        for step in steps:
            if step.get("step") == step_name:
                step["status"] = status
                return
        # 如果步骤不存在，添加新步骤
        steps.append({"step": step_name, "status": status})

    def store_result(self, key: str, value: Any):
        """
        存储中间结果

        Args:
            key: 结果键
            value: 结果值
        """
        self.intermediate_results[key] = value

    def complete_task(self):
        """完成任务"""
        if self.current_task:
            self.current_task["status"] = "completed"
            self.current_task["completed_at"] = datetime.now().isoformat()

    def get_task_status(self) -> Optional[dict[str, Any]]:
        """
        获取任务状态

        Returns:
            任务状态信息
        """
        if not self.current_task:
            return None
        return {
            "task_id": self.current_task.get("task_id"),
            "name": self.current_task.get("name"),
            "status": self.current_task.get("status"),
            "steps": self.current_task.get("steps", []),
            "intermediate_results": self.intermediate_results,
        }

    # === 基类方法实现 ===

    def update(self, data: dict[str, Any]):
        """
        更新记忆

        Args:
            data: 包含更新数据的字典
        """
        if "current_task" in data:
            self.current_task = data["current_task"]
        if "intermediate_results" in data:
            self.intermediate_results = data["intermediate_results"]

    def get(self) -> dict[str, Any]:
        """获取记忆内容"""
        return self.to_dict()

    def clear(self):
        """清除记忆"""
        self.current_task = {}
        self.intermediate_results = {}

    def to_dict(self) -> dict[str, Any]:
        """序列化为字典"""
        return {
            "current_task": self.current_task,
            "intermediate_results": self.intermediate_results,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkingMemory":
        """
        从字典创建

        Args:
            data: 包含记忆数据的字典

        Returns:
            WorkingMemory 实例
        """
        memory = cls()
        memory.current_task = data.get("current_task", {})
        memory.intermediate_results = data.get("intermediate_results", {})
        return memory
