"""
@generated-by AI: matthewmli
@generated-date 2026-03-23
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTool(ABC):
    """工具基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """工具参数 schema"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行工具
        
        Args:
            **kwargs: 工具参数
        
        Returns:
            执行结果
        """
        pass
    
    def to_openai_tool(self) -> Dict[str, Any]:
        """
        转换为 OpenAI 工具格式
        
        Returns:
            OpenAI 工具定义
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
