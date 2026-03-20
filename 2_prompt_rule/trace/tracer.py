from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class StepType(str, Enum):
    """Trace 步骤类型"""
    USER_INPUT = "user_input"           # 用户输入
    LLM_CALL = "llm_call"               # LLM 调用
    TOOL_CALL = "tool_call"             # 工具调用
    FINAL_OUTPUT = "final_output"       # 最终输出
    ERROR = "error"                     # 错误


class TraceStep(BaseModel):
    """
    单个 Trace 步骤
    """
    step: int = Field(..., description="步骤序号")
    timestamp: str = Field(..., description="时间戳")
    type: StepType = Field(..., description="步骤类型")
    input_data: Optional[Any] = Field(None, description="输入数据")
    output_data: Optional[Any] = Field(None, description="输出数据")
    duration_ms: Optional[int] = Field(None, description="耗时(毫秒)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class Tracer:
    """
    执行追踪器
    
    记录 Agent 执行的每一步，支持保存到文件
    """
    
    def __init__(self, session_id: str | None = None):
        """
        初始化 Tracer
        
        Args:
            session_id: 会话ID(可选)
        """
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.steps: list[TraceStep] = []
        self._start_time: float | None = None
    
    def start_timer(self):
        """开始计时"""
        self._start_time = datetime.now().timestamp()
    
    def _get_duration_ms(self) -> int | None:
        """获取耗时(毫秒)"""
        if self._start_time is None:
            return None
        duration = (datetime.now().timestamp() - self._start_time) * 1000
        self._start_time = None
        return int(duration)
    
    def log(
        self,
        step_type: StepType,
        input_data: Any = None,
        output_data: Any = None,
        metadata: dict[str, Any] | None = None,
        duration_ms: int | None = None
    ) -> TraceStep:
        """
        记录一个步骤
        
        Args:
            step_type: 步骤类型
            input_data: 输入数据
            output_data: 输出数据
            metadata: 元数据
            duration_ms: 耗时(如未提供,会自动计算)
            
        Returns:
            TraceStep 对象
        """
        step = TraceStep(
            step=len(self.steps) + 1,
            timestamp=datetime.now().isoformat(),
            type=step_type,
            input_data=input_data,
            output_data=output_data,
            duration_ms=duration_ms or self._get_duration_ms(),
            metadata=metadata or {}
        )
        self.steps.append(step)
        return step
    
    def log_user_input(self, content: str) -> TraceStep:
        """记录用户输入"""
        return self.log(StepType.USER_INPUT, input_data=content)
    
    def log_llm_call(
        self,
        messages: list[dict],
        response: str,
        duration_ms: int | None = None
    ) -> TraceStep:
        """记录 LLM 调用"""
        return self.log(
            StepType.LLM_CALL,
            input_data={"message_count": len(messages)},
            output_data=response,
            duration_ms=duration_ms
        )
    
    def log_tool_call(
        self,
        tool_name: str,
        arguments: dict,
        result: str,
        duration_ms: int | None = None
    ) -> TraceStep:
        """记录工具调用"""
        return self.log(
            StepType.TOOL_CALL,
            input_data={"tool": tool_name, "arguments": arguments},
            output_data=result,
            duration_ms=duration_ms
        )
    
    def log_final_output(self, content: str) -> TraceStep:
        """记录最终输出"""
        return self.log(StepType.FINAL_OUTPUT, output_data=content)
    
    def log_error(self, error: str, metadata: dict | None = None) -> TraceStep:
        """记录错误"""
        return self.log(StepType.ERROR, output_data=error, metadata=metadata)

    
    def summary(self) -> str:
        """
        生成摘要
        
        Returns:
            可读的摘要字符串
        """
        lines = [
            f"=== Trace Summary ===",
            f"Session ID: {self.session_id}",
            f"Total Steps: {len(self.steps)}",
            ""
        ]
        
        for step in self.steps:
            duration = f" [{step.duration_ms}ms]" if step.duration_ms else ""
            lines.append(f"Step {step.step}: {step.type.value}{duration}")
            if step.input_data:
                lines.append(f"  Input: {step.input_data}")
            if step.output_data:
                output = str(step.output_data)[:100]
                lines.append(f"  Output: {output}...")
        
        return "\n".join(lines)
