"""
@generated-by AI: matthewmli
@generated-date 2026-03-23
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径，支持绝对导入
sys.path.insert(0, str(Path(__file__).parent))

import os
from dotenv import load_dotenv
from session.session_store import SessionStore
from session.conversation_manager import ConversationManager
from memory.long_term import LongTermMemory
from memory.short_term import ShortTermMemory
from memory.working import WorkingMemory
from memory.writer import MemoryWriter
from memory.reader import MemoryReader
from tools.tool_registry import ToolRegistry
from tools.task_tools import CreateTaskTool, ExecuteTaskTool, QueryTaskTool
from agent.agent import Agent

# 加载环境变量
load_dotenv()


def print_help():
    """打印帮助信息"""
    help_text = """
╔════════════════════════════════════════════════════════╗
║             任务管理 Agent - 命令帮助                    ║
╠════════════════════════════════════════════════════════╣
║ 命令格式:                                               ║
║   /<command> [arguments]                               ║
║                                                         ║
║ 可用命令:                                               ║
║   /new              - 创建新会话                        ║
║   /list             - 列出所有会话                      ║
║   /switch <id>      - 切换到指定会话                    ║
║   /delete <id>      - 删除指定会话                      ║
║   /memory           - 查看当前记忆状态                  ║
║   /help             - 显示此帮助信息                    ║
║   /exit             - 退出程序                          ║
║                                                         ║
║ 直接输入文字即可与 Agent 对话                            ║
╚════════════════════════════════════════════════════════╝
"""
    print(help_text)


def print_memory_status(memory_reader: MemoryReader):
    """打印记忆状态"""
    print("\n" + "="*60)
    print("当前记忆状态")
    print("="*60)
    
    # 短期记忆
    short_term = memory_reader.read_short_term()
    if short_term:
        print("\n【短期记忆】")
        print(f"  当前意图: {short_term.get('current_intent', '无')}")
        print(f"  最近话题: {', '.join(short_term.get('recent_topics', []))}")
    else:
        print("\n【短期记忆】空")
    
    # 长期记忆
    long_term = memory_reader.read_long_term("")
    if long_term:
        print("\n【长期记忆】")
        prefs = long_term.get('user_preferences', {})
        if prefs:
            print(f"  用户偏好: {prefs}")
        facts = long_term.get('important_facts', [])
        if facts:
            print(f"  重要事实: {len(facts)} 条")
    else:
        print("\n【长期记忆】空")
    
    # 工作记忆
    working = memory_reader.read_working()
    if working and working.get('current_task'):
        print("\n【工作记忆】")
        task = working['current_task']
        print(f"  当前任务: {task.get('name', '未知')}")
        print(f"  任务状态: {task.get('status', '未知')}")
    else:
        print("\n【工作记忆】空")
    
    print("="*60 + "\n")


def main():
    """CLI 主程序"""
    # === AI Generated Code Start matthewmli===
    print("\n🤖 正在初始化任务管理 Agent...")
    
    # 1. 初始化组件
    # SessionStore
    session_store = SessionStore(data_dir="data/sessions")
    
    # ConversationManager
    conversation_manager = ConversationManager(
        session_store=session_store,
        max_history_turns=5
    )
    
    # 三种记忆
    long_term_memory = LongTermMemory(storage_path="data/long_term_memory.json")
    short_term_memory = ShortTermMemory()
    working_memory = WorkingMemory()
    
    # 加载长期记忆
    long_term_memory.load()
    
    # MemoryWriter & MemoryReader
    memory_writer = MemoryWriter(
        short_term_memory=short_term_memory,
        long_term_memory=long_term_memory,
        working_memory=working_memory
    )
    
    memory_reader = MemoryReader(
        short_term_memory=short_term_memory,
        long_term_memory=long_term_memory,
        working_memory=working_memory
    )
    
    # ToolRegistry
    tool_registry = ToolRegistry()
    tool_registry.register(CreateTaskTool())
    tool_registry.register(ExecuteTaskTool())
    tool_registry.register(QueryTaskTool())
    
    # Agent
    system_prompt = """你是一个任务管理助手，帮助用户创建、执行和查询任务。

你可以使用以下工具：
- create_task: 创建新任务
- execute_task: 执行任务
- query_task: 查询任务状态

请根据用户的需求，合理使用这些工具来帮助用户管理任务。"""
    
    agent = Agent(
        system_prompt=system_prompt,
        conversation_manager=conversation_manager,
        memory_reader=memory_reader,
        memory_writer=memory_writer,
        tool_registry=tool_registry
    )
    
    print("✅ 初始化完成！输入 /help 查看可用命令\n")
    
    # 创建默认会话
    session = conversation_manager.create_session()
    print(f"📝 已创建默认会话: {session.session_id}\n")
    
    # 2. 命令解析与对话循环
    while True:
        try:
            user_input = input("👤 你: ").strip()
            
            # 空输入跳过
            if not user_input:
                continue
            
            # 命令处理
            if user_input.startswith('/'):
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else None
                
                # new - 创建新会话
                if command == '/new':
                    session = conversation_manager.create_session()
                    print(f"✅ 已创建新会话: {session.session_id}\n")
                
                # list - 列出所有会话
                elif command == '/list':
                    sessions = conversation_manager.list_sessions()
                    print(f"\n📋 共 {len(sessions)} 个会话:")
                    current_id = conversation_manager.current_session.session_id if conversation_manager.current_session else None
                    for idx, s in enumerate(sessions, 1):
                        marker = "👉 " if s.session_id == current_id else "   "
                        print(f"{marker}{idx}. {s.session_id} - {s.status.value} ({len(s.messages)} 条消息)")
                    print()
                
                # switch - 切换会话
                elif command == '/switch':
                    if not args:
                        print("❌ 请提供会话ID，例如: /switch <session_id>\n")
                        continue
                    session_id = args.strip()
                    session = conversation_manager.get_session(session_id)
                    if session:
                        conversation_manager.current_session = session
                        print(f"✅ 已切换到会话: {session_id}\n")
                    else:
                        print(f"❌ 会话不存在: {session_id}\n")
                
                # delete - 删除会话
                elif command == '/delete':
                    if not args:
                        print("❌ 请提供会话ID，例如: /delete <session_id>\n")
                        continue
                    session_id = args.strip()
                    conversation_manager.delete_session(session_id)
                    print(f"✅ 已删除会话: {session_id}\n")
                
                # memory - 查看记忆状态
                elif command == '/memory':
                    print_memory_status(memory_reader)
                
                # help - 显示帮助
                elif command == '/help':
                    print_help()
                
                # exit - 退出
                elif command == '/exit':
                    print("\n👋 再见！正在保存数据...")
                    # 保存长期记忆
                    long_term_memory.save()
                    print("✅ 数据已保存，感谢使用！\n")
                    break
                
                else:
                    print(f"❌ 未知命令: {command}，输入 /help 查看可用命令\n")
            
            # 普通对话
            else:
                response = agent.chat(user_input)
                print(f"🤖 Agent: {response}\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 检测到中断，正在退出...")
            long_term_memory.save()
            print("✅ 数据已保存，感谢使用！\n")
            break
        
        except Exception as e:
            print(f"❌ 发生错误: {e}\n")
    # === AI Generated Code End matthewmli===


if __name__ == "__main__":
    main()
