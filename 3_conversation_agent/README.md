# 第三周：多轮对话与会话管理 Agent

## 项目目标

实现一个支持多会话管理的对话 Agent，专注于会话管理的核心功能。

---

## 技术决策

| 决策项 | 选择 | 说明 |
|--------|------|------|
| 存储方式 | JSON 文件 + 内存缓存 | 简单、易调试、适合学习 |
| History 管理 | 简单截断 | 保留最近 N 轮（默认 10 轮） |
| 状态管理 | 5 种标准状态 | completed、waiting_for_user、waiting_for_tool、suspended、failed |
| 模块划分 | 分离式 | SessionStore（存储层）+ ConversationManager（业务层） |
| 交互方式 | 命令行 CLI | 专注核心逻辑 |
| 功能范围 | 极简 Agent | 无工具、无规则，只专注会话管理 |

---

## 核心功能列表

### 1. 会话管理功能

- [ ] 创建新会话
- [ ] 列出所有会话
- [ ] 切换会话
- [ ] 删除会话
- [ ] 查看当前会话状态
- [ ] 查看当前会话历史

### 2. 历史管理功能

- [ ] 保存对话历史
- [ ] 自动截断历史（保留最近 N 轮）
- [ ] 可配置截断阈值

### 3. 状态管理功能

- [ ] 定义 5 种会话状态
- [ ] 更新会话状态
- [ ] 状态持久化

### 4. 持久化功能

- [ ] 保存会话到 JSON 文件
- [ ] 从 JSON 文件加载会话
- [ ] 程序重启后恢复所有会话
- [ ] 删除会话文件

### 5. 对话功能

- [ ] 极简 Agent（只调用 LLM）
- [ ] 多轮对话
- [ ] 上下文保持

---

## 目录结构

```
3_conversation_agent/
├── agent/
│   ├── __init__.py          # 包初始化
│   ├── agent.py             # 极简 Agent 类
│   └── message.py           # Message 消息类
├── session/
│   ├── __init__.py          # 包初始化
│   ├── models.py            # Session 数据模型
│   ├── session_store.py     # 会话存储（JSON 文件）
│   ├── conversation_manager.py  # 会话管理器
│   └── session_status.py    # 会话状态枚举
├── data/
│   └── sessions/            # 会话 JSON 文件存储目录
├── main.py                  # CLI 主程序
├── requirements.txt         # 依赖包
└── README.md                # 本文件
```

---

## 模块职责说明

### 1. agent/message.py - 消息模型

**Message 类**
```
字段：
  - role: str           # user / assistant / system
  - content: str        # 消息内容
  - timestamp: datetime # 时间戳
```

**需要实现的方法：**
- `to_dict()` - 转换为字典
- `from_dict(data)` - 从字典创建

---

### 2. session/session_status.py - 会话状态

**SessionStatus 枚举**
```
枚举值：
  - COMPLETED: 已完成
  - WAITING_FOR_USER: 等待用户输入
  - WAITING_FOR_TOOL: 等待工具结果
  - SUSPENDED: 挂起
  - FAILED: 失败
```

---

### 3. session/models.py - 会话模型

**Session 类**
```
字段：
  - session_id: str         # 会话唯一标识
  - user_id: str            # 用户标识
  - messages: List[Message] # 消息历史
  - status: SessionStatus   # 当前状态
  - created_at: datetime    # 创建时间
  - updated_at: datetime    # 更新时间
  - title: str              # 会话标题
```

**需要实现的方法：**
- `to_dict()` - 转换为字典
- `from_dict(data)` - 从字典创建
- `add_message(role, content)` - 添加消息
- `update_status(status)` - 更新状态

---

### 4. session/session_store.py - 会话存储

**SessionStore 类**

**职责：** 只管存取，不管业务逻辑

**需要实现的方法：**
- `__init__(data_dir)` - 初始化存储目录
- `save_session(session)` - 保存会话到 JSON 文件
- `load_session(session_id)` - 从文件加载会话
- `delete_session(session_id)` - 删除会话文件
- `list_sessions()` - 列出所有会话 ID
- `session_exists(session_id)` - 检查会话是否存在

---

### 5. session/conversation_manager.py - 会话管理器

**ConversationManager 类**

**职责：** 管理会话的业务逻辑

**需要实现的方法：**
- `__init__(session_store)` - 初始化管理器
- `create_session(user_id)` - 创建新会话
- `get_session(session_id)` - 获取指定会话
- `switch_session(session_id)` - 切换当前会话
- `delete_session(session_id)` - 删除会话
- `add_message(session_id, role, content)` - 添加消息
- `get_current_session()` - 获取当前会话
- `list_all_sessions()` - 列出所有会话
- `truncate_history(session_id, max_turns)` - 截断历史
- `update_status(session_id, status)` - 更新会话状态

---

### 6. agent/agent.py - 极简 Agent

**Agent 类**

**职责：** 只做最基础的 LLM 调用

**需要实现的方法：**
- `__init__()` - 初始化 Agent
- `chat(user_input, messages)` - 调用 LLM 生成回复

---

### 7. main.py - CLI 主程序

**需要实现的命令：**
- `new` - 创建新会话
- `list` - 列出所有会话
- `switch <id>` - 切换到指定会话
- `delete <id>` - 删除指定会话
- `status` - 查看当前会话状态
- `history` - 查看当前会话历史
- `help` - 显示帮助
- `exit` - 退出并保存

**需要实现的逻辑：**
- 命令解析
- 会话管理器初始化
- Agent 初始化
- 循环读取用户输入
- 调用 Agent 生成回复
- 保存会话

---

## 验收标准

### 功能验收
- [ ] 能创建多个会话（至少 3 个）
- [ ] 能在不同会话间切换
- [ ] 不同会话的消息互不干扰
- [ ] 能删除指定会话
- [ ] 能查看当前会话的历史和状态
- [ ] 能列出所有会话

### 历史管理验收
- [ ] 历史消息超过阈值时自动截断
- [ ] 截断后仍能正常对话
- [ ] 截断参数可配置（默认 10 轮）

### 持久化验收
- [ ] 程序退出时会话自动保存
- [ ] 程序重启后能恢复所有会话
- [ ] 会话数据不丢失

### 状态管理验收
- [ ] 会话状态能正确设置和更新
- [ ] 状态变更后能正确保存
- [ ] 恢复会话时状态正确

### 代码质量
- [ ] 代码结构清晰，职责分离
- [ ] 有适当的注释和文档
- [ ] 变量命名规范

---

## 实现顺序建议

1. **数据模型层**
   - message.py
   - session_status.py
   - models.py

2. **存储层**
   - session_store.py

3. **业务层**
   - conversation_manager.py

4. **Agent 层**
   - agent.py

5. **CLI 层**
   - main.py

6. **测试验收**
   - 运行 CLI 测试所有功能
   - 验证持久化
   - 验证多会话管理

---

## 使用示例

```bash
# 启动程序
python main.py

# 创建新会话
> new
Created session: session_abc123

# 列出所有会话
> list
[1] session_abc123 (active, 0 messages)

# 开始对话
> 你好
Agent: 你好！有什么可以帮你的？

> 今天天气怎么样
Agent: 抱歉，我没有实时天气数据，但我可以陪你聊天。

# 查看状态
> status
Session: session_abc123
Status: completed
Messages: 4 messages

# 创建另一个会话
> new
Created session: session_def456

# 切换回第一个会话
> switch session_abc123
Switched to session: session_abc123

# 退出
> exit
Sessions saved. Bye!
```

---

## 注意事项

1. **环境变量**：需要在 `.env` 文件中配置 `OPENAI_API_KEY`
2. **数据目录**：`data/sessions/` 目录需要有写权限
3. **截断阈值**：默认保留最近 10 轮对话，可在代码中修改
4. **会话 ID**：使用 UUID 或时间戳生成唯一 ID

---

## 学习重点

通过本项目，你将掌握：

1. ✅ Session 的概念和设计
2. ✅ 多会话管理的实现
3. ✅ 历史消息的处理策略（截断）
4. ✅ 会话状态的流转
5. ✅ 持久化和恢复机制
6. ✅ 分层设计思想（存储层 vs 业务层）

---

## 下一周预告

第四周将在本周基础上，增加：
- 短期记忆、长期记忆、工作记忆
- 记忆的存储和检索
- 记忆与会话的结合
