from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Optional

class MessageRole(str, Enum):
    """
    消息角色枚举
    
    继承 str 和 Enum，可以直接当字符串使用:
        role = MessageRole.USER
        assert role == "user"  # True
    """
    SYSTEM = "system"      # 系统提示词
    USER = "user"          # 用户输入
    ASSISTANT = "assistant"  # 助手回复
    TOOL = "tool"          # 工具执行结果


class ToolCall(BaseModel):
    """工具调用请求 - 模型决定调用工具时返回"""
    id: str = Field(..., description="工具调用唯一ID")
    type: str = Field(default="function", description="调用类型")
    function: dict[str, Any] = Field(..., description="函数调用信息")

    @property
    def name(self) -> str:
        """工具名称"""
        return self.function.get("name", "")

    @property
    def arguments(self) -> dict[str, Any]:
        """工具参数"""
        import json
        args_str = self.function.get("arguments", "{}")
        return json.loads(args_str) if isinstance(args_str, str) else args_str


class Message(BaseModel):
    """
    消息数据结构
    
    不同角色的职责:
    - SYSTEM: 设定 Agent 行为规则、能力边界
    - USER: 用户的问题或指令
    - ASSISTANT: Agent 的思考、回复或工具调用请求
    - TOOL: 工具执行后的结果回填
    """
    role: MessageRole = Field(..., description="消息角色")
    content: Optional[str] = Field(None, description="消息内容")
    tool_calls: Optional[list[ToolCall]] = Field(None, description="工具调用列表(仅assistant)")
    tool_call_id: Optional[str] = Field(None, description="工具调用ID(仅tool消息)")
    name: Optional[str] = Field(None, description="工具名称(仅tool消息)")
    
    def to_openai_dict(self) -> dict[str, Any]:
        """
        转换为 OpenAI API 所需的格式
        
        Returns:
            符合 OpenAI messages 格式的字典
        """
        msg = {"role": self.role.value}
        
        if self.content is not None:
            msg["content"] = self.content
            
        if self.tool_calls:
            msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": tc.function
                }
                for tc in self.tool_calls
            ]
            
        if self.tool_call_id:
            msg["tool_call_id"] = self.tool_call_id
            
        if self.name:
            msg["name"] = self.name
            
        return msg


# === 便捷创建函数 ===

def system_message(content: str) -> Message:
    """创建系统消息"""
    return Message(role=MessageRole.SYSTEM, content=content)


def user_message(content: str) -> Message:
    """创建用户消息"""
    return Message(role=MessageRole.USER, content=content)


def assistant_message(content: Optional[str] = None, tool_calls: Optional[list[ToolCall]] = None) -> Message:
    """创建助手消息"""
    return Message(role=MessageRole.ASSISTANT, content=content, tool_calls=tool_calls)


def tool_message(tool_call_id: str, content: str, name: Optional[str] = None) -> Message:
    """创建工具结果消息"""
    return Message(role=MessageRole.TOOL, content=content, tool_call_id=tool_call_id, name=name)
