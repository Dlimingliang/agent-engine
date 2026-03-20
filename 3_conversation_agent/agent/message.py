"""
消息模型
"""
from datetime import datetime
from typing import Dict, Any


class Message:
    """
    消息类：表示对话中的一条消息
    
    字段：
        role: str - 消息角色（user / assistant / system）
        content: str - 消息内容
        timestamp: datetime - 时间戳
    """
    
    def __init__(self, role: str, content: str, timestamp: datetime = None):
        """
        初始化消息
        
        TODO: 实现初始化逻辑
        - 设置 role
        - 设置 content
        - 设置 timestamp（如果未提供，使用当前时间）
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        TODO: 实现转换逻辑
        - 将消息对象转换为字典
        - timestamp 需要转换为 ISO 格式字符串
        
        返回格式：
        {
            "role": "user",
            "content": "消息内容",
            "timestamp": "2026-03-20T10:00:00"
        }
        """
        pass
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """
        从字典创建消息对象
        
        TODO: 实现创建逻辑
        - 从字典中提取数据
        - timestamp 需要从字符串解析为 datetime
        - 返回 Message 对象
        """
        pass
    
    def __repr__(self) -> str:
        """字符串表示"""
        pass
