# 数据库配置指南

## 1. MySQL 数据库配置

### 1.1 安装 MySQL

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

#### macOS

```bash
brew install mysql
brew services start mysql
```

#### Windows

下载 MySQL 安装包并运行安装程序。

### 1.2 配置连接

#### Python 连接 MySQL

```python
import mysql.connector

# 创建连接
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="mydb"
)

# 创建游标
cursor = conn.cursor()

# 执行查询
cursor.execute("SELECT * FROM users")
results = cursor.fetchall()

# 关闭连接
cursor.close()
conn.close()
```

#### 使用 SQLAlchemy

```python
from sqlalchemy import create_engine

# 创建引擎
engine = create_engine("mysql+pymysql://user:password@localhost/mydb")

# 执行查询
with engine.connect() as conn:
    result = conn.execute("SELECT * FROM users")
    for row in result:
        print(row)
```

### 1.3 连接池配置

```python
from mysql.connector import pooling

# 创建连接池
pool = pooling.ConnectionPool(
    pool_name="mypool",
    pool_size=5,
    host="localhost",
    user="root",
    password="your_password",
    database="mydb"
)

# 获取连接
conn = pool.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
results = cursor.fetchall()
conn.close()  # 归还连接池
```

## 2. PostgreSQL 数据库配置

### 2.1 安装 PostgreSQL

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### macOS

```bash
brew install postgresql
brew services start postgresql
```

### 2.2 配置连接

#### Python 连接 PostgreSQL

```python
import psycopg2

# 创建连接
conn = psycopg2.connect(
    host="localhost",
    database="mydb",
    user="postgres",
    password="your_password"
)

# 创建游标
cursor = conn.cursor()

# 执行查询
cursor.execute("SELECT * FROM users")
results = cursor.fetchall()

# 关闭连接
cursor.close()
conn.close()
```

### 2.3 使用 SQLAlchemy

```python
from sqlalchemy import create_engine

# 创建引擎
engine = create_engine("postgresql://user:password@localhost/mydb")

# 执行查询
with engine.connect() as conn:
    result = conn.execute("SELECT * FROM users")
    for row in result:
        print(row)
```

## 3. Redis 配置

### 3.1 安装 Redis

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
```

#### macOS

```bash
brew install redis
brew services start redis
```

### 3.2 配置连接

#### Python 连接 Redis

```python
import redis

# 创建连接
r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    password='your_password'  # 如果设置了密码
)

# 设置值
r.set('key', 'value')

# 获取值
value = r.get('key')
print(value.decode())  # value

# 设置过期时间
r.setex('temp_key', 3600, 'temporary value')  # 1小时后过期

# 删除键
r.delete('key')
```

### 3.3 常用操作

```python
# 列表操作
r.lpush('mylist', 'item1', 'item2', 'item3')
items = r.lrange('mylist', 0, -1)

# 哈希操作
r.hset('user:1', mapping={'name': '张三', 'age': 25})
user = r.hgetall('user:1')

# 集合操作
r.sadd('myset', 'member1', 'member2', 'member3')
members = r.smembers('myset')

# 有序集合
r.zadd('leaderboard', {'player1': 100, 'player2': 200, 'player3': 150})
top_players = r.zrange('leaderboard', 0, -1, withscores=True, desc=True)
```

## 4. MongoDB 配置

### 4.1 安装 MongoDB

#### Ubuntu/Debian

```bash
# 添加 MongoDB 仓库
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# 安装
sudo apt update
sudo apt install -y mongodb-org

# 启动服务
sudo systemctl start mongod
sudo systemctl enable mongod
```

#### macOS

```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

### 4.2 配置连接

#### Python 连接 MongoDB

```python
from pymongo import MongoClient

# 创建连接
client = MongoClient('mongodb://localhost:27017/')

# 选择数据库
db = client['mydb']

# 选择集合
collection = db['users']

# 插入文档
user = {
    'name': '张三',
    'age': 25,
    'email': 'zhangsan@example.com'
}
result = collection.insert_one(user)
print(f"插入的文档ID: {result.inserted_id}")

# 查询文档
user = collection.find_one({'name': '张三'})
print(user)

# 查询多个文档
for user in collection.find({'age': {'$gt': 20}}):
    print(user)

# 更新文档
collection.update_one(
    {'name': '张三'},
    {'$set': {'age': 26}}
)

# 删除文档
collection.delete_one({'name': '张三'})
```

### 4.3 索引配置

```python
# 创建索引
collection.create_index([('name', 1)])  # 1 表示升序
collection.create_index([('age', -1)])  # -1 表示降序

# 创建复合索引
collection.create_index([('name', 1), ('age', -1)])

# 创建唯一索引
collection.create_index([('email', 1)], unique=True)
```

## 5. SQLite 配置

### 5.1 Python 内置 SQLite

Python 自带 SQLite 支持，无需额外安装。

```python
import sqlite3

# 创建连接（如果数据库不存在会自动创建）
conn = sqlite3.connect('mydb.db')

# 创建游标
cursor = conn.cursor()

# 创建表
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    email TEXT UNIQUE
)
''')

# 插入数据
cursor.execute('''
INSERT INTO users (name, age, email) VALUES (?, ?, ?)
''', ('张三', 25, 'zhangsan@example.com'))

# 提交事务
conn.commit()

# 查询数据
cursor.execute('SELECT * FROM users')
rows = cursor.fetchall()

for row in rows:
    print(row)

# 关闭连接
conn.close()
```

## 6. 数据库连接最佳实践

### 6.1 使用环境变量

```python
import os
from dotenv import load_dotenv

load_dotenv()

# 从环境变量读取配置
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

# 创建连接
import mysql.connector

conn = mysql.connector.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
```

### 6.2 使用连接池

```python
# MySQL 连接池
from mysql.connector import pooling

dbconfig = {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "mydb"
}

connection_pool = pooling.ConnectionPool(
    pool_name="mypool",
    pool_size=10,
    **dbconfig
)

# 使用连接
def get_connection():
    return connection_pool.get_connection()
```

### 6.3 异常处理

```python
import mysql.connector
from mysql.connector import Error

def execute_query(query, params=None):
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="mydb"
        )
        cursor = conn.cursor()
        
        cursor.execute(query, params or ())
        
        if query.strip().upper().startswith('SELECT'):
            return cursor.fetchall()
        else:
            conn.commit()
            return cursor.rowcount
            
    except Error as e:
        print(f"数据库错误: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
```

## 7. 性能优化建议

### 7.1 索引优化

- 为经常查询的字段创建索引
- 避免在索引列上使用函数
- 复合索引遵循最左前缀原则

### 7.2 查询优化

- 使用 EXPLAIN 分析查询计划
- 避免 SELECT *
- 使用 LIMIT 限制返回结果
- 合理使用 JOIN

### 7.3 连接优化

- 使用连接池减少连接开销
- 及时关闭不用的连接
- 设置合理的连接超时时间

## 8. 安全建议

1. **不要硬编码密码**：使用环境变量或配置文件
2. **使用参数化查询**：防止 SQL 注入
3. **最小权限原则**：数据库用户只授予必要的权限
4. **定期备份**：设置自动备份策略
5. **加密连接**：生产环境使用 SSL/TLS 加密

## 总结

正确配置数据库连接是应用程序稳定运行的基础。记住：

1. 选择合适的数据库系统
2. 使用连接池提高性能
3. 做好异常处理
4. 注意安全性
5. 定期优化和维护

掌握这些配置方法，你就可以在 Python 项目中轻松使用各种数据库了！
