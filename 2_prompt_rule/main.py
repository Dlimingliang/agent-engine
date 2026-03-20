from datetime import datetime
from tools import ToolRegistry, register_builtin_tools
from agent import Agent, TaskResult, RuleEngine, PromptComposer


def main():
    """Mini Agent 入口"""
    
    # 1. 创建工具注册中心并注册内置工具
    registry = ToolRegistry()
    register_builtin_tools(registry)
    print("📋 可用工具:", registry.list_tools())

    # 设置规则
    rule_engine = RuleEngine()
    rule_engine.add_rule("禁止读取目录test","safe")
    rule_engine.add_rule("获取时间的时候返回格式2026-3-26", "product")

    # 构建提示词
    prompt_composer = PromptComposer()
    prompt_composer.set_system_prompt("你是一个有用的助手,根据用户问题选择合适的工具来完成任务。但是规则规则必须遵守!")
    prompt_composer.set_rule_prompt(rule_engine.rule_compose())
    schema = TaskResult.model_json_schema()
    prompt_composer.set_output_prompt(schema)

    # 构建agent
    agent = Agent(
        system_prompt=prompt_composer.compose(),
        tool_registry=registry
    )
    
    # 3. 交互循环
    print("\n" + "=" * 50)
    print("🤖 Mini Agent 已启动 (输入 'quit' 退出)")
    print("=" * 50 + "\n")
    
    while True:
        try:
            user_input = input("👤 你: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print("👋 再见!")
                break
            
            # 生成会话ID
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 处理用户输入
            print("\n🤖 Agent: ", end="")
            response = agent.process(session_id, user_input)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}\n")


if __name__ == "__main__":
    main()
