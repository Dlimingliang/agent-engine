# Python 基础教程

## 1. 变量和数据类型

Python 是一门动态类型语言，变量不需要声明类型。

### 1.1 基本数据类型

Python 支持以下基本数据类型：

- **整数（int）**：如 `42`、`-100`
- **浮点数（float）**：如 `3.14`、`-0.001`
- **字符串（str）**：如 `'Hello'`、`"World"`
- **布尔值（bool）**：`True` 或 `False`
- **空值（None）**：表示没有值

### 1.2 变量赋值

```python
# 变量赋值示例
name = "Python"
age = 33
pi = 3.14159
is_awesome = True
```

## 2. 条件语句

Python 使用 `if`、`elif`、`else` 进行条件判断。

### 2.1 if 语句

```python
age = 18

if age >= 18:
    print("成年人")
else:
    print("未成年人")
```

### 2.2 多条件判断

```python
score = 85

if score >= 90:
    print("优秀")
elif score >= 80:
    print("良好")
elif score >= 60:
    print("及格")
else:
    print("不及格")
```

## 3. 循环语句

Python 提供了 `for` 循环和 `while` 循环。

### 3.1 for 循环

```python
# 遍历列表
fruits = ["苹果", "香蕉", "橙子"]
for fruit in fruits:
    print(fruit)

# 使用 range
for i in range(5):
    print(i)  # 输出 0, 1, 2, 3, 4
```

### 3.2 while 循环

```python
count = 0
while count < 5:
    print(count)
    count += 1
```

## 4. 函数

函数是组织好的、可重复使用的代码块。

### 4.1 定义函数

```python
def greet(name):
    """问候函数"""
    return f"你好，{name}！"

# 调用函数
message = greet("Python")
print(message)  # 输出：你好，Python！
```

### 4.2 函数参数

Python 函数支持多种参数类型：

```python
# 默认参数
def greet(name, greeting="你好"):
    return f"{greeting}，{name}！"

# 关键字参数
greet(name="Python", greeting="欢迎")

# 可变参数
def sum_all(*numbers):
    return sum(numbers)

sum_all(1, 2, 3, 4, 5)  # 返回 15
```

### 4.3 返回值

函数可以返回多个值：

```python
def get_user_info():
    name = "张三"
    age = 25
    return name, age

user_name, user_age = get_user_info()
```

## 5. 列表

列表是 Python 中最常用的数据结构之一。

### 5.1 创建列表

```python
# 创建列表
numbers = [1, 2, 3, 4, 5]
fruits = ["苹果", "香蕉", "橙子"]
mixed = [1, "hello", 3.14, True]
```

### 5.2 列表操作

```python
# 访问元素
fruits = ["苹果", "香蕉", "橙子"]
print(fruits[0])  # 苹果
print(fruits[-1])  # 橙子

# 添加元素
fruits.append("葡萄")
fruits.insert(0, "西瓜")

# 删除元素
fruits.remove("香蕉")
del fruits[0]

# 切片
numbers = [0, 1, 2, 3, 4, 5]
print(numbers[1:4])  # [1, 2, 3]
print(numbers[::2])  # [0, 2, 4]
```

## 6. 字典

字典是键值对的集合。

### 6.1 创建字典

```python
# 创建字典
person = {
    "name": "张三",
    "age": 25,
    "city": "北京"
}
```

### 6.2 字典操作

```python
# 访问值
print(person["name"])  # 张三
print(person.get("age"))  # 25

# 添加/修改
person["email"] = "zhangsan@example.com"
person["age"] = 26

# 删除
del person["city"]

# 遍历
for key, value in person.items():
    print(f"{key}: {value}")
```

## 7. 异常处理

使用 `try`、`except` 处理异常。

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("不能除以零！")
except Exception as e:
    print(f"发生错误：{e}")
finally:
    print("无论如何都会执行")
```

## 8. 文件操作

### 8.1 读取文件

```python
# 方式一：读取全部内容
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()

# 方式二：逐行读取
with open("file.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())
```

### 8.2 写入文件

```python
# 覆盖写入
with open("file.txt", "w", encoding="utf-8") as f:
    f.write("Hello, Python!")

# 追加写入
with open("file.txt", "a", encoding="utf-8") as f:
    f.write("\n新的一行")
```

## 9. 类和对象

Python 是面向对象的编程语言。

### 9.1 定义类

```python
class Person:
    """人员类"""
    
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        return f"你好，我是{self.name}，今年{self.age}岁"
    
    def __str__(self):
        return f"Person(name={self.name}, age={self.age})"


# 创建对象
person = Person("张三", 25)
print(person.greet())  # 你好，我是张三，今年25岁
```

### 9.2 继承

```python
class Student(Person):
    """学生类，继承自 Person"""
    
    def __init__(self, name, age, grade):
        super().__init__(name, age)
        self.grade = grade
    
    def study(self, subject):
        return f"{self.name}正在学习{subject}"


student = Student("李四", 20, "大三")
print(student.greet())  # 继承自父类
print(student.study("Python"))  # 李四正在学习Python
```

## 10. 模块和包

### 10.1 导入模块

```python
# 导入整个模块
import math
print(math.pi)  # 3.14159...

# 导入特定函数
from math import sqrt, pi
print(sqrt(16))  # 4.0
print(pi)  # 3.14159...

# 使用别名
import numpy as np
```

### 10.2 自定义模块

创建 `mymodule.py`：

```python
# mymodule.py
def greet(name):
    return f"Hello, {name}!"

PI = 3.14159
```

使用自定义模块：

```python
from mymodule import greet, PI

print(greet("Python"))
print(PI)
```

## 总结

Python 是一门简洁、易学的编程语言，适合初学者入门。掌握以上基础知识后，你可以：

1. 编写简单的 Python 程序
2. 处理文件和数据
3. 创建自定义函数和类
4. 使用第三方库扩展功能

继续学习 Python 进阶内容，如装饰器、生成器、异步编程等，让你的代码更加强大！
