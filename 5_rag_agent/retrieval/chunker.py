"""
@generated-by AI: matthewmli
@generated-date 2026-03-26
"""
from typing import List, Dict, Any


class Chunker:
    """文档切片器，支持按段落切片"""
    
    def __init__(
        self, 
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separator: str = "\n\n"
    ):
        """
        初始化切片器
        
        Args:
            chunk_size: 每个块的最大字符数
            chunk_overlap: 块之间的重叠字符数
            separator: 分隔符，用于分割段落
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator
        
        print(f"🔪 Chunker 初始化完成")
        print(f"   块大小: {chunk_size} 字符")
        print(f"   重叠大小: {chunk_overlap} 字符")
        print(f"   分隔符: {repr(separator)}")
    
    def chunk_text(
        self, 
        text: str, 
        metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        切片单个文本
        
        Args:
            text: 文本内容
            metadata: 元数据（如文件名、来源等）
            
        Returns:
            片段列表，每个片段包含 text、chunk_id、metadata 等
        """
        if not text:
            return []
        
        if metadata is None:
            metadata = {}
        
        # 先按分隔符分割成段落
        paragraphs = text.split(self.separator)
        
        chunks = []
        current_chunk = ""
        chunk_id = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 如果当前段落就超过 chunk_size，需要进一步分割
            if len(para) > self.chunk_size:
                # 先保存当前累积的内容
                if current_chunk:
                    chunks.append(self._create_chunk(
                        current_chunk.strip(),
                        chunk_id,
                        metadata
                    ))
                    chunk_id += 1
                    current_chunk = ""
                
                # 将大段落切分成小块
                para_chunks = self._split_large_paragraph(para)
                for pc in para_chunks:
                    chunks.append(self._create_chunk(
                        pc,
                        chunk_id,
                        metadata
                    ))
                    chunk_id += 1
            
            # 如果当前段落可以加入当前块
            elif len(current_chunk) + len(para) + len(self.separator) <= self.chunk_size:
                if current_chunk:
                    current_chunk += self.separator + para
                else:
                    current_chunk = para
            
            # 当前块已满，保存并开始新块
            else:
                if current_chunk:
                    chunks.append(self._create_chunk(
                        current_chunk.strip(),
                        chunk_id,
                        metadata
                    ))
                    chunk_id += 1
                
                # 添加重叠内容
                if self.chunk_overlap > 0 and len(current_chunk) > self.chunk_overlap:
                    overlap_text = current_chunk[-self.chunk_overlap:]
                    current_chunk = overlap_text + self.separator + para
                else:
                    current_chunk = para
        
        # 保存最后一个块
        if current_chunk.strip():
            chunks.append(self._create_chunk(
                current_chunk.strip(),
                chunk_id,
                metadata
            ))
        
        return chunks
    
    def _split_large_paragraph(self, text: str) -> List[str]:
        """
        将过大的段落切分成小块
        
        Args:
            text: 大段落文本
            
        Returns:
            小块列表
        """
        chunks = []
        
        # 按句子分割（简单实现）
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            # 遇到句号、问号、感叹号时分割
            if char in ['。', '！', '？', '.', '!', '?']:
                sentences.append(current_sentence.strip())
                current_sentence = ""
        
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        # 将句子组合成块
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        # 如果句子太长，强制分割
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= self.chunk_size:
                final_chunks.append(chunk)
            else:
                # 强制按字符数分割
                for i in range(0, len(chunk), self.chunk_size):
                    final_chunks.append(chunk[i:i+self.chunk_size])
        
        return final_chunks
    
    def _create_chunk(
        self, 
        text: str, 
        chunk_id: int, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建片段对象
        
        Args:
            text: 片段文本
            chunk_id: 片段ID
            metadata: 元数据
            
        Returns:
            片段字典
        """
        chunk = {
            "text": text,
            "chunk_id": chunk_id,
            "char_count": len(text),
            **metadata  # 展开元数据
        }
        return chunk
    
    def chunk_document(self, document: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        切片单个文档
        
        Args:
            document: 文档字典，包含 path、content 等
            
        Returns:
            片段列表
        """
        metadata = {
            "source": document.get("filename", "unknown"),
            "path": document.get("path", ""),
            "type": document.get("type", "unknown")
        }
        
        chunks = self.chunk_text(document["content"], metadata)
        
        print(f"   📄 {document['filename']}: {len(chunks)} 个片段")
        
        return chunks
    
    def chunk_documents(self, documents: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        批量切片文档
        
        Args:
            documents: 文档列表
            
        Returns:
            所有片段列表
        """
        all_chunks = []
        
        print(f"\n🔪 开始切片 {len(documents)} 个文档...")
        
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        
        # 统计信息
        total_chars = sum(chunk['char_count'] for chunk in all_chunks)
        avg_chunk_size = total_chars / len(all_chunks) if all_chunks else 0
        
        print(f"\n✅ 切片完成!")
        print(f"📊 统计信息:")
        print(f"   文档数: {len(documents)}")
        print(f"   片段数: {len(all_chunks)}")
        print(f"   总字符: {total_chars:,}")
        print(f"   平均片段大小: {avg_chunk_size:.1f} 字符")
        
        return all_chunks


if __name__ == "__main__":
    # 测试代码
    print("=" * 50)
    print("测试 Chunker 模块")
    print("=" * 50)
    
    # ========== 测试 1: 基础切片 ==========
    print("\n📝 测试 1: 基础切片")
    
    chunker = Chunker(chunk_size=100, chunk_overlap=20)
    
    text = """
这是第一段内容。这是一些测试文本。

这是第二段内容。这里还有更多的文本内容用于测试切片功能。

这是第三段内容。我们需要确保切片功能能够正常工作。
"""
    
    chunks = chunker.chunk_text(text, metadata={"source": "test.txt"})
    
    print(f"\n生成 {len(chunks)} 个片段:")
    for chunk in chunks:
        print(f"\n[片段 {chunk['chunk_id']}]")
        print(f"字符数: {chunk['char_count']}")
        print(f"内容: {chunk['text'][:50]}...")
    
    # ========== 测试 2: 大段落切片 ==========
    print("\n📝 测试 2: 大段落切片")
    
    long_text = "这是一个很长的段落。" * 100
    chunks = chunker.chunk_text(long_text, metadata={"source": "long.txt"})
    
    print(f"\n生成 {len(chunks)} 个片段:")
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"\n[片段 {chunk['chunk_id']}]")
        print(f"字符数: {chunk['char_count']}")
        print(f"内容预览: {chunk['text'][:50]}...")
    
    if len(chunks) > 3:
        print(f"... 还有 {len(chunks) - 3} 个片段")
    
    # ========== 测试 3: 文档切片 ==========
    print("\n📝 测试 3: 文档切片")
    
    chunker = Chunker(chunk_size=200, chunk_overlap=30)
    
    documents = [
        {
            "path": "/path/to/doc1.txt",
            "filename": "doc1.txt",
            "content": "这是第一个文档的内容。\n\n这是第二段。\n\n这是第三段。" * 5,
            "type": "txt"
        },
        {
            "path": "/path/to/doc2.md",
            "filename": "doc2.md",
            "content": "# 标题\n\n这是Markdown文档。\n\n## 子标题\n\n这是另一段内容。" * 3,
            "type": "md"
        }
    ]
    
    all_chunks = chunker.chunk_documents(documents)
    
    print(f"\n片段详情:")
    for chunk in all_chunks[:5]:
        print(f"  [{chunk['chunk_id']}] {chunk['source']} - {chunk['char_count']} 字符")
    
    if len(all_chunks) > 5:
        print(f"  ... 还有 {len(all_chunks) - 5} 个片段")
    
    # ========== 测试 4: 不同参数对比 ==========
    print("\n📝 测试 4: 不同参数对比")
    
    test_text = "这是一段测试文本。" * 50
    
    chunker_small = Chunker(chunk_size=100, chunk_overlap=10)
    chunker_medium = Chunker(chunk_size=300, chunk_overlap=30)
    chunker_large = Chunker(chunk_size=500, chunk_overlap=50)
    
    chunks_small = chunker_small.chunk_text(test_text)
    chunks_medium = chunker_medium.chunk_text(test_text)
    chunks_large = chunker_large.chunk_text(test_text)
    
    print(f"\n参数对比:")
    print(f"  chunk_size=100:  {len(chunks_small)} 个片段")
    print(f"  chunk_size=300:  {len(chunks_medium)} 个片段")
    print(f"  chunk_size=500:  {len(chunks_large)} 个片段")
    
    print("\n✅ 所有测试完成！")
