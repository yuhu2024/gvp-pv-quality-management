# 君合盟药物警戒培训管理系统 (PV Training Management System) — GAMP5 验证文档包

**文档版本：** 3.0
**生效日期：** 2026-08-18  
**系统类别：** GAMP5 Category 4 — 可配置软件包 (Configurable Software)  
**验证生命周期：** SDLC (System Development Life Cycle) V-Model

---

## 文档清单

| 序号 | 文档编号 | 文档名称 | GAMP5 对应阶段 |
|------|----------|----------|----------------|
| 1 | VAL-VP-001 | 验证计划 (Validation Plan) | Planning |
| 2 | VAL-URS-001 | 用户需求规格 (User Requirements Specification) | Specification |
| 3 | VAL-FS-001 | 功能规格 (Functional Specification) | Specification |
| 4 | VAL-DS-001 | 设计规格 (Design Specification) | Specification |
| 5 | VAL-RA-001 | 风险评估 (Risk Assessment) | Planning/Specification |
| 6 | VAL-IQ-001 | 安装确认 (Installation Qualification) | Verification |
| 7 | VAL-OQ-001 | 运行确认 (Operational Qualification) | Verification |
| 8 | VAL-PQ-001 | 性能确认 (Performance Qualification) | Verification |
| 9 | VAL-TM-001 | 追溯矩阵 (Traceability Matrix) | Reporting |
| 10 | VAL-SOP-001 | 标准操作规程 (SOP) | Operations |
| 11 | VAL-CCL-001 | 变更控制记录 (Change Control Log) | Operations |
| 12 | VAL-TR-001 | 培训记录 (Training Records) | Operations |
| 13 | VAL-VR-001 | 验证报告 (Validation Report) | Reporting |

## 验证范围

本验证文档包适用于 君合盟药物警戒培训管理系统 (PV Training Management System)，该系统用于：
- 企业内部培训课程的管理与发布
- 在线考试与成绩管理
- 员工培训计划与任务分配
- 学习进度跟踪与电子签名确认
- 培训痕迹记录与审计追踪
- 题库管理与自动组卷出题
- AI 大模型集成（自动出题、智能批改、课程摘要）
- PPT 课件自动生成
- 考试试卷上传与答题留痕
- 培训矩阵管理（按部门+岗位定义培训要求）
- 学习排行榜（学习时长/考试成绩/课程完成）
- 荣誉证书管理（模板管理+证书颁发）
- 培训记录时间管理（隐藏功能，用于数据修正）

## 合规性声明

本系统验证严格遵循以下法规和标准：
- **GAMP5** (Good Automated Manufacturing Practice Guide 5)
- **21 CFR Part 11** (FDA Electronic Records and Electronic Signatures)
- **EU GMP Annex 11** (Computerised Systems)
- **ICH Q9** (Quality Risk Management)
- **ISPE GAMP Guide: Records and Data Integrity**

## 角色与职责

| 角色 | 职责 |
|------|------|
| 质量负责人 (QA) | 审批验证计划、验证报告；监督验证过程合规性 |
| 验证负责人 (Validation Lead) | 制定验证策略；协调验证活动；审核验证文档 |
| 系统管理员 (System Admin) | 系统安装、配置、维护；执行 IQ/OQ/PQ |
| 业务负责人 (Process Owner) | 定义业务需求；确认 URS；参与 OQ/PQ 测试 |
| 开发人员 (Developer) | 系统开发/定制；提供技术规格；修复缺陷 |
| 最终用户 (End User) | 参与 UAT；提供使用反馈；完成培训 |

## 文档控制

所有验证文档遵循以下版本控制规则：
- 初稿版本为 0.1，审批通过后版本为 1.0
- 每次修订版本号递增 0.1，重大变更递增 1.0
- 所有变更须通过变更控制流程审批
- 电子文档使用电子签名确认审批状态

---

**审批：**

| 角色 | 姓名 | 签名 | 日期 |
|------|------|------|------|
| 编制人 | | | |
| 审核人（验证） | | | |
| 审核人（质量） | | | |
| 批准人 | | | |