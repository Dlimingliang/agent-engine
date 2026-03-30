# 第七周 TODO 清单

## 📋 项目初始化

- [ ] 安装依赖：`pip install -r requirements.txt`
- [ ] 配置 `.env` 文件（LLM 相关配置）
- [ ] 创建 `logs/` 目录用于存储追踪日志
- [ ] 创建 `data/` 目录用于存储临时文件

---

## 🔧 Phase 1: 基础架构（2-3 天）

### 状态管理模块

#### state/task_state.py
- [ ] 实现 `TaskStateMachine.__init__`
- [ ] 实现 `transition` 状态转换逻辑
- [ ] 实现 `can_transition_to` 检查方法
- [ ] 实现 `get_allowed_actions` 获取允许动作
- [ ] 实现 `is_terminal` 判断终态
- [ ] 实现 `can_execute`, `can_pause`, `can_cancel`, `can_retry`
- [ ] 实现 `get_history` 状态历史
- [ ] 实现 `reset` 重置方法
- [ ] 编写单元测试

#### state/task_tracker.py
- [ ] 实现 `generate_task_id` 生成任务 ID
- [ ] 实现 `update_overall_status` 更新整体状态
- [ ] 实现 `update_step_status` 更新步骤状态
- [ ] 实现 `get_progress` 获取进度信息
- [ ] 实现 `get_summary` 获取任务摘要
- [ ] 实现 `mark_step_started/completed/failed` 方法
- [ ] 实现 `is_all_steps_completed` 和 `has_failed_steps`
- [ ] 编写单元测试

### 工具模块

#### tools/tool_registry.py
- [ ] 实现 `Tool.get_openai_tool_schema`
- [ ] 实现 `ToolRegistry.__init__`
- [ ] 实现 `register` 和 `unregister`
- [ ] 实现 `get_tool` 和 `has_tool`
- [ ] 实现 `execute` 执行工具
- [ ] 实现 `get_all_tools` 和 `get_tool_names`
- [ ] 实现 `get_openai_tools` 返回 OpenAI 格式
- [ ] 实现 `find_alternative` 查找替代工具
- [ ] 编写单元测试

#### tools/calculator.py
- [ ] 实现 `CalculatorTool.__init__`
- [ ] 实现 `execute` 执行计算
- [ ] 实现 `_safe_eval` 安全计算
- [ ] 实现 `_format_result` 格式化结果
- [ ] 编写单元测试

#### tools/file_tool.py
- [ ] 实现 `FileReadTool.__init__`
- [ ] 实现 `FileReadTool.execute` 读取文件
- [ ] 实现 `FileWriteTool.__init__`
- [ ] 实现 `FileWriteTool.execute` 写入文件
- [ ] 实现 `_ensure_directory` 确保目录存在
- [ ] 实现 `_validate_path` 路径安全验证
- [ ] 编写单元测试

#### tools/web_tool.py
- [ ] 实现 `WebSearchTool.__init__`
- [ ] 实现 `execute` 搜索（模拟）
- [ ] 实现 `_mock_search` 模拟搜索结果
- [ ] 实现 `WebFetchTool.__init__`
- [ ] 实现 `execute` 抓取网页
- [ ] 实现 `_extract_text` 提取文本
- [ ] 实现 `_validate_url` URL 验证
- [ ] 实现 `_clean_content` 清理内容
- [ ] 编写单元测试

---

## 🎯 Phase 2: 核心组件（3-4 天）

### 计划生成器

#### agent/planner.py（已创建基础代码）
- [x] 实现 `Planner.__init__`
- [x] 实现 `create_plan` 生成计划
- [ ] 实现 `update_plan` 更新计划
- [ ] 优化系统提示词
- [ ] 添加计划验证逻辑
- [ ] 编写单元测试

### 执行器

#### agent/executor.py
- [ ] 实现 `Executor.__init__`
- [ ] 实现 `execute_step` 执行单步
- [ ] 实现 `execute_plan` 执行计划
- [ ] 实现 `_check_tool_exists` 检查工具
- [ ] 实现 `_record_execution` 记录执行
- [ ] 实现 `get_execution_history` 获取历史
- [ ] 编写单元测试

### 验证器

#### agent/verifier.py
- [ ] 实现 `Verifier.__init__`
- [ ] 实现 `verify` 主验证方法
- [ ] 实现 `_verify_format` 格式验证
- [ ] 实现 `_verify_result` 结果验证
- [ ] 实现 `_verify_quality` 质量验证
- [ ] 实现 `_verify_tool_specific` 工具特定验证
- [ ] 实现 `_verify_file_write` 文件写入验证
- [ ] 实现 `_verify_web_search` 搜索验证
- [ ] 实现 `_verify_calculation` 计算验证
- [ ] 编写单元测试

---

## 🔄 Phase 3: 恢复机制（2-3 天）

### 重试处理器

#### recovery/retry_handler.py
- [ ] 实现 `RetryHandler.__init__`
- [ ] 实现 `should_retry` 判断重试策略
- [ ] 实现 `execute_with_retry` 带重试执行
- [ ] 实现 `_get_delay_time` 指数退避
- [ ] 实现 `get_retry_count` 和 `reset_retry_count`
- [ ] 实现 `_classify_error` 错误分类
- [ ] 实现 `is_retriable_error` 判断可重试
- [ ] 编写单元测试

### 错误恢复处理器

#### recovery/error_recovery.py
- [ ] 实现 `ErrorRecovery.__init__`
- [ ] 实现 `normalize_error` 标准化错误
- [ ] 实现 `inject_error_to_messages` 注入错误
- [ ] 实现 `extract_recovery_action` 提取动作
- [ ] 实现 `recover` 执行恢复
- [ ] 实现 `find_alternative_tool` 查找替代工具
- [ ] 实现 `_is_retriable` 判断可重试
- [ ] 实现 `_build_recovery_prompt` 构建提示
- [ ] 编写单元测试

---

## 🤖 Phase 4: Agent 集成（3-4 天）

### Task Agent

#### agent/task_agent.py
- [ ] 实现 `TaskAgent.__init__`
- [ ] 实现 `process` 处理任务入口
- [ ] 实现 `_plan` 生成计划
- [ ] 实现 `_execute_plan` 执行计划
- [ ] 实现 `_execute_step` 执行单步
- [ ] 实现 `_verify_step` 验证步骤
- [ ] 实现 `_handle_failure` 处理失败
- [ ] 实现 `_should_continue` 判断是否继续
- [ ] 实现 `_build_final_result` 构建结果
- [ ] 实现 `get_task_status` 获取状态
- [ ] 实现 `pause_task` 暂停任务
- [ ] 实现 `resume_task` 恢复任务
- [ ] 实现 `cancel_task` 取消任务
- [ ] 编写集成测试

### 追踪器

#### trace/tracer.py
- [ ] 实现 `Tracer.__init__`
- [ ] 实现 `start_timer` 和 `_get_duration_ms`
- [ ] 实现 `log_user_input`
- [ ] 实现 `log_plan_generation`
- [ ] 实现 `log_step_start`
- [ ] 实现 `log_step_execution`
- [ ] 实现 `log_step_verification`
- [ ] 实现 `log_retry`
- [ ] 实现 `log_error`
- [ ] 实现 `log_status_change`
- [ ] 实现 `log_final_output`
- [ ] 实现 `summary` 生成摘要
- [ ] 实现 `get_traces` 获取追踪记录
- [ ] 实现 `save_to_file` 保存文件
- [ ] 实现 `get_statistics` 获取统计
- [ ] 编写单元测试

---

## 🖥️ Phase 5: CLI 和测试（1-2 天）

### CLI 主程序

#### main.py
- [ ] 实现 `setup_tools` 设置工具
- [ ] 实现 `setup_agent` 设置 Agent
- [ ] 实现 `print_welcome` 打印欢迎
- [ ] 实现 `main` 主循环
- [ ] 实现 `handle_special_command` 处理命令
- [ ] 实现 `print_task_result` 打印结果

### 测试

#### tests/test_task_agent.py
- [ ] 完善 `TestPlanner` 测试类
- [ ] 完善 `TestExecutor` 测试类
- [ ] 完善 `TestVerifier` 测试类
- [ ] 完善 `TestTaskStateMachine` 测试类
- [ ] 完善 `TestTaskTracker` 测试类
- [ ] 完善 `TestRetryHandler` 测试类
- [ ] 完善 `TestErrorRecovery` 测试类
- [ ] 完善 `TestToolRegistry` 测试类
- [ ] 完善 `TestCalculatorTool` 测试类
- [ ] 完善 `TestFileTools` 测试类
- [ ] 完善 `TestTaskAgent` 测试类

---

## ✅ 验收测试

### 功能验收
- [ ] 能生成合理的执行计划
- [ ] 能逐步执行计划中的步骤
- [ ] 能验证执行结果
- [ ] 能处理工具调用失败
- [ ] 能根据失败情况选择恢复策略

### 任务验收
- [ ] 完成至少 3 个多步骤任务
- [ ] 任务执行过程可追踪
- [ ] 失败后能继续而不是直接结束
- [ ] 能正确区分不同类型的错误

### 测试验收
- [ ] 所有单元测试通过
- [ ] 测试覆盖率 > 80%
- [ ] 集成测试通过

---

## 📝 实现建议

### 开发顺序

1. **先实现工具层**：确保工具可以独立运行
2. **再实现状态管理**：状态机是核心基础
3. **然后实现执行器**：能执行步骤
4. **再实现验证器**：能验证结果
5. **接着实现重试和恢复**：能处理失败
6. **最后集成 Agent**：组合所有组件

### 调试技巧

1. 使用 `print` 或 `logging` 记录执行过程
2. 先测试单个组件，再集成测试
3. 使用模拟数据测试边界情况
4. 保存追踪日志用于分析问题

### 常见问题

1. **状态转换失败**：检查 VALID_TRANSITIONS 配置
2. **工具执行失败**：检查参数格式和工具实现
3. **重试无限循环**：检查 max_retries 设置
4. **验证总是失败**：检查验证逻辑和预期结果

---

## 🎯 预期成果

完成本项目后，你将获得：

1. ✅ 一个可运行的 Task Agent
2. ✅ 完整的计划-执行-验证流程
3. ✅ 智能的重试和恢复机制
4. ✅ 可追踪的任务执行过程
5. ✅ 完善的单元测试和集成测试

---

## 📚 学习资源

- OpenAI Function Calling 文档
- 状态机设计模式
- 重试模式（Retry Pattern）
- 错误处理最佳实践

---

**预计完成时间：10-15 天**

**祝你学习愉快！** 🚀
