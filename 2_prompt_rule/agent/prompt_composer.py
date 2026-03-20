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
            parts.append("\n## 必须按照如下要求输出 输出要求:\n" + output)
        return "\n".join(parts)