import sys
import math
import re
from pathlib import Path
from typing import Any

# 添加项目根目录到 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .tool_registry import Tool


class CalculatorTool(Tool):
    """
    计算器工具
    
    功能：执行数学表达式计算
    
    参数：
    - expression: 数学表达式字符串
    
    示例：
    - "2 + 3" → 5
    - "10 * 5" → 50
    - "sqrt(16)" → 4.0
    """
    
    def __init__(self):
        """
        初始化计算器工具
        """
        super().__init__(
            name="calculator",
            description="执行数学表达式计算。支持基本运算(+、-、*、/)和数学函数(sqrt、sin、cos、tan、log、exp等)。",
            parameters_schema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，如 '2 + 3' 或 'sqrt(16)'"
                    }
                },
                "required": ["expression"]
            }
        )
    
    def execute(self, expression: str, **kwargs) -> dict:
        """
        执行数学计算
        
        Args:
            expression: 数学表达式
            **kwargs: 其他参数
            
        Returns:
            dict: 计算结果
            {
                "success": bool,
                "result": 计算结果,
                "expression": 原始表达式,
                "error": 错误信息（如果失败）
            }
        """
        try:
            result = self._safe_eval(expression)
            formatted_result = self._format_result(result)
            
            return {
                "success": True,
                "result": result,
                "formatted": formatted_result,
                "expression": expression
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "expression": expression
            }
    
    def _safe_eval(self, expression: str) -> Any:
        """
        安全计算表达式
        
        Args:
            expression: 数学表达式
            
        Returns:
            Any: 计算结果
            
        Raises:
            ValueError: 不安全的表达式
        """
        # 将 ^ 替换为 **（幂运算）
        expression = expression.replace('^', '**')
        
        # 定义允许的字符：数字、运算符、括号、空格、小数点、函数名
        allowed_chars = re.compile(r'^[\d\s\+\-\*\/\(\)\.\,\^a-zA-Z_]+$')
        
        if not allowed_chars.match(expression):
            raise ValueError(f"表达式包含不安全的字符: {expression}")
        
        # 检查是否包含危险关键字
        dangerous_keywords = ['import', 'exec', 'eval', 'compile', 'open', 'file', '__']
        if any(keyword in expression.lower() for keyword in dangerous_keywords):
            raise ValueError(f"表达式包含不安全的关键字")
        
        # 创建安全的命名空间，只包含数学函数
        safe_namespace = {
            # 内置函数
            'int': int,
            'float': float,
            'str': str,
            # 数学函数
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'log': math.log,
            'log10': math.log10,
            'log2': math.log2,
            'exp': math.exp,
            'pow': pow,
            'abs': abs,
            'round': round,
            'floor': math.floor,
            'ceil': math.ceil,
            # 数学常量
            'pi': math.pi,
            'e': math.e,
            'inf': math.inf,
            'nan': math.nan,
            # 斐波那契函数
            'fibonacci': lambda n: self._fibonacci(n),
            'fib': lambda n: self._fibonacci(n),
        }
        
        try:
            result = eval(expression, {"__builtins__": {}}, safe_namespace)
            return result
        except Exception as e:
            raise ValueError(f"计算表达式失败: {str(e)}")
    
    def _format_result(self, result: Any) -> str:
        """
        格式化结果
        
        Args:
            result: 计算结果
            
        Returns:
            str: 格式化的结果字符串
        """
        if isinstance(result, float):
            # 如果是浮点数，保留适当小数位
            if result == int(result):
                return str(int(result))
            return f"{result:.6g}"
        elif isinstance(result, int):
            return str(result)
        else:
            return str(result)
    
    def _fibonacci(self, n: int) -> int:
        """
        计算斐波那契数列第 n 项
        
        Args:
            n: 第 n 项（从 1 开始）
            
        Returns:
            int: 斐波那契数列第 n 项的值
        """
        if n <= 0:
            return 0
        elif n == 1 or n == 2:
            return 1
        
        # 使用迭代方法计算
        a, b = 1, 1
        for _ in range(2, n):
            a, b = b, a + b
        return b
