"""
@generated-by AI: matthewmli
@generated-date 2026-03-23
"""
import json
from pathlib import Path
from typing import List, Optional
from .models import Session


class SessionStore:
    """
    会话存储
    
    只管存取，不管业务逻辑
    """
    
    def __init__(self, data_dir: str = "data/sessions"):
        """
        初始化存储
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir: Path = Path(data_dir)
        # 如果目录不存在，创建目录
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def save_session(self, session: Session):
        """
        保存会话到文件
        
        Args:
            session: 会话对象
        """
        file_path = self.data_dir / f"{session.session_id}.json"

        # 将 Session 对象转换为字典
        session_dict = session.to_dict()

        # 写入 JSON 文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(session_dict, f, indent=2, ensure_ascii=False)
    
    def load_session(self, session_id: str) -> Optional[Session]:
        """
        从文件加载会话
        
        Args:
            session_id: 会话ID
        
        Returns:
            会话对象
        """
        file_path = self.data_dir / f"{session_id}.json"

        # 检查文件是否存在
        if not file_path.exists():
            return None

        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            session_dict = json.load(f)

        # 从字典创建 Session 对象
        return Session.from_dict(session_dict)
    
    def delete_session(self, session_id: str):
        """
        删除会话文件
        
        Args:
            session_id: 会话ID
        """
        file_path = self.data_dir / f"{session_id}.json"

        # 检查文件是否存在
        if not file_path.exists():
            return False

        # 删除文件
        file_path.unlink()
        return True
    
    def list_sessions(self) -> List[str]:
        """
        列出所有会话ID
        
        Returns:
            会话ID列表
        """
        session_ids = []

        # 遍历数据目录
        for file_path in self.data_dir.glob("*.json"):
            # 提取文件名（去掉 .json 后缀）
            session_id = file_path.stem
            session_ids.append(session_id)

        return session_ids
    
    def session_exists(self, session_id: str) -> bool:
        """
        检查会话是否存在
        
        Args:
            session_id: 会话ID
        
        Returns:
            是否存在
        """
        file_path = self.data_dir / f"{session_id}.json"
        return file_path.exists()
