"""
@generated-by AI: matthewmli
@generated-date 2026-03-26
"""
import os
from typing import List, Dict, Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)


class VectorStore:
    """Qdrant 向量库封装类"""
    
    # 类级别的默认集合名称
    DEFAULT_COLLECTION = "knowledge_base"
    
    def __init__(
        self,
        collection_name: str = None,
        vector_size: int = 1024,
        distance: Distance = Distance.COSINE,
        path: Optional[str] = None
    ):
        """
        初始化向量存储
        
        Args:
            collection_name: 集合名称，默认为 "knowledge_base"
            vector_size: 向量维度（默认 1024，对应 bge-large-zh）
            distance: 距离度量方式（默认余弦相似度）
            path: 数据存储路径，默认为 ./data/qdrant_data/
        """
        # 设置默认集合名称
        if collection_name is None:
            collection_name = self.DEFAULT_COLLECTION
        
        # 设置默认存储路径
        if path is None:
            path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data",
                "qdrant_data"
            )
        
        # 确保目录存在
        os.makedirs(path, exist_ok=True)
        
        # 初始化 Qdrant 客户端（嵌入式模式）
        self.client = QdrantClient(path=path)
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.distance = distance
        
        print(f"📂 Qdrant 数据路径: {path}")
        print(f"📦 集合名称: {collection_name}")
        print(f"📏 向量维度: {vector_size}")
        print(f"🎯 距离度量: {distance}")
    
    def __del__(self):
        """析构函数，优雅关闭客户端"""
        try:
            if hasattr(self, 'client') and self.client:
                self.client.close()
        except:
            pass  # 忽略关闭时的错误
    
    def create_collection(self, overwrite: bool = False) -> bool:
        """
        创建集合
        
        Args:
            overwrite: 是否覆盖已存在的集合
            
        Returns:
            是否创建成功
        """
        try:
            # 检查集合是否存在
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if exists:
                if overwrite:
                    print(f"🗑️  集合已存在，正在删除...")
                    self.client.delete_collection(self.collection_name)
                else:
                    print(f"ℹ️  集合已存在: {self.collection_name}")
                    return True
            
            # 创建集合
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=self.distance
                )
            )
            
            print(f"✅ 集合创建成功: {self.collection_name}")
            return True
            
        except Exception as e:
            print(f"❌ 创建集合失败: {e}")
            return False
    
    def insert_vectors(
        self,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[int]] = None
    ) -> bool:
        """
        批量插入向量和元数据
        
        Args:
            vectors: 向量列表
            payloads: 元数据列表
            ids: ID 列表（可选，不提供则自动生成）
            
        Returns:
            是否插入成功
        """
        if not vectors or not payloads:
            print("❌ 向量或元数据为空")
            return False
        
        if len(vectors) != len(payloads):
            print(f"❌ 向量数量({len(vectors)})与元数据数量({len(payloads)})不匹配")
            return False
        
        try:
            # 生成 ID
            if ids is None:
                # 获取当前集合中的点数量，用于生成新 ID
                try:
                    info = self.client.get_collection(self.collection_name)
                    start_id = info.points_count
                except:
                    start_id = 0
                ids = list(range(start_id, start_id + len(vectors)))
            
            # 构造 PointStruct 列表
            points = [
                PointStruct(
                    id=ids[i],
                    vector=vectors[i],
                    payload=payloads[i]
                )
                for i in range(len(vectors))
            ]
            
            # 批量插入
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            print(f"✅ 成功插入 {len(vectors)} 个向量")
            return True
            
        except Exception as e:
            print(f"❌ 插入向量失败: {e}")
            return False
    
    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        score_threshold: Optional[float] = None,
        query_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        向量检索
        
        Args:
            query_vector: 查询向量
            top_k: 返回结果数量
            score_threshold: 相似度阈值（可选）
            query_filter: 过滤条件（可选）
                例如: {"source": "config.md"} 按文件名过滤
                例如: {"topic": "python"} 按主题过滤
            
        Returns:
            检索结果列表，格式: [
                {
                    "id": 1,
                    "score": 0.85,
                    "text": "文档内容",
                    "source": "doc.md",
                    ...其他元数据
                },
                ...
            ]
        """
        try:
            # 构造过滤条件
            filter_obj = None
            if query_filter:
                conditions = []
                for key, value in query_filter.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                filter_obj = Filter(must=conditions)
            
            # 执行检索（使用 query_points 方法，适配新版 API）
            try:
                results = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    limit=top_k,
                    score_threshold=score_threshold,
                    query_filter=filter_obj,
                    with_payload=True
                )
                
                # 格式化结果
                formatted_results = []
                for result in results.points:
                    formatted_results.append({
                        "id": result.id,
                        "score": result.score,
                        **result.payload  # 展开元数据
                    })
                
                return formatted_results
            except AttributeError:
                # 如果 query_points 不存在，尝试旧的 search 方法
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=top_k,
                    score_threshold=score_threshold,
                    query_filter=filter_obj,
                    with_payload=True
                )
                
                # 格式化结果
                formatted_results = []
                for result in results:
                    formatted_results.append({
                        "id": result.id,
                        "score": result.score,
                        **result.payload  # 展开元数据
                    })
                
                return formatted_results
            
        except Exception as e:
            print(f"❌ 检索失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def delete_collection(self) -> bool:
        """
        删除集合
        
        Returns:
            是否删除成功
        """
        try:
            self.client.delete_collection(self.collection_name)
            print(f"✅ 集合已删除: {self.collection_name}")
            return True
        except Exception as e:
            print(f"❌ 删除集合失败: {e}")
            return False
    
    def get_collection_info(self) -> Optional[Dict[str, Any]]:
        """
        获取集合信息
        
        Returns:
            集合信息字典
        """
        try:
            info = self.client.get_collection(self.collection_name)
            result = {
                "collection_name": self.collection_name,
                "points_count": info.points_count,
                "status": info.status.value,
            }
            
            # 尝试获取向量配置（不同版本的 API 可能不同）
            try:
                if hasattr(info.config.params, 'vectors'):
                    vectors_config = info.config.params.vectors
                    if hasattr(vectors_config, 'size'):
                        result["vector_size"] = vectors_config.size
                        result["distance"] = vectors_config.distance.value if hasattr(vectors_config, 'distance') else "unknown"
            except:
                pass
                
            return result
        except Exception as e:
            print(f"❌ 获取集合信息失败: {e}")
            return None
    
    def list_collections(self) -> List[str]:
        """
        列出所有集合
        
        Returns:
            集合名称列表
        """
        try:
            collections = self.client.get_collections().collections
            return [c.name for c in collections]
        except Exception as e:
            print(f"❌ 获取集合列表失败: {e}")
            return []
    
    def get_all_points(
        self,
        limit: int = 100,
        with_vectors: bool = False
    ) -> List[Dict[str, Any]]:
        """
        获取所有点（用于调试）
        
        Args:
            limit: 最大返回数量
            with_vectors: 是否包含向量
            
        Returns:
            点列表
        """
        try:
            results, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=with_vectors
            )
            
            points = []
            for point in results:
                point_data = {
                    "id": point.id,
                    **point.payload
                }
                if with_vectors:
                    point_data["vector"] = point.vector
                points.append(point_data)
            
            return points
            
        except Exception as e:
            print(f"❌ 获取点失败: {e}")
            return []
    
    def delete_points(self, ids: List[int]) -> bool:
        """
        删除指定的点
        
        Args:
            ids: 点 ID 列表
            
        Returns:
            是否删除成功
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=ids
            )
            print(f"✅ 成功删除 {len(ids)} 个点")
            return True
        except Exception as e:
            print(f"❌ 删除点失败: {e}")
            return False


if __name__ == "__main__":
    # 测试代码
    print("=" * 50)
    print("测试 VectorStore 模块")
    print("=" * 50)
    
    # 创建 VectorStore 实例（使用默认集合名）
    store = VectorStore()  # 默认使用 "knowledge_base" 集合
    
    # ========== 测试 1: 创建集合 ==========
    print("\n📋 测试 1: 创建集合")
    store.create_collection(overwrite=True)
    
    # ========== 测试 2: 插入向量 ==========
    print("\n📥 测试 2: 插入向量（带主题元数据）")
    
    # 模拟向量和元数据
    test_vectors = [
        [0.1] * 1024,
        [0.2] * 1024,
        [0.3] * 1024,
    ]
    
    # 元数据中包含主题信息
    test_payloads = [
        {"text": "Python 基础语法", "source": "python_basics.md", "topic": "python"},
        {"text": "MySQL 配置说明", "source": "mysql_config.md", "topic": "database"},
        {"text": "Python 函数定义", "source": "python_func.md", "topic": "python"},
    ]
    
    store.insert_vectors(test_vectors, test_payloads)
    
    # ========== 测试 3: 获取集合信息 ==========
    print("\n📊 测试 3: 获取集合信息")
    info = store.get_collection_info()
    if info:
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    # ========== 测试 4: 基础检索 ==========
    print("\n🔍 测试 4: 基础检索（不限制主题）")
    
    query_vector = [0.15] * 1024
    results = store.search(query_vector, top_k=3)
    
    print(f"检索到 {len(results)} 个结果:")
    for i, result in enumerate(results, 1):
        print(f"  [{i}] {result['text']} (主题: {result['topic']}, 相似度: {result['score']:.4f})")
    
    # ========== 测试 5: 按主题过滤检索 ==========
    print("\n🔎 测试 5: 按主题过滤检索")
    
    results = store.search(
        query_vector=query_vector,
        top_k=3,
        query_filter={"topic": "python"}  # 只搜索 Python 主题
    )
    
    print(f"过滤条件: topic = python")
    print(f"检索到 {len(results)} 个结果:")
    for i, result in enumerate(results, 1):
        print(f"  [{i}] {result['text']} (主题: {result['topic']}, 相似度: {result['score']:.4f})")
    
    # ========== 测试 6: 多集合演示（可选）==========
    print("\n📁 测试 6: 列出所有集合")
    collections = store.list_collections()
    print(f"当前所有集合: {collections}")
    
    print("\n💡 提示: 可以创建多个 VectorStore 实例来管理不同集合")
    print("   例如: python_store = VectorStore(collection_name='python_docs')")
    
    # ========== 测试 7: 删除集合 ==========
    print("\n🗑️  测试 7: 删除集合")
    store.delete_collection()
    
    print("\n✅ 所有测试完成！")
