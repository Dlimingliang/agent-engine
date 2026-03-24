"""
@generated-by AI: matthewmli
@generated-date 2026-03-23
"""
import uuid
from typing import List, Optional
from .models import Session
from .session_store import SessionStore
from .session_status import SessionStatus
from ..agent.message import MessageRole


class ConversationManager:
    """
    会话管理器
    
    管理会话的业务逻辑
    """
    
    def __init__(self, session_store: SessionStore, max_history_turns: int = 5):
        """
        初始化管理器
        
        Args:
            session_store: 会话存储
        """
        self.session_store: SessionStore = session_store
        self.current_session: Session | None = None
        self.session_cache: dict[str, Session] = {}
        self.max_history_turns: int = max_history_turns
    
    def create_session(self, user_id: str = "default_user") -> Session:
        """
        创建新会话
        
        Args:
            user_id: 用户ID
        
        Returns:
            新会话
        """
        session_id: str = uuid.uuid4().hex
        session = Session(session_id=session_id, user_id=user_id)
        self.session_store.save_session(session)
        self.current_session = session
        self.session_cache[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        获取指定会话
        
        Args:
            session_id: 会话ID
        
        Returns:
            会话对象
        """
        if session_id in self.session_cache:
            return self.session_cache[session_id]

        session = self.session_store.load_session(session_id)
        if session:
            self.session_cache[session_id] = session
            return session

        return None
    
    def switch_session(self, session_id: str) -> Optional[Session]:
        """
        切换当前会话
        
        Args:
            session_id: 会话ID
        
        Returns:
            当前会话
        """
        session = self.get_session(session_id)
        if session:
            self.current_session = session
            return session
        return None
    
    def delete_session(self, session_id: str):
        """
        删除会话
        
        Args:
            session_id: 会话ID
        """
        if not self.session_store.delete_session(session_id):
            return False

        # 从内存缓存中移除
        self.session_cache.pop(session_id, None)

        # 如果删除的是当前会话，将当前会话设为 None
        if self.current_session and self.current_session.session_id == session_id:
            self.current_session = None

        return True
    
    def get_current_session(self) -> Optional[Session]:
        """
        获取当前会话
        
        Returns:
            当前会话
        """
        return self.current_session
    
    def list_all_sessions(self) -> List[Session]:
        """
        列出所有会话
        
        Returns:
            会话列表
        """
        session_ids = self.session_store.list_sessions()
        sessions = []
        for session_id in session_ids:
            session = self.get_session(session_id)
            if session:
                sessions.append(session)
        return sessions
    
    def add_message(self, session_id: str, role: MessageRole, content: str):
        """
        添加消息
        
        Args:
            session_id: 会话ID
            role: 消息角色
            content: 消息内容
        """
        session = self.get_session(session_id)
        if not session:
            return

        # 添加消息
        session.add_message(role=role, content=content)

        # 自动截断检查（一轮对话 = 2条消息：user + assistant）
        message_count = len(session.messages)
        max_messages = self.max_history_turns * 2
        if message_count > max_messages:
            self.truncate_history(session_id, self.max_history_turns)

        # 保存会话
        self.session_store.save_session(session)
    
    def update_status(self, session_id: str, status: SessionStatus):
        """
        更新会话状态
        
        Args:
            session_id: 会话ID
            status: 新状态
        """
        session = self.get_session(session_id)
        if not session:
            return

        session.update_status(status)
        self.session_store.save_session(session)
    
    def save_all(self):
        """保存所有会话"""
        for session in self.session_cache.values():
            self.session_store.save_session(session)
    
    def truncate_history(self, session_id: str, max_turns: int = 10):
        """
        截断历史
        
        Args:
            session_id: 会话ID
            max_turns: 最大轮数
        """
        session = self.get_session(session_id)
        if not session:
            return

        # 计算需要保留的消息数量（一轮 = user + assistant = 2条消息）
        max_messages = max_turns * 2

        # 保留最近的消息
        if len(session.messages) > max_messages:
            session.messages = session.messages[-max_messages:]

        # 保存会话
        self.session_store.save_session(session)
