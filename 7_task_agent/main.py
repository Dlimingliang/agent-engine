import sys
from pathlib import Path

# 添加项目根目录到 sys.path
sys.path.insert(0, str(Path(__file__).parent))

from tools import (
    ToolRegistry,
    CalculatorTool,
    FileReadTool,
    FileWriteTool,
    WebSearchTool,
    WebFetchTool
)
from agent import TaskAgent
from dotenv import load_dotenv

load_dotenv()


def setup_tools() -> ToolRegistry:
    """
    设置工具注册表
    
    Returns:
        ToolRegistry: 工具注册表
    """
    # 1. 创建 ToolRegistry 实例
    registry = ToolRegistry()
    
    # 2. 注册所有工具
    registry.register(CalculatorTool())
    registry.register(FileReadTool())
    registry.register(FileWriteTool())
    registry.register(WebSearchTool())
    registry.register(WebFetchTool())
    
    # 3. 返回注册表
    return registry

def setup_agent() -> TaskAgent:
    """
    设置 Task Agent
    
    Returns:
        TaskAgent: Task Agent 实例
    """
    # 1. 获取工具注册表
    tool_registry = setup_tools()
    
    # 2. 定义 Agent 的系统提示词
    system_prompt = """你是一个任务执行助手，能够将复杂任务拆解为步骤并逐步执行。

你的核心能力包括：
1. 任务规划：将用户任务分解为可执行的步骤
2. 工具调用：使用各种工具完成特定操作
3. 结果验证：验证每一步的执行结果
4. 错误恢复：遇到错误时智能恢复

请根据用户的任务描述，制定合理的执行计划并逐步完成。"""
    
    # 3. 创建 TaskAgent 实例
    agent = TaskAgent(
        name="TaskAgent",
        role="任务执行助手",
        system_prompt=system_prompt,
        tool_registry=tool_registry,
        max_retries=3
    )
    
    # 4. 返回 Agent
    return agent


def print_welcome():
    """
    打印欢迎信息
    
    TODO: 打印欢迎信息和命令列表
    """
    print("=" * 60)
    print("Task Agent - 任务执行助手")
    print("=" * 60)
    print("可用命令:")
    print("  - 输入任务描述，Agent 将执行任务")
    print("  - status: 查看任务状态")
    print("  - pause: 暂停任务")
    print("  - resume: 恢复任务")
    print("  - cancel: 取消任务")
    print("  - help: 显示帮助信息")
    print("  - exit: 退出程序")
    print("=" * 60)


def main():
    """
    主函数
    """
    # 1. 设置 Agent
    agent = setup_agent()
    
    # 2. 打印欢迎信息
    print_welcome()
    
    # 3. 进入命令行循环
    while True:
        try:
            # a. 读取用户输入
            user_input = input("\n> ").strip()
            
            # 空输入跳过
            if not user_input:
                continue
            
            # b. 根据输入执行相应操作
            if not handle_special_command(agent, user_input):
                # c. 作为任务执行
                result = agent.process(user_input)
                print_task_result(result)
                
        except KeyboardInterrupt:
            print("\n\n检测到中断信号")
            if agent.task_tracker.overall_status == "executing":
                print("任务正在执行中，使用 'cancel' 命令取消任务")
            else:
                print("Bye!")
                break
        except Exception as e:
            print(f"\n❌ 发生错误: {str(e)}")


def handle_special_command(agent: TaskAgent, command: str) -> bool:
    """
    处理特殊命令
    
    Args:
        agent: Task Agent 实例
        command: 命令字符串
        
    Returns:
        bool: 是否是特殊命令
    """
    command_lower = command.lower()
    
    # status: 显示任务状态
    if command_lower == "status":
        status = agent.get_task_status()
        print("\n任务状态摘要")
        print("=" * 60)
        print(f"任务ID: {agent.task_tracker.task_id}")
        print(f"描述: {agent.task_tracker.task_description}")
        print(f"整体状态: {status.get('current_status', 'N/A')}")
        print(f"进度: {status.get('completed', 0)}/{status.get('total_steps', 0)} ({status.get('progress_percent', 0):.1f}%)")
        print(f"失败步骤: {status.get('failed', 0)}")
        
        # 显示步骤详情
        if agent.task_tracker.steps:
            print("\n步骤详情:")
            for step_id, step_status in agent.task_tracker.steps.items():
                status_icon = "✅" if step_status.status == "completed" else "❌" if step_status.status == "failed" else "⏳"
                print(f"  [{status_icon}] 步骤 {step_id}: {step_status.status}")
        return True
    
    # pause: 暂停任务
    elif command_lower == "pause":
        if agent.pause_task():
            print("✅ 任务已暂停")
        else:
            print("❌ 无法暂停任务（可能任务未在执行中）")
        return True
    
    # resume: 恢复任务
    elif command_lower == "resume":
        if agent.resume_task():
            print("✅ 任务已恢复")
        else:
            print("❌ 无法恢复任务（可能任务未暂停）")
        return True
    
    # cancel: 取消任务
    elif command_lower == "cancel":
        if agent.cancel_task():
            print("✅ 任务已取消")
        else:
            print("❌ 无法取消任务（可能任务已完成或已取消）")
        return True
    
    # help: 显示帮助
    elif command_lower == "help":
        print_welcome()
        return True
    
    # exit: 退出
    elif command_lower == "exit":
        print("Bye!")
        exit(0)
    
    # 不是特殊命令
    return False


def print_task_result(result):
    """
    打印任务结果
    
    Args:
        result: 任务结果
    """
    print("\n" + "=" * 60)
    print(result.message)
    print("=" * 60)
    
    # 如果有详细信息，显示简要信息
    if result.details:
        print(f"\n任务ID: {result.details.get('task_description', 'N/A')}")
        print(f"总步骤: {result.details.get('total_steps', 0)}")
        print(f"完成步骤: {result.details.get('completed_steps', 0)}")
        print(f"失败步骤: {result.details.get('failed_steps', 0)}")


if __name__ == "__main__":
    main()
