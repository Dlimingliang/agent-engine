# 第五周：RAG 基础与知识库接入

## 项目目标

实现一个支持文档问答的 Agent，从外部知识库检索信息并生成带引用的回答。

---

## 技术决策

| 决策项 | 选择 | 说明 |
|--------|------|------|
| 项目场景 | 文档问答 Agent | 导入文档、检索问答、引用溯源 |
| 向量数据库 | Qdrant | 高性能、开源、支持本地运行 |
| Embedding 模型 | BAAI/bge-large-zh | 中文最优、免费、本地运行 |
| 切片策略 | 按段落切片 | 简单高效，适合入门 |
| 检索方式 | 向量检索 | 支持 Top-K 召回 |
| 引用格式 | 文件名 + 片段ID | 便于溯源 |
| 存储方式 | 嵌入式模式 | 数据存储在本地文件 |

---

## 核心概念

### 1. Chunking（文档切片）

**定义**：将长文档切分成小块，便于向量化和检索。

**三种切片方式对比**：

| 方式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **按段落切片** | 简单、均匀 | 可能切断语义 | 通用场景（推荐入门） |
| **按语义切片** | 保持语义完整 | 计算量大、块大小不均 | 高质量要求场景 |
| **按标题切片** | 结构清晰 | 依赖文档格式 | Markdown/结构化文档 |

**本周末期采用**：按段落切片（固定字符数，如每 500 字）

```python
# 切片示例
text = "长文档内容..." * 1000
chunks = [text[i:i+500] for i in range(0, len(text), 500)]
```

**关键参数**：
- `chunk_size`: 每个块的大小（建议 300-800 字符）
- `chunk_overlap`: 块之间的重叠（建议 50-100 字符）

---

### 2. Embedding（向量化）

**定义**：将文本转换为数值向量，让计算机理解语义。

**工作流程**：
```
文本 → Embedding 模型 → 向量（1024 维）
```

**bge-large-zh 模型特点**：
- 参数量：326M
- 向量维度：1024
- 最大输入：512 tokens
- 支持中文：优秀
- 存储大小：~1.3GB

**使用示例**：
```python
from sentence_transformers import SentenceTransformer

# 加载模型（首次会自动下载）
model = SentenceTransformer("BAAI/bge-large-zh")

# 向量化文本
texts = ["如何配置数据库？", "Python 最佳实践"]
vectors = model.encode(texts)

# vectors.shape = (2, 1024)
```

**首次使用说明**：
- 模型会自动下载到 `~/.cache/huggingface/hub/`
- 下载时间：几分钟（视网速而定）
- 后续使用无需再次下载

---

### 3. 向量检索

**定义**：根据问题向量，在向量数据库中找最相似的文档块。

**工作流程**：
```
用户问题 → Embedding → 问题向量
                          ↓
                Qdrant 向量数据库
                          ↓
                返回 Top-K 相似文档块
```

**关键理解**：召回不是答案
- 召回：找出可能相关的文档片段
- 答案：从这些片段中生成最终回答

**示例**：
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# 连接数据库
client = QdrantClient(path="./qdrant_data")

# 创建集合
client.create_collection(
    collection_name="my_docs",
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
)

# 插入向量
client.upsert(
    collection_name="my_docs",
    points=[
        {"id": 1, "vector": [0.1, 0.2, ...], "payload": {"text": "文档内容", "source": "doc.md"}}
    ]
)

# 检索
results = client.search(
    collection_name="my_docs",
    query_vector=[0.15, 0.25, ...],  # 问题向量
    limit=5
)
```

---

### 4. 引用溯源

**定义**：答案必须标注来源，便于验证和调试。

**引用格式**：
```
回答: 根据文档，配置步骤如下：
1. 在 config.yaml 中设置参数 [来源: config.md#L23-45]
2. 运行初始化脚本 [来源: setup.md#L10-20]
```

**存储的元数据**：
```python
{
    "id": "chunk_001",
    "vector": [0.1, 0.2, ...],
    "payload": {
        "text": "文档内容...",
        "source": "docs/config.md",  # 文件名
        "chunk_id": 5,                # 片段ID
        "page": 3,                    # 页码（PDF）
        "start_char": 1200,           # 起始字符
        "end_char": 1700              # 结束字符
    }
}
```

---

## 核心功能列表

### 1. 文档导入功能

- [ ] 读取文档（支持 txt, md, pdf, docx）
- [ ] 按段落切片（chunk_size 可配置）
- [ ] 生成 Embedding 向量
- [ ] 存入 Qdrant 向量库
- [ ] 保存元数据（文件名、片段ID、位置）

### 2. 检索功能

- [ ] 问题向量化
- [ ] 向量相似度检索
- [ ] 返回 Top-K 文档块
- [ ] 支持元数据过滤（如按文件类型）

### 3. 问答功能

- [ ] 检索增强回答（RAG）
- [ ] 注入检索到的文档到 Prompt
- [ ] 生成带引用的回答
- [ ] 检索不到时降级回答

### 4. 引用功能

- [ ] 记录来源信息
- [ ] 在回答中插入引用标记
- [ ] 格式化输出引用列表

### 5. Agent 集成功能

- [ ] 集成到第四周的 Agent 框架
- [ ] 记忆 + RAG 双检索
- [ ] 区分记忆来源与文档来源

---

## 目录结构

```
5_rag_agent/
├── agent/
│   ├── __init__.py              # 包初始化
│   ├── agent.py                 # Agent 主类（复用第四周）
│   └── message.py               # Message 消息类
├── retrieval/
│   ├── __init__.py              # 包初始化
│   ├── embedder.py              # Embedding 模型封装
│   ├── vector_store.py          # Qdrant 向量库封装
│   ├── document_loader.py       # 文档加载器
│   ├── chunker.py               # 文档切片器
│   └── retriever.py             # 检索器
├── citation/
│   ├── __init__.py              # 包初始化
│   ├── citation_handler.py      # 引用处理器
│   └── source_tracker.py        # 来源追踪器
├── tools/
│   ├── __init__.py              # 包初始化
│   ├── rag_tool.py              # RAG 检索工具
│   └── tool_registry.py         # 工具注册
├── data/
│   ├── knowledge_base/          # 知识库文档目录
│   │   ├── python_basics.md
│   │   ├── database_config.md
│   │   └── ...
│   └── qdrant_data/             # Qdrant 数据存储
├── scripts/
│   └── import_docs.py           # 文档导入脚本
├── main.py                      # CLI 主程序
├── requirements.txt             # 依赖包
└── README.md                    # 本文件
```

---

## 模块职责说明

### 1. retrieval/embedder.py - Embedding 模型封装

**Embedder 类**

**职责**：封装 bge-large-zh 模型，提供向量化接口

**需要实现的方法**：
```python
class Embedder:
    def __init__(self, model_name="BAAI/bge-large-zh"):
        """加载模型"""
        
    def encode(self, texts: List[str]) -> List[List[float]]:
        """将文本列表转换为向量列表"""
        
    def encode_single(self, text: str) -> List[float]:
        """将单个文本转换为向量"""
        
    def get_dimension(self) -> int:
        """获取向量维度（1024）"""
```

**使用示例**：
```python
embedder = Embedder()
vectors = embedder.encode(["文本1", "文本2"])
# vectors.shape = (2, 1024)
```

---

### 2. retrieval/vector_store.py - Qdrant 向量库封装

**VectorStore 类**

**职责**：封装 Qdrant 客户端，提供向量存储和检索接口

**需要实现的方法**：
```python
class VectorStore:
    def __init__(self, collection_name: str, vector_size: int = 1024):
        """初始化 Qdrant 客户端"""
        
    def create_collection(self):
        """创建集合"""
        
    def insert_vectors(self, vectors: List[List[float]], payloads: List[dict]):
        """批量插入向量和元数据"""
        
    def search(self, query_vector: List[float], top_k: int = 5) -> List[dict]:
        """向量检索"""
        
    def delete_collection(self):
        """删除集合"""
        
    def get_collection_info(self) -> dict:
        """获取集合信息"""
```

**使用示例**：
```python
store = VectorStore("my_docs")

# 插入向量
store.insert_vectors(
    vectors=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
    payloads=[
        {"text": "文档1", "source": "doc1.md"},
        {"text": "文档2", "source": "doc2.md"}
    ]
)

# 检索
results = store.search(query_vector=[0.15, 0.25, ...], top_k=5)
```

---

### 3. retrieval/document_loader.py - 文档加载器

**DocumentLoader 类**

**职责**：读取不同格式的文档，返回文本内容

**需要实现的方法**：
```python
class DocumentLoader:
    def load_txt(self, file_path: str) -> str:
        """加载 txt 文件"""
        
    def load_markdown(self, file_path: str) -> str:
        """加载 markdown 文件"""
        
    def load_pdf(self, file_path: str) -> str:
        """加载 pdf 文件"""
        
    def load_docx(self, file_path: str) -> str:
        """加载 docx 文件"""
        
    def load_directory(self, dir_path: str) -> List[dict]:
        """加载目录下所有文档
        返回: [{"path": "...", "content": "...", "type": "md"}, ...]
        """
```

---

### 4. retrieval/chunker.py - 文档切片器

**Chunker 类**

**职责**：将长文档切分成小块

**需要实现的方法**：
```python
class Chunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """初始化切片参数"""
        
    def chunk_text(self, text: str, metadata: dict = None) -> List[dict]:
        """切片文本
        返回: [
            {"text": "片段1", "chunk_id": 0, "source": "doc.md", ...},
            {"text": "片段2", "chunk_id": 1, "source": "doc.md", ...},
        ]
        """
        
    def chunk_documents(self, documents: List[dict]) -> List[dict]:
        """批量切片文档"""
```

---

### 5. retrieval/retriever.py - 检索器

**Retriever 类**

**职责**：协调 Embedder 和 VectorStore，提供完整检索流程

**需要实现的方法**：
```python
class Retriever:
    def __init__(self, embedder: Embedder, vector_store: VectorStore):
        """初始化检索器"""
        
    def index_documents(self, documents: List[dict]):
        """索引文档（切片 + 向量化 + 存储）"""
        
    def retrieve(self, query: str, top_k: int = 5) -> List[dict]:
        """检索相关文档
        返回: [
            {"text": "文档片段", "source": "doc.md", "score": 0.85},
            ...
        ]
        """
```

---

### 6. citation/citation_handler.py - 引用处理器

**CitationHandler 类**

**职责**：在回答中插入引用标记

**需要实现的方法**：
```python
class CitationHandler:
    def format_answer_with_citations(
        self, 
        answer: str, 
        sources: List[dict]
    ) -> str:
        """格式化带引用的回答"""
        
    def format_citation_list(self, sources: List[dict]) -> str:
        """格式化引用列表"""
```

**输出示例**：
```
回答: 根据文档，配置步骤如下：
1. 在 config.yaml 中设置参数
2. 运行初始化脚本

引用来源:
[1] docs/config.md (片段 5, 相似度 0.85)
[2] docs/setup.md (片段 2, 相似度 0.82)
```

---

### 7. tools/rag_tool.py - RAG 检索工具

**RAGTool 类**

**职责**：作为 Agent 的工具，提供检索能力

**需要实现的方法**：
```python
class RAGTool:
    name = "retrieve_knowledge"
    description = "从知识库检索相关信息"
    
    def execute(self, query: str, top_k: int = 5) -> dict:
        """执行检索
        返回: {
            "results": [...],
            "has_results": True/False
        }
        """
```

---

### 8. scripts/import_docs.py - 文档导入脚本

**职责**：批量导入文档到向量库

**使用方式**：
```bash
# 导入单个文件
python scripts/import_docs.py --file docs/readme.md

# 导入目录
python scripts/import_docs.py --dir docs/

# 清空并重建索引
python scripts/import_docs.py --dir docs/ --rebuild
```

---

## Qdrant 使用详解

### 安装

```bash
pip install qdrant-client
```

### 基础用法

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# ========== 1. 连接数据库 ==========

# 方式一：嵌入式模式（推荐入门）
client = QdrantClient(path="./qdrant_data")

# 方式二：Docker 本地服务
# client = QdrantClient(host="localhost", port=6333)

# 方式三：Qdrant Cloud
# client = QdrantClient(url="https://xxx.qdrant.io", api_key="xxx")


# ========== 2. 创建集合 ==========

client.create_collection(
    collection_name="my_documents",
    vectors_config=VectorParams(
        size=1024,  # bge-large-zh 的维度
        distance=Distance.COSINE  # 余弦相似度
    )
)


# ========== 3. 插入向量 ==========

points = [
    PointStruct(
        id=1,
        vector=[0.1, 0.2, 0.3, ...],  # 1024 维向量
        payload={
            "text": "文档内容...",
            "source": "doc.md",
            "chunk_id": 0
        }
    ),
    PointStruct(
        id=2,
        vector=[0.4, 0.5, 0.6, ...],
        payload={
            "text": "另一段文档...",
            "source": "doc.md",
            "chunk_id": 1
        }
    )
]

client.upsert(
    collection_name="my_documents",
    points=points
)


# ========== 4. 检索向量 ==========

results = client.search(
    collection_name="my_documents",
    query_vector=[0.15, 0.25, 0.35, ...],  # 问题向量
    limit=5,  # Top-K
    with_payload=True  # 返回元数据
)

for result in results:
    print(f"分数: {result.score}")
    print(f"文本: {result.payload['text']}")
    print(f"来源: {result.payload['source']}")
    print("---")


# ========== 5. 其他常用操作 ==========

# 获取集合信息
info = client.get_collection("my_documents")
print(f"向量数量: {info.points_count}")

# 删除集合
client.delete_collection("my_documents")

# 按条件过滤
from qdrant_client.models import Filter, FieldCondition, MatchValue

results = client.search(
    collection_name="my_documents",
    query_vector=[...],
    query_filter=Filter(
        must=[
            FieldCondition(
                key="source",
                match=MatchValue(value="config.md")
            )
        ]
    ),
    limit=5
)
```

---

## Embedding 模型使用详解

### 安装

```bash
pip install sentence-transformers
```

### 基础用法

```python
from sentence_transformers import SentenceTransformer

# ========== 1. 加载模型 ==========

model = SentenceTransformer("BAAI/bge-large-zh")
# 首次运行会自动下载到 ~/.cache/huggingface/hub/


# ========== 2. 向量化文本 ==========

# 单个文本
text = "如何配置数据库？"
vector = model.encode(text)
# vector.shape = (1024,)

# 多个文本
texts = ["如何配置数据库？", "Python 最佳实践", "机器学习入门"]
vectors = model.encode(texts)
# vectors.shape = (3, 1024)


# ========== 3. 计算相似度 ==========

from sklearn.metrics.pairwise import cosine_similarity

vec1 = model.encode("如何配置数据库？")
vec2 = model.encode("数据库连接设置方法")

similarity = cosine_similarity([vec1], [vec2])[0][0]
print(f"相似度: {similarity}")  # 约 0.85


# ========== 4. 其他可用模型 ==========

# 中文模型
model = SentenceTransformer("BAAI/bge-base-zh")     # 更快
model = SentenceTransformer("BAAI/bge-small-zh")    # 最快

# 多语言模型
model = SentenceTransformer("BAAI/bge-m3")          # 多语言最强


# ========== 5. 高级用法 ==========

# 批量处理（提高效率）
texts = ["文本1", "文本2", ...] * 100
vectors = model.encode(
    texts,
    batch_size=32,        # 批大小
    show_progress_bar=True,  # 显示进度
    normalize_embeddings=True  # 归一化向量
)

# 指定设备
model = SentenceTransformer("BAAI/bge-large-zh", device="cuda")  # GPU
model = SentenceTransformer("BAAI/bge-large-zh", device="cpu")   # CPU
```

---

## 验收标准

### 功能验收

- [ ] 能导入 txt、md 格式的文档
- [ ] 能正确切片文档
- [ ] 能生成向量并存入 Qdrant
- [ ] 能根据问题检索相关文档

### 检索验收

- [ ] 至少 10 个测试问题中 7 个能命中正确文档
- [ ] 检索速度 < 500ms
- [ ] 返回结果包含相似度分数

### 引用验收

- [ ] 回答能标注引用来源
- [ ] 引用格式清晰易读
- [ ] 能追溯到原文档片段

### 降级验收

- [ ] 检索不到时能给出友好提示
- [ ] 不会因检索失败而崩溃

### 代码质量

- [ ] 代码结构清晰，职责分离
- [ ] 有适当的注释和文档
- [ ] 变量命名规范

---

## 实现顺序建议

### Phase 1: 基础设施

1. **环境准备**
   - 安装依赖
   - 测试 bge-large-zh 模型下载
   - 测试 Qdrant 连接

2. **Embedding 封装**
   - retrieval/embedder.py

3. **向量库封装**
   - retrieval/vector_store.py

### Phase 2: 文档处理

4. **文档加载**
   - retrieval/document_loader.py

5. **文档切片**
   - retrieval/chunker.py

6. **导入脚本**
   - scripts/import_docs.py

### Phase 3: 检索功能

7. **检索器**
   - retrieval/retriever.py

8. **引用处理**
   - citation/citation_handler.py

### Phase 4: Agent 集成

9. **RAG 工具**
   - tools/rag_tool.py

10. **Agent 集成**
    - agent/agent.py（复用第四周，添加 RAG 能力）

### Phase 5: CLI 和测试

11. **CLI 主程序**
    - main.py

12. **测试验收**
    - 准备知识库（20-50 篇文档）
    - 设计测试问题（10+ 个）
    - 验证检索准确率

---

## 使用示例

```bash
# ========== 1. 导入文档 ==========

# 导入单个文件
python scripts/import_docs.py --file data/knowledge_base/python_basics.md

# 导入整个目录
python scripts/import_docs.py --dir data/knowledge_base/

# 清空并重建索引
python scripts/import_docs.py --dir data/knowledge_base/ --rebuild


# ========== 2. 启动 Agent ==========

python main.py

# ========== 3. 问答交互 ==========

> Python 如何定义函数？
Agent: 根据知识库，Python 定义函数的语法如下：
```python
def function_name(parameters):
    """函数文档字符串"""
    # 函数体
    return result
```

引用来源:
[1] python_basics.md#L23-45 (相似度: 0.88)

> 如何连接数据库？
Agent: 数据库连接需要以下步骤：
1. 安装数据库驱动
2. 配置连接参数
3. 创建连接对象

引用来源:
[1] database_config.md#L10-30 (相似度: 0.85)
[2] database_config.md#L35-50 (相似度: 0.82)

> 什么是机器学习？
Agent: 抱歉，知识库中没有找到关于机器学习的相关信息。
建议您可以查阅其他资料或换个问题。

# ========== 4. 查看统计信息 ==========

> stats
[知识库统计]
文档数量: 35
向量数量: 520
存储大小: 12.5 MB
最后更新: 2024-01-15 10:30:00

# ========== 5. 退出 ==========

> exit
Bye!
```

---

## 注意事项

1. **环境变量**：需要在 `.env` 文件中配置 LLM 相关配置
   ```
   LLM_MODEL_ID=your_model
   LLM_API_KEY=your_api_key
   LLM_BASE_URL=your_base_url
   ```

2. **模型下载**：首次使用 bge-large-zh 会下载约 1.3GB 模型文件
   - 下载位置：`~/.cache/huggingface/hub/`
   - 确保网络畅通

3. **数据目录**：
   - `data/knowledge_base/` 存放知识库文档
   - `data/qdrant_data/` 存储 Qdrant 向量数据

4. **切片参数**：
   - `chunk_size`: 建议值 300-800 字符
   - `chunk_overlap`: 建议值 50-100 字符
   - 根据实际效果调整

5. **检索参数**：
   - `top_k`: 建议 3-10
   - 太少可能漏掉相关信息
   - 太多可能引入噪音

---

## 学习重点

通过本项目，你将掌握：

1. ✅ Chunking 的概念和实现
2. ✅ Embedding 向量化的原理和使用
3. ✅ 向量数据库 Qdrant 的基本操作
4. ✅ 向量检索的完整流程
5. ✅ 引用溯源的实现方法
6. ✅ RAG（检索增强生成）的核心思想

---

## 常见问题

### Q1: 模型下载很慢怎么办？

可以手动下载模型到本地，然后指定路径：

```python
# 方式一：使用镜像站
export HF_ENDPOINT=https://hf-mirror.com
model = SentenceTransformer("BAAI/bge-large-zh")

# 方式二：使用本地路径
model = SentenceTransformer("/path/to/local/model")
```

### Q2: Qdrant 数据存储在哪里？

嵌入式模式下，数据存储在指定的 `path` 目录：

```python
client = QdrantClient(path="./qdrant_data")
# 数据存储在 ./qdrant_data/ 目录下
```

### Q3: 如何查看已存储的向量？

```python
# 获取集合信息
info = client.get_collection("my_documents")
print(f"向量数量: {info.points_count}")

# 遍历所有向量
from qdrant_client.models import ScrollResult

results, _ = client.scroll(
    collection_name="my_documents",
    limit=100,
    with_payload=True,
    with_vectors=True
)

for point in results:
    print(f"ID: {point.id}")
    print(f"向量: {point.vector[:5]}...")  # 只显示前5维
    print(f"元数据: {point.payload}")
```

### Q4: 如何提高检索准确率？

1. **调整切片大小**：根据文档特点调整 chunk_size
2. **增加重叠**：提高 chunk_overlap 保持语义连续性
3. **优化召回数量**：增加 top_k 再人工筛选
4. **添加 Rerank**：对召回结果进行重排序（后续学习）

### Q5: 如何处理大文件？

对于大文件，建议：

```python
# 分批处理
batch_size = 100
for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i+batch_size]
    vectors = embedder.encode([c['text'] for c in batch])
    vector_store.insert_vectors(vectors, batch)
```

---

## 下一周预告

第六周将在本周基础上，增加：
- 记忆与 RAG 融合
- 双检索编排
- 上下文融合策略
- 来源区分标记
