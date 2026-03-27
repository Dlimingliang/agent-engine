"""
@generated-by AI: matthewmli
@generated-date 2026-03-26
"""
import os
import sys
import argparse

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval.document_loader import DocumentLoader
from retrieval.chunker import Chunker
from retrieval.embedder import Embedder
from retrieval.vector_store import VectorStore


def import_documents(
    input_path: str,
    collection_name: str = "knowledge_base",
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    rebuild: bool = False,
    recursive: bool = True
):
    """
    导入文档到向量库
    
    Args:
        input_path: 输入路径（文件或目录）
        collection_name: 集合名称
        chunk_size: 片段大小
        chunk_overlap: 片段重叠
        rebuild: 是否重建索引
        recursive: 是否递归加载子目录
    """
    print("=" * 60)
    print("📚 文档导入工具")
    print("=" * 60)
    
    # ========== 1. 初始化各模块 ==========
    print("\n📦 初始化模块...")
    
    loader = DocumentLoader()
    chunker = Chunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    embedder = Embedder()
    store = VectorStore(collection_name=collection_name)
    
    # ========== 2. 加载文档 ==========
    print("\n" + "=" * 60)
    print("第一步：加载文档")
    print("=" * 60)
    
    if os.path.isfile(input_path):
        # 加载单个文件
        documents = []
        doc = loader.load_file(input_path)
        if doc:
            documents.append(doc)
    elif os.path.isdir(input_path):
        # 加载目录
        documents = loader.load_directory(input_path, recursive=recursive)
    else:
        print(f"❌ 路径不存在: {input_path}")
        return
    
    if not documents:
        print("❌ 没有找到可加载的文档")
        return
    
    # ========== 3. 切片 ==========
    print("\n" + "=" * 60)
    print("第二步：文档切片")
    print("=" * 60)
    
    chunks = chunker.chunk_documents(documents)
    
    if not chunks:
        print("❌ 没有生成任何片段")
        return
    
    # ========== 4. 向量化 ==========
    print("\n" + "=" * 60)
    print("第三步：向量化")
    print("=" * 60)
    
    print(f"🔄 正在向量化 {len(chunks)} 个片段...")
    
    texts = [chunk['text'] for chunk in chunks]
    vectors = embedder.encode(texts, show_progress_bar=True)
    
    print(f"✅ 向量化完成！")
    print(f"   向量形状: {vectors.shape}")
    
    # ========== 5. 存储到向量库 ==========
    print("\n" + "=" * 60)
    print("第四步：存储到向量库")
    print("=" * 60)
    
    # 创建集合
    store.create_collection(overwrite=rebuild)
    
    # 准备 payloads
    payloads = []
    for chunk in chunks:
        payload = {
            "text": chunk['text'],
            "source": chunk['source'],
            "chunk_id": chunk['chunk_id'],
            "char_count": chunk['char_count']
        }
        # 添加可选字段
        if 'path' in chunk:
            payload['path'] = chunk['path']
        if 'type' in chunk:
            payload['type'] = chunk['type']
        
        payloads.append(payload)
    
    # 插入向量
    store.insert_vectors(vectors.tolist(), payloads)
    
    # ========== 6. 验证 ==========
    print("\n" + "=" * 60)
    print("第五步：验证")
    print("=" * 60)
    
    info = store.get_collection_info()
    if info:
        print(f"✅ 导入成功！")
        print(f"\n📊 集合信息:")
        print(f"   集合名称: {info['collection_name']}")
        print(f"   向量数量: {info['points_count']}")
        print(f"   状态: {info['status']}")
    
    print("\n" + "=" * 60)
    print("🎉 导入完成！")
    print("=" * 60)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="文档导入工具 - 将文档导入到向量库",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 导入单个文件
  python scripts/import_docs.py --file data/knowledge_base/readme.md
  
  # 导入整个目录
  python scripts/import_docs.py --dir data/knowledge_base/
  
  # 重建索引（清空原有数据）
  python scripts/import_docs.py --dir data/knowledge_base/ --rebuild
  
  # 自定义切片参数
  python scripts/import_docs.py --dir data/knowledge_base/ --chunk-size 300 --chunk-overlap 30
  
  # 指定集合名称
  python scripts/import_docs.py --dir data/knowledge_base/ --collection my_docs
        """
    )
    
    # 互斥参数组：file 或 dir
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--file',
        type=str,
        help='导入单个文件'
    )
    group.add_argument(
        '--dir',
        type=str,
        help='导入整个目录'
    )
    
    # 可选参数
    parser.add_argument(
        '--collection',
        type=str,
        default='knowledge_base',
        help='集合名称（默认: knowledge_base）'
    )
    
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=500,
        help='片段大小，单位：字符（默认: 500）'
    )
    
    parser.add_argument(
        '--chunk-overlap',
        type=int,
        default=50,
        help='片段重叠大小，单位：字符（默认: 50）'
    )
    
    parser.add_argument(
        '--rebuild',
        action='store_true',
        help='重建索引（清空原有数据）'
    )
    
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='不递归加载子目录'
    )
    
    args = parser.parse_args()
    
    # 确定输入路径
    input_path = args.file if args.file else args.dir
    
    # 执行导入
    import_documents(
        input_path=input_path,
        collection_name=args.collection,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        rebuild=args.rebuild,
        recursive=not args.no_recursive
    )


if __name__ == "__main__":
    main()
