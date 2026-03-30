import sys
from pathlib import Path
from typing import List, Optional, Any, Dict
from enum import Enum
from pydantic import BaseModel

# 添加项目根目录到 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class ToolErrorType(Enum):
    """
    工具错误类型枚举
    
    错误类型：
    - TOOL_NOT_FOUND: 工具不存在
    - INVALID_PARAMETERS: 参数错误
    - EXECUTION_ERROR: 执行错误
    - OUTPUT_MISMATCH: 输出不符预期
    """
    TOOL_NOT_FOUND = "tool_not_found"
    INVALID_PARAMETERS = "invalid_parameters"
    EXECUTION_ERROR = "execution_error"
    OUTPUT_MISMATCH = "output_mismatch"


class ToolError(BaseModel):
    """
    标准化工具错误
    
    字段：
    - error_type: 错误类型
    - tool_name: 工具名称
    - message: 错误消息
    - original_error: 原始错误信息
    - suggested_fix: 建议的修复方法
    """
    error_type: ToolErrorType
    tool_name: str
    message: str
    original_error: Optional[str] = None
    suggested_fix: Optional[str] = None
    
    def to_user_message(self) -> str:
        """
        转换为用户可读的消息
        
        Returns:
            str: 用户友好的错误消息
        """
        if self.error_type == ToolErrorType.TOOL_NOT_FOUND:
            return f"工具 '{self.tool_name}' 不存在"
        elif self.error_type == ToolErrorType.INVALID_PARAMETERS:
            return f"工具 '{self.tool_name}' 参数错误: {self.message}"
        elif self.error_type == ToolErrorType.EXECUTION_ERROR:
            return f"工具 '{self.tool_name}' 执行失败: {self.message}"
        elif self.error_type == ToolErrorType.OUTPUT_MISMATCH:
            return f"工具 '{self.tool_name}' 输出格式不符预期: {self.message}"
        else:
            return f"工具 '{self.tool_name}' 发生未知错误: {self.message}"
    
    def to_llm_context(self) -> str:
        """
        转换为 LLM 可理解的上下文
        
        Returns:
            str: LLM 友好的错误上下文
        """
        context = "[工具执行失败]\n"
        context += f"- 工具名称: {self.tool_name}\n"
        context += f"- 错误类型: {self.error_type.value}\n"
        context += f"- 错误信息: {self.message}\n"
        if self.original_error:
            context += f"- 原始错误: {self.original_error}\n"
        if self.suggested_fix:
            context += f"- 建议修复: {self.suggested_fix}\n"
        return context


class ErrorRecovery:
    """
    错误恢复处理器
    
    职责：
    1. 标准化错误信息
    2. 将错误注入消息流
    3. 提取恢复动作
    4. 执行恢复策略
    """
    
    def __init__(self, llm, tool_registry):
        """
        初始化错误恢复处理器
        
        Args:
            llm: LLM 客户端
            tool_registry: 工具注册表
            
        TODO:
        1. 保存 llm 引用
        2. 保存 tool_registry 引用
        """
        self.llm = llm
        self.tool_registry = tool_registry
    
    def normalize_error(self, step, error: Exception) -> ToolError:
        """
        标准化错误
        
        Args:
            step: 任务步骤
            error: 原始异常
            
        Returns:
            ToolError: 标准化的错误对象
        """
        error_str = str(error).lower()
        
        # 判断错误类型
        if "not found" in error_str or "不存在" in error_str:
            error_type = ToolErrorType.TOOL_NOT_FOUND
            suggested_fix = f"请检查工具名称是否正确，或寻找替代工具"
        elif "invalid" in error_str or "parameter" in error_str or "参数" in error_str:
            error_type = ToolErrorType.INVALID_PARAMETERS
            suggested_fix = "请检查参数格式和类型是否正确"
        elif "output" in error_str or "输出" in error_str or "format" in error_str:
            error_type = ToolErrorType.OUTPUT_MISMATCH
            suggested_fix = "请检查工具返回格式是否符合预期"
        else:
            error_type = ToolErrorType.EXECUTION_ERROR
            suggested_fix = "可以尝试重试或使用其他工具"
        
        return ToolError(
            error_type=error_type,
            tool_name=step.tool_name,
            message=str(error),
            original_error=str(error),
            suggested_fix=suggested_fix
        )
    
    def inject_error_to_messages(
        self,
        messages: List[Dict[str, Any]],
        error: ToolError
    ) -> List[Dict[str, Any]]:
        """
        将错误注入消息流
        
        Args:
            messages: 消息历史
            error: 工具错误
            
        Returns:
            List[dict]: 更新后的消息历史
            
        TODO:
        1. 创建 tool 角色消息，内容为 error.to_llm_context()
        2. 添加到 messages
        3. 创建 system 角色消息，提示 LLM 选择恢复动作：
           - 修改参数后重试
           - 换一个工具
           - 请求用户提供更多信息
           - 跳过当前步骤
        4. 添加到 messages
        5. 返回更新后的 messages
        """
        tool_message = {
            "role": "tool",
            "content": error.to_llm_context()
        }
        messages.append(tool_message)
        
        system_message = {
            "role": "system",
            "content": """工具执行失败。请根据错误信息选择以下恢复动作之一：
1. 修改参数后重试（retry）：修正工具参数后重新执行
2. 换一个工具（switch_tool）：使用其他工具完成相同任务
3. 请求用户提供更多信息（ask_user）：需要额外信息才能继续
4. 跳过当前步骤（skip）：跳过此步骤继续执行

请回复选择的动作及详细信息。"""
        }
        messages.append(system_message)
        return messages
    
    def extract_recovery_action(self, llm_response: str) -> Dict[str, Any]:
        """
        从 LLM 响应中提取恢复动作
        
        Args:
            llm_response: LLM 的响应文本
            
        Returns:
            Dict[str, Any]: 恢复动作
        """
        response_lower = llm_response.lower()
        
        # 解析 LLM 响应
        if "修改参数" in response_lower or "重试" in response_lower or "retry" in response_lower:
            return {
                "action": "retry",
                "details": {"fix": llm_response}
            }
        elif "换一个工具" in response_lower or "switch_tool" in response_lower:
            return {
                "action": "switch_tool",
                "details": {"alternative": llm_response}
            }
        elif "请求用户" in response_lower or "ask_user" in response_lower:
            return {
                "action": "ask_user",
                "details": {"question": llm_response}
            }
        elif "跳过" in response_lower or "skip" in response_lower:
            return {
                "action": "skip",
                "details": {}
            }
        else:
            # 默认重试
            return {
                "action": "retry",
                "details": {"fix": llm_response}
            }
    
    def recover(
        self,
        step,
        error: Exception,
        messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        执行恢复
        
        Args:
            step: 失败的步骤
            error: 异常
            messages: 消息历史
            
        Returns:
            Dict[str, Any]: 恢复结果
        """
        # 1. 标准化错误
        tool_error = self.normalize_error(step, error)
        
        # 2. 根据错误类型决定策略
        if tool_error.error_type == ToolErrorType.TOOL_NOT_FOUND:
            # 工具不存在，尝试找替代工具
            alternative = self.find_alternative_tool(step.tool_name)
            if alternative:
                return {
                    "action": "switch_tool",
                    "new_step": {
                        "tool_name": alternative,
                        "tool_args": step.tool_args
                    },
                    "message_to_user": f"工具 '{step.tool_name}' 不存在，已自动切换到 '{alternative}'"
                }
            else:
                return {
                    "action": "replan",
                    "new_step": None,
                    "message_to_user": f"工具 '{step.tool_name}' 不存在且无替代工具，需要重新规划"
                }
        
        elif tool_error.error_type == ToolErrorType.INVALID_PARAMETERS:
            # 参数错误，让 LLM 修正参数
            messages_with_error = self.inject_error_to_messages(messages.copy(), tool_error)
            llm_response = self.llm.invoke(messages_with_error)
            action = self.extract_recovery_action(llm_response.content if hasattr(llm_response, 'content') else str(llm_response))
            
            return {
                "action": "retry",
                "new_step": step.model_dump() if hasattr(step, 'model_dump') else step.__dict__,
                "message_to_user": None
            }
        
        else:
            # 其他错误（执行错误、输出不匹配），重试或跳过
            if self._is_retriable(error):
                messages_with_error = self.inject_error_to_messages(messages.copy(), tool_error)
                llm_response = self.llm.invoke(messages_with_error)
                action = self.extract_recovery_action(llm_response.content if hasattr(llm_response, 'content') else str(llm_response))
                
                return {
                    "action": action["action"],
                    "new_step": step.model_dump() if hasattr(step, 'model_dump') else step.__dict__,
                    "message_to_user": None
                }
            else:
                return {
                    "action": "skip",
                    "new_step": None,
                    "message_to_user": f"步骤执行失败且不可重试: {tool_error.message}"
                }
    
    def find_alternative_tool(self, tool_name: str) -> Optional[str]:
        """
        查找替代工具
        
        Args:
            tool_name: 原工具名称
            
        Returns:
            Optional[str]: 替代工具名称，如果没有则返回 None
        """
        # 工具映射关系
        tool_alternatives = {
            "web_search": ["web_fetch", "search"],
            "file_read": ["read_file", "load_file"],
            "file_write": ["write_file", "save_file"],
            "calculator": ["calc", "compute"],
            "web_fetch": ["fetch_url", "http_get"],
        }
        
        # 查找直接映射
        if tool_name in tool_alternatives:
            for alt in tool_alternatives[tool_name]:
                if self.tool_registry.has_tool(alt):
                    return alt
        
        # 尝试查找相似工具
        all_tools = self.tool_registry.list_tools()
        for tool in all_tools:
            if tool != tool_name and (tool_name in tool or tool in tool_name):
                return tool
        
        return None
    
    def _is_retriable(self, error: Exception) -> bool:
        """
        判断错误是否可重试
        
        Args:
            error: 异常对象
            
        Returns:
            bool: 是否可重试
        """
        error_str = str(error).lower()
        
        # 可重试的错误
        retriable_keywords = ["timeout", "rate limit", "temporarily", "connection", "network", "超时", "连接"]
        
        for keyword in retriable_keywords:
            if keyword in error_str:
                return True
        
        return False
    
    def _build_recovery_prompt(self, error: ToolError) -> str:
        """
        构建恢复提示
        
        Args:
            error: 工具错误
            
        Returns:
            str: 恢复提示文本
        """
        prompt = f"""工具执行失败，请选择恢复动作：

错误情况：
{error.to_llm_context()}

可选的恢复动作：
1. retry - 修改参数后重试
2. switch_tool - 切换到其他工具
3. ask_user - 请求用户提供更多信息
4. skip - 跳过当前步骤

请选择最合适的恢复动作并说明理由。"""
        
        return prompt
