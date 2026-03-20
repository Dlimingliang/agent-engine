class RuleEngine:
    """规则引擎"""
    
    def __init__(self):
        self.safe_rules: list[str] = []
        self.product_rules: list[str] = []

    def add_rule(self, rule: str, level: str):
        """添加规则"""
        if level == "safe":
            self.safe_rules.append(rule)
        else:
            self.product_rules.append(rule)

    def rule_compose(self) -> str:
        """将所有规则拼接为 prompt 片段"""
        parts: list[str] = []
        if self.safe_rules:
            rules_text = "\n".join(f"- {rule}" for rule in self.safe_rules)
            parts.append(f"\n## 安全规则\n{rules_text}")
        if self.product_rules:
            rules_text = "\n".join(f"- {rule}" for rule in self.product_rules)
            parts.append(f"\n## 产品规则\n{rules_text}")
        return "\n".join(parts)