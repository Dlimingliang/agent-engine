"""
会话状态枚举
"""
from enum import Enum


class SessionStatus(Enum):
    """
    会话状态枚举：定义会话的五种状态
    
    状态说明：
        COMPLETED: 已完成 - 当前任务已完成，Agent 已给出最终答案
        WAITING_FOR_USER: 等待用户输入 - Agent 需要更多信息才能继续
        WAITING_FOR_TOOL: 等待工具结果 - Agent 调用了工具，等待结果返回
        SUSPENDED: 挂起 - 会话暂停，但未结束，可以稍后恢复
        FAILED: 失败 - 当前任务失败，无法继续
    """
    
    COMPLETED = "completed"
    WAITING_FOR_USER = "waiting_for_user"
    WAITING_FOR_TOOL = "waiting_for_tool"
    SUSPENDED = "suspended"
    FAILED = "failed"
    
    def __str__(self) -> str:
        """字符串表示"""
        return self.value
