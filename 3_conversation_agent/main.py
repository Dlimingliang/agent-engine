"""
CLI 主程序
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent import Agent
from agent.message import MessageRole
from session import SessionStore, ConversationManager


class ConversationCLI:
    """
    命令行交互界面
    
    支持的命令：
        new              - 创建新会话
        list             - 列出所有会话
        switch <id>      - 切换到指定会话
        delete <id>      - 删除指定会话
        status           - 查看当前会话状态
        history          - 查看当前会话历史
        help             - 显示帮助
        exit             - 退出并保存
    """
    
    def __init__(self):
        """
        初始化 CLI
        
        TODO: 实现初始化逻辑
        1. 初始化 SessionStore
        2. 初始化 ConversationManager
        3. 初始化 Agent
        4. 设置运行标志
        """
        # === AI Generated Code Start matthewmli===
        self.session_store: SessionStore = SessionStore(data_dir="./data/sessions")
        self.conversation_manager: ConversationManager = ConversationManager(self.session_store)
        self.agent: Agent = Agent()
        self.running: bool = True
        # === AI Generated Code End matthewmli===
        
    
    def run(self):
        """
        运行主循环
        
        TODO: 实现主循环逻辑
        1. 打印欢迎信息
        2. 显示帮助信息
        3. 循环读取用户输入
        4. 解析命令或作为对话输入
        5. 退出时保存所有会话
        """
        # === AI Generated Code Start matthewmli===
        print("=" * 60)
        print("欢迎使用对话式 Agent 系统!")
        print("=" * 60)
        self.cmd_help()
        print()
        
        while self.running:
            try:
                user_input = input("\n> ").strip()
                if not user_input:
                    continue
                    
                self.handle_command(user_input)
            except KeyboardInterrupt:
                print("\n\n收到中断信号，正在退出...")
                self.cmd_exit()
                break
            except EOFError:
                print("\n\n输入结束，正在退出...")
                self.cmd_exit()
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
        # === AI Generated Code End matthewmli===
    
    def handle_command(self, user_input: str):
        """
        处理用户输入
        
        TODO: 实现命令解析逻辑
        1. 检查是否是命令（以 / 开头或是特定关键词）
        2. 如果是命令，调用对应的处理方法
        3. 如果不是命令，作为对话输入处理
        
        参数：
            user_input: str - 用户输入
        """
        # === AI Generated Code Start matthewmli===
        # 解析命令
        parts = user_input.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # 命令分发
        if command == "new":
            self.cmd_new()
        elif command == "list":
            self.cmd_list()
        elif command == "switch":
            if args:
                self.cmd_switch(args)
            else:
                print("❌ 请提供会话 ID")
        elif command == "delete":
            if args:
                self.cmd_delete(args)
            else:
                print("❌ 请提供会话 ID")
        elif command == "status":
            self.cmd_status()
        elif command == "history":
            self.cmd_history()
        elif command == "help":
            self.cmd_help()
        elif command == "exit":
            self.cmd_exit()
        else:
            # 不是命令，作为对话输入处理
            self.handle_chat(user_input)
        # === AI Generated Code End matthewmli===
    
    def cmd_new(self):
        """
        创建新会话
        
        TODO: 实现创建逻辑
        1. 调用 ConversationManager.create_session()
        2. 打印创建成功的消息
        3. 显示新会话的 ID
        """
        # === AI Generated Code Start matthewmli===
        session = self.conversation_manager.create_session()
        print(f"✅ 创建新会话成功!")
        print(f"   会话 ID: {session.session_id}")
        # === AI Generated Code End matthewmli===
    
    def cmd_list(self):
        """
        列出所有会话
        
        TODO: 实现列出逻辑
        1. 调用 ConversationManager.list_all_sessions()
        2. 格式化显示会话列表
        3. 显示会话 ID、状态、消息数量、创建时间
        """
        # === AI Generated Code Start matthewmli===
        sessions = self.conversation_manager.list_all_sessions()
        
        if not sessions:
            print("📋 暂无会话，使用 'new' 命令创建新会话")
            return
        
        print(f"\n📋 所有会话 (共 {len(sessions)} 个):")
        print("-" * 80)
        current_session = self.conversation_manager.get_current_session()
        current_id = current_session.session_id if current_session else None
        
        for session in sessions:
            current_marker = "👉 " if session.session_id == current_id else "   "
            msg_count = len(session.messages)
            print(f"{current_marker}ID: {session.session_id}")
            print(f"   状态: {session.status.value} | 消息数: {msg_count} | 创建时间: {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 80)
        # === AI Generated Code End matthewmli===
    
    def cmd_switch(self, session_id: str):
        """
        切换会话
        
        TODO: 实现切换逻辑
        1. 调用 ConversationManager.switch_session()
        2. 打印切换结果（成功/失败）
        
        参数：
            session_id: str - 会话 ID
        """
        # === AI Generated Code Start matthewmli===
        if self.conversation_manager.switch_session(session_id):
            print(f"✅ 切换到会话: {session_id}")
        else:
            print(f"❌ 会话不存在: {session_id}")
        # === AI Generated Code End matthewmli===
    
    def cmd_delete(self, session_id: str):
        """
        删除会话
        
        TODO: 实现删除逻辑
        1. 确认删除操作
        2. 调用 ConversationManager.delete_session()
        3. 打印删除结果
        
        参数：
            session_id: str - 会话 ID
        """
        # === AI Generated Code Start matthewmli===
        # 确认删除
        confirm = input(f"⚠️  确认删除会话 {session_id}? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("❌ 取消删除")
            return
        
        if self.conversation_manager.delete_session(session_id):
            print(f"✅ 删除会话成功: {session_id}")
        else:
            print(f"❌ 删除会话失败: {session_id}")
        # === AI Generated Code End matthewmli===
    
    def cmd_status(self):
        """
        查看当前会话状态
        
        TODO: 实现状态查看逻辑
        1. 获取当前会话
        2. 如果没有当前会话，提示用户
        3. 显示会话 ID、状态、消息数量、创建时间、更新时间
        """
        # === AI Generated Code Start matthewmli===
        session = self.conversation_manager.get_current_session()
        
        if not session:
            print("❌ 当前没有活跃会话，请使用 'new' 创建或 'switch' 切换会话")
            return
        
        print(f"\n📊 当前会话状态:")
        print("-" * 60)
        print(f"会话 ID: {session.session_id}")
        print(f"用户 ID: {session.user_id}")
        print(f"状态: {session.status.value}")
        print(f"消息数量: {len(session.messages)}")
        print(f"创建时间: {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"更新时间: {session.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        # === AI Generated Code End matthewmli===
    
    def cmd_history(self):
        """
        查看当前会话历史
        
        TODO: 实现历史查看逻辑
        1. 获取当前会话
        2. 如果没有当前会话，提示用户
        3. 遍历消息列表，格式化显示
        4. 显示每条消息的角色和内容
        """
        # === AI Generated Code Start matthewmli===
        session = self.conversation_manager.get_current_session()
        
        if not session:
            print("❌ 当前没有活跃会话")
            return
        
        if not session.messages:
            print("📝 当前会话暂无历史消息")
            return
        
        print(f"\n📝 会话历史 (共 {len(session.messages)} 条):")
        print("=" * 60)
        
        for i, msg in enumerate(session.messages, 1):
            role_display = "🧑 用户" if msg.role == "user" else "🤖 助手"
            timestamp = msg.timestamp.strftime('%H:%M:%S')
            print(f"\n[{i}] {role_display} ({timestamp})")
            print(f"{msg.content}")
            print("-" * 60)
        # === AI Generated Code End matthewmli===
    
    def cmd_help(self):
        """
        显示帮助信息
        
        TODO: 实现帮助显示逻辑
        - 显示所有可用命令及其说明
        """
        # === AI Generated Code Start matthewmli===
        print("\n💡 可用命令:")
        print("-" * 60)
        print("  new              - 创建新会话")
        print("  list             - 列出所有会话")
        print("  switch <id>      - 切换到指定会话")
        print("  delete <id>      - 删除指定会话")
        print("  status           - 查看当前会话状态")
        print("  history          - 查看当前会话历史")
        print("  help             - 显示帮助信息")
        print("  exit             - 退出并保存")
        print("-" * 60)
        print("💬 直接输入文本即可与 Agent 对话")
        # === AI Generated Code End matthewmli===
    
    def cmd_exit(self):
        """
        退出程序
        
        TODO: 实现退出逻辑
        1. 保存所有会话
        2. 打印退出消息
        3. 设置运行标志为 False
        """
        # === AI Generated Code Start matthewmli===
        print("\n💾 正在保存所有会话...")
        self.conversation_manager.save_all_sessions()
        print("✅ 保存完成")
        print("👋 再见!")
        self.running = False
        # === AI Generated Code End matthewmli===
    
    def handle_chat(self, user_input: str):
        """
        处理对话输入
        
        TODO: 实现对话逻辑
        1. 检查是否有当前会话
        2. 如果没有，提示用户先创建会话
        3. 获取当前会话
        4. 调用 Agent.chat() 生成回复
        5. 添加用户消息和 Agent 回复到会话
        6. 打印 Agent 回复
        
        参数：
            user_input: str - 用户输入
        """
        # === AI Generated Code Start matthewmli===
        session = self.conversation_manager.get_current_session()
        
        if not session:
            print("❌ 当前没有活跃会话，请先使用 'new' 创建会话")
            return
        
        # 调用 Agent 生成回复
        response = self.agent.chat(user_input, session.messages)
        
        if not response:
            print("❌ Agent 回复失败")
            return
        
        # 添加用户消息
        self.conversation_manager.add_message(
            session_id=session.session_id,
            role=MessageRole.USER,
            content=user_input
        )
        
        # 添加 Agent 回复
        self.conversation_manager.add_message(
            session_id=session.session_id,
            role=MessageRole.ASSISTANT,
            content=response
        )
        
        # 打印 Agent 回复
        print(f"\n🤖 Agent: {response}")
        # === AI Generated Code End matthewmli===


def main():
    """主函数"""
    cli = ConversationCLI()
    cli.run()


if __name__ == "__main__":
    main()
