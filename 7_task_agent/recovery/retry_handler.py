import sys
import time
from pathlib import Path
from typing import Callable, Any, Optional, Dict
from enum import Enum
from pydantic import BaseModel

# 添加项目根目录到 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class RetryStrategy(Enum):
    """
    重试策略枚举
    
    策略说明：
    - IMMEDIATE: 立即重试
    - DELAYED: 延迟重试
    - DEGRADED: 降级重试（切换工具）
    - ABORT: 放弃重试，需要人工介入
    """
    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    DEGRADED = "degraded"
    ABORT = "abort"


class RetryPolicy(BaseModel):
    """
    重试策略配置
    
    配置项：
    - max_retries: 最大重试次数
    - strategy: 重试策略
    - delay_seconds: 延迟秒数
    - fallback_tool: 备选工具名称
    """
    max_retries: int = 3
    strategy: RetryStrategy = RetryStrategy.IMMEDIATE
    delay_seconds: int = 2
    fallback_tool: Optional[str] = None


class RetryHandler:
    """
    重试处理器
    
    职责：
    1. 判断是否应该重试
    2. 选择重试策略
    3. 执行带重试的操作
    4. 记录重试次数
    """
    
    def __init__(self, max_retries: int = 3):
        """
        初始化重试处理器
        
        Args:
            max_retries: 最大重试次数
        """
        self.max_retries = max_retries
        self.retry_counts: Dict[int, int] = {}  # step_id -> retry_count
    
    def should_retry(
        self,
        step,
        error: Exception,
        current_attempts: int
    ) -> RetryStrategy:
        """
        判断是否应该重试，以及使用什么策略
        
        Args:
            step: 任务步骤
            error: 错误异常
            current_attempts: 当前重试次数
            
        Returns:
            RetryStrategy: 重试策略
        """
        # 1. 检查是否超过最大重试次数
        if current_attempts >= self.max_retries:
            return RetryStrategy.ABORT
        
        # 2. 根据错误类型选择策略
        error_type = self._classify_error(error)
        
        if error_type in ["timeout", "rate_limit"]:
            return RetryStrategy.DELAYED
        elif error_type == "invalid_param":
            return RetryStrategy.ABORT
        elif error_type == "permission":
            return RetryStrategy.ABORT
        elif error_type == "service_unavailable":
            return RetryStrategy.DEGRADED
        else:
            return RetryStrategy.IMMEDIATE
    
    def execute_with_retry(
        self,
        step,
        executor: Callable,
        policy: RetryPolicy
    ) -> Any:
        """
        带重试的执行
        
        Args:
            step: 任务步骤
            executor: 执行函数
            policy: 重试策略
            
        Returns:
            Any: 执行结果
            
        Raises:
            RuntimeError: 超过最大重试次数或不可重试
        """
        retry_count = 0
        
        while retry_count <= policy.max_retries:
            try:
                # 执行函数
                result = executor(step)
                return result
                
            except Exception as e:
                # 判断重试策略
                strategy = self.should_retry(step, e, retry_count)
                
                # 如果是 ABORT，抛出异常
                if strategy == RetryStrategy.ABORT:
                    raise RuntimeError(f"不可重试的错误: {str(e)}") from e
                
                # 增加重试计数
                retry_count += 1
                
                # 如果超过最大次数，抛出异常
                if retry_count > policy.max_retries:
                    raise RuntimeError(f"超过最大重试次数 ({policy.max_retries}): {str(e)}") from e
                
                # 根据策略等待（DELAYED）
                if strategy == RetryStrategy.DELAYED:
                    delay = self._get_delay_time(retry_count, policy)
                    time.sleep(delay)
                
                # 如果是 DEGRADED，切换工具
                if strategy == RetryStrategy.DEGRADED and policy.fallback_tool:
                    # 修改 step 的工具名称
                    if hasattr(step, 'tool_name'):
                        step.tool_name = policy.fallback_tool
        
        # 不应该到达这里
        raise RuntimeError("执行失败，未知错误")
    
    def _get_delay_time(self, attempt: int, policy: RetryPolicy) -> float:
        """
        计算延迟时间（指数退避）
        
        Args:
            attempt: 当前尝试次数
            policy: 重试策略
            
        Returns:
            float: 延迟秒数
        """
        # 指数退避算法: delay = base_delay * (2 ^ attempt)
        base_delay = policy.delay_seconds
        delay = base_delay * (2 ** attempt)
        
        # 设置最大延迟限制（避免等待时间过长）
        max_delay = 60  # 最多等待 60 秒
        return min(delay, max_delay)
    
    def get_retry_count(self, step_id: int) -> int:
        """
        获取步骤的重试次数
        
        Args:
            step_id: 步骤 ID
            
        Returns:
            int: 重试次数
        """
        return self.retry_counts.get(step_id, 0)
    
    def reset_retry_count(self, step_id: int):
        """
        重置步骤的重试次数
        
        Args:
            step_id: 步骤 ID
        """
        self.retry_counts[step_id] = 0
    
    def _classify_error(self, error: Exception) -> str:
        """
        分类错误类型
        
        Args:
            error: 异常对象
            
        Returns:
            str: 错误类型（timeout, rate_limit, invalid_param, permission, service_unavailable, unknown）
        """
        error_str = str(error).lower()
        
        # 判断错误类型
        if "timeout" in error_str or "connection" in error_str:
            return "timeout"
        elif "rate limit" in error_str or "429" in error_str:
            return "rate_limit"
        elif "invalid" in error_str or "400" in error_str:
            return "invalid_param"
        elif "permission" in error_str or "403" in error_str:
            return "permission"
        elif "503" in error_str or "service unavailable" in error_str:
            return "service_unavailable"
        else:
            return "unknown"
    
    def is_retriable_error(self, error: Exception) -> bool:
        """
        判断是否为可重试的错误
        
        Args:
            error: 异常对象
            
        Returns:
            bool: 是否可重试
        """
        error_type = self._classify_error(error)
        
        # 可重试的错误类型
        retriable_types = ["timeout", "rate_limit", "service_unavailable"]
        
        return error_type in retriable_types
