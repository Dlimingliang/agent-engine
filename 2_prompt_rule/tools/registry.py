from typing import Callable, Any
from pydantic import BaseModel, Field


class Tool(BaseModel):
    """
    工具定义
    
    包含工具的元信息和执行函数
    """
    name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")
    parameters: dict[str, Any] = Field(..., description="参数 JSON Schema")
    func: Callable = Field(..., description="执行函数", exclude=True)  # 不序列化
    
    def to_openai_schema(self) -> dict[str, Any]:
        """
        转换为 OpenAI tools 格式
        
        Returns:
            OpenAI API 所需的工具 schema
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    def execute(self, **kwargs) -> str:
        """
        执行工具
        
        Args:
            **kwargs: 工具参数
            
        Returns:
            工具执行结果(字符串格式)
        """
        try:
            result = self.func(**kwargs)
            # 确保返回字符串
            if isinstance(result, str):
                return result
            import json
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return f"工具执行错误: {str(e)}"

class ToolRegistry:
    """
    工具注册中心
    
    管理所有可用工具，支持注册、查询、执行
    """
    
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    
    def register(self, name: str, description: str, parameters: dict[str, Any], func: Callable):
        """
        注册工具
        
        Args:
            name: 工具名称
            description: 工具描述
            parameters: 参数 JSON Schema
            func: 执行函数
        """
        tool = Tool(
            name=name,
            description=description,
            parameters=parameters,
            func=func
        )
        self._tools[name] = tool
    
    def get(self, name: str) -> Tool | None:
        """获取工具"""
        return self._tools.get(name)
    
    def execute(self, name: str, arguments: dict[str, Any]) -> str:
        """
        执行工具
        
        Args:
            name: 工具名称
            arguments: 工具参数
            
        Returns:
            执行结果
            
        Raises:
            ValueError: 工具不存在
        """
        tool = self.get(name)
        if not tool:
            return f"错误: 工具 '{name}' 不存在"
        return tool.execute(**arguments)
    
    def get_openai_tools(self) -> list[dict[str, Any]]:
        """
        获取所有工具的 OpenAI schema
        
        Returns:
            OpenAI API 所需的 tools 列表
        """
        return [tool.to_openai_schema() for tool in self._tools.values()]
    
    def list_tools(self) -> list[str]:
        """列出所有工具名称"""
        return list(self._tools.keys())
    
    def __contains__(self, name: str) -> bool:
        """支持 `name in registry` 语法"""
        return name in self._tools
