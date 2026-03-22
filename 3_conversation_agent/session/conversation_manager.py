"""
会话管理器
"""
import uuid
from typing import Optional
from datetime import datetime
from .models import Session
from .session_store import SessionStore
from .session_status import SessionStatus
from ..agent.message import Message, MessageRole


class ConversationManager:
    """
    会话管理器：管理会话的业务逻辑
    
    职责：
        - 创建、切换、删除会话
        - 管理历史消息
        - 维护当前活跃会话
        - 历史消息截断
    
    注意：
        业务层，不直接操作文件
    """
    
    def __init__(self, session_store: SessionStore, max_history_turns: int = 10):
        """
        初始化管理器
        
        TODO: 实现初始化逻辑
        1. 设置 session_store
        2. 设置最大历史轮次（默认 10）
        3. 初始化当前会话为 None
        4. 初始化内存缓存（session_cache）
        
        参数：
            session_store: SessionStore - 会话存储器
            max_history_turns: int - 最大历史轮次（用于截断）
        """
        self.session_store = session_store
        self.max_history_turns = max_history_turns
        self.current_session: Session | None = None
        self.session_cache : dict[str, Session] = {}
    
    def create_session(self, user_id: str = "default_user") -> Session:
        """
        创建新会话
        
        TODO: 实现创建逻辑
        1. 生成唯一的 session_id（使用 uuid 或时间戳）
        2. 创建 Session 对象
        3. 保存到存储器
        4. 添加到内存缓存
        5. 设置为当前会话
        6. 返回 Session 对象
        
        参数：
            user_id: str - 用户 ID（默认 "default_user"）
            
        返回：
            Session - 创建的会话对象
        """
        session_id: str = uuid.uuid4().hex
        session = Session(session_id=session_id, user_id=user_id)
        self.session_store.save_session(session)
        self.current_session = session
        self.session_cache[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Session|None:
        """
        获取指定会话
        
        TODO: 实现获取逻辑
        1. 先从内存缓存中查找
        2. 如果缓存中没有，从存储器加载
        3. 如果加载成功，添加到缓存
        4. 返回 Session 对象（不存在则返回 None）
        
        参数：
            session_id: str - 会话 ID
            
        返回：
            Optional[Session] - 会话对象，不存在则返回 None
        """
        if session_id in self.session_cache:
            return self.session_cache[session_id]
        if self.session_store.load_session(session_id):
            session = self.session_store.load_session(session_id)
            self.session_cache[session_id] = session
            return session
        return None

    def switch_session(self, session_id: str) -> bool:
        """
        切换当前会话
        
        TODO: 实现切换逻辑
        1. 检查会话是否存在
        2. 如果存在，设置为当前会话，返回 True
        3. 如果不存在，返回 False
        
        参数：
            session_id: str - 会话 ID
            
        返回：
            bool - 是否切换成功
        """
        if self.get_session(session_id):
            self.current_session = self.get_session(session_id)
            return True
        return False


    def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        TODO: 实现删除逻辑
        1. 从存储器删除文件
        2. 从内存缓存中移除
        3. 如果删除的是当前会话，将当前会话设为 None
        4. 返回是否删除成功
        
        参数：
            session_id: str - 会话 ID
            
        返回：
            bool - 是否删除成功
        """
        self.session_store.delete_session(session_id)
        self.session_cache.pop(session_id, None)
        if self.current_session.session_id == session_id:
            self.current_session = None
        return True

    def add_message(self, session_id: str, role: MessageRole, content: str, auto_truncate: bool = True):
        """
        添加消息到会话
        
        TODO: 实现添加逻辑
        1. 获取会话
        2. 调用会话的 add_message 方法
        3. 如果 auto_truncate=True，检查是否需要截断
        4. 保存会话
        
        参数：
            session_id: str - 会话 ID
            role: str - 消息角色
            content: str - 消息内容
            auto_truncate: bool - 是否自动截断历史
        """
        self.current_session.add_message(role=role, content=content)
        if auto_truncate and self.current_session.messages.length > self.max_history_turns:
            self.truncate_history(session_id, self.max_history_turns)


    
    def truncate_history(self, session_id: str, max_turns: int = None):
        """
        截断历史消息
        
        TODO: 实现截断逻辑
        1. 获取会话
        2. 如果未指定 max_turns，使用默认值
        3. 计算需要保留的消息数量（max_turns * 2，因为一轮对话有 user + assistant）
        4. 保留最近的消息
        5. 更新会话
        6. 保存会话

        参数：
            session_id: str - 会话 ID
            max_turns: int - 最大轮次（None 则使用默认值）
        """
        pass
    
    def get_current_session(self) -> Optional[Session]:
        """
        获取当前会话
        
        TODO: 实现获取逻辑
        - 返回当前活跃会话（可能为 None）
        
        返回：
            Optional[Session] - 当前会话
        """
        return self.current_session
    
    def list_all_sessions(self) -> list[Session]:
        """
        列出所有会话
        
        TODO: 实现列出逻辑
        1. 从存储器获取所有会话 ID
        2. 加载所有会话
        3. 返回会话列表
        
        返回：
            List[Session] - 所有会话列表
        """
        pass
    
    def update_status(self, session_id: str, status: SessionStatus):
        """
        更新会话状态
        
        TODO: 实现更新逻辑
        1. 获取会话
        2. 调用会话的 update_status 方法
        3. 保存会话
        
        参数：
            session_id: str - 会话 ID
            status: SessionStatus - 新状态
        """

    def save_all_sessions(self):
        """
        保存所有会话
        
        TODO: 实现保存逻辑
        1. 遍历内存缓存中的所有会话
        2. 逐个保存到存储器
        """
        pass
