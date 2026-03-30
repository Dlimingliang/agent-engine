# === AI Generated Code Start matthewmli @generated-date 2025-03-30 ===
import sys
import time
from pathlib import Path
from typing import Any, Callable
from pydantic import BaseModel

# 添加项目根目录到 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ..tools import ToolRegistry
from ..state.task_state import TaskStatus
from .planner import ExecutionPlan, TaskStep
# === AI Generated Code End matthewmli @generated-date 2025-03-30 ===


class ExecutionResult(BaseModel):
    """单步执行结果"""
    step_id: int
    success: bool
    result: Any | None = None
    error: str | None = None
    duration_ms: float | None = None
    timestamp: float | None = None


class ExecutionHistoryRecord(BaseModel):
    """
    执行历史记录 - 完整记录步骤执行信息
    
    包含：
    - 步骤信息（描述、工具、参数）
    - 执行结果（成功/失败、输出、错误）
    - 时间信息（时间戳、耗时）
    """
    # 步骤信息
    step_id: int
    description: str = ""
    tool_name: str
    tool_args: dict[str, Any] = {}
    
    # 执行结果
    success: bool
    result: Any | None = None
    error: str | None = None
    
    # 时间信息
    timestamp: float
    duration_ms: float | None = None
    
    def to_summary(self) -> str:
        """生成执行摘要"""
        status = "✅ 成功" if self.success else "❌ 失败"
        return f"[步骤{self.step_id}] {self.description} - {status} ({self.duration_ms:.1f}ms)"


class Executor:
    """
    执行器 - 负责执行计划中的每个步骤
    
    职责：
    1. 调用工具执行任务步骤
    2. 记录执行结果
    3. 处理执行错误
    4. 更新步骤状态
    """
    
    def __init__(self, tool_registry: ToolRegistry):
        """
        初始化执行器
        
        Args:
            tool_registry: 工具注册表
        """
        self.tool_registry: ToolRegistry = tool_registry
        self.execution_history: list[ExecutionHistoryRecord] = []
    
    def execute_step(self, step: TaskStep) -> ExecutionResult:
        """
        执行单个步骤
        
        Args:
            step: 要执行的步骤
            
        Returns:
            ExecutionResult: 执行结果
        """
        # 检查工具是否存在
        if not self._check_tool_exists(step.tool_name):
            result = ExecutionResult(
                step_id=step.step_id,
                success=False,
                error=f"工具 '{step.tool_name}' 不存在",
                timestamp=time.time()
            )
            self._record_execution(step, result)
            return result
        
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 调用工具执行
            tool_result = self.tool_registry.execute(
                step.tool_name,
                step.tool_args
            )
            
            # 记录结束时间
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            # 判断执行是否成功
            # 工具返回的结果可能是 dict，检查 success 字段
            if isinstance(tool_result, dict):
                success = tool_result.get("success", True)
                error_msg = tool_result.get("error") if not success else None
            else:
                success = True
                error_msg = None
            
            # 创建执行结果
            result = ExecutionResult(
                step_id=step.step_id,
                success=success,
                result=tool_result,
                error=error_msg,
                duration_ms=duration_ms,
                timestamp=end_time
            )
            
        except Exception as e:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            result = ExecutionResult(
                step_id=step.step_id,
                success=False,
                error=f"工具执行异常: {str(e)}",
                duration_ms=duration_ms,
                timestamp=end_time
            )
        
        # 记录执行历史
        self._record_execution(step, result)
        
        return result
    
    def execute_plan(
        self,
        plan: ExecutionPlan,
        step_callback: Callable[[TaskStep, ExecutionResult], None] | None = None,
        stop_on_failure: bool = True
    ) -> ExecutionPlan:
        """
        执行整个计划
        
        Args:
            plan: 执行计划
            step_callback: 步骤完成回调函数
            stop_on_failure: 是否在失败时停止
            
        Returns:
            ExecutionPlan: 更新后的计划
        """
        # 遍历计划中的步骤
        for step in plan.steps:
            # 跳过已完成的步骤
            if step.status == TaskStatus.COMPLETED:
                continue
            
            # 更新步骤状态为执行中
            step.status = TaskStatus.EXECUTING
            
            # 执行步骤
            result = self.execute_step(step)
            
            # 更新步骤状态和结果
            if result.success:
                step.status = TaskStatus.COMPLETED
                step.result = result.result
            else:
                step.status = TaskStatus.FAILED
                step.error = result.error
            
            # 调用回调函数
            if step_callback:
                step_callback(step, result)
            
            # 如果失败且设置为失败时停止，则中断执行
            if not result.success and stop_on_failure:
                break
        
        # 更新计划的当前步骤索引
        for i, step in enumerate(plan.steps):
            if step.status != TaskStatus.COMPLETED:
                plan.current_step_index = i
                break
        else:
            plan.current_step_index = len(plan.steps)
        
        return plan
    
    def _check_tool_exists(self, tool_name: str) -> bool:
        """
        检查工具是否存在
        
        Args:
            tool_name: 工具名称
            
        Returns:
            bool: 是否存在
        """
        return self.tool_registry.has_tool(tool_name)
    
    def _record_execution(self, step: TaskStep, result: ExecutionResult):
        """
        记录执行历史
        
        Args:
            step: 执行的步骤
            result: 执行结果
        """
        # 创建完整的历史记录
        record = ExecutionHistoryRecord(
            step_id=step.step_id,
            description=step.description,
            tool_name=step.tool_name,
            tool_args=step.tool_args,
            success=result.success,
            result=result.result,
            error=result.error,
            timestamp=result.timestamp or time.time(),
            duration_ms=result.duration_ms
        )
        self.execution_history.append(record)
    
    def get_execution_history(self) -> list[ExecutionHistoryRecord]:
        """
        获取执行历史
        
        Returns:
            list: 执行历史记录列表
        """
        return self.execution_history
    
    def get_last_execution(self) -> ExecutionHistoryRecord | None:
        """
        获取最后一次执行结果
        
        Returns:
            ExecutionHistoryRecord | None: 最后一次执行记录
        """
        if self.execution_history:
            return self.execution_history[-1]
        return None
    
    def clear_history(self):
        """清空执行历史"""
        self.execution_history.clear()
    
    def get_statistics(self) -> dict[str, Any]:
        """
        获取执行统计信息
        
        Returns:
            dict: 统计信息
        """
        if not self.execution_history:
            return {
                "total_executions": 0,
                "successful": 0,
                "failed": 0,
                "total_duration_ms": 0,
                "average_duration_ms": 0
            }
        
        total = len(self.execution_history)
        successful = sum(1 for r in self.execution_history if r.success)
        failed = total - successful
        total_duration = sum(r.duration_ms or 0 for r in self.execution_history)
        
        return {
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "total_duration_ms": total_duration,
            "average_duration_ms": total_duration / total if total > 0 else 0
        }
    
    def retry_step(self, step: TaskStep, max_retries: int = 3) -> ExecutionResult:
        """
        重试执行步骤
        
        Args:
            step: 要重试的步骤
            max_retries: 最大重试次数
            
        Returns:
            ExecutionResult: 执行结果
        """
        last_result = None
        
        for attempt in range(max_retries):
            print(f"重试步骤 {step.step_id} (尝试 {attempt + 1}/{max_retries})...")
            
            result = self.execute_step(step)
            
            if result.success:
                return result
            
            last_result = result
            
            # 如果是工具不存在的错误，不再重试
            if "不存在" in (result.error or ""):
                break
        
        return last_result or ExecutionResult(
            step_id=step.step_id,
            success=False,
            error="重试次数已用尽"
        )
