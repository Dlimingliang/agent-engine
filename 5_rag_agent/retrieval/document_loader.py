"""
@generated-by AI: matthewmli
@generated-date 2026-03-26
"""
import os
from typing import List, Dict, Optional
import re


class DocumentLoader:
    """文档加载器，支持多种格式文档的读取"""
    
    SUPPORTED_EXTENSIONS = ['.txt', '.md', '.pdf', '.docx']
    
    def __init__(self):
        """初始化文档加载器"""
        print("📄 DocumentLoader 初始化完成")
    
    def load_file(self, file_path: str) -> Optional[Dict[str, str]]:
        """
        加载单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            文档字典，包含 path、content、type 等信息，失败返回 None
        """
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return None
        
        # 获取文件扩展名
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext not in self.SUPPORTED_EXTENSIONS:
            print(f"❌ 不支持的文件格式: {ext}")
            return None
        
        # 根据扩展名选择加载方法
        try:
            if ext == '.txt':
                content = self._load_txt(file_path)
            elif ext == '.md':
                content = self._load_markdown(file_path)
            elif ext == '.pdf':
                content = self._load_pdf(file_path)
            elif ext == '.docx':
                content = self._load_docx(file_path)
            else:
                return None
            
            if content is None:
                return None
            
            # 返回文档信息
            return {
                "path": file_path,
                "filename": os.path.basename(file_path),
                "content": content,
                "type": ext[1:],  # 去掉点号
                "size": len(content)
            }
            
        except Exception as e:
            print(f"❌ 加载文件失败 {file_path}: {e}")
            return None
    
    def _load_txt(self, file_path: str) -> Optional[str]:
        """加载 txt 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ 加载 TXT: {os.path.basename(file_path)} ({len(content)} 字符)")
            return content
        except Exception as e:
            print(f"❌ 加载 TXT 失败: {e}")
            return None
    
    def _load_markdown(self, file_path: str) -> Optional[str]:
        """加载 markdown 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ 加载 Markdown: {os.path.basename(file_path)} ({len(content)} 字符)")
            return content
        except Exception as e:
            print(f"❌ 加载 Markdown 失败: {e}")
            return None
    
    def _load_pdf(self, file_path: str) -> Optional[str]:
        """加载 PDF 文件"""
        try:
            import pypdf
            
            text_content = []
            with open(file_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                for page_num, page in enumerate(reader.pages, 1):
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            content = '\n\n'.join(text_content)
            print(f"✅ 加载 PDF: {os.path.basename(file_path)} ({len(content)} 字符)")
            return content
            
        except ImportError:
            print("❌ 缺少 pypdf 库，请运行: pip install pypdf")
            return None
        except Exception as e:
            print(f"❌ 加载 PDF 失败: {e}")
            return None
    
    def _load_docx(self, file_path: str) -> Optional[str]:
        """加载 Word 文档"""
        try:
            from docx import Document
            
            doc = Document(file_path)
            text_content = []
            
            for para in doc.paragraphs:
                if para.text.strip():
                    text_content.append(para.text)
            
            content = '\n\n'.join(text_content)
            print(f"✅ 加载 DOCX: {os.path.basename(file_path)} ({len(content)} 字符)")
            return content
            
        except ImportError:
            print("❌ 缺少 python-docx 库，请运行: pip install python-docx")
            return None
        except Exception as e:
            print(f"❌ 加载 DOCX 失败: {e}")
            return None
    
    def load_directory(
        self, 
        dir_path: str, 
        recursive: bool = True,
        extensions: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """
        加载目录下的所有文档
        
        Args:
            dir_path: 目录路径
            recursive: 是否递归加载子目录
            extensions: 指定文件扩展名列表，如 ['.md', '.txt']
            
        Returns:
            文档列表
        """
        if not os.path.exists(dir_path):
            print(f"❌ 目录不存在: {dir_path}")
            return []
        
        if extensions is None:
            extensions = self.SUPPORTED_EXTENSIONS
        
        documents = []
        
        print(f"\n📂 开始扫描目录: {dir_path}")
        print(f"   递归: {recursive}")
        print(f"   扩展名: {extensions}")
        
        # 遍历目录
        if recursive:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    _, ext = os.path.splitext(file)
                    if ext.lower() in extensions:
                        file_path = os.path.join(root, file)
                        doc = self.load_file(file_path)
                        if doc:
                            documents.append(doc)
        else:
            for file in os.listdir(dir_path):
                _, ext = os.path.splitext(file)
                if ext.lower() in extensions:
                    file_path = os.path.join(dir_path, file)
                    doc = self.load_file(file_path)
                    if doc:
                        documents.append(doc)
        
        print(f"\n✅ 共加载 {len(documents)} 个文档")
        
        # 统计信息
        total_size = sum(doc['size'] for doc in documents)
        type_stats = {}
        for doc in documents:
            doc_type = doc['type']
            type_stats[doc_type] = type_stats.get(doc_type, 0) + 1
        
        print(f"📊 统计信息:")
        print(f"   总字符数: {total_size:,}")
        print(f"   文件类型: {type_stats}")
        
        return documents


if __name__ == "__main__":
    # 测试代码
    print("=" * 50)
    print("测试 DocumentLoader 模块")
    print("=" * 50)
    
    loader = DocumentLoader()
    
    # ========== 测试 1: 创建测试文件 ==========
    print("\n📝 测试 1: 创建测试文件")
    
    test_dir = "./test_docs"
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建测试文本文件
    with open(f"{test_dir}/test.txt", 'w', encoding='utf-8') as f:
        f.write("这是一个测试文本文件。\n" * 10)
    
    # 创建测试 Markdown 文件
    with open(f"{test_dir}/test.md", 'w', encoding='utf-8') as f:
        f.write("# 测试文档\n\n")
        f.write("## 第一章\n\n")
        f.write("这是第一段内容。\n\n")
        f.write("## 第二章\n\n")
        f.write("这是第二段内容。\n")
    
    # 创建子目录
    os.makedirs(f"{test_dir}/subdir", exist_ok=True)
    with open(f"{test_dir}/subdir/nested.md", 'w', encoding='utf-8') as f:
        f.write("# 嵌套文档\n\n这是一个嵌套目录中的文档。\n")
    
    print(f"✅ 测试文件创建完成")
    
    # ========== 测试 2: 加载单个文件 ==========
    print("\n📄 测试 2: 加载单个文件")
    
    doc = loader.load_file(f"{test_dir}/test.txt")
    if doc:
        print(f"   文件名: {doc['filename']}")
        print(f"   类型: {doc['type']}")
        print(f"   大小: {doc['size']} 字符")
        print(f"   内容预览: {doc['content'][:50]}...")
    
    # ========== 测试 3: 加载目录（递归）==========
    print("\n📂 测试 3: 加载目录（递归）")
    
    docs = loader.load_directory(test_dir, recursive=True)
    
    print(f"\n加载的文档列表:")
    for i, doc in enumerate(docs, 1):
        print(f"  [{i}] {doc['filename']} ({doc['type']}, {doc['size']} 字符)")
    
    # ========== 测试 4: 加载目录（不递归）==========
    print("\n📂 测试 4: 加载目录（不递归）")
    
    docs = loader.load_directory(test_dir, recursive=False)
    
    print(f"\n加载的文档列表:")
    for i, doc in enumerate(docs, 1):
        print(f"  [{i}] {doc['filename']} ({doc['type']}, {doc['size']} 字符)")
    
    # ========== 测试 5: 指定扩展名 ==========
    print("\n📂 测试 5: 只加载 Markdown 文件")
    
    docs = loader.load_directory(test_dir, recursive=True, extensions=['.md'])
    
    print(f"\n加载的文档列表:")
    for i, doc in enumerate(docs, 1):
        print(f"  [{i}] {doc['filename']} ({doc['type']}, {doc['size']} 字符)")
    
    # ========== 清理测试文件 ==========
    print("\n🗑️  清理测试文件")
    import shutil
    shutil.rmtree(test_dir)
    print("✅ 测试文件已删除")
    
    print("\n✅ 所有测试完成！")
