# 设计规格 (Design Specification)

**文档编号：** VAL-DS-001  
**版本：** 2.0  
**生效日期：** 2026-07-24  

---

## 1. 目的

本文档描述 君合盟药物警戒君合盟药物警戒培训管理系统 (PV Training Management System) 的技术架构、数据模型设计、接口设计和安全设计，为系统开发和验证提供详细的技术蓝图。

## 2. 系统架构

### 2.1 三层架构

```
┌─────────────────────────────────────────────────────────────┐
│  表示层 (Presentation Layer)                                 │
│  - HTML5 Templates (Bootstrap 5)                            │
│  - JavaScript (Vanilla JS)                                  │
│  - Canvas 手写签名板                                        │
├─────────────────────────────────────────────────────────────┤
│  业务逻辑层 (Business Logic Layer)                           │
│  - Django Views / URL Routing                               │
│  - Django Forms                                             │
│  - Custom Business Rules (RBAC, Anti-cheat, Scoring)        │
├─────────────────────────────────────────────────────────────┤
│  数据访问层 (Data Access Layer)                              │
│  - Django ORM                                               │
│  - PostgreSQL (Primary DB)                                  │
│  - Redis (Cache / Session, Optional)                        │
│  - File System (Media Uploads)                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 部署架构

```
[User Browser]
      │ HTTPS
      ▼
[Nginx 1.25] ──→ Static Files (CSS/JS/Images)
      │
      │ Proxy Pass (Unix Socket)
      ▼
[Gunicorn 4 Workers] ──→ [Django Application]
      │
      ├────────→ [PostgreSQL 15]
      └────────→ [Redis 7] (Optional)
```

## 3. Django 项目结构

```
training_system/
├── apps/
│   ├── users/          # 用户、部门、角色、权限
│   ├── courses/        # 课程、分类、资料、进度
│   ├── exams/          # 考试、题目、答卷、成绩
│   ├── plans/          # 培训计划、任务、分配
│   ├── logs/           # 学习日志、操作日志
│   ├── config/         # 系统配置、成绩权重
│   ├── certificates/   # 证书模板、证书
│   ├── ranking/        # 学习排名
│   ├── signatures/     # 电子签名
│   ├── question_bank/  # 题库管理（QuestionBank, KnowledgePoint 模型）
│   └── llm/            # 大模型接入（LLMProvider, AIUsageLog 模型, LLMClient 统一客户端, AIService 服务层）
├── templates/          # HTML 模板
├── static/             # CSS/JS/图片
├── media/              # 用户上传文件
├── training_system/    # 项目配置 (settings, urls, wsgi)
├── deploy/             # 部署脚本
└── validation/         # 验证文档
```

## 4. 数据模型设计 (ER Diagram)

### 4.1 核心实体关系

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  Department │       │    User     │       │    Role     │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │◄──────┤ id (PK)     │──────►│ id (PK)     │
│ name        │  1:N  │ username    │  N:1  │ name        │
│ code (UQ)   │       │ employee_id │       │ code (UQ)   │
│ description │       │ department  │       │ permissions │
└─────────────┘       │ role        │       └─────────────┘
                      └─────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
   ┌─────────┐        ┌──────────┐        ┌─────────────┐
   │  Course │        │   Exam   │        │ TrainingPlan│
   ├─────────┤        ├──────────┤        ├─────────────┤
   │ id (PK) │        │ id (PK)  │        │ id (PK)     │
   │ title   │        │ title    │        │ title       │
   │ status  │        │ duration │        │ start_date  │
   │ creator │        │ pass_scr │        │ end_date    │
   └────┬────┘        └────┬─────┘        └──────┬──────┘
        │                  │                     │
        ▼                  ▼                     ▼
   ┌──────────┐      ┌──────────┐         ┌──────────┐
   │CourseMat.│      │ Question │         │ PlanTask │
   ├──────────┤      ├──────────┤         ├──────────┤
   │ id (PK)  │      │ id (PK)  │         │ id (PK)  │
   │ course(FK)│     │ exam(FK) │         │ plan(FK) │
   │ file     │      │ q_type   │         │ task_type│
   │ file_type│      │ score    │         └────┬─────┘
   └──────────┘      └──────────┘              │
                                               ▼
                                         ┌──────────┐
                                         │TaskAssign│
                                         ├──────────┤
                                         │ id (PK)  │
                                         │ task(FK) │
                                         │ user(FK) │
                                         │ status   │
                                         └──────────┘

┌──────────────┐       ┌────────────────┐
│ KnowledgePoint│       │  QuestionBank  │
├──────────────┤       ├────────────────┤
│ id (PK)      │◄──M2M─┤ id (PK)        │
│ name         │       │ question_text  │
│ parent (FK)  │◄──┐   │ question_type  │
└──────────────┘   │   │ difficulty     │
         ▲          │   │ score          │
         └──────────┘   │ usage_count    │
                        └───────┬────────┘
                                │ M2M
                                ▼
                        ┌────────────────┐
                        │ KnowledgePoint │
                        └────────────────┘

┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│ PaperTemplate │ 1:N   │   PaperRule   │       │  AnswerLog    │
├───────────────┤──────►├───────────────┤       ├───────────────┤
│ id (PK)       │       │ id (PK)       │       │ id (PK)       │
│ name          │       │ template (FK) │       │ attempt (FK)  │◄── ExamAttempt
│ duration      │       │ question_type │       │ question (FK) │
│ pass_score    │       │ count         │       │ old_answer    │
└───────────────┘       │ score_per_q   │       │ new_answer    │
                        │ difficulty    │       │ action_type   │
                        └───────────────┘       │ elapsed_secs  │
                                                │ ip_address    │
                                                └───────────────┘

┌───────────────┐       ┌───────────────┐
│  LLMProvider  │ 1:N   │  AIUsageLog   │
├───────────────┤──────►├───────────────┤
│ id (PK)       │       │ id (PK)       │
│ name          │       │ provider (FK) │
│ provider      │       │ task_type     │
│ api_key       │       │ tokens        │
│ base_url      │       │ duration_ms   │
│ model_name    │       │ is_success    │
│ temperature   │       │ error_message │
│ max_tokens    │       └───────────────┘
│ is_default    │
└───────────────┘
```

### 4.2 关键模型字段详述

#### User (apps/users/models.py)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BigAutoField | PK | Django 默认主键 |
| username | CharField | UQ, max=150 | 登录用户名 |
| employee_id | CharField | UQ, max=50 | 工号 |
| password | CharField | max=128 | PBKDF2 哈希密码 |
| department | ForeignKey | FK→Department, SET_NULL | 所属部门 |
| role | ForeignKey | FK→Role, SET_NULL | 角色 |
| phone | CharField | max=20 | 手机号 |
| gender | CharField | choices | 性别 |
| avatar | ImageField | upload_to='avatars/' | 头像 |
| position | CharField | max=100 | 职位 |
| is_active | BooleanField | default=True | 账号状态 |
| date_joined | DateTimeField | auto_now_add | 注册时间 |
| last_login | DateTimeField | nullable | 最后登录 |

#### Signature (apps/signatures/models.py)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | AutoField | PK | 主键 |
| signed_by | ForeignKey | FK→User, CASCADE | 签名者 |
| signature_type | CharField | choices (exam/checkin) | 签名类型 |
| signature_image | ImageField | upload_to=signature_upload_path | 签名图片 |
| signed_at | DateTimeField | auto_now_add | 签名时间戳 |
| ip_address | GenericIPAddressField | nullable | IP 地址 |
| user_agent | CharField | max=500 | 设备信息 |
| content_type | ForeignKey | FK→ContentType, nullable | GFK 类型 |
| object_id | PositiveIntegerField | nullable | GFK ID |

#### ExamAttempt (apps/exams/models.py)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | AutoField | PK | 主键 |
| exam | ForeignKey | FK→Exam, CASCADE | 关联考试 |
| user | ForeignKey | FK→User, CASCADE | 考生 |
| score | PositiveIntegerField | nullable | 得分 |
| is_passed | BooleanField | nullable | 是否及格 |
| start_time | DateTimeField | auto_now_add | 开始时间 |
| end_time | DateTimeField | nullable | 结束时间 |
| status | CharField | choices | 状态 |

#### LearningLog (apps/logs/models.py)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | AutoField | PK | 主键 |
| user | ForeignKey | FK→User, CASCADE | 操作用户 |
| action_type | CharField | choices | 操作类型 |
| course | ForeignKey | FK→Course, SET_NULL | 关联课程 |
| exam | ForeignKey | FK→Exam, SET_NULL | 关联考试 |
| material | ForeignKey | FK→CourseMaterial, SET_NULL | 关联资料 |
| detail | TextField | | 详情 |
| ip_address | GenericIPAddressField | nullable | IP |
| user_agent | CharField | max=500 | 设备 |
| duration | PositiveIntegerField | nullable | 停留时长 |
| created_at | DateTimeField | auto_now_add | 记录时间 |

#### QuestionBank (apps/question_bank/models.py)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BigAutoField | PK | 主键 |
| question_text | TextField | | 题目内容 |
| question_type | CharField | choices (single_choice/multi_choice/true_false/fill_blank/short_answer) | 题目类型 |
| difficulty | CharField | choices (easy/medium/hard) | 难度等级 |
| score | PositiveIntegerField | default=1 | 默认分值 |
| knowledge_points | ManyToManyField | M2M→KnowledgePoint | 关联知识点 |
| tags | CharField | max=500, blank | 标签（逗号分隔） |
| usage_count | PositiveIntegerField | default=0 | 使用次数 |
| created_at | DateTimeField | auto_now_add | 创建时间 |
| updated_at | DateTimeField | auto_now | 更新时间 |

#### PaperTemplate (apps/exams/models.py)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | AutoField | PK | 主键 |
| name | CharField | max=200, UQ | 模板名称 |
| duration | PositiveIntegerField | default=60 | 考试时长（分钟） |
| pass_score | PositiveIntegerField | default=60 | 及格分 |
| description | TextField | blank | 模板说明 |
| created_at | DateTimeField | auto_now_add | 创建时间 |

#### PaperRule (apps/exams/models.py)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | AutoField | PK | 主键 |
| template | ForeignKey | FK→PaperTemplate, CASCADE | 所属模板 |
| question_type | CharField | choices | 题目类型 |
| count | PositiveIntegerField | | 题目数量 |
| score_per_question | PositiveIntegerField | default=1 | 每题分值 |
| difficulty | CharField | choices, blank | 难度要求 |

#### AnswerLog (apps/exams/models.py)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BigAutoField | PK | 主键 |
| attempt | ForeignKey | FK→ExamAttempt, CASCADE | 关联考试作答 |
| question | ForeignKey | FK→QuestionBank, CASCADE | 关联题目 |
| old_answer | TextField | blank | 变更前答案 |
| new_answer | TextField | | 变更后答案 |
| action_type | CharField | choices (create/change/delete) | 操作类型 |
| elapsed_seconds | PositiveIntegerField | nullable | 答题耗时（秒） |
| ip_address | GenericIPAddressField | nullable | IP 地址 |
| created_at | DateTimeField | auto_now_add | 记录时间 |

#### LLMProvider (apps/llm/models.py)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | AutoField | PK | 主键 |
| name | CharField | max=100, UQ | 配置名称 |
| provider | CharField | max=50 | 供应商（openai/zhipu/deepseek 等） |
| api_key | CharField | max=500 | API 密钥（加密存储） |
| base_url | URLField | max=500 | API 端点地址 |
| model_name | CharField | max=100 | 模型名称 |
| temperature | FloatField | default=0.7 | 温度参数 |
| max_tokens | PositiveIntegerField | default=2048 | 最大 token 数 |
| is_default | BooleanField | default=False | 是否默认供应商 |
| created_at | DateTimeField | auto_now_add | 创建时间 |
| updated_at | DateTimeField | auto_now | 更新时间 |

## 5. 接口设计

### 5.1 内部 API 接口

| URL | 方法 | 功能 | 权限 |
|-----|------|------|------|
| /signature/api/save/ | POST | 保存电子签名 | 登录用户 |
| /courses/material/<pk>/video-progress/ | POST | 更新视频进度 | 登录用户 |
| /exams/<pk>/take/ | GET/POST | 参加考试 | 登录用户 |
| /exams/<pk>/result/ | GET | 查看成绩 | 登录用户 |
| /courses/<pk>/checkin/ | GET | 课程签到 | 登录用户 |
| /exams/attempt/<id>/answer-log/ | POST | 答题留痕 API | 登录用户 |
| /llm/providers/<id>/test/ | GET | 模型连通性测试 | 管理员 |
| /llm/ai/course-summary/<id>/ | GET | AI 课程摘要 | 登录用户 |
| /llm/ai/grade/<exam_id>/ | POST | AI 批改简答 | 管理员 |

### 5.2 签名板参数

GET `/signature/pad/?type=exam&target_type=examattempt&target_id=1&redirect_url=...&title=...`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 是 | exam / checkin |
| target_type | string | 否 | 关联对象类型 |
| target_id | int | 否 | 关联对象ID |
| redirect_url | string | 是 | 签名完成后跳转地址 |
| title | string | 否 | 页面标题 |

## 6. 安全设计

### 6.1 身份认证

- Django 内置 SessionAuthentication
- 密码使用 PBKDF2 (sha256, 260000 iterations)
- 生产环境启用 HTTPS (SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE)
- 登录视图添加 @csrf_exempt 以兼容浏览器自动化工具（仅限登录接口）

### 6.2 权限控制

- 基于角色的权限模型 (RBAC)
- Permission 模型定义 10 模块 × 7 操作 = 70 种权限组合
- 视图函数中使用 `_is_admin_or_manager()` 和 `@user_passes_test` 进行权限校验
- 管理员和普通用户在列表视图中看到不同内容

### 6.3 数据保护

- 数据库密码等敏感信息通过环境变量配置
- 生产环境 .env 文件不纳入版本控制
- 文件上传限制类型和大小（最大 100MB）
- Nginx 配置阻止访问 .env, .git, .pyc 等敏感文件

### 6.4 审计追踪

- 所有关键操作记录到 LearningLog / OperationLog
- 记录包含用户、时间、IP、设备信息
- 日志表无 DELETE/UPDATE 接口，只能通过 Admin 查看
- 电子签名记录包含完整的时间戳和元数据

## 7. 备份与恢复设计

### 7.1 备份策略

| 备份项 | 方法 | 频率 | 保留期 |
|--------|------|------|--------|
| SQLite 数据库 | 文件复制（.backup 或 cp） | 每日 02:00 | 30 天 |
| 媒体文件 (上传) | rsync 增量同步 | 每日 02:00 | 30 天 |
| 配置文件 | tar 打包 | 每日 02:00 | 30 天 |

### 7.2 恢复流程

1. 停止应用服务
2. 恢复 SQLite：将备份的 db.sqlite3 文件复制回数据目录
3. 恢复媒体文件：`rsync -a` 从备份目录恢复
4. 验证数据完整性（关键记录数校验）
5. 启动应用服务
6. 执行冒烟测试

## 8. 环境配置

### 8.1 环境变量

| 变量名 | 开发默认值 | 生产要求 | 说明 |
|--------|-----------|----------|------|
| DJANGO_SECRET_KEY | 默认密钥 | 必须修改 | 加密签名密钥 |
| DJANGO_DEBUG | True | False | 调试模式 |
| DJANGO_ALLOWED_HOSTS | * | 具体域名 | 允许主机 |
| DB_ENGINE | sqlite3 | postgresql | 数据库引擎 |
| DB_NAME | db.sqlite3 | 数据库名 | 数据库名称 |
| DB_USER | 空 | 用户名 | 数据库用户 |
| DB_PASSWORD | 空 | 强密码 | 数据库密码 |
| DB_HOST | 空 | 主机地址 | 数据库主机 |
| DB_PORT | 空 | 5432 | 数据库端口 |
| REDIS_URL | 空 | redis://... | Redis 连接 |
| SECURE_SSL_REDIRECT | False | True | HTTPS 强制跳转 |
| STATIC_ROOT | staticfiles | /var/www/static | 静态文件目录 |
| MEDIA_ROOT | media | /var/www/media | 媒体文件目录 |

---

**审批：**

| 角色 | 姓名 | 签名 | 日期 |
|------|------|------|------|
| 编制人 | | | |
| 审核人（技术） | | | |
| 审核人（质量） | | | |
| 批准人 | | | |
