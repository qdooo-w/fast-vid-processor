# 数据库集成指南

本指南详细介绍如何将数据库模块集成到音频处理系统中，包括数据库结构、API 使用、集成模式和最佳实践。

## 数据库概述

数据库模块是一个基于 SQLite 的轻量级数据管理系统，专为音频处理系统设计，主要用于：

- **文件管理**：存储和管理音频文件信息，防止重复处理
- **任务管理**：跟踪和管理处理任务，确保任务正确执行
- **状态跟踪**：详细记录任务的执行状态和结果
- **数据统计**：提供系统运行的统计信息

## 目录结构

```
database/
├── database.py        # 数据库核心模块
└── INTEGRATION_GUIDE.md  # 本文档
```

## 快速集成

### 1. 导入数据库模块

```python
from database import db
```

### 2. 基本使用示例

```python
# 1. 处理音频文件前检查
file_hash = calculate_file_hash(audio_path)
if db.check_file_exists(file_hash):
    print("文件已处理过，跳过")
    return

# 2. 保存文件信息
db.save_file_info(file_hash, original_name, storage_path)

# 3. 创建任务
task_id = generate_task_id()
db.create_task(task_id, file_hash, "transcribe")

# 4. 更新任务状态
db.update_task_status(task_id, "running")

# 5. 任务完成
try:
    # 处理逻辑...
    db.update_task_status(task_id, "success", result_path)
except Exception as e:
    db.update_task_status(task_id, "failed", error_message=str(e))
```

## 数据库结构

### 1. files 表

| 字段名 | 数据类型 | 约束 | 描述 |
|--------|----------|------|------|
| `file_hash` | TEXT | PRIMARY KEY | 文件的唯一标识符 |
| `original_name` | TEXT | | 文件的原始名称 |
| `storage_path` | TEXT | | 文件的存储路径 |
| `upload_time` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 文件上传时间 |
| `upload_count` | INTEGER | DEFAULT 1 | 文件上传次数 |

### 2. tasks 表

| 字段名 | 数据类型 | 约束 | 描述 |
|--------|----------|------|------|
| `task_id` | TEXT | PRIMARY KEY | 任务的唯一标识符 |
| `file_hash` | TEXT | NOT NULL | 关联的文件哈希值 |
| `task_type` | TEXT | NOT NULL | 任务类型 |
| `status` | TEXT | DEFAULT 'pending' | 任务状态 |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 任务创建时间 |
| `started_at` | TIMESTAMP | | 任务开始时间 |
| `completed_at` | TIMESTAMP | | 任务完成时间 |
| `result_path` | TEXT | | 结果文件路径 |
| `error_message` | TEXT | | 错误信息 |
| `UNIQUE` | | (file_hash, task_type) | 防止重复任务 |

### 3. 索引

| 索引名 | 表 | 字段 | 目的 |
|--------|------|------|------|
| `idx_tasks_file` | tasks | file_hash | 加速按文件查询任务 |
| `idx_tasks_type` | tasks | task_type | 加速按类型查询任务 |
| `idx_tasks_status` | tasks | status | 加速按状态查询任务 |

## API 参考

### 1. 文件操作

#### `check_file_exists(file_hash: str) -> bool`
检查文件是否已存在于数据库中。

**参数**：
- `file_hash`：文件的哈希值

**返回值**：
- `bool`：文件是否存在

**使用场景**：处理音频前检查文件是否已处理过

#### `save_file_info(file_hash: str, original_name: str = None, storage_path: str = None) -> bool`
保存文件信息到数据库。

**参数**：
- `file_hash`：文件的哈希值
- `original_name`：文件的原始名称
- `storage_path`：文件的存储路径

**返回值**：
- `bool`：保存是否成功（文件不存在时返回 True）

**使用场景**：处理新文件时保存文件信息

#### `get_file_info(file_hash: str) -> Optional[Dict[str, Any]]`
获取文件信息。

**参数**：
- `file_hash`：文件的哈希值

**返回值**：
- `Dict`：文件信息字典
- `None`：文件不存在

**使用场景**：需要获取文件详细信息时

#### `increment_upload_count(file_hash: str)`
增加文件的上传次数。

**参数**：
- `file_hash`：文件的哈希值

**使用场景**：文件被重复上传时统计

### 2. 任务操作

#### `create_task(task_id: str, file_hash: str, task_type: str = "transcribe") -> bool`
创建新任务。

**参数**：
- `task_id`：任务的唯一标识符
- `file_hash`：关联的文件哈希值
- `task_type`：任务类型（默认：transcribe）

**返回值**：
- `bool`：创建是否成功（任务不存在时返回 True）

**使用场景**：开始新的处理任务前

#### `get_task(task_id: str) -> Optional[Dict[str, Any]]`
获取任务信息。

**参数**：
- `task_id`：任务的唯一标识符

**返回值**：
- `Dict`：任务信息字典
- `None`：任务不存在

**使用场景**：需要获取任务详细信息时

#### `find_task(file_hash: str, task_type: str) -> Optional[Dict[str, Any]]`
根据文件哈希和任务类型查找任务。

**参数**：
- `file_hash`：文件的哈希值
- `task_type`：任务类型

**返回值**：
- `Dict`：任务信息字典
- `None`：任务不存在

**使用场景**：检查特定文件的特定任务是否存在

#### `update_task_status(task_id: str, status: str, result_path: str = None, error_message: str = None)`
更新任务状态。

**参数**：
- `task_id`：任务的唯一标识符
- `status`：新状态（pending, running, success, failed）
- `result_path`：结果文件路径（成功时使用）
- `error_message`：错误信息（失败时使用）

**使用场景**：更新任务执行状态

#### `get_file_tasks(file_hash: str) -> List[Dict[str, Any]]`
获取文件的所有任务。

**参数**：
- `file_hash`：文件的哈希值

**返回值**：
- `List[Dict]`：任务信息列表

**使用场景**：查看文件的所有处理历史

### 3. 统计和工具方法

#### `get_stats() -> Dict[str, Any]`
获取数据库统计信息。

**返回值**：
- `Dict`：包含文件数量和任务统计的字典

**使用场景**：系统监控和报告

#### `cleanup_old_data(days: int = 30)`
清理指定天数前的失败任务。

**参数**：
- `days`：天数，默认 30

**使用场景**：定期清理旧的失败任务，优化数据库大小

## 任务类型

| 任务类型 | 描述 | 适用模块 |
|----------|------|----------|
| `extract_audio` | 从视频中提取音频 | 视频处理模块 |
| `transcribe` | 音频转录为文本 | 转录模块 |
| `ai_summarize` | AI 生成文本总结 | AI 总结模块 |
| `extract_keyframes` | 提取视频关键帧 | 视频处理模块 |

## 任务状态

| 状态 | 描述 | 转换路径 |
|------|------|----------|
| `pending` | 任务已创建但未开始 | 初始状态 |
| `running` | 任务正在执行中 | pending → running |
| `success` | 任务执行成功 | running → success |
| `failed` | 任务执行失败 | running → failed |

## 集成模式

### 1. 基本集成模式

```python
from database import db
import hashlib
import uuid

def process_audio(audio_path):
    """处理音频文件的完整流程"""
    # 1. 计算文件哈希
    file_hash = calculate_file_hash(audio_path)
    original_name = get_original_name(audio_path)
    storage_path = audio_path
    
    # 2. 检查文件是否已处理
    if db.check_file_exists(file_hash):
        print(f"文件 {original_name} 已处理过，跳过")
        return None
    
    # 3. 保存文件信息
    db.save_file_info(file_hash, original_name, storage_path)
    
    # 4. 创建转录任务
    transcribe_task_id = f"transcribe_{uuid.uuid4().hex[:8]}"
    db.create_task(transcribe_task_id, file_hash, "transcribe")
    
    # 5. 执行转录
    db.update_task_status(transcribe_task_id, "running")
    
    try:
        # 转录逻辑...
        transcript_path = do_transcribe(audio_path)
        
        # 6. 标记转录成功
        db.update_task_status(transcribe_task_id, "success", transcript_path)
        
        # 7. 创建 AI 总结任务
        summarize_task_id = f"summarize_{uuid.uuid4().hex[:8]}"
        db.create_task(summarize_task_id, file_hash, "ai_summarize")
        
        # 8. 执行 AI 总结
        db.update_task_status(summarize_task_id, "running")
        
        # AI 总结逻辑...
        summary_path = do_ai_summary(transcript_path)
        
        # 9. 标记总结成功
        db.update_task_status(summarize_task_id, "success", summary_path)
        
        return {
            "transcript_path": transcript_path,
            "summary_path": summary_path
        }
        
    except Exception as e:
        # 10. 标记任务失败
        db.update_task_status(transcribe_task_id, "failed", error_message=str(e))
        print(f"处理失败: {e}")
        return None

def calculate_file_hash(file_path):
    """计算文件的 MD5 哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_original_name(file_path):
    """获取文件的原始名称"""
    return os.path.basename(file_path)
```



### 2. 状态查询模式

```python
def check_task_status(task_id):
    """检查任务执行状态"""
    task = db.get_task(task_id)
    if not task:
        return "任务不存在"
    
    status = task['status']
    if status == 'success':
        return f"任务成功完成，结果路径: {task['result_path']}"
    elif status == 'failed':
        return f"任务失败，错误: {task['error_message']}"
    elif status == 'running':
        return "任务正在执行中"
    else:
        return "任务等待执行"

def get_file_process_history(file_hash):
    """获取文件的处理历史"""
    tasks = db.get_file_tasks(file_hash)
    if not tasks:
        return "文件未处理过"
    
    history = []
    for task in tasks:
        history.append(f"{task['task_type']}: {task['status']}")
    
    return "\n".join(history)
```

## 最佳实践

### 1. 文件哈希计算

**推荐方法**：使用文件内容的 MD5 哈希值

```python
import hashlib

def calculate_file_hash(file_path):
    """计算文件的 MD5 哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
```

### 2. 任务 ID 生成

**推荐方法**：使用 UUID 生成唯一的任务 ID

```python
import uuid

def generate_task_id(task_type):
    """生成唯一的任务 ID"""
    return f"{task_type}_{uuid.uuid4().hex[:8]}"
```

### 3. 错误处理

**推荐方法**：使用 try-except 块捕获异常，并更新任务状态

```python
try:
    # 任务执行逻辑
    db.update_task_status(task_id, "success", result_path)
except Exception as e:
    db.update_task_status(task_id, "failed", error_message=str(e))
    print(f"任务失败: {e}")
```

### 4. 事务处理

**推荐方法**：对于批量操作，使用事务确保数据一致性

```python
def batch_save_files(file_infos):
    """批量保存文件信息"""
    from database import FileDB
    
    db_instance = FileDB()
    conn = db_instance._get_conn()
    
    try:
        conn.execute('BEGIN TRANSACTION')
        
        for file_info in file_infos:
            file_hash = file_info['file_hash']
            original_name = file_info['original_name']
            storage_path = file_info['storage_path']
            
            conn.execute(
                "INSERT OR IGNORE INTO files (file_hash, original_name, storage_path) VALUES (?, ?, ?)",
                (file_hash, original_name, storage_path)
            )
        
        conn.execute('COMMIT')
        return True
    except Exception as e:
        conn.execute('ROLLBACK')
        print(f"批量保存失败: {e}")
        return False
    finally:
        conn.close()
```

### 5. 定期维护

**推荐方法**：定期清理旧的失败任务

```python
def scheduled_maintenance():
    """定期维护任务"""
    from database import db
    
    # 清理 30 天前的失败任务
    db.cleanup_old_data(days=30)
    
    # 获取统计信息
    stats = db.get_stats()
    print(f"维护完成！\n文件总数: {stats['files']}\n任务统计: {stats['tasks']}")
```

## 性能优化

### 1. 索引使用

数据库已经为以下字段创建了索引：
- `tasks.file_hash`：加速按文件查询任务
- `tasks.task_type`：加速按类型查询任务
- `tasks.status`：加速按状态查询任务

### 2. 批量操作

对于大量数据操作，建议使用批量处理以提高性能：

- **批量插入**：使用事务批量插入多条记录
- **批量查询**：使用 IN 子句一次性查询多条记录
- **批量更新**：使用 CASE 语句批量更新记录

### 3. 缓存策略

对于频繁访问的数据，可以使用内存缓存：

```python
class TaskCache:
    """任务缓存类"""
    def __init__(self):
        self.cache = {}
        self.expiry = {}
    
    def get_task(self, task_id):
        """获取缓存的任务信息"""
        if task_id in self.cache:
            # 检查是否过期（5分钟）
            if time.time() - self.expiry.get(task_id, 0) < 300:
                return self.cache[task_id]
            else:
                del self.cache[task_id]
                del self.expiry[task_id]
        
        # 从数据库获取
        task = db.get_task(task_id)
        if task:
            self.cache[task_id] = task
            self.expiry[task_id] = time.time()
        
        return task

# 使用缓存
task_cache = TaskCache()
task = task_cache.get_task(task_id)
```

## 故障排除

### 1. 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `UNIQUE constraint failed` | 重复任务 | 使用 `find_task` 检查任务是否存在 |
| `Database is locked` | 并发访问 | 确保连接正确关闭，使用短事务 |
| `No such table` | 数据库未初始化 | 确保正确导入数据库模块，会自动初始化 |
| `OperationError` | 文件权限 | 确保数据库文件有写入权限 |

### 2. 诊断命令

```python
# 检查数据库连接
from database import db
print("数据库连接成功")

# 检查数据库结构
import sqlite3
conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# 检查 tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# 检查 files 表
cursor.execute("PRAGMA table_info(files);")
print("Files table columns:", cursor.fetchall())

# 检查 tasks 表
cursor.execute("PRAGMA table_info(tasks);")
print("Tasks table columns:", cursor.fetchall())

conn.close()
```

### 3. 数据恢复

如果数据库文件损坏，可以：

1. **删除损坏的数据库文件**：`app.db`
2. **重启应用**：系统会自动创建新的数据库文件
3. **重新导入数据**：如果有备份，可以重新导入

## 扩展功能

### 1. 添加新的任务类型

1. **定义任务类型常量**：

```python
# 在 constants.py 中
TASK_TYPES = {
    'EXTRACT_AUDIO': 'extract_audio',
    'TRANSCRIBE': 'transcribe',
    'AI_SUMMARIZE': 'ai_summarize',
    'EXTRACT_KEYFRAMES': 'extract_keyframes',
    'NEW_TASK_TYPE': 'new_task_type'  # 新任务类型
}
```

2. **在相关模块中使用**：

```python
from constants import TASK_TYPES

db.create_task(task_id, file_hash, TASK_TYPES['NEW_TASK_TYPE'])
```

### 2. 扩展数据库表

如果需要添加新的字段或表：

1. **修改 `database.py` 中的 `_init_db` 方法**：

```python
def _init_db(self):
    """创建数据库表（如果不存在）"""
    with self._get_conn() as conn:
        # 现有表结构...
        
        # 添加新表或字段
        conn.execute('''
            CREATE TABLE IF NOT EXISTS new_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value TEXT
            )
        ''')
        
        conn.commit()
```

2. **添加相应的 API 方法**：

```python
def add_new_record(self, name, value):
    """添加新记录"""
    with self._get_conn() as conn:
        conn.execute(
            "INSERT INTO new_table (name, value) VALUES (?, ?)",
            (name, value)
        )
        conn.commit()
```

## 版本兼容性

### 与旧版本数据库的兼容性

| 功能 | 旧版本 | 新版本 | 兼容性 |
|------|--------|--------|--------|
| 文件管理 | 基本支持 | 增强支持 | 向后兼容 |
| 任务管理 | 基本支持 | 增强支持 | 向后兼容 |
| 任务去重 | 不支持 | 支持 | 新功能 |
| 详细状态 | 不支持 | 支持 | 新功能 |
| API 方法 | 部分支持 | 完整支持 | 向后兼容 |

### 迁移注意事项

1. **自动初始化**：新版本会自动创建所需的表和字段
2. **数据保留**：旧的数据会被保留，新字段会使用默认值
3. **API 兼容**：旧的 API 方法仍然可用，新方法提供更多功能

## 监控与日志

### 日志输出

数据库模块会生成详细的操作日志：

```
2026-02-09 18:51:07,723 - INFO - 数据库初始化完成: app.db
2026-02-09 18:51:07,922 - INFO - 文件保存成功: abc123def456
2026-02-09 18:51:07,976 - INFO - 任务创建成功: task-001 (extract_audio)
2026-02-09 18:51:08,024 - INFO - 任务开始: task-001
2026-02-09 18:51:08,027 - INFO - 任务成功完成: task-001
```

### 监控指标

| 指标 | 描述 | 监控频率 |
|------|------|----------|
| 文件总数 | 数据库中的文件数量 | 每日 |
| 任务总数 | 数据库中的任务数量 | 每日 |
| 失败任务数 | 失败的任务数量 | 每日 |
| 数据库大小 | 数据库文件的大小 | 每周 |

## 总结

数据库模块是音频处理系统的重要组成部分，提供了可靠的数据管理功能，确保系统高效运行。通过本指南，您应该能够：

1. **快速集成**：将数据库模块集成到您的代码中
2. **正确使用**：使用数据库 API 管理文件和任务
3. **优化性能**：应用最佳实践提高系统性能
4. **扩展功能**：根据需要扩展数据库功能

如果您在集成过程中遇到任何问题，请参考本文档的相关部分，或联系系统管理员获取帮助。

---

**✨ 数据库集成指南 v1.0**
