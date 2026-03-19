# Mini Agent Runtime

/**
 * @generated-by AI : matthewmli
 * @generated-date 2026-03-19
 */

第1周项目: 最小 Agent Runtime

## 项目结构

```
1_agent_runtime/
├── agent/           # Agent 核心实现
│   ├── __init__.py
│   ├── agent.py     # Agent 主类
│   └── message.py   # 消息数据结构
├── tools/           # 工具模块
│   ├── __init__.py
│   ├── registry.py  # 工具注册中心
│   └── builtins.py  # 内置工具实现
├── trace/           # Trace 模块
│   ├── __init__.py
│   └── tracer.py    # 执行追踪器
├── config.py        # 配置管理
├── main.py          # 入口文件
├── requirements.txt
├── .env.example
└── README.md
```

## 快速开始

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env .env
# 编辑 .env 填入你的 API Key

# 4. 运行
python main.py
```

## 本周目标

- [x] 消息模型理解
- [x] Agent 最小闭环
- [x] 工具 Schema
- [x] 结构化输出
- [x] Trace 基础
- [ ] 实现可运行的 Mini Agent

## 交付物

- Agent 主类
- Message 数据结构
- ToolRegistry
- 可读的 trace 日志
