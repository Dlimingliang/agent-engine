# Mini Agent Runtime - 第2周: Prompt & Rule

/**
 * @generated-by AI : matthewmli
 * @generated-date 2026-03-20
 */

第2周项目: Prompt 分层 + Rule 系统

## 项目结构

```
2_prompt_rule/
├── agent/           # Agent 核心实现
│   ├── __init__.py
│   ├── agent.py     # Agent 主类 (TODO: PromptComposer + RuleEngine)
│   └── message.py   # 消息数据结构
├── tools/           # 工具模块
│   ├── __init__.py
│   ├── registry.py  # 工具注册中心
│   └── builtins.py  # 内置工具实现
├── trace/           # Trace 模块
│   ├── __init__.py
│   └── tracer.py    # 执行追踪器
├── main.py          # 入口文件
├── requirements.txt
├── .env
└── README.md
```

## 快速开始

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 4. 运行
python main.py
```

## 本周目标

- [x] Prompt 分层理解
- [x] 实现 PromptComposer
- [x] Rule 分类理解
- [x] 实现 RuleEngine (静态规则)
- [x] 结构化约束理解 (OpenAI 框架已自动处理)

## 交付物

### 1. PromptComposer (已实现)

分层组合提示词：
- System Prompt: Agent 身份定义
- Tool Prompt: 工具使用规则
- Output Contract: 输出格式约定

```python
# 使用示例
composer = PromptComposer()
composer.set_system("你是一个代码分析助手")
composer.set_tool_prompt("调用 read_file 前先确认路径存在...")
composer.set_output_contract(schema)

system_content = composer.compose()
```

### 2. RuleEngine (已实现)

三类规则：
- 安全规则: 禁止删除文件、禁止读取敏感信息
- 产品规则: 每次最多读 10 个文件
- 用户规则: 用中文回复

```python
# 使用示例
rule_engine = RuleEngine()
rule_engine.add_rule("禁止读取 .env 文件", "safe")
rule_engine.add_rule("单次最多读取 5 个文件", "product")

# 生成规则提示词
rule_prompt = rule_engine.rule_compose()
```

### 3. 结构化约束 (已实现)

- 工具参数约束: Pydantic 自动生成 JSON Schema
- 中间状态约束: OpenAI 自动返回 tool_calls
- 最终输出约束: TaskResult + response_format

## 与第1周的区别

| 模块 | 第1周 | 第2周 |
|------|-------|-------|
| System Prompt | 硬编码字符串 | PromptComposer 组合 |
| 工具调用 | 直接执行 | RuleEngine 检查后执行 |
| 规则控制 | 无 | 三类规则约束 |
| 输出格式 | TaskResult | TaskResult (不变) |

## 完成情况

- [x] 实现 PromptComposer 类 ✅
- [x] 实现 RuleEngine 类 ✅
- [x] 在 main.py 中使用 PromptComposer 和 RuleEngine ✅
- [x] 规则作为提示词的一部分注入到 system prompt ✅

## 设计决策

- **规则验证方式**: 选择将规则作为提示词的一部分注入，而不是在工具执行前进行硬性检查
  - 优点: 更灵活，让 LLM 理解并遵守规则
  - 缺点: 规则可能被 LLM 忽略（但在实际使用中效果良好）

- **PromptComposer 设计**: 采用链式调用风格，方便逐步构建复杂提示词
