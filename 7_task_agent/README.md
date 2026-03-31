# 第七周：计划、执行、验证、重试

## 项目目标

实现一个具备任务执行能力的 Agent，能够将复杂任务拆解为步骤，逐步执行并验证结果，失败后能够智能恢复。

---

## 技术决策

| 决策项 | 选择 | 说明 |
|--------|------|------|
| 项目场景 | Task Agent | 复杂任务执行、计划生成、失败恢复 |
| 计划生成 | LLM 驱动 | 使用 LLM 分析任务并生成步骤 |
| 执行模式 | Plan-Execute | 先规划后执行，支持状态追踪 |
| 验证策略 | 多层验证 | 格式验证、结果验证、质量验证 |
| 重试策略 | 分类重试 | 立即重试、延迟重试、降级重试 |
| 状态管理 | 状态机 | 严格的状态转换规则 |
| 错误恢复 | 智能决策 | 错误注入消息流，LLM 辅助决策 |

---

## 核心概念

### 1. Plan-and-Execute（计划与执行）

**定义**：复杂任务先拆解为步骤，再逐步执行。

**为什么需要？**
- ✅ 可追踪：知道当前执行到哪一步
- ✅ 可恢复：中途失败可以从某一步继续
- ✅ 可调试：知道哪一步出了问题
- ✅ 可验证：每一步都可以单独验证

**执行流程**：
```
用户任务 → Planner 生成计划 → Executor 逐步执行
    ↓
每步执行 → Verifier 验证结果 → 成功/失败
    ↓
失败 → RetryHandler 决定策略 → 重试/改计划/人工介入
```

---

### 2. Verifier（验证器）

**定义**：验证工具执行结果是否真正达成目标。

**三个验证层次**：

| 层次 | 验证内容 | 示例 |
|------|---------|------|
| 格式验证 | 输出格式是否正确 | JSON 字段是否齐全 |
| 结果验证 | 是否真正达成目标 | 邮件是否真的发送 |
| 质量验证 | 输出质量是否达标 | 报告是否足够详细 |

**验证流程**：
```python
result = tool.execute(args)
verification = verifier.verify(step, result)

if verification.success:
    # 进入下一步
else:
    # 触发重试或改计划
```

---

### 3. Retry（重试策略）

**定义**：失败后选择合适的恢复策略。

**三种重试类型**：

| 类型 | 适用场景 | 策略 |
|------|---------|------|
| 立即重试 | 临时性错误 | 直接重试，无延迟 |
| 延迟重试 | 需要等待 | 延迟 N 秒后重试 |
| 降级重试 | 主服务不可用 | 切换备用工具 |

**三种恢复路径**：
1. **重试**：同样的步骤再试一次
2. **改计划**：换一种执行方式
3. **人工介入**：让用户决策

**重试原则**：
- 幂等性：重试不会产生副作用
- 指数退避：延迟时间递增
- 有界重试：最大重试次数限制

---

### 4. 工具失败恢复

**定义**：错误信息作为新信息，进入决策流程。

**恢复流程**：
```
Tool Error → 标准化错误 → 注入消息流 → LLM 决策 → 继续执行
```

**四种错误类型**：

| 错误类型 | 恢复策略 |
|---------|---------|
| 工具不存在 | 找替代工具或改计划 |
| 参数错误 | LLM 修正参数 |
| 执行错误 | 重试或降级 |
| 输出不符 | 重新解析或请求澄清 |

---

### 5. 任务状态机

**定义**：管理任务的生命周期状态，确保状态转换合法。

**任务状态**：
```
PENDING        - 待执行
PLANNING       - 正在制定计划
EXECUTING      - 正在执行
VERIFYING      - 正在验证
WAITING_USER   - 等待用户确认
COMPLETED      - 已完成
FAILED         - 失败
CANCELLED      - 已取消
PAUSED         - 已暂停
```

**状态转换图**：
```
PENDING → PLANNING → EXECUTING → VERIFYING → COMPLETED
                         ↓              ↓
                    WAITING_USER    FAILED → 重试
                         ↓
                      PAUSED
```

---

## 核心功能列表

### 1. 计划生成功能

- [ ] 根据任务描述生成执行计划
- [ ] 每个步骤包含工具名、参数、预期输出
- [ ] 支持根据反馈更新计划
- [ ] 计划格式结构化（JSON Schema）

### 2. 执行功能

- [ ] 逐步执行计划中的每个步骤
- [ ] 调用对应工具并获取结果
- [ ] 更新步骤状态
- [ ] 记录执行日志

### 3. 验证功能

- [ ] 格式验证：检查输出格式
- [ ] 结果验证：检查是否达成目标
- [ ] 质量验证：检查输出质量
- [ ] 返回验证结果和建议

### 4. 重试功能

- [ ] 判断错误类型
- [ ] 选择重试策略（立即/延迟/降级）
- [ ] 记录重试次数
- [ ] 超过最大次数触发改计划

### 5. 错误恢复功能

- [ ] 标准化错误信息
- [ ] 将错误注入消息流
- [ ] LLM 辅助决策恢复路径
- [ ] 支持跳过步骤或请求用户

### 6. 状态管理功能

- [ ] 维护任务整体状态
- [ ] 维护每个步骤状态
- [ ] 状态转换合法性检查
- [ ] 提供状态查询接口

---

## 目录结构

```
7_task_agent/
├── agent/
│   ├── __init__.py              # 包初始化
│   ├── task_agent.py            # Task Agent 主类
│   ├── planner.py               # 计划生成器
│   ├── executor.py              # 执行器
│   └── verifier.py              # 验证器
├── state/
│   ├── __init__.py              # 包初始化
│   ├── task_state.py            # 任务状态机
│   └── task_tracker.py          # 任务跟踪器
├── recovery/
│   ├── __init__.py              # 包初始化
│   ├── retry_handler.py         # 重试处理器
│   └── error_recovery.py        # 错误恢复处理器
├── tools/
│   ├── __init__.py              # 包初始化
│   ├── tool_registry.py         # 工具注册
│   ├── calculator.py            # 计算工具
│   ├── file_tool.py             # 文件工具
│   └── web_tool.py              # 网页工具
├── trace/
│   ├── __init__.py              # 包初始化
├── tests/
│   └── test_task_agent.py       # 测试用例
├── main.py                      # CLI 主程序
├── requirements.txt             # 依赖包
└── README.md                    # 本文件
```

---

## 模块职责说明

### 1. agent/planner.py - 计划生成器

**Planner 类**

**职责**：根据任务描述生成结构化执行计划

**需要实现的方法**：
```python
class Planner:
    def __init__(self, model: str = None):
        """初始化计划生成器"""
        
    def create_plan(self, task: str, available_tools: List[str]) -> ExecutionPlan:
        """生成执行计划"""
        
    def update_plan(self, plan: ExecutionPlan, feedback: str) -> ExecutionPlan:
        """根据反馈更新计划"""
```

---

### 2. agent/executor.py - 执行器

**Executor 类**

**职责**：逐步执行计划中的步骤

**需要实现的方法**：
```python
class Executor:
    def __init__(self, tool_registry: ToolRegistry):
        """初始化执行器"""
        
    def execute_step(self, step: TaskStep) -> dict:
        """执行单个步骤"""
        
    def execute_plan(self, plan: ExecutionPlan) -> ExecutionPlan:
        """执行整个计划"""
```

---

### 3. agent/verifier.py - 验证器

**Verifier 类**

**职责**：验证执行结果

**需要实现的方法**：
```python
class Verifier:
    def verify(self, step: TaskStep, result: dict) -> VerificationResult:
        """验证执行结果"""
        
    def _verify_format(self, result: dict) -> bool:
        """格式验证"""
        
    def _verify_result(self, step: TaskStep, result: dict) -> bool:
        """结果验证"""
```

---

### 4. state/task_state.py - 任务状态机

**TaskStateMachine 类**

**职责**：管理任务状态转换

**需要实现的方法**：
```python
class TaskStateMachine:
    def __init__(self):
        """初始化状态机"""
        
    def transition(self, new_status: TaskStatus, reason: str) -> bool:
        """状态转换"""
        
    def can_transition_to(self, new_status: TaskStatus) -> bool:
        """检查是否可以转换"""
        
    def get_allowed_actions(self) -> Set[str]:
        """获取允许的动作"""
```

---

### 5. state/task_tracker.py - 任务跟踪器

**TaskTracker 类**

**职责**：跟踪任务执行进度

**需要实现的方法**：
```python
class TaskTracker:
    def __init__(self, task_id: str):
        """初始化跟踪器"""
        
    def update_step_status(self, step_id: int, status: TaskStatus, result: dict):
        """更新步骤状态"""
        
    def get_progress(self) -> dict:
        """获取进度信息"""
        
    def get_summary(self) -> str:
        """获取任务摘要"""
```

---

### 6. recovery/retry_handler.py - 重试处理器

**RetryHandler 类**

**职责**：处理重试逻辑

**需要实现的方法**：
```python
class RetryHandler:
    def __init__(self, max_retries: int = 3):
        """初始化重试处理器"""
        
    def should_retry(self, step: TaskStep, error: Exception) -> RetryStrategy:
        """判断是否应该重试"""
        
    def execute_with_retry(self, step: TaskStep, executor: Callable) -> Any:
        """带重试的执行"""
```

---

### 7. recovery/error_recovery.py - 错误恢复处理器

**ErrorRecovery 类**

**职责**：处理工具失败后的恢复

**需要实现的方法**：
```python
class ErrorRecovery:
    def __init__(self, llm):
        """初始化错误恢复处理器"""
        
    def normalize_error(self, step: TaskStep, error: Exception) -> ToolError:
        """标准化错误"""
        
    def inject_error_to_messages(self, messages: List[dict], error: ToolError) -> List[dict]:
        """将错误注入消息流"""
        
    def recover(self, step: TaskStep, error: Exception, context: dict) -> dict:
        """执行恢复"""
```

---

### 8. agent/task_agent.py - Task Agent 主类

**TaskAgent 类**

**职责**：协调所有组件，完成复杂任务

**需要实现的方法**：
```python
class TaskAgent:
    def __init__(self, name: str, tool_registry: ToolRegistry):
        """初始化 Agent"""
        
    def process(self, task: str) -> TaskResult:
        """处理任务"""
        
    def _run_plan_execute_loop(self, plan: ExecutionPlan) -> TaskResult:
        """执行计划-执行循环"""
        
    def _handle_step_failure(self, step: TaskStep, error: Exception) -> str:
        """处理步骤失败"""
```

---

## 验收标准

### 功能验收

- [ ] 能生成合理的执行计划
- [ ] 能逐步执行计划中的步骤
- [ ] 能验证执行结果
- [ ] 能处理工具调用失败
- [ ] 能根据失败情况选择恢复策略

### 任务验收

- [ ] 至少能稳定完成 3 个多步骤任务
- [ ] 任务执行过程可追踪
- [ ] 失败后能继续而不是直接结束
- [ ] 能正确区分不同类型的错误

### 代码质量

- [ ] 代码结构清晰，职责分离
- [ ] 有适当的注释和文档
- [ ] 状态转换逻辑正确
- [ ] 错误处理完善

---

## 实现顺序建议

### Phase 1: 基础架构

1. **状态管理**
   - state/task_state.py
   - state/task_tracker.py

2. **工具层**
   - tools/tool_registry.py
   - tools/calculator.py
   - tools/file_tool.py
   - tools/web_tool.py

### Phase 2: 核心组件

3. **计划生成器**
   - agent/planner.py（已创建）

4. **执行器**
   - agent/executor.py

5. **验证器**
   - agent/verifier.py

### Phase 3: 恢复机制

6. **重试处理器**
   - recovery/retry_handler.py

7. **错误恢复**
   - recovery/error_recovery.py

### Phase 4: Agent 集成

8. **Task Agent**
   - agent/task_agent.py

### Phase 5: 测试和 CLI

9. **CLI 主程序**
    - main.py

---

## 使用示例

```bash
# ========== 1. 启动 Agent ==========

python main.py

# ========== 2. 任务执行 ==========

> 计算斐波那契数列的第10项，并将结果保存到文件
🧠 Planner 正在生成执行计划...
✅ 计划生成成功，共 3 个步骤
  步骤 1: 计算斐波那契数列第10项 (工具: calculator)
  步骤 2: 格式化结果 (工具: formatter)
  步骤 3: 保存到文件 (工具: file_write)

执行步骤 1/3...
✅ 步骤 1 完成: fib(10) = 55

执行步骤 2/3...
✅ 步骤 2 完成: 已格式化

执行步骤 3/3...
🔍 正在验证...
✅ 验证通过: 文件已创建
✅ 步骤 3 完成

✅ 任务完成！
结果: 斐波那契数列第10项为 55，已保存到 fibonacci_10.txt

> 搜索 Python 最佳实践并生成报告
🧠 Planner 正在生成执行计划...
✅ 计划生成成功，共 4 个步骤
  步骤 1: 搜索相关内容 (工具: web_search)
  步骤 2: 抓取详细页面 (工具: web_fetch)
  步骤 3: 整理信息 (工具: formatter)
  步骤 4: 生成报告 (工具: file_write)

执行步骤 1/4...
❌ 步骤 1 失败: 网络超时
🔄 策略: 延迟重试 (等待 2 秒)
重试 1/3...
✅ 步骤 1 完成: 找到 5 篇相关文章

执行步骤 2/4...
✅ 步骤 2 完成: 已抓取 3 篇文章内容

执行步骤 3/4...
✅ 步骤 3 完成: 已整理要点

执行步骤 4/4...
🔍 正在验证...
✅ 验证通过: 报告包含必需章节
✅ 步骤 4 完成

✅ 任务完成！

> exit
Bye!
```

---

## 任务状态查询

```bash
> status

任务状态摘要
=============
任务ID: task_20240115_001
描述: 计算 Fibonacci 数列并保存
整体状态: COMPLETED
进度: 3/3 (100%)
失败步骤: 0

步骤详情:
[✅] 步骤 1: 计算 fib(10) - 已完成
[✅] 步骤 2: 格式化结果 - 已完成  
[✅] 步骤 3: 保存到文件 - 已完成
```

---

## 注意事项

1. **环境变量**：需要在 `.env` 文件中配置 LLM 相关配置
   ```
   LLM_MODEL_ID=your_model
   LLM_API_KEY=your_api_key
   LLM_BASE_URL=your_base_url
   ```

2. **工具注册**：确保所有需要的工具都已注册到 ToolRegistry

3. **状态一致性**：状态转换必须通过状态机，不能直接修改

4. **错误处理**：所有工具调用都应该有 try-except 包裹

5. **日志记录**：使用 trace 模块记录执行过程

---

## 学习重点

通过本项目，你将掌握：

1. ✅ Plan-and-Execute 模式的实现
2. ✅ 多层验证策略的设计
3. ✅ 智能重试机制的实现
4. ✅ 工具失败恢复的处理
5. ✅ 任务状态机的管理
6. ✅ 复杂任务的可追踪执行

---

## 常见问题

### Q1: 如何设计合理的执行计划？

关键点：
- 每个步骤应该是原子操作
- 步骤之间依赖关系清晰
- 每步都有明确的工具和参数
- 步骤数量适中（3-10 步）

### Q2: 验证失败后怎么办？

验证失败会触发：
1. 查看验证失败原因
2. 选择重试或改计划
3. 如果是质量问题，可能需要人工介入

### Q3: 如何避免无限重试？

设置最大重试次数（建议 3 次），超过后：
- 改计划：让 Planner 重新规划
- 请求人工：让用户决策

### Q4: 状态机的作用是什么？

确保：
- 状态转换合法
- 终态不可转换
- 动作与状态匹配
- 状态历史可追溯

### Q5: 如何处理用户中断？

支持 PAUSED 状态：
- 用户可以暂停任务
- 可以从中断点恢复
- 也可以取消任务

---

## 下一周预告

第八周将在本周基础上，增加：
- 可观测性（Trace 完整链路）
- 调试能力（Debug 面板）
- 评估系统（质量评估）
- 回放机制（失败案例回放）
