import sys
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel, PrivateAttr
from datetime import datetime
import uuid

# 添加项目根目录到 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .task_state import TaskStatus, TaskStateMachine


class StepStatus(BaseModel):
    """
    单个步骤的状态
    
    记录：
    - 步骤 ID
    - 步骤状态
    - 重试次数
    - 最后错误信息
    - 执行结果
    """
    step_id: int
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = 0
    last_error: str | None = None
    result: dict[str, Any] | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class TaskTracker(BaseModel):
    """
    任务跟踪器
    
    职责：
    1. 跟踪任务整体状态
    2. 跟踪每个步骤的状态
    3. 提供进度查询
    4. 生成任务摘要
    
    与 TaskStateMachine 联合使用：
    - TaskStateMachine 负责状态转换验证和历史记录
    - TaskTracker 负责任务生命周期管理和步骤跟踪
    """
    task_id: str
    task_description: str = ""
    # 使用私有属性存储状态机，确保状态转换经过验证
    _state_machine: TaskStateMachine = PrivateAttr(default_factory=TaskStateMachine)
    steps: Dict[int, StepStatus] = {}
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    class Config:
        use_enum_values: bool = True
    
    @property
    def overall_status(self) -> TaskStatus:
        """
        获取当前整体状态（通过状态机）
        
        Returns:
            TaskStatus: 当前状态
        """
        return self._state_machine.get_current_status()
    
    @staticmethod
    def generate_task_id() -> str:
        """
        生成任务 ID
        
        Returns:
            str: 任务 ID (格式: task_YYYYMMDD_HHMMSS_UUID)
            
        TODO: 生成格式化的任务 ID
        """
        str_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"task_{str_time}_{str(uuid.uuid4())}"
    
    def update_overall_status(self, new_status: TaskStatus, reason: str = "") -> bool:
        """
        更新整体状态（通过状态机验证）
        
        Args:
            new_status: 新状态
            reason: 更新原因
            
        Returns:
            bool: 是否更新成功（状态转换是否合法）
            
        说明：
        状态转换由 TaskStateMachine 验证，只有合法的转换才会成功
        """
        success = self._state_machine.transition(new_status, reason)
        if success:
            self.updated_at = datetime.now()
        return success
    
    def update_step_status(
        self,
        step_id: int,
        status: TaskStatus,
        error: str | None = None,
        result: dict[str, Any] | None = None
    ):
        """
        更新步骤状态
        
        Args:
            step_id: 步骤 ID
            status: 新状态
            error: 错误信息
            result: 执行结果
            
        TODO:
        1. 如果步骤不存在，创建新的 StepStatus
        2. 更新步骤状态
        3. 如果有错误，更新 last_error 和 attempts
        4. 如果有结果，更新 result
        5. 更新时间戳
        """
        if step_id not in self.steps:
            self.steps[step_id] = StepStatus(
                step_id=step_id,
                status=status,
            )
        else:
            self.steps[step_id].status = status
        if error:
            self.steps[step_id].last_error = error
            self.steps[step_id].attempts += 1
        if result:
            self.steps[step_id].result = result

        self.updated_at= datetime.now()
    
    def get_step_status(self, step_id: int) -> StepStatus | None:
        """
        获取步骤状态
        
        Args:
            step_id: 步骤 ID
            
        Returns:
            StepStatus | None: 步骤状态
            
        TODO: 返回指定步骤的状态
        """
        return self.steps.get(step_id)

    def get_progress(self) -> dict[str, int | float | str]:
        """
        获取任务进度
        
        Returns:
            dict: 进度信息
            {
                "total_steps": 总步骤数,
                "completed": 已完成数,
                "failed": 失败数,
                "pending": 待执行数,
                "progress_percent": 进度百分比,
                "current_status": 当前状态
            }
            
        TODO:
        1. 统计总步骤数
        2. 统计各状态的步骤数
        3. 计算进度百分比
        4. 返回进度信息
        """
        total_steps = len(self.steps)
        completed_steps = sum(
            1 for step in self.steps.values()
            if step.status == TaskStatus.COMPLETED
        )
        failed_steps = sum(
            1 for step in self.steps.values()
            if step.status == TaskStatus.FAILED
        )
        return {
            "total_steps": total_steps,
            "completed": completed_steps,
            "failed": failed_steps,
            "progress_percent": 100 * completed_steps / total_steps if total_steps > 0 else 0,
            "current_status": self.overall_status.value,
        }
    
    def get_summary(self) -> str:
        """
        获取任务摘要
        
        Returns:
            str: 任务摘要文本
            
        TODO:
        生成格式化的任务摘要：
        - 任务 ID 和描述
        - 整体状态
        - 进度统计
        - 步骤详情列表
        """
        """获取任务摘要"""
        progress = self.get_progress()
        summary = f"""
        任务状态摘要
        =============
        任务ID: {self.task_id}
        描述: {self.task_description}
        整体状态: {self.overall_status.value}
        进度: {progress['completed']}/{progress['total_steps']} ({progress['progress_percent']:.1f}%)
        失败步骤: {progress['failed']}
                """
        return summary
    
    def get_detailed_status(self) -> dict[str, Any]:
        """
        获取详细状态
        
        Returns:
            dict: 详细状态信息
            
        TODO:
        返回包含以下信息的字典：
        - task_id
        - task_description
        - overall_status
        - progress
        - created_at
        - updated_at
        - duration (seconds)
        - steps_detail (每个步骤的详细信息)
        """
        return {
            "task_id": self.task_id,
            "task_description": self.task_description,
            "overall_status": self.overall_status.value,
            "progress": self.get_progress(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "duration": (datetime.now() - self.created_at).total_seconds(),
            "steps_detail": self.steps,
        }
    
    def mark_step_started(self, step_id: int):
        """
        标记步骤开始
        
        Args:
            step_id: 步骤 ID
            
        TODO:
        1. 更新步骤状态为 EXECUTING
        2. 记录 started_at 时间
        """
        if step_id in self.steps:
            self.steps[step_id].status = TaskStatus.EXECUTING
            self.steps[step_id].started_at = datetime.now()
    
    def mark_step_completed(self, step_id: int, result: dict[str, Any]):
        """
        标记步骤完成
        
        Args:
            step_id: 步骤 ID
            result: 执行结果
            
        TODO:
        1. 更新步骤状态为 COMPLETED
        2. 记录 result
        3. 记录 completed_at 时间
        """
        if step_id in self.steps:
            self.steps[step_id].status = TaskStatus.COMPLETED
            self.steps[step_id].result = result
            self.steps[step_id].completed_at = datetime.now()
    
    def mark_step_failed(self, step_id: int, error: str):
        """
        标记步骤失败
        
        Args:
            step_id: 步骤 ID
            error: 错误信息
            
        TODO:
        1. 更新步骤状态为 FAILED
        2. 记录 last_error
        3. 增加 attempts 计数
        """
        if step_id in self.steps:
            self.steps[step_id].status = TaskStatus.FAILED
            self.steps[step_id].last_error = error
            self.steps[step_id].attempts += 1

    
    def is_all_steps_completed(self) -> bool:
        """
        判断是否所有步骤都已完成
        
        Returns:
            bool: 是否全部完成
            
        TODO: 检查是否所有步骤状态都为 COMPLETED
        """
        # 如果没有步骤，返回 False
        if not self.steps:
            return False
        # 检查所有步骤是否都为 COMPLETED 状态
        return all(
            step.status == TaskStatus.COMPLETED 
            for step in self.steps.values()
        )
    
    def has_failed_steps(self) -> bool:
        """
        判断是否有失败的步骤
        
        Returns:
            bool: 是否有失败步骤
            
        TODO: 检查是否有步骤状态为 FAILED
        """
        # 检查是否有任何步骤状态为 FAILED
        return any(
            step.status == TaskStatus.FAILED 
            for step in self.steps.values()
        )
    
    def get_failed_steps(self) -> list[StepStatus]:
        """
        获取所有失败的步骤
        
        Returns:
            list: 失败步骤列表
            
        TODO: 返回所有状态为 FAILED 的步骤
        """
        # 返回所有状态为 FAILED 的步骤对象列表
        return [
            step for step in self.steps.values() 
            if step.status == TaskStatus.FAILED
        ]
    
    # ========== 状态机代理方法 ==========
    # 以下方法委托给内部 TaskStateMachine，提供便捷访问
    
    def get_status_history(self) -> list[dict[str, str | TaskStatus]]:
        """
        获取状态变更历史
        
        Returns:
            list: 状态变更历史列表
        """
        return self._state_machine.get_history()
    
    def get_allowed_actions(self) -> set[str]:
        """
        获取当前状态允许的动作
        
        Returns:
            set[str]: 允许的动作集合
        """
        return self._state_machine.get_allowed_actions()
    
    def get_allowed_transitions(self) -> set[TaskStatus]:
        """
        获取允许的状态转换目标
        
        Returns:
            set[TaskStatus]: 允许转换到的状态集合
        """
        return self._state_machine.get_allowed_transitions()
    
    def can_pause(self) -> bool:
        """判断是否可以暂停"""
        return self._state_machine.can_pause()
    
    def can_cancel(self) -> bool:
        """判断是否可以取消"""
        return self._state_machine.can_cancel()
    
    def can_retry(self) -> bool:
        """判断是否可以重试"""
        return self._state_machine.can_retry()
    
    def is_terminal(self) -> bool:
        """判断是否为终态"""
        return self._state_machine.is_terminal()
