import sys
import json
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field
from datetime import datetime

# 添加项目根目录到 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from state.task_state import TaskStatus


class TaskStep(BaseModel):
    """
    单个任务步骤
    
    属性：
    - step_id: 步骤编号
    - description: 步骤描述
    - tool_name: 使用的工具名称
    - tool_args: 工具参数
    - expected_output: 预期输出描述
    - status: 步骤状态
    - result: 执行结果
    - error: 错误信息
    - dependencies: 依赖的步骤ID列表
    """
    step_id: int
    description: str
    tool_name: str
    tool_args: dict[str, Any] = Field(default_factory=dict)
    expected_output: str = ""
    status: TaskStatus = TaskStatus.PENDING
    result: dict[str, Any] | None = None
    error: str | None = None
    dependencies: list[int] = Field(default_factory=list)
    
    class Config:
        use_enum_values = True


class ExecutionPlan(BaseModel):
    """
    执行计划
    
    属性：
    - task_description: 任务描述
    - steps: 步骤列表
    - created_at: 创建时间
    - updated_at: 更新时间
    - current_step_index: 当前执行到的步骤索引
    """
    task_description: str
    steps: list[TaskStep] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    current_step_index: int = 0
    
    def get_current_step(self) -> TaskStep | None:
        """获取当前步骤"""
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None
    
    def get_step_by_id(self, step_id: int) -> TaskStep | None:
        """根据ID获取步骤"""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def update_step_status(self, step_id: int, status: TaskStatus, result: dict | None = None, error: str | None = None):
        """更新步骤状态"""
        step = self.get_step_by_id(step_id)
        if step:
            step.status = status
            if result:
                step.result = result
            if error:
                step.error = error
            self.updated_at = datetime.now()
    
    def get_completed_steps(self) -> list[TaskStep]:
        """获取已完成的步骤"""
        return [s for s in self.steps if s.status == TaskStatus.COMPLETED]
    
    def get_pending_steps(self) -> list[TaskStep]:
        """获取待执行的步骤"""
        return [s for s in self.steps if s.status == TaskStatus.PENDING]
    
    def get_failed_steps(self) -> list[TaskStep]:
        """获取失败的步骤"""
        return [s for s in self.steps if s.status == TaskStatus.FAILED]
    
    def is_completed(self) -> bool:
        """检查计划是否全部完成"""
        return all(s.status == TaskStatus.COMPLETED for s in self.steps)
    
    def has_failures(self) -> bool:
        """检查是否有失败步骤"""
        return any(s.status == TaskStatus.FAILED for s in self.steps)
    
    def get_progress(self) -> dict[str, Any]:
        """获取进度信息"""
        total = len(self.steps)
        completed = len(self.get_completed_steps())
        failed = len(self.get_failed_steps())
        pending = len(self.get_pending_steps())
        
        return {
            "total_steps": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "progress_percent": (completed / total * 100) if total > 0 else 0,
            "current_step": self.current_step_index + 1
        }


class Planner:
    """
    计划生成器 - 根据任务描述生成结构化执行计划
    
    职责：
    1. 分析任务需求
    2. 生成执行步骤
    3. 为每个步骤选择合适的工具
    4. 支持根据反馈更新计划
    """
    
    def __init__(self, model: str | None = None, llm_client: Any = None):
        """
        初始化计划生成器
        
        Args:
            model: LLM 模型名称
            llm_client: LLM 客户端实例
        """
        self.model = model
        self.llm_client = llm_client
    
    def create_plan(self, task: str, tools_schema: list[dict]) -> ExecutionPlan:
        """
        生成执行计划
        
        Args:
            task: 任务描述
            tools_schema: 可用工具的 schema 列表
            
        Returns:
            ExecutionPlan: 生成的执行计划
            
        如果有 LLM 客户端，使用 LLM 生成计划；
        否则使用基于规则的简单规划
        """
        if self.llm_client:
            return self._create_plan_with_llm(task, tools_schema)
        else:
            return self._create_plan_with_rules(task, tools_schema)
    
    def update_plan(self, plan: ExecutionPlan, feedback: str) -> ExecutionPlan:
        """
        根据反馈更新计划
        
        Args:
            plan: 原计划
            feedback: 反馈信息（错误信息、执行结果等）
            
        Returns:
            ExecutionPlan: 更新后的计划
        """
        if self.llm_client:
            return self._update_plan_with_llm(plan, feedback)
        else:
            return self._update_plan_with_rules(plan, feedback)
    
    def _create_plan_with_llm(self, task: str, tools_schema: list[dict]) -> ExecutionPlan:
        """
        使用 LLM 生成计划
        
        Args:
            task: 任务描述
            tools_schema: 可用工具的 schema 列表
            
        Returns:
            ExecutionPlan: 执行计划
        """
        prompt = f"""
你是一个任务规划助手。请将以下任务分解为具体的执行步骤。

任务：{task}

可用工具及其参数：
{json.dumps(tools_schema, indent=2, ensure_ascii=False)}

请按以下 JSON 格式输出执行计划：
{{
    "steps": [
        {{
            "step_id": 1,
            "description": "步骤描述",
            "tool_name": "工具名称",
            "tool_args": {{}},
            "expected_output": "预期输出描述",
            "dependencies": []
        }}
    ]
}}

重要提示：
1. 每个步骤应该是一个原子操作
2. tool_name 必须是可用工具之一
3. **tool_args 必须包含工具所需的所有必需参数**，参数名称和类型必须与工具 schema 中定义的完全一致
4. 步骤之间可以有依赖关系
5. 步骤数量控制在 3-10 步之间
6. **确保为每个工具提供正确的参数值**，例如：
   - calculator 工具需要 expression 参数
   - file_write 工具需要 file_path 和 content 参数
   - file_read 工具需要 file_path 参数
   - web_search 工具需要 query 参数
   - web_fetch 工具需要 url 参数
"""
        
        try:
            # 调用 LLM
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            # 解析响应
            content = response.choices[0].message.content
            plan_data = self._parse_llm_response(content)
            
            # 创建 ExecutionPlan
            steps = [
                TaskStep(**step_data)
                for step_data in plan_data.get("steps", [])
            ]
            
            return ExecutionPlan(
                task_description=task,
                steps=steps
            )
        except Exception as e:
            print(f"LLM 生成计划失败: {e}")
            # 降级到规则规划
            return self._create_plan_with_rules(task, tools_schema)
    
    def _create_plan_with_rules(self, task: str, tools_schema: list[dict]) -> ExecutionPlan:
        """
        使用基于规则的简单规划
        
        Args:
            task: 任务描述
            tools_schema: 可用工具的 schema 列表
            
        Returns:
            ExecutionPlan: 执行计划
        """
        steps = []
        step_id = 1
        
        # 简单的关键词匹配规则
        task_lower = task.lower()
        
        # 检测是否包含计算相关
        if any(kw in task_lower for kw in ['计算', '算', 'calculate', 'math', '求']):
            # 提取斐波那契相关的表达式
            import re
            fib_match = re.search(r'斐波那契.*?第\s*(\d+)\s*项', task)
            if fib_match:
                n = fib_match.group(1)
                # 斐波那契数列第n项的近似公式
                expression = f"int(((1 + sqrt(5)) / 2) ** {n} / sqrt(5) + 0.5)"
            else:
                expression = "1 + 1"  # 默认简单表达式
            
            steps.append(TaskStep(
                step_id=step_id,
                description="执行计算操作",
                tool_name="calculator",
                tool_args={"expression": expression},
                expected_output="计算结果"
            ))
            step_id += 1
        
        # 检测是否包含文件操作
        if any(kw in task_lower for kw in ['文件', 'file', '读取', 'read', '写入', 'write', '保存', 'save']):
            if '读' in task_lower or 'read' in task_lower:
                steps.append(TaskStep(
                    step_id=step_id,
                    description="读取文件内容",
                    tool_name="file_read",
                    tool_args={"file_path": "待确定的文件路径"},
                    expected_output="文件内容"
                ))
                step_id += 1
            
            if '写' in task_lower or '保存' in task_lower or 'write' in task_lower or 'save' in task_lower:
                steps.append(TaskStep(
                    step_id=step_id,
                    description="写入文件",
                    tool_name="file_write",
                    tool_args={"file_path": "待确定的文件路径", "content": "待确定的内容"},
                    expected_output="写入成功"
                ))
                step_id += 1
        
        # 检测是否包含网络操作
        if any(kw in task_lower for kw in ['搜索', 'search', '查找', 'find', '网页', 'web']):
            steps.append(TaskStep(
                step_id=step_id,
                description="执行网页搜索",
                tool_name="web_search",
                tool_args={"query": "待确定的搜索关键词"},
                expected_output="搜索结果列表"
            ))
            step_id += 1
        
        if any(kw in task_lower for kw in ['抓取', 'fetch', '获取网页', '访问']):
            steps.append(TaskStep(
                step_id=step_id,
                description="抓取网页内容",
                tool_name="web_fetch",
                tool_args={"url": "待确定的URL"},
                expected_output="网页内容"
            ))
            step_id += 1
        
        # 如果没有匹配到任何规则，创建一个通用步骤
        if not steps:
            # 从 tools_schema 中获取第一个工具
            first_tool = tools_schema[0] if tools_schema else None
            tool_name = first_tool["function"]["name"] if first_tool else "unknown"
            
            steps.append(TaskStep(
                step_id=1,
                description=f"执行任务: {task}",
                tool_name=tool_name,
                tool_args={},
                expected_output="任务执行结果"
            ))
        
        return ExecutionPlan(
            task_description=task,
            steps=steps
        )
    
    def _update_plan_with_llm(self, plan: ExecutionPlan, feedback: str) -> ExecutionPlan:
        """
        使用 LLM 更新计划
        
        Args:
            plan: 原计划
            feedback: 反馈信息
            
        Returns:
            ExecutionPlan: 更新后的计划
        """
        prompt = f"""
当前执行计划：
{json.dumps(plan.model_dump(), indent=2, ensure_ascii=False)}

反馈信息：
{feedback}

请根据反馈信息调整执行计划。输出格式与创建计划相同。
"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            plan_data = self._parse_llm_response(content)
            
            steps = [
                TaskStep(**step_data)
                for step_data in plan_data.get("steps", [])
            ]
            
            plan.steps = steps
            plan.updated_at = datetime.now()
            
            return plan
        except Exception as e:
            print(f"LLM 更新计划失败: {e}")
            return plan
    
    def _update_plan_with_rules(self, plan: ExecutionPlan, feedback: str) -> ExecutionPlan:
        """
        使用基于规则的计划更新
        
        Args:
            plan: 原计划
            feedback: 反馈信息
            
        Returns:
            ExecutionPlan: 更新后的计划
        """
        # 简单的规则：如果反馈包含错误，重置失败步骤的状态
        feedback_lower = feedback.lower()
        
        if '错误' in feedback or 'error' in feedback_lower or '失败' in feedback:
            for step in plan.steps:
                if step.status == TaskStatus.FAILED:
                    step.status = TaskStatus.PENDING
                    step.error = None
        
        plan.updated_at = datetime.now()
        return plan
    
    def _parse_llm_response(self, content: str) -> dict:
        """
        解析 LLM 响应内容
        
        Args:
            content: LLM 返回的内容
            
        Returns:
            dict: 解析后的字典
        """
        # 尝试提取 JSON
        try:
            # 尝试直接解析
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # 尝试从 markdown 代码块中提取
        if "```json" in content:
            start = content.index("```json") + 7
            end = content.index("```", start)
            json_str = content[start:end].strip()
            return json.loads(json_str)
        elif "```" in content:
            start = content.index("```") + 3
            end = content.index("```", start)
            json_str = content[start:end].strip()
            return json.loads(json_str)
        
        # 无法解析，返回空字典
        return {"steps": []}
