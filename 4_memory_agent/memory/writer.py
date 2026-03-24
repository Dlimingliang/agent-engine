"""
@generated-by AI: matthewmli
@generated-date 2026-03-23
"""
from typing import Any, Optional

from .long_term import LongTermMemory
from .short_term import ShortTermMemory
from .working import WorkingMemory


class MemoryWriter:
    """
    记忆写入器

    使用混合策略（规则 + LLM）判断是否需要更新记忆
    """

    # 意图关键词映射
    INTENT_KEYWORDS = {
        "create_task": ["创建", "新建", "添加任务", "帮我建"],
        "execute_task": ["执行", "运行", "开始任务", "做这个任务"],
        "query_task": ["查询", "查看", "我的任务", "任务列表", "有什么任务"],
        "delete_task": ["删除", "取消", "移除"],
    }

    # 状态变更关键词
    STATUS_KEYWORDS = {
        "completed": ["完成", "成功", "做好了", "搞定"],
        "failed": ["失败", "出错", "不行"],
        "cancelled": ["取消", "放弃"],
    }

    # 偏好关键词
    PREFERENCE_KEYWORDS = ["我喜欢", "默认", "以后", "总是", "习惯"]

    # 事实关键词
    FACT_KEYWORDS = ["我是", "我在", "我的", "我是做", "我从事"]

    def __init__(
        self,
        short_term_memory: ShortTermMemory,
        long_term_memory: LongTermMemory,
        working_memory: WorkingMemory,
        llm_client: Any = None,
    ):
        """
        初始化记忆写入器

        Args:
            short_term_memory: 短期记忆实例
            long_term_memory: 长期记忆实例
            working_memory: 工作记忆实例
            llm_client: LLM 客户端（用于智能判断）
        """
        self.short_term_memory = short_term_memory
        self.long_term_memory = long_term_memory
        self.working_memory = working_memory
        self.llm_client = llm_client

    def should_update_short_term(
        self, user_input: str, assistant_response: str
    ) -> tuple[bool, Optional[str]]:
        """
        判断是否需要更新短期记忆

        Args:
            user_input: 用户输入
            assistant_response: Agent 回复

        Returns:
            (是否更新, 更新原因)
        """
        # 意图判断
        matched, intent = self._rule_judge_intent(user_input)
        if matched and intent:
            return True, f"检测到意图: {intent}"

        # 状态变更判断
        for status, keywords in self.STATUS_KEYWORDS.items():
            if any(kw in assistant_response for kw in keywords):
                return True, f"检测到状态变更: {status}"

        return False, None

    def should_update_long_term(
        self, user_input: str, assistant_response: str
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        判断是否需要更新长期记忆

        Args:
            user_input: 用户输入
            assistant_response: Agent 回复

        Returns:
            (是否更新, 更新类型, 更新内容)
        """
        # 第一步：规则判断偏好
        matched, preference = self._rule_judge_preference(user_input)
        if matched and preference:
            return True, "preference", preference

        # 第二步：规则判断事实
        for kw in self.FACT_KEYWORDS:
            if kw in user_input:
                # 提取事实内容
                fact = user_input.replace(kw, "").strip()
                if fact:
                    return True, "fact", fact

        # 第三步：LLM 判断（如果有客户端）
        if self.llm_client:
            return self._llm_judge(user_input, assistant_response)

        return False, None, None

    def should_update_working(
        self, user_input: str, assistant_response: str
    ) -> tuple[bool, Optional[str]]:
        """
        判断是否需要更新工作记忆

        Args:
            user_input: 用户输入
            assistant_response: Agent 回复

        Returns:
            (是否更新, 更新原因)
        """
        # 任务创建判断
        if any(kw in user_input for kw in self.INTENT_KEYWORDS["create_task"]):
            return True, "任务创建"

        # 步骤完成判断
        if any(kw in assistant_response for kw in ["步骤", "完成", "成功"]):
            return True, "步骤更新"

        # 任务结束判断
        if any(kw in assistant_response for kw in ["任务完成", "任务结束", "已取消"]):
            return True, "任务结束"

        return False, None

    def write_memory(self, memory_type: str, data: dict[str, Any]):
        """
        执行记忆写入

        Args:
            memory_type: 记忆类型 (short_term/long_term/working)
            data: 写入数据
        """
        if memory_type == "short_term":
            self.short_term_memory.update(data)
        elif memory_type == "long_term":
            self.long_term_memory.update(data)
            # 长期记忆持久化
            self.long_term_memory.save()
        elif memory_type == "working":
            self.working_memory.update(data)

    def process_update(self, user_input: str, assistant_response: str):
        """
        处理记忆更新（主入口）

        Args:
            user_input: 用户输入
            assistant_response: Agent 回复
        """
        # 1. 判断并更新短期记忆
        should_update, _ = self.should_update_short_term(user_input, assistant_response)
        if should_update:
            _, intent = self._rule_judge_intent(user_input)
            if intent:
                self.short_term_memory.update_intent(intent)
                # 添加话题
                self.short_term_memory.add_topic(intent.replace("_task", ""))

        # 2. 判断并更新长期记忆
        should_update, update_type, content = self.should_update_long_term(
            user_input, assistant_response
        )
        if should_update and content:
            if update_type == "preference":
                # 简单解析偏好 (格式: "我喜欢..." -> key)
                self.long_term_memory.add_preference(content[:20], True)
            elif update_type == "fact":
                self.long_term_memory.add_fact(content)

        # 3. 判断并更新工作记忆
        should_update, reason = self.should_update_working(user_input, assistant_response)
        if should_update:
            if reason == "任务创建":
                # 从回复中提取任务信息
                self._update_task_from_response(assistant_response)
            elif reason == "任务结束":
                self.working_memory.complete_task()

    def _rule_judge_preference(self, text: str) -> tuple[bool, Optional[str]]:
        """
        规则判断：偏好

        Args:
            text: 输入文本

        Returns:
            (是否匹配, 偏好内容)
        """
        for kw in self.PREFERENCE_KEYWORDS:
            if kw in text:
                # 提取偏好内容
                idx = text.index(kw) + len(kw)
                preference = text[idx:].strip()
                if preference:
                    return True, preference
        return False, None

    def _rule_judge_intent(self, text: str) -> tuple[bool, Optional[str]]:
        """
        规则判断：意图

        Args:
            text: 输入文本

        Returns:
            (是否匹配, 意图类型)
        """
        for intent, keywords in self.INTENT_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return True, intent
        return False, None

    def _llm_judge(
        self, user_input: str, assistant_response: str
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        LLM 判断：是否需要长期记忆

        Args:
            user_input: 用户输入
            assistant_response: Agent 回复

        Returns:
            (是否需要记住, 记忆类型, 记忆内容)
        """
        if not self.llm_client:
            return False, None, None

        # 构建判断提示
        prompt = f"""请判断以下对话是否包含需要长期记住的信息。

用户输入: {user_input}
助手回复: {assistant_response}

如果需要记住，请返回 JSON 格式:
{{"should_remember": true, "type": "preference/fact/decision", "content": "具体内容"}}

如果不需要记住，请返回:
{{"should_remember": false}}

只返回 JSON，不要其他内容。"""

        try:
            # 调用 LLM（假设客户端有 chat 方法）
            response = self.llm_client.chat(prompt)
            # 解析响应
            import json

            result = json.loads(response)
            if result.get("should_remember"):
                return True, result.get("type"), result.get("content")
        except Exception:
            pass

        return False, None, None

    def _update_task_from_response(self, response: str):
        """
        从回复中提取任务信息并更新工作记忆

        Args:
            response: Agent 回复
        """
        import re

        # 尝试提取任务 ID
        task_id_match = re.search(r"task[_-]?(\w+)", response)
        # 尝试提取任务名称
        task_name_match = re.search(r"任务[：:]\s*([^，。,\n]+)", response)

        if task_id_match or task_name_match:
            task_id = task_id_match.group(0) if task_id_match else "unknown"
            task_name = task_name_match.group(1) if task_name_match else "未命名任务"
            self.working_memory.init_task(task_id, task_name)
