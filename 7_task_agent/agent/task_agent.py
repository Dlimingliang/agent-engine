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
from .planner import Planner, ExecutionPlan
from .executor import Executor
from .verifier import Verifier
from state import TaskTracker, TaskStatus
from recovery import RetryHandler, ErrorRecovery
from trace import Tracer

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
        # TODO: 初始化基础属性
        # - name, role, system_prompt
        # - tool_registry
        # - max_retries
        
        # TODO: 初始化 LLM 客户端
        # - 从环境变量读取配置
        # - 创建 OpenAI 客户端
        
        # TODO: 初始化核心组件
        # - Planner: 计划生成器
        # - Executor: 执行器
        # - Verifier: 验证器
        # - RetryHandler: 重试处理器
        # - ErrorRecovery: 错误恢复处理器
        
        # TODO: 初始化状态管理
        # - TaskTracker: 任务跟踪器
        # - messages: 消息历史
        
        pass
    
    def process(self, task: str, session_id: Optional[str] = None) -> TaskResult:
        """
        处理任务
        
        Args:
            task: 任务描述
            session_id: 会话 ID
            
        Returns:
            TaskResult: 任务执行结果
            
        TODO:
        1. 生成 session_id（如果没有）
        2. 初始化 Tracer
        3. 记录用户输入
        4. 调用 Planner 生成执行计划
        5. 执行计划-执行循环
        6. 返回最终结果
        """
        pass
    
    def _plan(self, task: str) -> ExecutionPlan:
        """
        生成执行计划
        
        Args:
            task: 任务描述
            
        Returns:
            ExecutionPlan: 执行计划
            
        TODO:
        1. 获取可用工具列表
        2. 调用 Planner.create_plan
        3. 更新任务状态为 PLANNING
        4. 返回计划
        """
        pass
    
    def _execute_plan(self, plan: ExecutionPlan, tracer: Tracer) -> TaskResult:
        """
        执行计划
        
        Args:
            plan: 执行计划
            tracer: 追踪器
            
        Returns:
            TaskResult: 任务结果
            
        TODO:
        1. 更新任务状态为 EXECUTING
        2. 遍历计划中的每个步骤
        3. 执行步骤 -> 验证结果 -> 处理失败
        4. 更新任务状态
        5. 返回最终结果
        """
        pass
    
    def _execute_step(
        self,
        step,
        plan: ExecutionPlan,
        tracer: Tracer
    ) -> tuple[bool, Any]:
        """
        执行单个步骤
        
        Args:
            step: 任务步骤
            plan: 执行计划
            tracer: 追踪器
            
        Returns:
            tuple[bool, Any]: (是否成功, 结果或错误)
            
        TODO:
        1. 调用 Executor.execute_step
        2. 记录执行日志
        3. 如果成功，调用 Verifier 验证
        4. 如果失败或验证失败，调用重试逻辑
        5. 返回执行结果
        """
        pass
    
    def _verify_step(self, step, result: Any, tracer: Tracer) -> bool:
        """
        验证步骤结果
        
        Args:
            step: 任务步骤
            result: 执行结果
            tracer: 追踪器
            
        Returns:
            bool: 是否验证通过
            
        TODO:
        1. 调用 Verifier.verify
        2. 记录验证结果
        3. 返回是否通过
        """
        pass
    
    def _handle_failure(
        self,
        step,
        error: Exception,
        plan: ExecutionPlan,
        tracer: Tracer
    ) -> tuple[str, Optional[ExecutionPlan]]:
        """
        处理步骤失败
        
        Args:
            step: 失败的步骤
            error: 错误信息
            plan: 当前计划
            tracer: 追踪器
            
        Returns:
            tuple[str, Optional[ExecutionPlan]]: (恢复动作, 新计划)
            
        TODO:
        1. 调用 RetryHandler 判断重试策略
        2. 如果可以重试，返回 "retry"
        3. 如果需要改计划，调用 Planner.update_plan
        4. 如果需要人工介入，返回 "human"
        5. 记录失败处理日志
        """
        pass
    
    def _should_continue(self, plan: ExecutionPlan) -> bool:
        """
        判断是否应该继续执行
        
        Args:
            plan: 执行计划
            
        Returns:
            bool: 是否继续
            
        TODO:
        1. 检查是否还有待执行的步骤
        2. 检查任务状态是否为终态
        3. 返回是否继续
        """
        pass
    
    def _build_final_result(self, plan: ExecutionPlan, success: bool) -> TaskResult:
        """
        构建最终结果
        
        Args:
            plan: 执行计划
            success: 是否成功
            
        Returns:
            TaskResult: 任务结果
            
        TODO:
        1. 汇总所有步骤结果
        2. 生成最终消息
        3. 构建详细信息
        4. 返回 TaskResult
        """
        pass
    
    def get_task_status(self) -> dict:
        """
        获取任务状态
        
        Returns:
            dict: 任务状态信息
            
        TODO: 返回 TaskTracker 的状态摘要
        """
        pass
    
    def pause_task(self) -> bool:
        """
        暂停任务
        
        Returns:
            bool: 是否成功暂停
            
        TODO: 将任务状态转换为 PAUSED
        """
        pass
    
    def resume_task(self) -> bool:
        """
        恢复任务
        
        Returns:
            bool: 是否成功恢复
            
        TODO: 将任务状态从 PAUSED 转换为 EXECUTING
        """
        pass
    
    def cancel_task(self) -> bool:
        """
        取消任务
        
        Returns:
            bool: 是否成功取消
            
        TODO: 将任务状态转换为 CANCELLED
        """
        pass
