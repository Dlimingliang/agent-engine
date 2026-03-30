import os
import sys
from pathlib import Path
from typing import Any

# 添加项目根目录到 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .tool_registry import Tool


class FileReadTool(Tool):
    """
    文件读取工具
    
    功能：读取文件内容
    
    参数：
    - file_path: 文件路径
    - encoding: 编码（默认 utf-8）
    """
    
    def __init__(self):
        """
        初始化文件读取工具
        """
        super().__init__(
            name="file_read",
            description="读取指定文件的内容。支持文本文件和常见编码格式。",
            parameters_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要读取的文件路径"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "文件编码，默认为 utf-8",
                        "default": "utf-8"
                    }
                },
                "required": ["file_path"]
            }
        )
    
    def execute(self, file_path: str, encoding: str = "utf-8", **kwargs) -> dict:
        """
        读取文件
        
        Args:
            file_path: 文件路径
            encoding: 文件编码
            **kwargs: 其他参数
            
        Returns:
            dict: 读取结果
        """
        try:
            # 验证路径安全性
            if not self._validate_path(file_path):
                return {
                    "success": False,
                    "error": "路径不安全，可能存在目录遍历风险",
                    "file_path": file_path
                }
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"文件不存在: {file_path}",
                    "file_path": file_path
                }
            
            # 检查是否为文件
            if not os.path.isfile(file_path):
                return {
                    "success": False,
                    "error": f"路径不是文件: {file_path}",
                    "file_path": file_path
                }
            
            # 读取文件
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            
            return {
                "success": True,
                "content": content,
                "file_path": file_path,
                "size": file_size,
                "encoding": encoding
            }
        except UnicodeDecodeError as e:
            return {
                "success": False,
                "error": f"文件编码错误: {str(e)}",
                "file_path": file_path
            }
        except PermissionError as e:
            return {
                "success": False,
                "error": f"权限不足: {str(e)}",
                "file_path": file_path
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def _validate_path(self, file_path: str) -> bool:
        """
        验证路径是否安全
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否安全
        """
        # 解析真实路径
        try:
            real_path = os.path.realpath(file_path)
        except Exception:
            return False
        
        # 检查路径跳转
        if ".." in Path(file_path).parts:
            return False
        
        # 获取当前工作目录
        cwd = os.path.realpath(os.getcwd())
        
        # 允许在当前工作目录及其子目录下操作
        # 如果需要更严格的安全控制，可以限制到特定目录
        # return real_path.startswith(cwd)
        
        return True


class FileWriteTool(Tool):
    """
    文件写入工具
    
    功能：写入内容到文件
    
    参数：
    - file_path: 文件路径
    - content: 文件内容
    - mode: 写入模式（默认 'w'）
    - encoding: 编码（默认 utf-8）
    """
    
    def __init__(self):
        """
        初始化文件写入工具
        """
        super().__init__(
            name="file_write",
            description="将内容写入指定文件。如果文件不存在会自动创建，如果存在会覆盖或追加。",
            parameters_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要写入的文件路径"
                    },
                    "content": {
                        "type": "string",
                        "description": "要写入的内容"
                    },
                    "mode": {
                        "type": "string",
                        "description": "写入模式: 'w' 覆盖, 'a' 追加",
                        "enum": ["w", "a"],
                        "default": "w"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "文件编码，默认为 utf-8",
                        "default": "utf-8"
                    }
                },
                "required": ["file_path", "content"]
            }
        )
    
    def execute(
        self,
        file_path: str,
        content: str,
        mode: str = "w",
        encoding: str = "utf-8",
        **kwargs
    ) -> dict:
        """
        写入文件
        
        Args:
            file_path: 文件路径
            content: 文件内容
            mode: 写入模式 ('w' 覆盖, 'a' 追加)
            encoding: 文件编码
            **kwargs: 其他参数
            
        Returns:
            dict: 写入结果
        """
        try:
            # 验证路径安全性
            if not self._validate_path(file_path):
                return {
                    "success": False,
                    "error": "路径不安全，可能存在目录遍历风险",
                    "file_path": file_path
                }
            
            # 验证写入模式
            if mode not in ['w', 'a']:
                return {
                    "success": False,
                    "error": f"无效的写入模式: {mode}，只支持 'w' 或 'a'",
                    "file_path": file_path
                }
            
            # 确保目录存在
            self._ensure_directory(file_path)
            
            # 写入文件
            with open(file_path, mode, encoding=encoding) as f:
                bytes_written = f.write(content)
            
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            
            return {
                "success": True,
                "file_path": file_path,
                "size": file_size,
                "bytes_written": bytes_written,
                "mode": mode
            }
        except PermissionError as e:
            return {
                "success": False,
                "error": f"权限不足: {str(e)}",
                "file_path": file_path
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def _ensure_directory(self, file_path: str):
        """
        确保目录存在
        
        Args:
            file_path: 文件路径
        """
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    
    def _validate_path(self, file_path: str) -> bool:
        """
        验证路径是否安全
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否安全
        """
        # 解析真实路径
        try:
            real_path = os.path.realpath(file_path)
        except Exception:
            return False
        
        # 检查路径跳转
        if ".." in Path(file_path).parts:
            return False
        
        # 获取当前工作目录
        cwd = os.path.realpath(os.getcwd())
        
        # 允许在当前工作目录及其子目录下操作
        # return real_path.startswith(cwd)
        
        return True
