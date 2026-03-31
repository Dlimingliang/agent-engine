import os
import sys
from pathlib import Path
from typing import Any
from pydantic import BaseModel

# 添加项目根目录到 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .planner import TaskStep


class VerificationResult(BaseModel):
    """验证结果"""
    success: bool
    message: str
    details: dict[str, Any] | None = None
    suggestions: list[str] | None = None
    
    class Config:
        use_enum_values = True


class Verifier:
    """
    验证器 - 验证工具执行结果
    
    职责：
    1. 格式验证：检查输出格式是否正确
    2. 结果验证：检查是否真正达成目标
    3. 质量验证：检查输出质量
    4. 提供改进建议
    """
    
    def __init__(self):
        """
        初始化验证器
        """
        # 验证规则配置
        self.quality_thresholds = {
            "min_content_length": 10,       # 最小内容长度
            "max_content_length": 100000,   # 最大内容长度
            "min_search_results": 1,        # 最小搜索结果数
            "max_search_results": 100       # 最大搜索结果数
        }
    
    def verify(self, step: TaskStep, result: Any) -> VerificationResult:
        """
        验证执行结果
        
        Args:
            step: 执行的步骤
            result: 执行结果
            
        Returns:
            VerificationResult: 验证结果
        """
        # 1. 检查结果是否为空
        if result is None:
            return VerificationResult(
                success=False,
                message="执行结果为空",
                details={"error": "result_is_none"},
                suggestions=["检查工具是否正确执行", "查看执行日志获取详细信息"]
            )
        
        # 2. 进行格式验证
        format_valid, format_msg = self._verify_format(result, step.expected_output)
        if not format_valid:
            return VerificationResult(
                success=False,
                message=f"格式验证失败: {format_msg}",
                details={"error": "format_validation_failed"},
                suggestions=["检查返回数据格式", "确认工具返回的数据结构"]
            )
        
        # 3. 进行结果验证
        result_valid, result_msg = self._verify_result(step, result)
        if not result_valid:
            return VerificationResult(
                success=False,
                message=f"结果验证失败: {result_msg}",
                details={"error": "result_validation_failed"},
                suggestions=["重试执行", "检查参数是否正确", "确认目标是否可达"]
            )
        
        # 4. 进行质量验证
        quality_valid, quality_msg, suggestions = self._verify_quality(step, result)
        
        # 5. 汇总验证结果
        all_valid = format_valid and result_valid and quality_valid
        
        if all_valid:
            return VerificationResult(
                success=True,
                message="所有验证通过",
                details={
                    "format": format_msg,
                    "result": result_msg,
                    "quality": quality_msg
                }
            )
        else:
            return VerificationResult(
                success=False,
                message=f"质量验证失败: {quality_msg}",
                details={"error": "quality_validation_failed"},
                suggestions=suggestions
            )
    
    def _verify_format(self, result: Any, expected_format: str | None = None) -> tuple[bool, str]:
        """
        格式验证
        
        Args:
            result: 执行结果
            expected_format: 预期格式
            
        Returns:
            tuple[bool, str]: (是否通过, 错误信息)
        """
        # 1. 检查结果是否为 None
        if result is None:
            return False, "结果为 None"
        
        # 2. 检查结果类型
        if not isinstance(result, (dict, list, str, int, float, bool)):
            return False, f"不支持的结果类型: {type(result).__name__}"
        
        # 3. 如果是字典，检查是否有必需字段
        if isinstance(result, dict):
            # 检查是否有 success 字段
            if "success" not in result:
                return False, "结果字典缺少 'success' 字段"
            
            # 如果 success 为 False，检查是否有 error 字段
            if result.get("success") is False and "error" not in result:
                return False, "失败的执行结果缺少 'error' 字段"
        
        # 4. 如果有预期格式描述，进行简单匹配
        if expected_format:
            # 这里可以做更复杂的格式验证
            # 目前只做简单的非空检查
            pass
        
        return True, "格式验证通过"
    
    def _verify_result(self, step: TaskStep, result: Any) -> tuple[bool, str]:
        """
        结果验证 - 验证是否真正达成目标
        
        Args:
            step: 执行的步骤
            result: 执行结果
            
        Returns:
            tuple[bool, str]: (是否通过, 错误信息)
        """
        # 1. 根据工具名称判断验证逻辑
        tool_name = step.tool_name
        
        # 2. 执行工具特定验证
        tool_result = self._verify_tool_specific(tool_name, result)
        
        if not tool_result.success:
            return False, tool_result.message
        
        # 3. 对于特定工具的额外验证
        if tool_name == "calculator":
            return self._verify_calculation(result)
        elif tool_name == "file_write":
            return self._verify_file_write(result)
        elif tool_name == "web_search":
            return self._verify_web_search(result)
        elif tool_name == "file_read":
            return self._verify_file_read(result)
        elif tool_name == "web_fetch":
            return self._verify_web_fetch(result)
        
        return True, "结果验证通过"
    
    def _verify_quality(self, step: TaskStep, result: Any) -> tuple[bool, str, list[str]]:
        """
        质量验证
        
        Args:
            step: 执行的步骤
            result: 执行结果
            
        Returns:
            tuple[bool, str, list]: (是否通过, 错误信息, 改进建议)
        """
        suggestions = []
        
        # 1. 根据工具类型进行不同的质量验证
        tool_name = step.tool_name
        
        if isinstance(result, dict) and result.get("success"):
            # 对于 file_write 工具，检查写入的字节数
            if tool_name == "file_write":
                bytes_written = result.get("bytes_written", 0)
                if bytes_written == 0:
                    suggestions.append("写入的字节数为 0，可能没有实际写入内容")
                    return False, "写入内容为空", suggestions
                suggestions.append("文件写入质量良好")
                return True, "质量验证通过", suggestions
            
            # 对于 calculator 工具，检查结果是否存在
            elif tool_name == "calculator":
                calc_result = result.get("result")
                if calc_result is None:
                    suggestions.append("计算结果为空")
                    return False, "计算结果为空", suggestions
                suggestions.append("计算结果质量良好")
                return True, "质量验证通过", suggestions
            
            # 对于 file_read 工具，检查读取的内容
            elif tool_name == "file_read":
                content = result.get("content", "")
                if isinstance(content, str) and len(content) < self.quality_thresholds["min_content_length"]:
                    suggestions.append("读取的内容过于简短")
                    return False, "读取内容不足", suggestions
                suggestions.append("文件读取质量良好")
                return True, "质量验证通过", suggestions
            
            # 对于 web_search 和 web_fetch 工具，检查内容长度
            elif tool_name in ["web_search", "web_fetch"]:
                content = result.get("content", result.get("result", ""))
                if isinstance(content, str):
                    if len(content) < self.quality_thresholds["min_content_length"]:
                        suggestions.append("输出内容过于简短，建议提供更详细的信息")
                        return False, "内容长度不足", suggestions
                    elif len(content) > self.quality_thresholds["max_content_length"]:
                        suggestions.append("输出内容过长，建议进行截断或分页")
                suggestions.append("网络请求质量良好")
                return True, "质量验证通过", suggestions
            
            # 对于其他工具，使用通用的内容长度检查
            else:
                content = result.get("content", result.get("result", ""))
                if isinstance(content, str):
                    if len(content) < self.quality_thresholds["min_content_length"]:
                        suggestions.append("输出内容过于简短，建议提供更详细的信息")
                        return False, "内容长度不足", suggestions
                    elif len(content) > self.quality_thresholds["max_content_length"]:
                        suggestions.append("输出内容过长，建议进行截断或分页")
        
        # 2. 检查输出是否完整
        if isinstance(result, dict):
            # 对于文件操作，检查文件路径是否完整
            if "file_path" in result:
                file_path = result["file_path"]
                if not file_path or not isinstance(file_path, str):
                    suggestions.append("文件路径不完整或格式错误")
                    return False, "文件路径不完整", suggestions
            
            # 对于网络操作，检查 URL 是否完整
            if "url" in result:
                url = result.get("url", "")
                if not url or not isinstance(url, str):
                    suggestions.append("URL 不完整或格式错误")
                    return False, "URL 不完整", suggestions
        
        # 3. 提供改进建议
        if not suggestions:
            suggestions.append("输出质量良好")
        
        return True, "质量验证通过", suggestions
    
    def _verify_tool_specific(self, tool_name: str, result: Any) -> VerificationResult:
        """
        工具特定验证
        
        Args:
            tool_name: 工具名称
            result: 执行结果
            
        Returns:
            VerificationResult: 验证结果
        """
        # 检查是否为字典类型
        if not isinstance(result, dict):
            return VerificationResult(
                success=True,
                message="非字典类型结果，跳过工具特定验证"
            )
        
        # 检查 success 字段
        if "success" not in result:
            return VerificationResult(
                success=False,
                message="结果缺少 'success' 字段"
            )
        
        if result.get("success") is False:
            error_msg = result.get("error", "未知错误")
            return VerificationResult(
                success=False,
                message=f"工具执行失败: {error_msg}"
            )
        
        return VerificationResult(
            success=True,
            message="工具特定验证通过"
        )
    
    def _verify_file_write(self, result: dict[str, Any]) -> tuple[bool, str]:
        """
        验证文件写入结果
        
        Args:
            result: 文件写入结果
            
        Returns:
            tuple[bool, str]: (是否通过, 错误信息)
        """
        # 1. 检查返回的 success 字段
        if not result.get("success"):
            return False, result.get("error", "文件写入失败")
        
        # 2. 检查文件路径是否存在
        file_path = result.get("file_path")
        if not file_path:
            return False, "缺少文件路径信息"
        
        if not os.path.exists(file_path):
            return False, f"文件不存在: {file_path}"
        
        # 3. 检查文件大小是否合理
        file_size = result.get("size", os.path.getsize(file_path))
        
        if file_size == 0:
            return False, "文件大小为 0，可能写入失败"
        
        return True, f"文件写入成功，大小: {file_size} 字节"
    
    def _verify_file_read(self, result: dict[str, Any]) -> tuple[bool, str]:
        """
        验证文件读取结果
        
        Args:
            result: 文件读取结果
            
        Returns:
            tuple[bool, str]: (是否通过, 错误信息)
        """
        # 1. 检查返回的 success 字段
        if not result.get("success"):
            return False, result.get("error", "文件读取失败")
        
        # 2. 检查内容是否存在
        content = result.get("content")
        if content is None:
            return False, "读取的内容为空"
        
        # 3. 检查文件大小
        file_size = result.get("size", 0)
        if file_size == 0:
            return False, "文件大小为 0"
        
        return True, f"文件读取成功，大小: {file_size} 字节"
    
    def _verify_web_search(self, result: dict[str, Any]) -> tuple[bool, str]:
        """
        验证网页搜索结果
        
        Args:
            result: 搜索结果
            
        Returns:
            tuple[bool, str]: (是否通过, 错误信息)
        """
        # 1. 检查是否有搜索结果
        if not result.get("success"):
            return False, result.get("error", "搜索失败")
        
        results = result.get("results", [])
        
        # 2. 检查结果数量是否合理
        if len(results) < self.quality_thresholds["min_search_results"]:
            return False, "没有找到搜索结果"
        
        if len(results) > self.quality_thresholds["max_search_results"]:
            return False, "搜索结果过多，可能查询过于宽泛"
        
        # 3. 检查结果内容是否相关
        for item in results:
            if not isinstance(item, dict):
                continue
            
            # 检查必需字段
            if not all(key in item for key in ["title", "url"]):
                return False, "搜索结果格式不完整"
        
        return True, f"搜索成功，找到 {len(results)} 条结果"
    
    def _verify_web_fetch(self, result: dict[str, Any]) -> tuple[bool, str]:
        """
        验证网页抓取结果
        
        Args:
            result: 抓取结果
            
        Returns:
            tuple[bool, str]: (是否通过, 错误信息)
        """
        # 1. 检查返回的 success 字段
        if not result.get("success"):
            return False, result.get("error", "网页抓取失败")
        
        # 2. 检查内容是否存在
        content = result.get("content")
        if not content:
            return False, "抓取的内容为空"
        
        # 3. 检查内容长度
        content_length = result.get("content_length", len(content))
        if content_length < self.quality_thresholds["min_content_length"]:
            return False, "抓取的内容过短"
        
        # 4. 检查状态码
        status_code = result.get("status_code")
        if status_code and status_code != 200:
            return False, f"HTTP 状态码异常: {status_code}"
        
        return True, f"网页抓取成功，内容长度: {content_length} 字符"
    
    def _verify_calculation(self, result: dict[str, Any]) -> tuple[bool, str]:
        """
        验证计算结果
        
        Args:
            result: 计算结果
            
        Returns:
            tuple[bool, str]: (是否通过, 错误信息)
        """
        # 1. 检查结果是否为数字
        if not result.get("success"):
            return False, result.get("error", "计算失败")
        
        calc_result = result.get("result")
        
        if calc_result is None:
            return False, "计算结果为空"
        
        # 2. 检查结果是否为数字类型
        if not isinstance(calc_result, (int, float)):
            return False, f"计算结果类型错误: {type(calc_result).__name__}"
        
        # 3. 检查结果是否在合理范围
        # 这里可以添加更复杂的范围检查
        if isinstance(calc_result, float):
            if calc_result != calc_result:  # NaN check
                return False, "计算结果为 NaN"
            if abs(calc_result) > 1e100:
                return False, "计算结果数值过大，可能存在溢出"
        
        return True, f"计算成功，结果: {result.get('formatted', calc_result)}"
