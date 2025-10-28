# Python 容器学习笔记

## 一、列表

## 1. 创建与访问

```python
nums = [1, 2, 3, 4, 5]
print(nums[0])      # 访问第一个元素
print(nums[-1])     # 访问最后一个元素
```

### 2. 增删改查

```python
# 增
nums.append(6)            # 追加元素
nums.insert(2, 10)        # 在索引 2 处插入元素
nums.extend([7, 8])       # 扩展列表

# 删
nums.remove(3)            # 删除指定值
del nums[0]               # 删除指定索引
nums.pop()                # 删除最后一个元素

# 改
nums[1] = 99              # 修改某个元素

# 查
print(nums.index(99))     # 查找元素索引
print(99 in nums)         # 判断元素是否存在
```

### 3. 切片（Slicing）

```python
print(nums[1:4])      # 从索引1到3
print(nums[::-1])     # 反转列表
```

### 4. 列表推导式（List Comprehension）

```python
squares = [x**2 for x in range(5)]
evens = [x for x in range(10) if x % 2 == 0]
```

### 5. 解包（Unpacking）

```python
a, b, c = [1, 2, 3]
first, *middle, last = [1, 2, 3, 4, 5]
```

------

## 二、字典（Dictionary）

### 1. 创建与访问

```python
person = {'name': 'Alice', 'age': 20}
print(person['name'])
print(person.get('age'))
```

### 2. 增删改查

```python
# 增
person['city'] = 'Shanghai'

# 删
del person['age']
person.pop('name')

# 改
person['city'] = 'Beijing'

# 查
print('city' in person)
print(person.keys())
print(person.values())
```

### 3. 字典推导式（Dict Comprehension）

```python
squares = {x: x**2 for x in range(5)}
```

### 4. 合并与解包

```python
a = {'x': 1, 'y': 2}
b = {'y': 3, 'z': 4}
merged = {**a, **b}    # 合并字典
```

------

## 三、元组（Tuple）

### 1. 创建与访问

```python
t = (1, 2, 3)
print(t[0])
```

### 2. 切片与嵌套

```python
print(t[:2])
nested = ((1, 2), (3, 4))
```

### 3. 解包

```python
a, b, c = (1, 2, 3)
x, *y = (10, 20, 30, 40)
```

### 4. 特点

- 元组是**不可变对象**（immutable）
- 可用于**字典键**或**集合元素**

------

## 四、小结

- **列表（List）**：可变序列，常用于存储可修改的数据集合。
- **字典（Dict）**：键值映射结构，支持高效查找。
- **元组（Tuple）**：不可变序列，适合存储固定结构的数据。