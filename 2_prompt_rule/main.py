from datetime import datetime
from tools import ToolRegistry, register_builtin_tools
from agent import Agent, TaskResult


def main():
    """Mini Agent 入口"""
    
    # 1. 创建工具注册中心并注册内置工具
    registry = ToolRegistry()
    register_builtin_tools(registry)
    
    print("📋 可用工具:", registry.list_tools())

    schema = TaskResult.model_json_schema()
    
    # === AI Generated Code Start matthewmli ===
    # TODO: 使用 PromptComposer 组合 system_prompt
    # TODO: 添加 RuleEngine 规则
    # === AI Generated Code End matthewmli ===
    
    # 2. 创建 Agent
    system_prompt = f"""你是一个有用的助手。
请根据用户问题选择合适的工具来完成任务。

当收集所有信息之后,请返回json格式的数据
{schema}
"""

    agent = Agent(
        name="MiniAgent",
        role="assistant",
        system_prompt=system_prompt,
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
