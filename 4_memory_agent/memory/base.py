"""
@generated-by AI: matthewmli
@generated-date 2026-03-23
"""
from abc import ABC, abstractmethod
from typing import Any


class BaseMemory(ABC):
    """记忆基类"""
    
    @abstractmethod
    def update(self, data: dict[str, Any]):
        """
        更新记忆
        
        Args:
            data: 记忆数据
        """
        pass
    
    @abstractmethod
    def get(self) -> dict[str, Any]:
        """
        获取记忆内容
        
        Returns:
            记忆数据
        """
        pass
    
    @abstractmethod
    def clear(self):
        """清除记忆"""
        pass
    
    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """
        序列化为字典
        
        Returns:
            字典格式数据
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseMemory":
        """
        从字典创建记忆
        
        Args:
            data: 字典数据
        
        Returns:
            记忆实例
        """
        pass
