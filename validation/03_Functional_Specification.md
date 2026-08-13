# 功能规格 (Functional Specification)

**文档编号：** VAL-FS-001
**版本：** 2.0
**生效日期：** 2026-07-24  

---

## 1. 目的

本文档基于 URS (VAL-URS-001)，详细描述 君合盟药物警戒君合盟药物警戒培训管理系统 (PV Training Management System) 的功能实现方式，为系统开发、测试和验证提供技术依据。

## 2. 功能模块映射

### 2.1 用户与账号管理 (USR)

| URS 编号 | 功能规格 | 实现方式 | 验证方法 |
|----------|----------|----------|----------|
| USR-001 | 用户 CRUD 操作 | Django Admin + 自定义视图 | OQ-001 |
| USR-002 | 唯一性约束 | 数据库 UNIQUE 约束 + 表单校验 | OQ-002 |
| USR-003 | 密码复杂度 | Django Password Validators + 自定义校验 | OQ-003 |
| USR-004 | Excel 批量导入 | openpyxl 读取 + 事务批量创建 | OQ-004 |
| USR-005 | 部门/角色模型 | ForeignKey 关联 Department/Role | OQ-005 |
| USR-006 | 登录/登出日志 | LearningLog 模型自动记录 | OQ-006 |
| USR-007 | 个人资料编辑 | UserProfileForm 表单 | OQ-007 |

**技术实现：**
- User 模型继承 Django AbstractUser，扩展 employee_id、department、role、phone、gender、avatar、position 字段
- 密码使用 Django 默认 PBKDF2 哈希算法
- 部门模型：name, code, description
- 角色模型：name, code, description, permissions (M2M)

### 2.2 课程与资料管理 (CRS)

| URS 编号 | 功能规格 | 实现方式 | 验证方法 |
|----------|----------|----------|----------|
| CRS-001 | 多级分类 | Category 模型自引用 ForeignKey (parent) | OQ-008 |
| CRS-002 | 文件上传 | Django FileField + 类型校验 | OQ-009 |
| CRS-003 | 审核工作流 | status 字段状态机：draft→pending_review→approved→rejected→published | OQ-010 |
| CRS-004 | 审计字段 | created_by, reviewer, review_note, reviewed_at, published_at | OQ-011 |
| CRS-005 | 视频防作弊 | JavaScript 30秒跳跃限制 + 后端 95% 阈值校验 | OQ-012 |
| CRS-006 | 文件大小自动计算 | save() 方法中读取 file.size | OQ-013 |
| CRS-007 | PPT 自动生成 | ppt_generator.py，python-pptx 生成封面/大纲/摘要页 | OQ-046 |
| CRS-008 | 文件类型展示 | course_detail.html 彩色图标 + 视频 player + PDF iframe | OQ-047 |

**技术实现：**
- Course 模型：title, category, description, creator, status, reviewer, review_note, reviewed_at, published_at
- CourseMaterial 模型：course (FK), title, file_type, file, file_size, description, upload_time, download_count, status
- Category 模型：parent (self FK), name, code, description, order, is_active
- 文件存储路径：`courses/materials/YYYY/MM/`
- PPT 转换：LibreOffice headless 模式 → PDF → pdftoppm → PNG

### 2.3 考试管理 (EXM)

| URS 编号 | 功能规格 | 实现方式 | 验证方法 |
|----------|----------|----------|----------|
| EXM-001 | 5种题型支持 | Question 模型 question_type 字段 (CharField choices) | OQ-014 |
| EXM-002 | 考试计时 | 服务端计算剩余时间 + JS 倒计时，双重校验 | OQ-015 |
| EXM-003 | 自动评分 | Question.check_answer() 方法，按题型分别处理 | OQ-016 |
| EXM-004 | 考试记录 | ExamAttempt 模型记录 start_time, end_time, score, status | OQ-017 |
| EXM-005 | 考试签名 | 提交前跳转签名板 → 签名后返回 → 提交时关联 signature_id | OQ-018 |
| EXM-006 | 成绩查看 | exam_score_view 管理员视图，加载签名信息 | OQ-019 |
| EXM-007 | 试卷上传与展示 | Exam 模型 exam_paper FileField，答题页 iframe 内嵌 PDF 预览 | OQ-043 |
| EXM-008 | 答题留痕 | AnswerLog 模型，JS 实时监听答案变更 + 后端 API 记录 | OQ-044 |
| EXM-009 | 留痕查看 | attempt_logs.html 时间线视图，按题目分组展示 | OQ-045 |

**技术实现：**
- Exam 模型：title, description, course (FK), duration, total_score, pass_score, is_published, created_by, exam_paper (FileField)
- Question 模型：exam (FK), question_text, question_type, option_a/b/c/d, correct_answer, score, order
- ExamAttempt 模型：exam (FK), user (FK), score, is_passed, start_time, end_time, status
- Answer 模型：attempt (FK), question (FK), user_answer, is_correct, score
- AnswerLog 模型：answer (FK), user (FK), old_value, new_value, changed_at
- 超时判断：`(now - start_time) >= duration`
- 答题留痕：前端 JS 监听答案变更事件 → AJAX POST → 后端 API 创建 AnswerLog 记录

### 2.4 培训计划 (PLN)

| URS 编号 | 功能规格 | 实现方式 | 验证方法 |
|----------|----------|----------|----------|
| PLN-001 | 计划创建 | TrainingPlan 模型：title, description, start_date, end_date, status | OQ-020 |
| PLN-002 | 关联课程/考试 | ManyToManyField 关联 Course 和 Exam | OQ-021 |
| PLN-003 | 任务分配 | PlanTask → TaskAssignment 模型 | OQ-022 |
| PLN-004 | 状态跟踪 | TaskAssignment.status 字段（pending/in_progress/completed/overdue） | OQ-023 |
| PLN-005 | 完成计时 | save() 方法中 status=completed 时自动计算 completion_duration | OQ-024 |

### 2.5 日志与审计 (LOG)

| URS 编号 | 功能规格 | 实现方式 | 验证方法 |
|----------|----------|----------|----------|
| LOG-001 | 操作记录 | LearningLog 模型，视图函数中显式创建 | OQ-025 |
| LOG-002 | 完整元数据 | user, action_type, course/exam/material (FK), detail, ip_address, user_agent, duration, created_at | OQ-026 |
| LOG-003 | 不可篡改 | 无删除/编辑接口；数据库层面无 DELETE 权限给应用用户 | OQ-027 |
| LOG-004 | 日志查询 | Django Admin 列表视图 + 筛选器 | OQ-028 |
| LOG-005 | 操作日志 | OperationLog 模型记录管理操作 | OQ-029 |

### 2.6 电子签名 (SIG)

| URS 编号 | 功能规格 | 实现方式 | 验证方法 |
|----------|----------|----------|----------|
| SIG-001 | 手写签名 | HTML5 Canvas + 触摸事件监听，支持手机 | OQ-030 |
| SIG-002 | 签名绑定 | GenericForeignKey 关联 ExamAttempt/CourseProgress | OQ-031 |
| SIG-003 | 完整元数据 | signed_by, signature_type, signature_image, signed_at, ip_address, user_agent | OQ-032 |
| SIG-004 | 加密存储 | 签名图片保存为 PNG 到 `signatures/YYYY/MM/UUID.png` | OQ-033 |
| SIG-005 | 记录锁定 | 签名关联后系统层面不开放 ExamAttempt/CourseProgress 的修改接口 | OQ-034 |
| SIG-006 | 签名展示 | result.html / course_detail.html 展示签名图片和时间戳 | OQ-035 |

**技术实现：**
- Signature 模型：signed_by (FK), signature_type (exam/checkin), signature_image, signed_at, ip_address, user_agent, content_type (GFK), object_id, content_object
- Canvas 绘制：touch-action:none 防止滚动，同时支持 mouse 和 touch 事件
- 图片处理：PIL 验证并统一转换为 PNG 格式

### 2.7 安全与权限 (SEC)

| URS 编号 | 功能规格 | 实现方式 | 验证方法 |
|----------|----------|----------|----------|
| SEC-001 | RBAC | Django auth + 自定义 Permission/Role 模型 | OQ-036 |
| SEC-002 | 细粒度权限 | Permission 模型：module + action → code (如 course:create) | OQ-037 |
| SEC-003 | HTTPS | Nginx SSL 配置 + Django SECURE_SSL_REDIRECT | IQ-003 |
| SEC-004 | 密码哈希 | Django PBKDF2PasswordHasher (默认) | OQ-038 |
| SEC-005 | 会话超时 | SESSION_COOKIE_AGE = 86400 秒 | OQ-039 |
| SEC-006 | 生产安全 | DEBUG=False, SECURE_HSTS, X-Frame-Options=DENY | IQ-004 |

### 2.8 系统配置 (CFG)

| URS 编号 | 功能规格 | 实现方式 | 验证方法 |
|----------|----------|----------|----------|
| CFG-001 | 成绩权重 | ScoreWeightConfig 模型：video_weight, material_weight, exam_weight | OQ-040 |
| CFG-002 | 参数配置 | SystemConfig 模型：key-value 对，支持多种数据类型 | OQ-041 |
| CFG-003 | 配置审计 | 配置变更通过 Django Admin，自动记录到操作日志 | OQ-042 |

### 2.9 基础设施 (INF)

| URS 编号 | 功能规格 | 实现方式 | 验证方法 |
|----------|----------|----------|----------|
| INF-001 | PostgreSQL | psycopg2-binary 驱动，生产环境默认 | IQ-001 |
| INF-002 | Redis 缓存 | django-redis，CACHES 配置，可选启用 | IQ-002 |
| INF-003 | Nginx + Gunicorn | supervisor 管理 4 workers，Unix socket 通信 | IQ-005 |
| INF-004 | 自动备份 | backup.sh：pg_dump + rsync，每日 cron 执行 | IQ-006 |
| INF-005 | 保留策略 | backup.sh 中 find -mtime +30 -delete | IQ-007 |

### 2.10 题库管理 (QBN)

| URS 编号 | 功能规格 | 实现方式 | 验证方法 |
|----------|----------|----------|----------|
| QBN-001 | 题目 CRUD | QuestionBank 模型 + question_list_view 筛选视图 | OQ-048 |
| QBN-002 | 多维度信息 | question_type, difficulty, score, knowledge_points (M2M), tags | OQ-049 |
| QBN-003 | 筛选 | GET 参数过滤：type/difficulty/kp/tag/search/active | OQ-050 |
| QBN-004 | Excel 导入导出 | openpyxl 读写 + question_export/import_view | OQ-051 |
| QBN-005 | 知识点树形 | KnowledgePoint 模型 self FK (parent) | OQ-052 |
| QBN-006 | 统计面板 | question_stats_view，Django aggregate 聚合 | OQ-053 |

**技术实现：**
- QuestionBank 模型：question_text, question_type, option_a, option_b, option_c, option_d, correct_answer, analysis, score, difficulty, tags, usage_count, is_active, created_by, knowledge_points (M2M → KnowledgePoint)
- KnowledgePoint 模型：name, parent (self FK), description, order
- to_exam_question() 方法：将题库题目转换为考试题目
- 筛选视图：GET 参数过滤 type/difficulty/kp/tag/search/active，支持分页
- Excel 导入导出：openpyxl 读写，question_export/import_view 处理文件上传下载
- 统计面板：question_stats_view，Django aggregate 聚合各维度数量统计

### 2.11 自动出卷 (ATP)

| URS 编号 | 功能规格 | 实现方式 | 验证方法 |
|----------|----------|----------|----------|
| ATP-001 | 出卷模板 | PaperTemplate + PaperRule 模型，模板创建/编辑视图 | OQ-054 |
| ATP-002 | 知识点限定 | PaperRule.knowledge_point_ids TextField 存储逗号分隔 ID | OQ-055 |
| ATP-003 | 随机组卷 | PaperRule.select_questions() + PaperTemplate.generate_exam() | OQ-056 |
| ATP-004 | 总分计算 | generate_exam() 中 aggregate Sum score 后回写 | OQ-057 |
| ATP-005 | 使用计数 | generate_exam() 中 F('usage_count') + 1 | OQ-058 |

**技术实现：**
- PaperTemplate 模型：name, description, duration, pass_score, is_active, created_by, rules (related_name)
- PaperRule 模型：template (FK), question_type, count, score_per_question, difficulty, knowledge_point_ids (TextField, 逗号分隔 ID), order
- generate_exam() 核心逻辑：遍历 rules → select_questions() 随机抽题 → to_exam_question() → 计算总分
- 总分计算：aggregate Sum(score) 后回写 Exam.total_score
- 使用计数：F('usage_count') + 1 原子更新

### 2.12 PPT 自动生成 (PPT)

| URS 编号 | 功能规格 | 实现方式 | 验证方法 |
|----------|----------|----------|----------|
| PPT-001 | PPT 生成 | apps/courses/ppt_generator.py，python-pptx 库 | OQ-059 |
| PPT-002 | 页面结构 | 封面/概述/大纲/资料摘要/结束页，标准模板 | OQ-060 |
| PPT-003 | 文件类型色块 | RGB 颜色映射 ppt=#d04423/word=#2b579a/pdf=#e74c3c/video=#28a745 | OQ-061 |

**技术实现：**
- ppt_generator.py 位于 apps/courses/，使用 python-pptx 库
- 标准模板结构：封面页 → 概述页 → 大纲页 → 资料摘要页 → 结束页
- 文件类型彩色映射：PPT=#d04423, Word=#2b579a, PDF=#e74c3c, Video=#28a745

### 2.13 大模型接入 (AI)

| URS 编号 | 功能规格 | 实现方式 | 验证方法 |
|----------|----------|----------|----------|
| AI-001 | 多模型接入 | LLMProvider 模型 + LLMClient 统一客户端 (urllib) | OQ-062 |
| AI-002 | 模型配置 | provider/base_url/model_name/temperature/max_tokens/api_key | OQ-063 |
| AI-003 | AI 出题 | AIService.generate_questions() → JSON 解析 → QuestionBank.create | OQ-064 |
| AI-004 | AI 批改 | AIService.grade_essay() → score + comment → Answer 更新 | OQ-065 |
| AI-005 | AI 摘要 | AIService.summarize_course() → AJAX 渲染 | OQ-066 |
| AI-006 | 调用日志 | AIUsageLog 模型：task_type, tokens, duration_ms, is_success | OQ-067 |
| AI-007 | 默认模型 | LLMProvider.is_default 单例约束，LLMClient 优先使用默认 | OQ-068 |

**技术实现：**
- LLMProvider 模型：name, provider (choices: kimi/doubao/qwen/openai/custom), api_key, base_url, model_name, temperature, max_tokens, is_active, is_default
- LLMClient：urllib.request 调用 OpenAI 兼容 /chat/completions 端点，60 秒超时
- AIService：generate_questions / grade_essay / summarize_course / generate_ppt_outline，_parse_json_response 解析 AI 返回
- AIUsageLog 模型：provider (FK), task_type, input_text, output_text, prompt/completion/total_tokens, duration_ms, is_success, error_message
- 支持模型：Kimi (api.moonshot.cn/v1), 豆包 (ark.cn-beijing.volces.com/api/v3), 千问 (dashscope.aliyuncs.com/compatible-mode/v1), OpenAI, 自定义
- LLMProvider.is_default 单例约束，LLMClient 优先使用默认模型

---

**审批：**

| 角色 | 姓名 | 签名 | 日期 |
|------|------|------|------|
| 编制人 | | | |
| 审核人（技术） | | | |
| 审核人（质量） | | | |
| 批准人 | | | |
