from typing import Any
from pydantic import BaseModel


class Tool(BaseModel):
    """
    工具基类
    
    所有工具都应该继承此类并实现 execute 方法
    """
    name: str
    description: str
    parameters_schema: dict = {}
    
    def execute(self, **kwargs) -> Any:
        """
        执行工具
        
        Args:
            **kwargs: 工具参数
            
        Returns:
            Any: 执行结果
            
        Raises:
            NotImplementedError: 子类必须实现此方法
        """
        raise NotImplementedError("子类必须实现 execute 方法")
    
    def get_openai_tool_schema(self) -> dict:
        """
        获取 OpenAI 工具 schema
        
        Returns:
            dict: OpenAI 工具 schema
            
        生成 OpenAI 格式的工具定义：
        {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema
            }
        }
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema
            }
        }


class ToolRegistry:
    """
    工具注册表
    
    职责：
    1. 注册和管理工具
    2. 查询工具信息
    3. 执行工具调用
    4. 提供 OpenAI 工具列表
    """
    
    def __init__(self):
        """
        初始化工具注册表
        """
        self._tools: dict[str, Tool] = {}
    
    def register(self, tool: Tool):
        """
        注册工具
        
        Args:
            tool: 工具实例
        """
        if tool.name in self._tools:
            print(f"警告: 工具 '{tool.name}' 已存在，将被覆盖")
        self._tools[tool.name] = tool
    
    def unregister(self, tool_name: str) -> bool:
        """
        注销工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            bool: 是否成功注销
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
            return True
        return False
    
    def get_tool(self, tool_name: str) -> Tool | None:
        """
        获取工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            Tool | None: 工具实例，不存在则返回 None
        """
        return self._tools.get(tool_name)
    
    def has_tool(self, tool_name: str) -> bool:
        """
        检查工具是否存在
        
        Args:
            tool_name: 工具名称
            
        Returns:
            bool: 是否存在
        """
        return tool_name in self._tools
    
    def execute(self, tool_name: str, arguments: dict) -> Any:
        """
        执行工具
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            Any: 执行结果
            
        Raises:
            ValueError: 工具不存在
        """
        tool = self.get_tool(tool_name)
        if tool is None:
            raise ValueError(f"工具 '{tool_name}' 不存在")
        
        try:
            return tool.execute(**arguments)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            }
    
    def get_all_tools(self) -> list[Tool]:
        """
        获取所有工具
        
        Returns:
            list[Tool]: 工具列表
        """
        return list(self._tools.values())
    
    def get_tool_names(self) -> list[str]:
        """
        获取所有工具名称
        
        Returns:
            list[str]: 工具名称列表
        """
        return list(self._tools.keys())
    
    def get_openai_tools(self) -> list[dict]:
        """
        获取 OpenAI 工具列表
        
        Returns:
            list[dict]: OpenAI 工具 schema 列表
        """
        return [tool.get_openai_tool_schema() for tool in self._tools.values()]
    
    def find_alternative(self, tool_name: str) -> str | None:
        """
        查找替代工具
        
        Args:
            tool_name: 原工具名称
            
        Returns:
            str | None: 替代工具名称
        """
        # 定义替代工具映射
        alternatives = {
            "calculator": ["math_eval", "compute"],
            "file_read": ["read_file", "cat"],
            "file_write": ["write_file", "save_file"],
            "web_search": ["search", "google_search"],
            "web_fetch": ["fetch", "http_get"]
        }
        
        # 查找替代工具
        if tool_name in alternatives:
            for alt_name in alternatives[tool_name]:
                if alt_name in self._tools:
                    return alt_name
        
        # 尝试模糊匹配
        for name in self._tools.keys():
            if tool_name.lower() in name.lower() or name.lower() in tool_name.lower():
                return name
        
        return None
    
    def get_tools_by_category(self, category: str) -> list[Tool]:
        """
        按类别获取工具
        
        Args:
            category: 工具类别
            
        Returns:
            list[Tool]: 该类别的工具列表
        """
        # 定义类别映射
        category_mapping = {
            "math": ["calculator"],
            "file": ["file_read", "file_write"],
            "web": ["web_search", "web_fetch"],
            "io": ["file_read", "file_write"]
        }
        
        if category not in category_mapping:
            return []
        
        tools = []
        for tool_name in category_mapping[category]:
            tool = self.get_tool(tool_name)
            if tool:
                tools.append(tool)
        
        return tools
