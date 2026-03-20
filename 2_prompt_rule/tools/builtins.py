import json
from datetime import datetime
from pydantic import BaseModel, Field

from .registry import ToolRegistry

# ============================================
# 工具1: 获取当前时间
# ============================================
class GetCurrentTimeArgs(BaseModel):
    """获取当前时间的参数（无参数）"""
    pass


def get_current_time() -> str:
    """
    获取当前的日期和时间

    Returns:
        格式化的时间字符串
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")




# ============================================
# 工具2: 读取文件
# ============================================
class ReadFileArgs(BaseModel):
    """read_file 工具参数约束"""
    file_path: str = Field(description="文件绝对路径")

def read_file(file_path: str) -> str:
    """
    读取指定路径的文件内容
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件内容或错误信息
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"错误: 文件 '{file_path}' 不存在"
    except PermissionError:
        return f"错误: 没有权限读取文件 '{file_path}'"
    except Exception as e:
        return f"错误: 读取文件失败 - {str(e)}"


# ============================================
# 工具3: 网页获取 (模拟版)
# ============================================

def fetch_url(url: str, timeout: int = 10) -> str:
    """
    获取网页内容 (模拟版，返回提示信息)
    
    Args:
        url: 网页 URL
        timeout: 超时时间(秒)
        
    Returns:
        模拟的网页内容
    """
    # 这是模拟版本，实际项目中可用 requests 或 httpx
    return json.dumps({
        "status": "mock",
        "message": "这是模拟的网页内容",
        "url": url,
        "timeout": timeout,
        "hint": "实际项目中请安装 requests: pip install requests"
    }, ensure_ascii=False, indent=2)


FETCH_URL_SCHEMA = {
    "type": "object",
    "properties": {
        "url": {
            "type": "string",
            "description": "要获取的网页 URL"
        },
        "timeout": {
            "type": "integer",
            "description": "超时时间(秒)，默认10秒",
            "default": 10
        }
    },
    "required": ["url"]
}


# ============================================
# 注册函数
# ============================================

def register_builtin_tools(registry: ToolRegistry):
    """
    注册内置工具到 Registry
    
    Args:
        registry: ToolRegistry 实例
    """
    time_schema = GetCurrentTimeArgs.model_json_schema()
    registry.register(
        name="get_current_time",
        description="获取当前的日期和时间",
        parameters=time_schema,
        func=get_current_time
    )

    # 生成 JSON Schema
    file_schema = ReadFileArgs.model_json_schema()
    registry.register(
        name="read_file",
        description="读取指定路径的文件内容",
        parameters=file_schema,
        func=read_file
    )
    
    registry.register(
        name="fetch_url",
        description="获取网页内容",
        parameters=FETCH_URL_SCHEMA,
        func=fetch_url
    )
