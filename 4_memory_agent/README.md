# 第四周：记忆系统 Agent

## 项目目标

实现一个支持三种记忆（短期、长期、工作）的任务管理 Agent，专注于记忆系统的核心功能。

---

## 技术决策

| 决策项 | 选择 | 说明 |
|--------|------|------|
| 项目场景 | 任务管理 Agent | 创建、执行、查询任务，工具模拟 |
| 记忆范围 | 三种记忆全部实现 | 短期记忆 + 长期记忆 + 工作记忆 |
| 长期记忆存储 | 单独 JSON 文件 | 跨会话持久化，支持检索 |
| 短期/工作记忆存储 | 随 Session 存储 | 会话级生命周期，随会话清理 |
| 写入策略 | 混合策略 | 规则判断（快速）+ LLM 判断（智能） |
| 读取策略 | 按类型读取 | 短期/长期/工作分别读取 |
| 交互方式 | CLI + 多会话管理 | 可演示长期记忆跨会话效果 |

---

## 核心概念

### 1. 短期记忆（Short-term Memory）

**定义**：当前会话最近几轮的关键状态，关注意图和状态跟踪。

**存储内容**：
```
{
  "current_intent": "create_task",      # 当前意图
  "intent_context": {...},              # 意图相关上下文
  "recent_topics": ["任务创建", "天气"], # 最近话题
  "last_updated": "2024-01-15 10:30:00"
}
```

**生命周期**：会话级，会话结束清除。

**更新时机**：
- 用户意图切换时（规则判断）
- 检测到状态变更时（规则/LLM判断）

---

### 2. 长期记忆（Long-term Memory）

**定义**：跨会话持久化的重要信息，存储用户偏好、重要事实、历史决策。

**存储内容**：
```
{
  "user_preferences": {
    "default_priority": "high",
    "preferred_task_type": "code_review"
  },
  "important_facts": [
    {"content": "用户喜欢简洁的回复", "timestamp": "..."},
    {"content": "用户是 Python 开发者", "timestamp": "..."}
  ],
  "key_decisions": [
    {"decision": "选择 SQLite 作为存储", "reason": "...", "timestamp": "..."}
  ]
}
```

**生命周期**：永久持久化，跨会话复用。

**写入触发**：
- 用户明确表达偏好（规则："我喜欢..."、"默认..."）
- LLM 判断为重要信息

---

### 3. 工作记忆（Working Memory）

**定义**：任务执行过程中的计划、进度、中间结果。

**存储内容**：
```
{
  "current_task": {
    "task_id": "task_001",
    "name": "代码审查",
    "status": "in_progress",
    "steps": [
      {"step": "获取待审查文件", "status": "completed"},
      {"step": "运行静态检查", "status": "in_progress"},
      {"step": "生成报告", "status": "pending"}
    ]
  },
  "intermediate_results": {
    "files_found": 5,
    "issues_detected": 3
  }
}
```

**生命周期**：任务级，任务完成/取消后清除。

**更新时机**：
- 任务创建时初始化
- 步骤完成时更新进度
- 任务结束时清理

---

## 核心功能列表

### 1. 任务管理功能（工具模拟）

- [ ] 创建任务（create_task）
- [ ] 执行任务（execute_task）
- [ ] 查询任务（query_task）
- [ ] 列出所有任务（list_tasks）

### 2. 短期记忆功能

- [ ] 意图识别与跟踪
- [ ] 意图上下文管理
- [ ] 话题列表维护
- [ ] 意图切换检测

### 3. 长期记忆功能

- [ ] 用户偏好存储
- [ ] 重要事实记录
- [ ] 关键决策保存
- [ ] 跨会话检索

### 4. 工作记忆功能

- [ ] 任务进度跟踪
- [ ] 步骤状态管理
- [ ] 中间结果存储
- [ ] 任务完成清理

### 5. 记忆写入功能

- [ ] 规则判断器（关键词触发）
- [ ] LLM 判断器（智能判断）
- [ ] 混合策略协调

### 6. 记忆读取功能

- [ ] 按类型读取接口
- [ ] 记忆注入到上下文
- [ ] Token 预算控制

### 7. 会话管理功能

- [ ] 创建新会话
- [ ] 列出所有会话
- [ ] 切换会话
- [ ] 删除会话
- [ ] 会话持久化

---

## 目录结构

```
4_memory_agent/
├── agent/
│   ├── __init__.py              # 包初始化
│   ├── agent.py                 # Agent 主类
│   └── message.py               # Message 消息类
├── memory/
│   ├── __init__.py              # 包初始化
│   ├── base.py                  # 记忆基类
│   ├── short_term.py            # 短期记忆
│   ├── long_term.py             # 长期记忆
│   ├── working.py               # 工作记忆
│   ├── writer.py                # 记忆写入器
│   └── reader.py                # 记忆读取器
├── tools/
│   ├── __init__.py              # 包初始化
│   ├── base.py                  # 工具基类
│   ├── task_tools.py            # 任务工具（模拟）
│   └── tool_registry.py         # 工具注册
├── session/
│   ├── __init__.py              # 包初始化
│   ├── models.py                # Session 数据模型
│   ├── session_store.py         # 会话存储（JSON 文件）
│   ├── conversation_manager.py  # 会话管理器
│   └── session_status.py        # 会话状态枚举
├── data/
│   ├── sessions/                # 会话 JSON 文件存储目录
│   └── long_term_memory.json    # 长期记忆存储文件
├── main.py                      # CLI 主程序
├── requirements.txt             # 依赖包
└── README.md                    # 本文件
```

---

## 模块职责说明

### 1. agent/message.py - 消息模型

**Message 类**
```
字段：
  - role: str           # user / assistant / system / tool
  - content: str        # 消息内容
  - timestamp: datetime # 时间戳
  - tool_calls: list    # 工具调用（可选）
  - tool_call_id: str   # 工具调用ID（可选）
```

**需要实现的方法：**
- `to_dict()` - 转换为字典
- `from_dict(data)` - 从字典创建

---

### 2. memory/base.py - 记忆基类

**BaseMemory 类**

**需要实现的方法：**
- `update(data)` - 更新记忆
- `get()` - 获取记忆内容
- `clear()` - 清除记忆
- `to_dict()` - 序列化
- `from_dict(data)` - 反序列化

---

### 3. memory/short_term.py - 短期记忆

**ShortTermMemory 类**
```
字段：
  - current_intent: str       # 当前意图
  - intent_context: dict      # 意图上下文
  - recent_topics: list       # 最近话题列表
  - last_updated: datetime    # 最后更新时间
```

**需要实现的方法：**
- `update_intent(intent, context)` - 更新意图
- `add_topic(topic)` - 添加话题
- `clear_intent()` - 清除意图
- `get_context_summary()` - 获取上下文摘要

---

### 4. memory/long_term.py - 长期记忆

**LongTermMemory 类**
```
字段：
  - user_preferences: dict      # 用户偏好
  - important_facts: list       # 重要事实
  - key_decisions: list         # 关键决策
```

**需要实现的方法：**
- `add_preference(key, value)` - 添加偏好
- `add_fact(content, metadata)` - 添加事实
- `add_decision(decision, reason)` - 添加决策
- `get_relevant(query)` - 检索相关记忆
- `save()` - 保存到文件
- `load()` - 从文件加载

---

### 5. memory/working.py - 工作记忆

**WorkingMemory 类**
```
字段：
  - current_task: dict        # 当前任务
  - task_steps: list          # 任务步骤
  - intermediate_results: dict # 中间结果
```

**需要实现的方法：**
- `init_task(task_id, name)` - 初始化任务
- `update_step(step_name, status)` - 更新步骤状态
- `store_result(key, value)` - 存储中间结果
- `complete_task()` - 完成任务
- `clear()` - 清除工作记忆

---

### 6. memory/writer.py - 记忆写入器

**MemoryWriter 类**

**职责：** 判断是否需要更新记忆，执行写入

**需要实现的方法：**
- `should_update_short_term(input, response)` - 判断是否更新短期记忆
- `should_update_long_term(input, response)` - 判断是否更新长期记忆
- `should_update_working(input, response)` - 判断是否更新工作记忆
- `write_memory(memory_type, data)` - 执行写入

**混合策略实现：**
```python
def should_update_long_term(self, user_input, assistant_response):
    # 第一步：规则判断（快速）
    preference_keywords = ["我喜欢", "默认", "以后", "总是"]
    if any(kw in user_input for kw in preference_keywords):
        return True, "preference"
    
    # 第二步：LLM 判断（智能）
    return self._llm_judge(user_input, assistant_response)
```

---

### 7. memory/reader.py - 记忆读取器

**MemoryReader 类**

**职责：** 按类型读取记忆，组装到上下文

**需要实现的方法：**
- `read_short_term()` - 读取短期记忆
- `read_long_term(query)` - 读取相关长期记忆
- `read_working()` - 读取工作记忆
- `build_memory_context(query)` - 组装记忆上下文

**上下文组装示例：**
```python
def build_memory_context(self, query):
    context = []
    
    # 长期记忆（相关偏好和事实）
    long_term = self.read_long_term(query)
    if long_term:
        context.append(f"[用户偏好] {long_term.get('preferences')}")
    
    # 工作记忆（当前任务状态）
    working = self.read_working()
    if working:
        context.append(f"[当前任务] {working.get('current_task')}")
    
    # 短期记忆（当前意图）
    short_term = self.read_short_term()
    if short_term:
        context.append(f"[当前意图] {short_term.get('current_intent')}")
    
    return "\n".join(context)
```

---

### 8. tools/task_tools.py - 任务工具

**CreateTaskTool**
```
功能：创建任务
参数：
  - task_name: str    # 任务名称
  - priority: str     # 优先级（high/medium/low）
返回：task_id, status
```

**ExecuteTaskTool**
```
功能：执行任务
参数：
  - task_id: str      # 任务ID
返回：execution_result, status
```

**QueryTaskTool**
```
功能：查询任务
参数：
  - task_id: str      # 任务ID（可选，不传则查询所有）
返回：task_info
```

**ListTasksTool**
```
功能：列出所有任务
参数：无
返回：tasks_list
```

---

### 9. agent/agent.py - Agent 主类

**Agent 类**

**职责：** 协调记忆、工具、会话，处理对话

**需要实现的方法：**
- `__init__()` - 初始化（记忆、工具、会话管理器）
- `chat(user_input)` - 处理用户输入
- `_build_context()` - 组装上下文（Prompt + 记忆 + 历史）
- `_call_llm()` - 调用 LLM
- `_handle_tool_calls()` - 处理工具调用
- `_update_memories()` - 更新记忆

---

### 10. main.py - CLI 主程序

**需要实现的命令：**
- `new` - 创建新会话
- `list` - 列出所有会话
- `switch <id>` - 切换会话
- `delete <id>` - 删除会话
- `memory` - 查看当前记忆状态
- `help` - 显示帮助
- `exit` - 退出

---

## 验收标准

### 功能验收

- [ ] 能创建、执行、查询任务
- [ ] 任务工具能正确模拟调用
- [ ] 多会话能正常切换和管理

### 短期记忆验收

- [ ] 能识别和跟踪用户意图
- [ ] 意图切换时能正确更新
- [ ] 会话结束时自动清除

### 长期记忆验收

- [ ] 能存储用户偏好
- [ ] 能跨会话检索
- [ ] 能正确持久化到文件

### 工作记忆验收

- [ ] 任务创建时能初始化
- [ ] 能跟踪任务进度
- [ ] 任务完成时能清理

### 写入策略验收

- [ ] 规则判断能正确触发
- [ ] LLM 判断能智能识别
- [ ] 混合策略能协调工作

### 读取策略验收

- [ ] 能按类型读取记忆
- [ ] 记忆能正确注入上下文
- [ ] 不同会话的记忆隔离正确

### 代码质量

- [ ] 代码结构清晰，职责分离
- [ ] 有适当的注释和文档
- [ ] 变量命名规范

---

## 实现顺序建议

### Phase 1: 基础框架（复用第三周）

1. **数据模型层**
   - message.py
   - session_status.py
   - models.py

2. **存储层**
   - session_store.py

3. **会话管理**
   - conversation_manager.py

### Phase 2: 记忆系统核心

4. **记忆基类**
   - memory/base.py

5. **三种记忆实现**
   - memory/short_term.py
   - memory/long_term.py
   - memory/working.py

6. **记忆读写**
   - memory/writer.py
   - memory/reader.py

### Phase 3: 工具层

7. **任务工具**
   - tools/base.py
   - tools/task_tools.py
   - tools/tool_registry.py

### Phase 4: Agent 层

8. **Agent 主类**
   - agent/agent.py
   - 集成记忆、工具、会话

### Phase 5: CLI 层

9. **CLI 主程序**
   - main.py
   - 新增 memory 命令

### Phase 6: 测试验收

10. **测试验收**
    - 运行 CLI 测试所有功能
    - 验证记忆系统
    - 验证跨会话能力

---

## 使用示例

```bash
# 启动程序
python main.py

# 创建新会话
> new
Created session: session_abc123

# 创建任务
> 帮我创建一个代码审查任务
Agent: 好的，已创建任务 task_001（代码审查），优先级默认为 high。

# 查询任务
> 查询我的任务
Agent: 您有 1 个任务：
  - task_001: 代码审查 (status: pending, priority: high)

# 执行任务
> 执行 task_001
Agent: 正在执行任务 task_001...
  步骤 1/3: 获取待审查文件 ✓
  步骤 2/3: 运行静态检查 ✓
  步骤 3/3: 生成报告 ✓
  任务完成！发现 3 个问题。

# 查看记忆状态
> memory
[短期记忆]
  当前意图: query_task
  最近话题: 任务管理

[长期记忆]
  用户偏好: default_priority=high

[工作记忆]
  当前任务: task_001 (completed)

# 创建新会话，测试长期记忆跨会话
> new
Created session: session_def456

# 长期记忆仍然存在
> 创建一个测试任务
Agent: 好的，已创建任务 task_002（测试），优先级使用您的默认设置 high。

# 切换回第一个会话
> switch session_abc123
Switched to session: session_abc123

# 短期记忆和工作记忆恢复到该会话状态
> memory
[短期记忆]
  当前意图: execute_task
  最近话题: 任务执行

[工作记忆]
  当前任务: task_001 (completed)

# 退出
> exit
Sessions saved. Long-term memory saved. Bye!
```

---

## 注意事项

1. **环境变量**：需要在 `.env` 文件中配置 `OPENAI_API_KEY`
2. **数据目录**：
   - `data/sessions/` 目录存储会话
   - `data/long_term_memory.json` 存储长期记忆
3. **记忆隔离**：
   - 长期记忆：全局共享
   - 短期/工作记忆：会话隔离
4. **工具模拟**：任务工具仅模拟执行，返回固定格式的结果

---

## 学习重点

通过本项目，你将掌握：

1. ✅ 三种记忆的概念和区别
2. ✅ 记忆的生命周期管理
3. ✅ 混合写入策略的实现
4. ✅ 按类型读取记忆的方法
5. ✅ 记忆与上下文的组装
6. ✅ 长期记忆的跨会话能力

---

## 下一周预告

第五周将在本周基础上，增加：
- 多 Agent 协作
- Agent 间通信
- 任务拆分与分发
