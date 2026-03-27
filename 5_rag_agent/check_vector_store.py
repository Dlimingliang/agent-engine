#!/usr/bin/env python3
"""
@generated-by AI: matthewmli
@generated-date 2026-03-27
"""
"""检查向量库状态"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from retrieval.vector_store import VectorStore
from qdrant_client import QdrantClient

def main():
    print("=" * 60)
    print("检查向量库状态")
    print("=" * 60)
    
    # 1. 检查默认路径下的数据目录
    default_path = os.path.join(os.path.dirname(__file__), "data", "qdrant_data")
    print(f"\n📁 默认数据目录: {default_path}")
    
    if os.path.exists(default_path):
        print("✅ 数据目录存在")
        
        # 列出目录内容
        items = os.listdir(default_path)
        if items:
            print(f"   目录内容: {items}")
        else:
            print("   ⚠️  目录为空")
    else:
        print("❌ 数据目录不存在")
        return
    
    # 2. 连接向量库并检查集合
    print("\n" + "=" * 60)
    print("连接向量库")
    print("=" * 60)
    
    try:
        client = QdrantClient(path=default_path)
        
        # 获取所有集合
        collections = client.get_collections().collections
        print(f"\n📊 发现 {len(collections)} 个集合:")
        
        for collection in collections:
            print(f"\n  集合名称: {collection.name}")
            
            # 获取集合详细信息
            info = client.get_collection(collection.name)
            print(f"  向量数量: {info.points_count}")
            print(f"  状态: {info.status.value}")
            
            # 尝试获取向量维度
            try:
                if hasattr(info.config.params, 'vectors'):
                    vectors_config = info.config.params.vectors
                    if hasattr(vectors_config, 'size'):
                        print(f"  向量维度: {vectors_config.size}")
                        if hasattr(vectors_config, 'distance'):
                            print(f"  距离度量: {vectors_config.distance.value}")
            except:
                pass
        
        # 3. 显示集合详细信息（使用已有的 client 实例）
        print("\n" + "=" * 60)
        print("集合详细信息")
        print("=" * 60)
        
        info = client.get_collection("knowledge_base")
        print(f"\n✅ 集合信息:")
        print(f"  集合名称: knowledge_base")
        print(f"  向量数量: {info.points_count}")
        print(f"  状态: {info.status.value}")
            
        # 4. 随机查看几个向量样本
        print("\n" + "=" * 60)
        print("查看向量样本（前 3 个）")
        print("=" * 60)
        
        try:
            # 使用 scroll 方法获取前几个点
            points, _ = client.scroll(
                collection_name="knowledge_base",
                limit=3,
                with_payload=True,
                with_vectors=False
            )
            
            if points:
                print(f"\n找到 {len(points)} 个样本:")
                for i, point in enumerate(points, 1):
                    print(f"\n[样本 {i}]")
                    print(f"  ID: {point.id}")
                    print(f"  Payload 字段: {list(point.payload.keys())}")
                    
                    # 显示部分 payload 内容
                    if 'source' in point.payload:
                        print(f"  来源: {point.payload['source']}")
                    if 'chunk_id' in point.payload:
                        print(f"  片段ID: {point.payload['chunk_id']}")
                    if 'text' in point.payload:
                        text = point.payload['text']
                        preview = text[:80] + "..." if len(text) > 80 else text
                        print(f"  文本预览: {preview}")
            else:
                print("⚠️  集合中没有向量")
                
        except Exception as e:
            print(f"❌ 获取样本失败: {e}")
        
    except Exception as e:
        print(f"❌ 连接向量库失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
