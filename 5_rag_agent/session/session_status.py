"""
@generated-by AI: matthewmli
@generated-date 2026-03-23
"""
from enum import Enum


class SessionStatus(Enum):
    """会话状态枚举"""
    
    COMPLETED = "completed"              # 已完成
    WAITING_FOR_USER = "waiting_for_user"  # 等待用户输入
    WAITING_FOR_TOOL = "waiting_for_tool"  # 等待工具结果
    SUSPENDED = "suspended"              # 挂起
    FAILED = "failed"                    # 失败
