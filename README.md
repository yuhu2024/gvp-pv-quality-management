# 君合盟药物警戒培训管理系统 - 使用说明

## 快速启动

### 1. 安装依赖
```bash
cd training_system
pip install -r requirements.txt
```

### 2. 配置数据库
编辑 `training_system/settings.py`，修改 DATABASES 配置：

**SQLite（默认，无需额外配置）：**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**PostgreSQL：**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'training_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. 初始化数据库
```bash
python manage.py migrate
```

### 4. 创建初始数据（部门、角色、管理员账号）
```bash
python scripts/init_data.py
```

### 5. 启动开发服务器
```bash
python manage.py runserver 0.0.0.0:8000
```

### 6. 访问系统
- 地址：http://localhost:8000
- 管理员账号：admin / admin123
- 培训管理员：trainer / trainer123

---

## 批量创建300个账号

### 方式一：脚本批量生成
```bash
cd training_system
python scripts/batch_create_users.py --count 300 --prefix trainee --department 技术部 --role 学员
```

参数说明：
- `--count`：创建数量（默认300）
- `--prefix`：用户名前缀（默认 trainee）
- `--department`：部门名称（需先创建部门）
- `--role`：角色（管理员/培训管理员/学员，默认学员）

生成的账号格式：
- 用户名：trainee001, trainee002, ... trainee300
- 默认密码：Abc@12345

### 方式二：Excel批量导入
1. 下载模板：`templates_import/user_import_template.xlsx`
2. 按照模板格式填写用户信息（工号、姓名、用户名、密码、部门、角色、手机号）
3. 通过管理后台"用户管理 → 批量导入"上传Excel文件
4. 或使用命令行：
```bash
python scripts/import_users_excel.py --file your_users.xlsx --skip-existing
```

---

## 功能模块

### 1. 用户管理
- 用户列表：查看所有用户，支持按部门/角色/关键词筛选
- 创建用户：单个创建用户
- 批量导入：Excel文件批量导入用户
- 个人资料：编辑个人信息

### 2. 课程管理
- 课程列表：查看所有课程，支持分类筛选和搜索
- 创建课程：创建新课程
- 上传资料：上传PPT、Word、PDF、视频等资料
- 在线预览：在线查看PPT、Word、PDF，在线播放视频
- 下载资料：下载课程资料（记录下载次数）

### 3. 在线考试
- 考试列表：查看所有考试
- 创建考试：创建考试并添加题目（单选/多选/判断/填空/简答）
- 参加考试：在线答题，自动倒计时，超时自动提交
- 自动评分：单选/多选/判断/填空自动评分，简答需手动评分
- 成绩管理：查看考试成绩和及格情况

### 4. 培训计划
- 计划列表：查看所有培训计划
- 创建计划：创建培训计划，关联课程和考试
- 分配任务：选择任务并批量分配给指定用户
- 我的任务：学员查看自己的待完成任务
- 完成任务：学员标记任务完成（自动记录完成时间）

### 5. 学习痕迹记录
- 学习记录：记录登录/登出、查看课程、下载资料、参加考试等行为
- 操作日志：记录管理员的创建/更新/删除/导入/分配等操作
- 用户统计：查看指定用户的培训完成情况汇总
- 导出记录：导出学习记录为Excel文件

---

## 项目结构

```
training_system/
├── manage.py                    # Django管理入口
├── requirements.txt             # 依赖包
├── training_system/             # 项目配置
│   ├── settings.py              # 核心配置
│   ├── urls.py                  # 主路由
│   └── wsgi.py / asgi.py
├── apps/
│   ├── users/                   # 用户与账号管理
│   ├── courses/                 # 课程资料管理
│   ├── exams/                   # 在线考试
│   ├── plans/                   # 培训计划与任务分配
│   └── logs/                    # 学习痕迹记录
├── templates/                   # 前端模板（30+个HTML文件）
├── static/                      # 静态资源（CSS/JS）
├── media/                       # 上传文件存储
├── scripts/                     # 工具脚本
│   ├── batch_create_users.py    # 批量创建用户
│   └── import_users_excel.py    # Excel导入用户
└── templates_import/            # Excel导入模板
```

---

## 技术栈
- 后端：Python 3.10 + Django 4.2
- 数据库：SQLite（默认）/ PostgreSQL
- 前端：Bootstrap 5 + Bootstrap Icons
- 文件处理：openpyxl（Excel）、Pillow（图片）
