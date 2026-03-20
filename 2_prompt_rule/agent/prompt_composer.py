import json


class PromptComposer:
    def __init__(self,):
        self.system_prompt = ""
        self.tool_prompt = ""
        self.rule_prompt = ""
        self.output_prompt = ""
    def set_system_prompt(self, prompt):
        """设置系统提示词"""
        self.system_prompt = prompt
        return self
    def set_tool_prompt(self, prompt):
        """设置工具提示词"""
        self.tool_prompt = prompt
        return self
    def set_output_prompt(self, prompt):
        """设置输出格式"""
        self.output_prompt = prompt
        return self
    def set_rule_prompt(self, prompt):
        """设置规则提示"""
        self.rule_prompt = prompt
        return self
    def compose(self) -> str:
        parts = [self.system_prompt]
        if self.rule_prompt:
            parts.append("\n## 规则说明\n" + self.rule_prompt)
        if self.tool_prompt:
            parts.append("\n## 工具说明\n" + self.tool_prompt)
        if self.output_prompt:
            if isinstance(self.output_prompt, dict):
                output = json.dumps(self.output_prompt, indent=2, ensure_ascii=False, default=str)
            else:
                output = str(self.output_prompt)
            parts.append("\n## 输出格式要求\n"
                       "完成任务后,你必须返回纯JSON格式的数据,符合以下schema:\n"
                       f"{output}\n"
                       "注意:\n"
                       "- 只返回JSON数据,不要包含schema定义\n"
                       "- 不要添加任何额外的说明文字\n"
                       "- 确保JSON格式正确,可以被直接解析")
        return "\n".join(parts)