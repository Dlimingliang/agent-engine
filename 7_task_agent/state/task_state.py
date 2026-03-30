from enum import Enum
from typing import Set, Optional
from datetime import datetime


class TaskStatus(Enum):
    """
    任务状态枚举
    
    状态说明：
    - PENDING: 待执行
    - PLANNING: 正在制定计划
    - EXECUTING: 正在执行
    - VERIFYING: 正在验证
    - WAITING_USER: 等待用户确认
    - COMPLETED: 已完成
    - FAILED: 失败
    - CANCELLED: 已取消
    - PAUSED: 已暂停
    """
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    WAITING_USER = "waiting_user"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


# 定义合法的状态转换
# Key: 当前状态, Value: 可以转换到的状态集合
VALID_TRANSITIONS = {
    TaskStatus.PENDING: {
        TaskStatus.PLANNING,
        TaskStatus.CANCELLED
    },
    TaskStatus.PLANNING: {
        TaskStatus.EXECUTING,
        TaskStatus.FAILED,
        TaskStatus.PENDING
    },
    TaskStatus.EXECUTING: {
        TaskStatus.VERIFYING,
        TaskStatus.WAITING_USER,
        TaskStatus.FAILED,
        TaskStatus.PAUSED
    },
    TaskStatus.VERIFYING: {
        TaskStatus.COMPLETED,
        TaskStatus.EXECUTING,
        TaskStatus.FAILED
    },
    TaskStatus.WAITING_USER: {
        TaskStatus.EXECUTING,
        TaskStatus.CANCELLED,
        TaskStatus.PAUSED
    },
    TaskStatus.PAUSED: {
        TaskStatus.EXECUTING,
        TaskStatus.CANCELLED
    },
    TaskStatus.FAILED: {
        TaskStatus.PENDING,
        TaskStatus.CANCELLED
    },
    # 终态不可转换
    TaskStatus.COMPLETED: set(),
    TaskStatus.CANCELLED: set()
}


class TaskStateMachine:
    """
    任务状态机
    
    职责：
    1. 维护当前状态
    2. 检查状态转换合法性
    3. 记录状态变更历史
    4. 提供状态查询接口
    """
    
    def __init__(self):
        """
        初始化状态机
        
        TODO:
        1. 设置初始状态为 PENDING
        2. 初始化状态变更历史列表
        """
        self.status = TaskStatus.PENDING
        self.history: list = []
    
    def transition(self, new_status: TaskStatus, reason: str = "") -> bool:
        """
        状态转换
        
        Args:
            new_status: 新状态
            reason: 转换原因
            
        Returns:
            bool: 是否转换成功
            
        TODO:
        1. 检查是否可以转换到新状态
        2. 如果可以，更新当前状态
        3. 记录状态变更历史
        4. 打印状态转换日志
        5. 返回是否成功
        """
        if self.can_transition_to(new_status):
            old_status = self.status
            self.status = new_status
            self.history.append({
                "old_status": old_status,
                "new_status": new_status,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })
            return True
        return False
    
    def can_transition_to(self, new_status: TaskStatus) -> bool:
        """
        检查是否可以转换到新状态
        
        Args:
            new_status: 目标状态
            
        Returns:
            bool: 是否可以转换
            
        TODO: 检查新状态是否在 VALID_TRANSITIONS[current_status] 中
        """
        if new_status not in VALID_TRANSITIONS.get(self.status, set()):
            return False
        return True
    
    def get_current_status(self) -> TaskStatus:
        """
        获取当前状态
        
        Returns:
            TaskStatus: 当前状态
            
        TODO: 返回当前状态
        """
        return self.status
    
    def get_allowed_transitions(self) -> Set[TaskStatus]:
        """
        获取允许的转换目标
        
        Returns:
            Set[TaskStatus]: 允许转换到的状态集合
            
        TODO: 返回 VALID_TRANSITIONS[current_status]
        """
        return VALID_TRANSITIONS.get(self.status, set())
    
    def get_allowed_actions(self) -> Set[str]:
        """
        获取当前状态允许的动作
        
        Returns:
            Set[str]: 允许的动作集合
            
        TODO:
        根据当前状态返回允许的动作：
        - PENDING: {"start", "cancel"}
        - EXECUTING: {"pause", "cancel"}
        - PAUSED: {"resume", "cancel"}
        - FAILED: {"retry", "cancel"}
        - COMPLETED: {}
        - CANCELLED: {}
        """
        """获取当前状态允许的动作"""
        actions = {
            TaskStatus.PENDING: {"start", "cancel"},
            TaskStatus.PLANNING: {"wait"},
            TaskStatus.EXECUTING: {"pause", "cancel"},
            TaskStatus.VERIFYING: {"wait"},
            TaskStatus.WAITING_USER: {"confirm", "cancel", "pause"},
            TaskStatus.PAUSED: {"resume", "cancel"},
            TaskStatus.FAILED: {"retry", "cancel"},
            TaskStatus.COMPLETED: set(),
            TaskStatus.CANCELLED: set()
        }
        return actions.get(self.status, set())
    
    def is_terminal(self) -> bool:
        """
        判断是否为终态
        
        Returns:
            bool: 是否为终态
            
        TODO: 检查当前状态是否为 COMPLETED 或 CANCELLED
        """
        if self.status == TaskStatus.COMPLETED or self.status == TaskStatus.CANCELLED:
            return True
        return False
    
    def can_execute(self) -> bool:
        """
        判断是否可以执行
        
        Returns:
            bool: 是否可以执行
            
        TODO: 检查当前状态是否为 EXECUTING
        """
        return self.status in [TaskStatus.EXECUTING]
    
    def can_pause(self) -> bool:
        """
        判断是否可以暂停
        
        Returns:
            bool: 是否可以暂停
            
        TODO: 检查当前状态是否为 EXECUTING 或 WAITING_USER
        """
        return self.status in [TaskStatus.EXECUTING, TaskStatus.WAITING_USER]

    def can_cancel(self) -> bool:
        """
        判断是否可以取消
        
        Returns:
            bool: 是否可以取消
            
        TODO: 检查当前状态不是终态
        """
        return self.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
    
    def can_retry(self) -> bool:
        """
        判断是否可以重试
        
        Returns:
            bool: 是否可以重试
            
        TODO: 检查当前状态是否为 FAILED
        """
        return self.status in [TaskStatus.FAILED]
    
    def get_history(self) -> list:
        """
        获取状态变更历史
        
        Returns:
            list: 状态变更历史列表
            
        TODO: 返回状态变更历史
        """
        return self.history
    
    def reset(self):
        """
        重置状态机
        
        TODO:
        1. 将状态重置为 PENDING
        2. 清空历史记录
        """
        self.status = TaskStatus.PENDING
        self.history.clear()
