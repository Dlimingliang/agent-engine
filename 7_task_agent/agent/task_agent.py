import json
import os
import sys
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# 添加项目根目录到 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools import ToolRegistry
from .planner import Planner, ExecutionPlan, TaskStep
from .executor import Executor
from .verifier import Verifier
from state import TaskTracker, TaskStatus
from recovery import RetryHandler, ErrorRecovery, RetryPolicy

load_dotenv()


class TaskResult(BaseModel):
    """任务执行结果"""
    success: bool
    message: str
    details: Optional[dict] = None


class TaskAgent:
    """
    Task Agent - 具备任务执行能力的 Agent
    
    核心能力：
    1. 任务计划生成
    2. 分步执行
    3. 结果验证
    4. 失败恢复
    5. 状态追踪
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        tool_registry: ToolRegistry,
        max_retries: int = 3
    ):
        """
        初始化 Task Agent
        
        Args:
            name: Agent 名称
            role: Agent 角色
            system_prompt: 系统提示词
            tool_registry: 工具注册表
            max_retries: 最大重试次数
        """
        # 基本参数
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.tool_registry = tool_registry
        self.max_retries = max_retries

        # LLM 配置
        self.model = os.getenv("LLM_MODEL_ID")
        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("LLM_BASE_URL")
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=60)

        # 规划、执行、验证、重试、回复处理器
        self.planner = Planner(self.model, self.client)
        self.executor = Executor(self.tool_registry)
        self.verifier = Verifier()
        self.retry_handler = RetryHandler(self.max_retries)
        self.error_recovery = ErrorRecovery(self.client,self.tool_registry)

        # 初始化状态管理
        self.task_tracker = TaskTracker(task_id=TaskTracker.generate_task_id())
        self.message = []



    
    def process(self, task: str, session_id: Optional[str] = None) -> TaskResult:
        """
        处理任务
        
        Args:
            task: 任务描述
            session_id: 会话 ID
            
        Returns:
            TaskResult: 任务执行结果
        """
        # 1. 生成 session_id（如果没有）
        if session_id is None:
            session_id = TaskTracker.generate_task_id()
        
        try:
            # 2. 更新任务状态为 PLANNING
            self.task_tracker.update_overall_status(TaskStatus.PLANNING, "开始规划任务")
            self.task_tracker.task_description = task
            
            # 3. 调用 Planner 生成执行计划
            print(f"🧠 Planner 正在生成执行计划...")
            plan = self._plan(task)
            print(f"✅ 计划生成成功，共 {len(plan.steps)} 个步骤")
            
            # 显示计划步骤
            for step in plan.steps:
                print(f"  步骤 {step.step_id}: {step.description} (工具: {step.tool_name})")
            
            # 4. 执行计划
            result = self._execute_plan(plan)
            
            return result
            
        except Exception as e:
            self.task_tracker.update_overall_status(TaskStatus.FAILED, str(e))
            
            return TaskResult(
                success=False,
                message=f"任务执行失败: {str(e)}",
                details={"error": str(e)}
            )

    def _plan(self, task: str) -> ExecutionPlan:
        """
        生成执行计划
        
        Args:
            task: 任务描述
            
        Returns:
            ExecutionPlan: 执行计划
        """
        # 1. 获取可用工具的完整 schema
        tools_schema = self.tool_registry.get_openai_tools()
        
        # 2. 调用 Planner.create_plan
        plan = self.planner.create_plan(task, tools_schema)
        
        # 3. 更新任务状态
        self.task_tracker.update_overall_status(TaskStatus.EXECUTING, "计划生成完成，开始执行")
        
        # 4. 初始化步骤状态
        for step in plan.steps:
            self.task_tracker.update_step_status(
                step.step_id,
                TaskStatus.PENDING,
                None,
                None
            )
        
        return plan
    
    def _execute_plan(self, plan: ExecutionPlan) -> TaskResult:
        """
        执行计划
        
        Args:
            plan: 执行计划
            
        Returns:
            TaskResult: 任务结果
        """
        # 遍历计划中的每个步骤
        while self._should_continue(plan):
            # 获取当前步骤
            current_step = plan.get_current_step()
            if current_step is None:
                break
            
            # 检查步骤状态
            if current_step.status == TaskStatus.COMPLETED:
                # 跳过已完成的步骤
                plan.current_step_index += 1
                continue
            
            print(f"\n执行步骤 {current_step.step_id}/{len(plan.steps)}...")
            
            # 执行步骤
            success, result_or_error = self._execute_step(current_step, plan)
            
            if success:
                # 验证步骤结果
                verification_passed = self._verify_step(current_step, result_or_error)
                
                if verification_passed:
                    print(f"✅ 步骤 {current_step.step_id} 完成")
                    plan.update_step_status(
                        current_step.step_id,
                        TaskStatus.COMPLETED,
                        result=result_or_error
                    )
                    self.task_tracker.update_step_status(
                        current_step.step_id,
                        TaskStatus.COMPLETED,
                        None,
                        result_or_error
                    )
                    plan.current_step_index += 1
                else:
                    print(f"❌ 步骤 {current_step.step_id} 验证失败")
                    plan.update_step_status(
                        current_step.step_id,
                        TaskStatus.FAILED,
                        error="验证失败"
                    )
                    self.task_tracker.update_step_status(
                        current_step.step_id,
                        TaskStatus.FAILED,
                        "验证失败",
                        None
                    )
                    # 处理失败
                    recovery_action, new_plan = self._handle_failure(
                        current_step, 
                        Exception("验证失败"),
                        plan
                    )
                    
                    if recovery_action == "retry":
                        # 重试当前步骤
                        continue
                    elif recovery_action == "replan" and new_plan:
                        # 使用新计划
                        plan = new_plan
                    elif recovery_action == "skip":
                        # 跳过当前步骤
                        plan.current_step_index += 1
                    else:
                        # 其他情况,停止执行
                        break
            else:
                print(f"❌ 步骤 {current_step.step_id} 失败: {result_or_error}")
                plan.update_step_status(
                    current_step.step_id,
                    TaskStatus.FAILED,
                    error=str(result_or_error)
                )
                self.task_tracker.update_step_status(
                    current_step.step_id,
                    TaskStatus.FAILED,
                    str(result_or_error),
                    None
                )
                
                # 处理失败
                recovery_action, new_plan = self._handle_failure(
                    current_step,
                    result_or_error,
                    plan
                )
                
                if recovery_action == "retry":
                    # 重试当前步骤
                    continue
                elif recovery_action == "replan" and new_plan:
                    # 使用新计划
                    plan = new_plan
                elif recovery_action == "skip":
                    # 跳过当前步骤
                    plan.current_step_index += 1
                else:
                    # 其他情况,停止执行
                    break
        
        # 构建最终结果
        success = plan.is_completed()
        result = self._build_final_result(plan, success)
        
        # 更新任务状态
        if success:
            self.task_tracker.update_overall_status(TaskStatus.COMPLETED, "任务完成")
        else:
            self.task_tracker.update_overall_status(TaskStatus.FAILED, "任务失败")
        
        return result
    
    def _execute_step(
        self,
        step: TaskStep,
        plan: ExecutionPlan
    ) -> tuple[bool, Any]:
        """
        执行单个步骤
        
        Args:
            step: 任务步骤
            plan: 执行计划
            
        Returns:
            tuple[bool, Any]: (是否成功, 结果或错误)
        """
        # 标记步骤开始
        self.task_tracker.mark_step_started(step.step_id)
        step.status = TaskStatus.EXECUTING
        
        try:
            # 调用 Executor.execute_step
            result = self.executor.execute_step(step)
            
            # 返回执行结果
            if result.success:
                return True, result.result
            else:
                return False, Exception(result.error or "执行失败")
                
        except Exception as e:
            return False, e
    
    def _verify_step(self, step: TaskStep, result: Any) -> bool:
        """
        验证步骤结果
        
        Args:
            step: 任务步骤
            result: 执行结果
            
        Returns:
            bool: 是否验证通过
        """
        print(f"🔍 正在验证步骤 {step.step_id}...")
        
        # 调用 Verifier.verify
        verification_result = self.verifier.verify(step, result)
        
        if verification_result.success:
            print(f"✅ 验证通过: {verification_result.message}")
            return True
        else:
            print(f"❌ 验证失败: {verification_result.message}")
            if verification_result.suggestions:
                print(f"💡 建议: {', '.join(verification_result.suggestions)}")
            return False
    
    def _handle_failure(
        self,
        step: TaskStep,
        error: Exception,
        plan: ExecutionPlan
    ) -> tuple[str, Optional[ExecutionPlan]]:
        """
        处理步骤失败
        
        Args:
            step: 失败的步骤
            error: 错误信息
            plan: 当前计划
            
        Returns:
            tuple[str, Optional[ExecutionPlan]]: (恢复动作, 新计划)
        """
        # 1. 获取当前重试次数
        current_attempts = self.retry_handler.get_retry_count(step.step_id)
        
        # 2. 调用 RetryHandler 判断重试策略
        strategy = self.retry_handler.should_retry(step, error, current_attempts)
        
        print(f"🔄 恢复策略: {strategy.value}")
        
        # 3. 根据策略执行不同操作
        if strategy.value == "immediate":
            # 立即重试
            self.retry_handler.retry_counts[step.step_id] = current_attempts + 1
            print(f"   立即重试 (尝试 {current_attempts + 1}/{self.max_retries})")
            return "retry", None
            
        elif strategy.value == "delayed":
            # 延迟重试
            import time
            delay = self.retry_handler._get_delay_time(
                current_attempts, 
                RetryPolicy(max_retries=self.max_retries)
            )
            print(f"   延迟重试 (等待 {delay:.1f} 秒)")
            time.sleep(delay)
            self.retry_handler.retry_counts[step.step_id] = current_attempts + 1
            return "retry", None
            
        elif strategy.value == "degraded":
            # 降级重试 - 尝试寻找替代工具
            alternative_tool = self.tool_registry.find_alternative(step.tool_name)
            if alternative_tool:
                print(f"   降级重试: 使用替代工具 '{alternative_tool}'")
                step.tool_name = alternative_tool
                self.retry_handler.retry_counts[step.step_id] = current_attempts + 1
                return "retry", None
            else:
                print(f"   无法找到替代工具，需要重新规划")
                # 改计划
                feedback = f"步骤 {step.step_id} 执行失败: {str(error)}。请重新规划。"
                new_plan = self.planner.update_plan(plan, feedback)
                return "replan", new_plan
                
        else:
            # ABORT - 放弃重试
            print(f"   放弃重试，任务失败")
            return "abort", None
    
    def _should_continue(self, plan: ExecutionPlan) -> bool:
        """
        判断是否应该继续执行
        
        Args:
            plan: 执行计划
            
        Returns:
            bool: 是否继续
        """
        # 1. 检查是否还有待执行的步骤
        has_pending = any(
            step.status == TaskStatus.PENDING for step in plan.steps
        )
        
        # 2. 检查是否有正在执行的步骤
        has_executing = any(
            step.status == TaskStatus.EXECUTING for step in plan.steps
        )
        
        # 3. 检查任务状态是否为终态
        is_terminal = self.task_tracker.is_terminal()
        
        # 4. 如果所有步骤都已完成,也停止
        all_completed = all(
            step.status == TaskStatus.COMPLETED for step in plan.steps
        ) if plan.steps else False
        
        # 5. 返回是否继续
        # 继续条件:有待执行或正在执行的步骤,且不是终态,且不是全部完成
        return (has_pending or has_executing) and not is_terminal and not all_completed

    
    def _build_final_result(self, plan: ExecutionPlan, success: bool) -> TaskResult:
        """
        构建最终结果
        
        Args:
            plan: 执行计划
            success: 是否成功
            
        Returns:
            TaskResult: 任务结果
        """
        # 1. 汇总所有步骤结果
        completed_steps = plan.get_completed_steps()
        failed_steps = plan.get_failed_steps()
        
        # 2. 生成最终消息
        if success:
            message = f"✅ 任务完成！\n"
            message += f"结果: {plan.task_description}\n"
            message += f"共执行 {len(plan.steps)} 个步骤，全部成功。"
        else:
            message = f"❌ 任务失败！\n"
            message += f"原因: {plan.task_description}\n"
            message += f"已完成 {len(completed_steps)}/{len(plan.steps)} 个步骤。\n"
            if failed_steps:
                message += f"失败步骤: {', '.join([f'步骤{s.step_id}' for s in failed_steps])}"
        
        # 3. 构建详细信息
        details = {
            "task_description": plan.task_description,
            "total_steps": len(plan.steps),
            "completed_steps": len(completed_steps),
            "failed_steps": len(failed_steps),
            "steps_detail": [
                {
                    "step_id": step.step_id,
                    "description": step.description,
                    "status": step.status,
                    "result": step.result
                }
                for step in plan.steps
            ]
        }
        
        # 4. 返回 TaskResult
        return TaskResult(
            success=success,
            message=message,
            details=details
        )
    
    def get_task_status(self) -> dict:
        """
        获取任务状态
        
        Returns:
            dict: 任务状态信息
            
        TODO: 返回 TaskTracker 的状态摘要
        """
        return self.task_tracker.get_progress()

    
    def pause_task(self) -> bool:
        """
        暂停任务
        
        Returns:
            bool: 是否成功暂停
            
        TODO: 将任务状态转换为 PAUSED
        """
        return self.task_tracker.update_overall_status(TaskStatus.PAUSED, )
    
    def resume_task(self) -> bool:
        """
        恢复任务
        
        Returns:
            bool: 是否成功恢复
            
        TODO: 将任务状态从 PAUSED 转换为 EXECUTING
        """
        return self.task_tracker.update_overall_status(TaskStatus.EXECUTING, )
    
    def cancel_task(self) -> bool:
        """
        取消任务
        
        Returns:
            bool: 是否成功取消
            
        TODO: 将任务状态转换为 CANCELLED
        """
        return self.task_tracker.update_overall_status(TaskStatus.CANCELLED, "用户取消")
