# === AI Generated Code Start matthewmli===
"""
会话存储类
"""
import json
from pathlib import Path
from .models import Session


class SessionStore:
    """
    会话存储类：负责会话数据的持久化
    
    职责：
        - 保存会话到 JSON 文件
        - 从 JSON 文件加载会话
        - 删除会话文件
        - 列出所有会话
    
    注意：
        只管存取，不管业务逻辑
    """
    
    def __init__(self, data_dir: str = "data/sessions"):
        """
        初始化存储器
        
        1. 设置数据存储目录
        2. 如果目录不存在，创建目录
        
        参数：
            data_dir: str - 数据存储目录路径
        """
        self.data_dir: Path = Path(data_dir)
        # 如果目录不存在，创建目录
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def save_session(self, session: Session) -> None:
        """
        保存会话到 JSON 文件
        
        1. 构建文件路径：{data_dir}/{session_id}.json
        2. 将 Session 对象转换为字典
        3. 序列化为 JSON 字符串（indent=2，ensure_ascii=False）
        4. 写入文件
        
        参数：
            session: Session - 要保存的会话对象
        """
        file_path = self.data_dir / f"{session.session_id}.json"
        
        # 将 Session 对象转换为字典
        session_dict = session.to_dict()
        
        # 写入 JSON 文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(session_dict, f, indent=2, ensure_ascii=False)
    
    def load_session(self, session_id: str) -> Session | None:
        """
        从文件加载会话
        
        1. 构建文件路径
        2. 检查文件是否存在
        3. 如果存在，读取文件内容
        4. 解析 JSON
        5. 从字典创建 Session 对象
        6. 返回 Session 对象
        7. 如果文件不存在，返回 None
        
        参数：
            session_id: str - 会话 ID
            
        返回：
            Optional[Session] - 会话对象，如果不存在则返回 None
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
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话文件
        
        1. 构建文件路径
        2. 检查文件是否存在
        3. 如果存在，删除文件，返回 True
        4. 如果不存在，返回 False
        
        参数：
            session_id: str - 会话 ID
            
        返回：
            bool - 是否删除成功
        """
        file_path = self.data_dir / f"{session_id}.json"
        
        # 检查文件是否存在
        if not file_path.exists():
            return False
        
        # 删除文件
        file_path.unlink()
        return True
    
    def list_sessions(self) -> list[str]:
        """
        列出所有会话 ID
        
        1. 遍历数据目录
        2. 找到所有 .json 文件
        3. 提取文件名（去掉 .json 后缀）
        4. 返回会话 ID 列表
        
        返回：
            List[str] - 会话 ID 列表
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
        
        1. 构建文件路径
        2. 检查文件是否存在
        3. 返回布尔值
        
        参数：
            session_id: str - 会话 ID
            
        返回：
            bool - 会话是否存在
        """
        file_path = self.data_dir / f"{session_id}.json"
        return file_path.exists()
