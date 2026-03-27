"""
@generated-by AI: matthewmli
@generated-date 2026-03-26
"""
import os
from sentence_transformers import SentenceTransformer
from typing import List, Optional
import numpy as np

class Embedder:
    """Embedding 模型封装类"""
    
    def __init__(
        self, 
        model_name: str = "BAAI/bge-large-zh",
        cache_folder: Optional[str] = None,
        device: str = "cpu"
    ):
        """
        初始化 Embedding 模型
        
        Args:
            model_name: 模型名称，默认使用 bge-large-zh
            cache_folder: 模型缓存目录，默认为 ./models/
            device: 运行设备，'cpu' 或 'cuda'
        """
        # 设置默认缓存目录
        if cache_folder is None:
            cache_folder = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                "data", 
                "models"
            )
        
        # 确保目录存在
        os.makedirs(cache_folder, exist_ok=True)
        
        print(f"📥 正在加载模型: {model_name}")
        print(f"📂 模型缓存目录: {cache_folder}")
        print(f"🖥️  运行设备: {device}")
        
        # 加载模型
        self.model = SentenceTransformer(
            model_name,
            cache_folder=cache_folder,
            device=device
        )
        
        self.model_name = model_name
        self.device = device
        
        print(f"✅ 模型加载成功！")
    
    def encode(self, texts: List[str], show_progress_bar: bool = False) -> np.ndarray:
        """
        将文本列表转换为向量列表
        
        Args:
            texts: 文本列表
            show_progress_bar: 是否显示进度条
            
        Returns:
            向量数组，shape: (len(texts), 1024)
        """
        if not texts:
            return np.array([])
        
        vectors = self.model.encode(
            texts,
            show_progress_bar=show_progress_bar,
            normalize_embeddings=True  # 归一化，便于计算余弦相似度
        )
        
        return vectors
    
    def encode_single(self, text: str) -> np.ndarray:
        """
        将单个文本转换为向量
        
        Args:
            text: 文本内容
            
        Returns:
            向量，shape: (1024,)
        """
        vector = self.model.encode(
            text,
            normalize_embeddings=True
        )
        return vector
    
    def get_dimension(self) -> int:
        """
        获取向量维度
        
        Returns:
            向量维度（1024）
        """
        return 1024  # bge-large-zh 的维度
    
    def get_model_info(self) -> dict:
        """
        获取模型信息
        
        Returns:
            模型信息字典
        """
        return {
            "model_name": self.model_name,
            "dimension": self.get_dimension(),
            "device": self.device,
            "max_seq_length": self.model.max_seq_length
        }


if __name__ == "__main__":
    # 测试代码
    print("=" * 50)
    print("测试 Embedder 模块")
    print("=" * 50)
    
    # 创建 Embedder 实例（模型会下载到 ./data/models/）
    embedder = Embedder()
    
    # 测试单个文本
    text = "如何配置数据库？"
    vector = embedder.encode_single(text)
    print(f"\n文本: {text}")
    print(f"向量维度: {vector.shape}")
    print(f"向量前5维: {vector[:5]}")
    
    # 测试批量编码
    texts = [
        "如何配置数据库？",
        "Python 最佳实践",
        "机器学习入门指南"
    ]
    vectors = embedder.encode(texts, show_progress_bar=True)
    print(f"\n批量编码:")
    print(f"文本数量: {len(texts)}")
    print(f"向量矩阵形状: {vectors.shape}")
    
    # 测试相似度计算
    from sklearn.metrics.pairwise import cosine_similarity
    
    vec1 = embedder.encode_single("如何配置数据库？")
    vec2 = embedder.encode_single("数据库连接设置方法")
    similarity = cosine_similarity([vec1], [vec2])[0][0]
    print(f"\n相似度测试:")
    print(f"文本1: 如何配置数据库？")
    print(f"文本2: 数据库连接设置方法")
    print(f"相似度: {similarity:.4f}")
    
    # 打印模型信息
    print(f"\n模型信息:")
    for key, value in embedder.get_model_info().items():
        print(f"  {key}: {value}")
    
    print("\n✅ 测试完成！")
