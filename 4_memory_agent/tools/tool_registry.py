"""
@generated-by AI: matthewmli
@generated-date 2026-03-23
"""
from typing import Dict, List, Any, Optional
from .base import BaseTool


class ToolRegistry:
    """工具注册器"""
    
    def __init__(self):
        """初始化工具注册器"""
        # === AI Generated Code Start matthewmli===
        self._tools: Dict[str, BaseTool] = {}
        # === AI Generated Code End matthewmli===
    
    def register(self, tool: BaseTool):
        """
        注册工具
        
        Args:
            tool: 工具实例
        """
        # === AI Generated Code Start matthewmli===
        self._tools[tool.name] = tool
        # === AI Generated Code End matthewmli===
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """
        获取工具
        
        Args:
            name: 工具名称
        
        Returns:
            工具实例
        """
        # === AI Generated Code Start matthewmli===
        return self._tools.get(name)
        # === AI Generated Code End matthewmli===
    
    def get_all_tools(self) -> List[BaseTool]:
        """
        获取所有工具
        
        Returns:
            工具列表
        """
        # === AI Generated Code Start matthewmli===
        return list(self._tools.values())
        # === AI Generated Code End matthewmli===
    
    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """
        获取 OpenAI 格式的工具列表
        
        Returns:
            OpenAI 工具定义列表
        """
        # === AI Generated Code Start matthewmli===
        return [tool.to_openai_tool() for tool in self._tools.values()]
        # === AI Generated Code End matthewmli===
    
    def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        执行工具
        
        Args:
            name: 工具名称
            **kwargs: 工具参数
        
        Returns:
            执行结果
        """
        # === AI Generated Code Start matthewmli===
        tool = self.get_tool(name)
        if not tool:
            return {
                "success": False,
                "error": f"工具 '{name}' 不存在",
                "message": "执行失败"
            }
        try:
            return tool.execute(**kwargs)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "执行失败"
            }
        # === AI Generated Code End matthewmli===
