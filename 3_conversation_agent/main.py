"""
CLI 主程序
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from agent import Agent
from session import SessionStore, ConversationManager, SessionStatus


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
        pass
    
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
        pass
    
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
        pass
    
    def cmd_new(self):
        """
        创建新会话
        
        TODO: 实现创建逻辑
        1. 调用 ConversationManager.create_session()
        2. 打印创建成功的消息
        3. 显示新会话的 ID
        """
        pass
    
    def cmd_list(self):
        """
        列出所有会话
        
        TODO: 实现列出逻辑
        1. 调用 ConversationManager.list_all_sessions()
        2. 格式化显示会话列表
        3. 显示会话 ID、状态、消息数量、创建时间
        """
        pass
    
    def cmd_switch(self, session_id: str):
        """
        切换会话
        
        TODO: 实现切换逻辑
        1. 调用 ConversationManager.switch_session()
        2. 打印切换结果（成功/失败）
        
        参数：
            session_id: str - 会话 ID
        """
        pass
    
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
        pass
    
    def cmd_status(self):
        """
        查看当前会话状态
        
        TODO: 实现状态查看逻辑
        1. 获取当前会话
        2. 如果没有当前会话，提示用户
        3. 显示会话 ID、状态、消息数量、创建时间、更新时间
        """
        pass
    
    def cmd_history(self):
        """
        查看当前会话历史
        
        TODO: 实现历史查看逻辑
        1. 获取当前会话
        2. 如果没有当前会话，提示用户
        3. 遍历消息列表，格式化显示
        4. 显示每条消息的角色和内容
        """
        pass
    
    def cmd_help(self):
        """
        显示帮助信息
        
        TODO: 实现帮助显示逻辑
        - 显示所有可用命令及其说明
        """
        pass
    
    def cmd_exit(self):
        """
        退出程序
        
        TODO: 实现退出逻辑
        1. 保存所有会话
        2. 打印退出消息
        3. 设置运行标志为 False
        """
        pass
    
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
        pass


def main():
    """主函数"""
    cli = ConversationCLI()
    cli.run()


if __name__ == "__main__":
    main()
