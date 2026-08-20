# 君合盟PV培训系统 · 界面优化实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将培训系统界面从 Bootstrap 默认风格提升至世界500强企业标准，建立统一的品牌设计系统

**Architecture:** 基于 Django 模板系统 + Bootstrap 5，通过重写全局 CSS 建立设计系统，分阶段改造 P0/P1/P2 模板。不引入新框架，不改后端逻辑。

**Tech Stack:** CSS Custom Properties, Bootstrap 5, Google Fonts (Inter + Noto Sans SC)

---

## 文件结构

| 文件 | 职责 |
|------|------|
| `static/css/style.css` | 全局设计系统，包含所有 CSS 变量和组件样式 |
| `templates/base.html` | 全局导航栏和页脚重构 |
| `templates/registration/login.html` | 登录页面重设计 |
| `templates/users/dashboard.html` | 学员仪表盘重设计 |
| `templates/courses/course_list.html` | 课程列表页样式更新 |
| `templates/exams/exam_list.html` | 考试列表页样式更新 |
| `templates/plans/my_tasks.html` | 任务列表页样式更新 |
| 其他 P1/P2 模板 | 批量样式统一 |

---

### 任务 1: 重写全局 CSS 设计系统

**Files:**
- Modify: `static/css/style.css`（全量重写）

- [ ] **Step 1: 建立 CSS 变量体系**

```css
/* ========================================
   君合盟药物警戒培训管理系统 - 全局样式
   v2.0 - Fortune 500 Design System
   ======================================== */

/* ---- 字体导入 ---- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Sans+SC:wght@300;400;500;600;700;800&display=swap');

/* ---- 品牌色系统 ---- */
:root {
  /* 主色 */
  --brand-navy: #0A1628;
  --brand-navy-light: #132347;
  --brand-indigo: #1A3A6B;
  --brand-teal: #0D9488;
  --brand-mint: #5EE4D0;

  /* 功能色 */
  --color-blue: #2563EB;
  --color-blue-bg: #EFF6FF;
  --color-green: #059669;
  --color-green-bg: #ECFDF5;
  --color-amber: #D97706;
  --color-amber-bg: #FFFBEB;
  --color-red: #DC2626;
  --color-red-bg: #FEF2F2;
  --color-purple: #6366F1;
  --color-purple-bg: #EEF2FF;

  /* 中性色 */
  --text-primary: #0A1628;
  --text-secondary: #374151;
  --text-tertiary: #6B7280;
  --text-muted: #9CA3AF;
  --border-color: #E5E7EB;
  --border-light: #F0F0F0;
  --bg-body: #F8FAFC;
  --bg-card: #FFFFFF;
  --bg-subtle: #FAFAFA;

  /* 阴影 */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 8px 30px rgba(0, 0, 0, 0.08);
  --shadow-xl: 0 4px 24px rgba(0, 0, 0, 0.12);

  /* 圆角 */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;

  /* 间距 */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;

  /* 字体 */
  --font-sans: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'SF Mono', 'Fira Code', 'Consolas', monospace;

  /* 过渡 */
  --transition-fast: 0.15s ease;
  --transition-normal: 0.2s ease;

  /* 导航栏 */
  --navbar-height: 56px;
}
```

- [ ] **Step 2: 基础样式 + 导航栏**

```css
/* ---- 基础样式 ---- */
body {
  font-family: var(--font-sans);
  background-color: var(--bg-body);
  color: var(--text-primary);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  line-height: 1.6;
  font-size: 14px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

main { flex: 1; }

a {
  color: var(--brand-teal);
  text-decoration: none;
  transition: color var(--transition-fast);
}
a:hover { color: #0F766E; }

/* ---- 导航栏 ---- */
.navbar {
  background: var(--brand-navy) !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  z-index: 1030;
  height: var(--navbar-height);
  padding: 0 0;
}
.navbar .container {
  height: 100%;
  display: flex;
  align-items: center;
}
.navbar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 0.95rem;
  letter-spacing: 0.3px;
  color: #fff !important;
  padding: 0;
  margin-right: 24px;
}
.navbar-brand .brand-logo {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, var(--brand-teal), var(--brand-mint));
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  color: #fff;
  font-weight: 700;
  flex-shrink: 0;
}
.navbar .nav-link {
  padding: 6px 14px;
  font-size: 0.82rem;
  font-weight: 500;
  color: rgba(255,255,255,0.65) !important;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  white-space: nowrap;
}
.navbar .nav-link:hover {
  color: #fff !important;
  background: rgba(255,255,255,0.08);
}
.navbar .nav-link.active {
  color: #fff !important;
  background: rgba(255,255,255,0.1);
  font-weight: 600;
}
.navbar .dropdown-menu {
  border: none;
  box-shadow: var(--shadow-xl);
  border-radius: var(--radius-md);
  padding: 6px;
  font-size: 0.82rem;
  margin-top: 8px;
  animation: dropdownFadeIn 0.15s ease;
  min-width: 200px;
}
.navbar .dropdown-item {
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  transition: background-color var(--transition-fast);
  font-size: 0.82rem;
  color: var(--text-secondary);
}
.navbar .dropdown-item:hover {
  background-color: #F0FDFA;
  color: var(--brand-teal);
}
.navbar .dropdown-item.active {
  background-color: #F0FDFA;
  color: var(--brand-teal);
  font-weight: 600;
}
.navbar .dropdown-header {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  padding: 6px 12px;
}
.navbar .dropdown-divider {
  margin: 4px 0;
  border-color: var(--border-light);
}
.user-dropdown-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px 4px 4px !important;
  border-radius: 20px !important;
  background: rgba(255,255,255,0.06) !important;
}
.user-dropdown-toggle:hover {
  background: rgba(255,255,255,0.1) !important;
}
.user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-purple), #8B5CF6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  color: #fff;
  font-weight: 600;
  flex-shrink: 0;
}
```

- [ ] **Step 3: 卡片组件样式**

```css
/* ---- 卡片样式 ---- */
.card {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-normal);
  background: var(--bg-card);
  animation: fadeIn 0.3s ease;
}
.card:hover {
  box-shadow: var(--shadow-md);
}
.card-header {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-light);
  font-weight: 600;
  padding: var(--space-4) var(--space-5);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0 !important;
}
.card-header h5 {
  margin-bottom: 0;
  font-size: 0.9rem;
  color: var(--text-primary);
}
.card-body {
  padding: var(--space-5);
}
.card-footer {
  background: var(--bg-card);
  border-top: 1px solid var(--border-light);
  border-radius: 0 0 var(--radius-lg) var(--radius-lg) !important;
}

/* ---- 统计卡片 ---- */
.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}
.stat-card:hover {
  border-color: #E0E0E0;
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}
.stat-card .stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  margin-bottom: var(--space-3);
}
.stat-card .stat-icon.blue { background: var(--color-blue-bg); color: var(--color-blue); }
.stat-card .stat-icon.green { background: var(--color-green-bg); color: var(--color-green); }
.stat-card .stat-icon.amber { background: var(--color-amber-bg); color: var(--color-amber); }
.stat-card .stat-icon.teal { background: #F0FDFA; color: var(--brand-teal); }
.stat-card .stat-icon.slate { background: #F1F5F9; color: #475569; }
.stat-card .stat-icon.purple { background: var(--color-purple-bg); color: var(--color-purple); }
.stat-card .stat-icon.red { background: var(--color-red-bg); color: var(--color-red); }

.stat-card .stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
  margin-bottom: 2px;
}
.stat-card .stat-label {
  font-size: 0.78rem;
  color: var(--text-tertiary);
}
.stat-card .stat-trend {
  font-size: 0.7rem;
  color: var(--color-green);
  margin-top: 6px;
}

/* 渐变背景的统计卡片 */
.stat-card.bg-primary { background: linear-gradient(135deg, var(--brand-navy), var(--brand-navy-light)); color: #fff; }
.stat-card.bg-primary .stat-label { color: rgba(255,255,255,0.7); }
.stat-card.bg-primary .stat-icon { background: rgba(255,255,255,0.15); color: #fff; }
.stat-card.bg-success { background: linear-gradient(135deg, var(--color-green), #047857); color: #fff; }
.stat-card.bg-success .stat-label { color: rgba(255,255,255,0.7); }
.stat-card.bg-success .stat-icon { background: rgba(255,255,255,0.15); color: #fff; }
.stat-card.bg-warning { background: linear-gradient(135deg, var(--color-amber), #B45309); color: #fff; }
.stat-card.bg-warning .stat-label { color: rgba(255,255,255,0.7); }
.stat-card.bg-warning .stat-icon { background: rgba(255,255,255,0.15); color: #fff; }
.stat-card.bg-info { background: linear-gradient(135deg, var(--brand-teal), #0F766E); color: #fff; }
.stat-card.bg-info .stat-label { color: rgba(255,255,255,0.7); }
.stat-card.bg-info .stat-icon { background: rgba(255,255,255,0.15); color: #fff; }
.stat-card.bg-secondary { background: linear-gradient(135deg, #475569, #334155); color: #fff; }
.stat-card.bg-secondary .stat-label { color: rgba(255,255,255,0.7); }
.stat-card.bg-secondary .stat-icon { background: rgba(255,255,255,0.15); color: #fff; }
.stat-card.bg-purple { background: linear-gradient(135deg, var(--color-purple), #7C3AED); color: #fff; }
.stat-card.bg-purple .stat-label { color: rgba(255,255,255,0.7); }
.stat-card.bg-purple .stat-icon { background: rgba(255,255,255,0.15); color: #fff; }
.stat-card.bg-danger { background: linear-gradient(135deg, var(--color-red), #B91C1C); color: #fff; }
.stat-card.bg-danger .stat-label { color: rgba(255,255,255,0.7); }
.stat-card.bg-danger .stat-icon { background: rgba(255,255,255,0.15); color: #fff; }
```

- [ ] **Step 4: 表格样式**

```css
/* ---- 表格样式 ---- */
.table {
  margin-bottom: 0;
  font-size: 0.82rem;
}
.table thead th {
  font-weight: 600;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-tertiary);
  background: var(--bg-subtle);
  border-bottom: 2px solid var(--border-color);
  padding: 10px var(--space-5);
  white-space: nowrap;
}
.table tbody td {
  padding: 12px var(--space-5);
  vertical-align: middle;
  border-bottom: 1px solid #F3F4F6;
  color: var(--text-secondary);
}
.table tbody tr:last-child td {
  border-bottom: none;
}
.table-hover tbody tr {
  transition: background-color var(--transition-fast);
}
.table-hover tbody tr:hover {
  background-color: #F9FAFB;
}
.table tbody tr.status-expired {
  background-color: #FEF2F2;
}
.table .btn-group .btn {
  padding: 3px 8px;
  font-size: 0.78rem;
}
```

- [ ] **Step 5: 按钮样式**

```css
/* ---- 按钮样式 ---- */
.btn {
  border-radius: var(--radius-md);
  font-weight: 500;
  font-size: 0.875rem;
  padding: 8px 16px;
  transition: all var(--transition-fast);
  white-space: nowrap;
}
.btn-sm {
  padding: 4px 10px;
  font-size: 0.78rem;
}
.btn-lg {
  padding: 12px 24px;
  font-size: 1rem;
}
.btn-primary {
  background-color: var(--brand-teal);
  border-color: var(--brand-teal);
  color: #fff;
}
.btn-primary:hover {
  background-color: #0F766E;
  border-color: #0F766E;
  color: #fff;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(13, 148, 136, 0.3);
}
.btn-primary:active { transform: translateY(0); }
.btn-success {
  background-color: var(--color-green);
  border-color: var(--color-green);
}
.btn-success:hover {
  background-color: #047857;
  border-color: #047857;
}
.btn-danger {
  background-color: var(--color-red);
  border-color: var(--color-red);
}
.btn-danger:hover {
  background-color: #B91C1C;
  border-color: #B91C1C;
}
.btn-outline-primary {
  color: var(--brand-teal);
  border-color: var(--brand-teal);
}
.btn-outline-primary:hover {
  background-color: var(--brand-teal);
  border-color: var(--brand-teal);
  color: #fff;
}
.btn-outline-secondary {
  color: var(--text-tertiary);
  border-color: var(--border-color);
}
.btn-outline-secondary:hover {
  background-color: #F9FAFB;
  border-color: var(--text-tertiary);
  color: var(--text-primary);
}
```

- [ ] **Step 6: 表单样式**

```css
/* ---- 表单样式 ---- */
.form-control, .form-select {
  border-radius: var(--radius-md);
  border: 1.5px solid var(--border-color);
  padding: 10px 12px;
  font-size: 0.875rem;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  color: var(--text-primary);
}
.form-control:focus, .form-select:focus {
  border-color: var(--brand-teal);
  box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.12);
}
.form-control.is-invalid, .form-select.is-invalid {
  border-color: var(--color-red);
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.12);
}
.form-label {
  font-weight: 500;
  font-size: 0.82rem;
  color: var(--text-primary);
  margin-bottom: 6px;
}
.form-text {
  font-size: 0.75rem;
  color: var(--text-tertiary);
}
.input-group-text {
  border-radius: var(--radius-md) 0 0 var(--radius-md);
  border: 1.5px solid var(--border-color);
  border-right: none;
  background: var(--bg-subtle);
  color: var(--text-tertiary);
  font-size: 0.875rem;
}
.input-group .form-control {
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
}
```

- [ ] **Step 7: 徽章 + 分页 + 其他组件**

```css
/* ---- 徽章样式 ---- */
.badge {
  font-weight: 500;
  border-radius: 4px;
  font-size: 0.7rem;
  padding: 3px 10px;
}
.badge.bg-primary { background: var(--color-blue-bg) !important; color: var(--color-blue); }
.badge.bg-success { background: var(--color-green-bg) !important; color: var(--color-green); }
.badge.bg-warning { background: var(--color-amber-bg) !important; color: var(--color-amber); }
.badge.bg-danger { background: var(--color-red-bg) !important; color: var(--color-red); }
.badge.bg-info { background: #F0FDFA !important; color: var(--brand-teal); }
.badge.bg-secondary { background: #F1F5F9 !important; color: #475569; }

/* ---- 分页 ---- */
.pagination { margin-bottom: 0; }
.pagination .page-link {
  border-radius: var(--radius-sm);
  margin: 0 2px;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  font-size: 0.82rem;
  padding: 6px 12px;
  transition: all var(--transition-fast);
}
.pagination .page-link:hover {
  background-color: #F0FDFA;
  border-color: var(--brand-teal);
  color: var(--brand-teal);
}
.pagination .page-item.active .page-link {
  background-color: var(--brand-teal);
  border-color: var(--brand-teal);
  color: #fff;
}
.pagination .page-item.disabled .page-link {
  color: var(--text-muted);
  pointer-events: none;
}

/* ---- 面包屑 ---- */
.breadcrumb {
  background: transparent;
  padding: 0;
  margin-bottom: var(--space-4);
  font-size: 0.82rem;
}
.breadcrumb-item a { color: var(--text-tertiary); }
.breadcrumb-item.active { color: var(--text-primary); font-weight: 500; }

/* ---- 页面标题 ---- */
.page-header {
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border-light);
}
.page-header h4 {
  font-weight: 700;
  font-size: 1.25rem;
  color: var(--text-primary);
  margin-bottom: 4px;
}
.page-header p {
  color: var(--text-tertiary);
  margin-bottom: 0;
  font-size: 0.85rem;
}

/* ---- 快速操作 ---- */
.quick-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  border-radius: 10px;
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  text-decoration: none;
  color: var(--text-primary);
  transition: all var(--transition-normal);
  cursor: pointer;
}
.quick-action:hover {
  border-color: var(--brand-teal);
  background: #F0FDFA;
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
  text-decoration: none;
  color: var(--brand-teal);
}
.quick-action .quick-action-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  margin-bottom: 8px;
  transition: transform var(--transition-normal);
}
.quick-action:hover .quick-action-icon {
  transform: scale(1.1);
}
.quick-action .quick-action-label {
  font-size: 0.82rem;
  font-weight: 500;
}

/* ---- 列表组 ---- */
.list-group-item {
  border-color: var(--border-light);
  padding: 12px var(--space-4);
  transition: background-color var(--transition-fast);
  font-size: 0.82rem;
  color: var(--text-secondary);
}
.list-group-item:hover {
  background-color: #F9FAFB;
}
.list-group-item:first-child {
  border-radius: var(--radius-md) var(--radius-md) 0 0;
}
.list-group-item:last-child {
  border-radius: 0 0 var(--radius-md) var(--radius-md);
}

/* ---- 任务列表 ---- */
.task-item {
  padding: 14px var(--space-5);
  border-bottom: 1px solid var(--border-light);
  transition: background-color var(--transition-fast);
}
.task-item:last-child { border-bottom: none; }
.task-item:hover { background-color: #F9FAFB; }
.task-item .task-title {
  font-weight: 500;
  font-size: 0.85rem;
  color: var(--text-primary);
  margin-bottom: 2px;
}
.task-item .task-title a {
  color: var(--text-primary);
}
.task-item .task-title a:hover {
  color: var(--brand-teal);
}
.task-item .task-meta {
  font-size: 0.75rem;
  color: var(--text-tertiary);
}
.task-item .task-deadline {
  font-size: 0.75rem;
  color: var(--text-muted);
}
.task-item .task-deadline.overdue {
  color: var(--color-red);
  font-weight: 600;
}

/* ---- 消息提示 ---- */
.message-container {
  position: relative;
  z-index: 1050;
}
.message-container .alert {
  border-radius: var(--radius-md);
  border: none;
  border-left: 4px solid transparent;
  padding: 12px var(--space-4);
  font-size: 0.85rem;
  animation: slideDown 0.3s ease;
}
.alert-success { background: var(--color-green-bg); color: #065F46; border-left-color: var(--color-green); }
.alert-danger { background: var(--color-red-bg); color: #991B1B; border-left-color: var(--color-red); }
.alert-warning { background: var(--color-amber-bg); color: #92400E; border-left-color: var(--color-amber); }
.alert-info { background: #F0FDFA; color: #0F766E; border-left-color: var(--brand-teal); }

/* ---- 空状态 ---- */
.empty-state {
  text-align: center;
  padding: 48px var(--space-4);
  color: var(--text-tertiary);
}
.empty-state .empty-icon {
  font-size: 3rem;
  color: var(--text-muted);
  margin-bottom: var(--space-4);
}
.empty-state h5 {
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}
.empty-state p {
  font-size: 0.85rem;
  max-width: 300px;
  margin: 0 auto;
}

/* ---- 进度条 ---- */
.progress {
  height: 8px;
  border-radius: 4px;
  background: var(--border-color);
  overflow: hidden;
}
.progress-bar {
  border-radius: 4px;
  transition: width 0.6s ease;
}
.progress-bar.bg-primary { background: var(--brand-teal); }
.progress-bar.bg-success { background: var(--color-green); }
.progress-bar.bg-warning { background: var(--color-amber); }
.progress-lg { height: 12px; border-radius: 6px; }
.progress-sm { height: 4px; border-radius: 2px; }

/* ---- 页脚 ---- */
.site-footer {
  background: var(--bg-card);
  border-top: 1px solid var(--border-light);
  margin-top: auto;
}
.site-footer p { font-size: 0.82rem; }
.site-footer a { font-size: 0.82rem; color: var(--text-tertiary); }
.site-footer a:hover { color: var(--brand-teal) !important; }
```

- [ ] **Step 8: 搜索栏 + 文件上传 + 回到顶部 + 滚动条 + 动画**

```css
/* ---- 搜索栏 ---- */
.search-bar {
  max-width: 360px;
}
.search-bar .form-control {
  border-radius: 20px;
  padding-left: 36px;
  background: var(--bg-subtle);
  border-color: transparent;
  font-size: 0.82rem;
}
.search-bar .form-control:focus {
  background: var(--bg-card);
  border-color: var(--brand-teal);
}
.search-bar .search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  z-index: 5;
}

/* ---- 文件上传区域 ---- */
.upload-area {
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-lg);
  padding: 40px 20px;
  text-align: center;
  transition: all var(--transition-normal);
  cursor: pointer;
  background: var(--bg-subtle);
}
.upload-area:hover, .upload-area.dragover {
  border-color: var(--brand-teal);
  background: #F0FDFA;
}
.upload-area .upload-icon {
  font-size: 3rem;
  color: var(--text-muted);
  margin-bottom: var(--space-4);
}
.upload-area:hover .upload-icon { color: var(--brand-teal); }

/* ---- 回到顶部 ---- */
.scroll-top {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 40px;
  height: 40px;
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 1040;
  opacity: 0.8;
  transition: opacity var(--transition-fast), transform var(--transition-fast);
  border-radius: 50% !important;
  padding: 0 !important;
}
.scroll-top:hover { opacity: 1; transform: translateY(-2px); }

/* ---- 滚动条 ---- */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #F1F1F1; }
::-webkit-scrollbar-thumb { background: #C1C1C1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #A1A1A1; }

/* ---- 动画 ---- */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes dropdownFadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ---- 响应式 ---- */
@media (max-width: 992px) {
  .stat-card .stat-value { font-size: 1.3rem; }
  .stat-card .stat-icon { width: 36px; height: 36px; font-size: 1rem; }
}
@media (max-width: 768px) {
  .navbar-brand { font-size: 0.88rem; }
  .card { border-radius: var(--radius-md); }
  .stat-card .stat-value { font-size: 1.2rem; }
  .page-header h4 { font-size: 1.1rem; }
  .table thead th { font-size: 0.65rem; padding: 8px 12px; }
  .table tbody td { padding: 8px 12px; font-size: 0.8rem; }
  .scroll-top { bottom: 20px; right: 20px; width: 36px; height: 36px; }
}
@media (max-width: 576px) {
  .container { padding-left: 12px; padding-right: 12px; }
  .stat-card .stat-value { font-size: 1.1rem; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
  }
}

/* ---- 打印 ---- */
@media print {
  .navbar, .site-footer, .scroll-top, .btn, .message-container { display: none !important; }
  body { background: #fff; }
  .card { box-shadow: none; border: 1px solid #ddd; }
  main { padding: 0 !important; }
}
```

- [ ] **Step 9: 验证 CSS 无错误**

Run: `cd /workspace/training_system && python manage.py check`
Expected: System check identified no issues (0 silenced)

- [ ] **Step 10: 提交**

```bash
git add static/css/style.css
git commit -m "feat(ui): rebuild global CSS with Fortune 500 design system

- Establish brand color system (navy + teal)
- Add Inter + Noto Sans SC typography
- Redesign navigation, cards, tables, buttons, forms
- 8px spacing system, refined shadows and animations"
```

---

### 任务 2: 重写导航栏（base.html）

**Files:**
- Modify: `templates/base.html`

- [ ] **Step 1: 更新 head 部分，加入 Google Fonts**

```html
{% load static %}
{% load widget_tweaks %}
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{{ SYSTEM_NAME }} - 药物警戒在线培训、考试测评与培训计划管理平台">
    <title>{% block title %}{{ SYSTEM_NAME }}{% endblock %}</title>

    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <!-- 自定义样式 -->
    <link href="{% static 'css/style.css' %}" rel="stylesheet">

    {% block extra_css %}{% endblock %}
</head>
```

- [ ] **Step 2: 重写导航栏 HTML**

```html
<body>
    <!-- 导航栏 -->
    <nav class="navbar navbar-expand-lg navbar-dark sticky-top">
        <div class="container">
            <a class="navbar-brand" href="{% url 'users:dashboard' %}">
                <span class="brand-logo">PV</span>
                <span class="brand-text">{{ SYSTEM_SHORT_NAME }}</span>
            </a>

            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
                    aria-controls="navbarNav" aria-expanded="false" aria-label="切换导航">
                <span class="navbar-toggler-icon"></span>
            </button>

            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    {% if user.is_authenticated and user.is_staff %}
                    <!-- 管理员：管理中心 -->
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle {% if request.resolver_match.url_name == 'admin_dashboard' %}active{% endif %}"
                           href="#" role="button" data-bs-toggle="dropdown">
                            <i class="bi bi-gear-fill me-1"></i>管理中心
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{% url 'courses:admin_dashboard' %}"><i class="bi bi-house-gear me-2"></i>管理首页</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><h6 class="dropdown-header">基础配置</h6></li>
                            <li><a class="dropdown-item" href="{% url 'courses:admin_category_list' %}"><i class="bi bi-tags me-2"></i>课程分类管理</a></li>
                            <li><a class="dropdown-item" href="/admin/users/department/"><i class="bi bi-diagram-3 me-2"></i>部门管理</a></li>
                            <li><a class="dropdown-item" href="{% url 'config:settings' %}"><i class="bi bi-sliders me-2"></i>系统参数</a></li>
                            <li><a class="dropdown-item" href="{% url 'llm:providers' %}"><i class="bi bi-robot me-2"></i>大模型配置</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><h6 class="dropdown-header">培训管理</h6></li>
                            <li><a class="dropdown-item" href="{% url 'plans:mandatory_overview' %}"><i class="bi bi-clipboard-check me-2"></i>强制培训总览</a></li>
                            <li><a class="dropdown-item" href="{% url 'plans:list' %}"><i class="bi bi-clipboard2-check me-2"></i>培训计划</a></li>
                            <li><a class="dropdown-item" href="{% url 'training_matrix:list' %}"><i class="bi bi-grid-3x3-gap-fill me-2"></i>培训矩阵</a></li>
                            <li><a class="dropdown-item" href="{% url 'courses:review_list' %}"><i class="bi bi-check2-square me-2"></i>审核管理</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><h6 class="dropdown-header">数据管理</h6></li>
                            <li><a class="dropdown-item" href="{% url 'logs:admin_dashboard' %}"><i class="bi bi-bar-chart-line me-2"></i>数据面板</a></li>
                            <li><a class="dropdown-item" href="{% url 'logs:export_exam_scores' %}"><i class="bi bi-file-earmark-excel me-2"></i>导出成绩</a></li>
                            <li><a class="dropdown-item" href="{% url 'logs:export_training_report' %}"><i class="bi bi-file-earmark-bar-graph me-2"></i>导出培训报告</a></li>
                            <li><a class="dropdown-item" href="{% url 'users:user_list' %}"><i class="bi bi-people me-2"></i>用户管理</a></li>
                            <li><a class="dropdown-item" href="{% url 'logs:operation_log' %}"><i class="bi bi-journal-text me-2"></i>操作日志</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/admin/" target="_blank"><i class="bi bi-terminal me-2"></i>Django后台</a></li>
                        </ul>
                    </li>
                    <!-- 管理员：考试中心 -->
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle {% if request.resolver_match.namespace == 'exams' or request.resolver_match.namespace == 'question_bank' %}active{% endif %}"
                           href="#" role="button" data-bs-toggle="dropdown">
                            <i class="bi bi-pencil-square me-1"></i>考试中心
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{% url 'exams:list' %}"><i class="bi bi-list-ul me-2"></i>考试列表</a></li>
                            <li><a class="dropdown-item" href="{% url 'exams:create' %}"><i class="bi bi-plus-circle me-2"></i>创建考试</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{% url 'question_bank:list' %}"><i class="bi bi-database me-2"></i>题库管理</a></li>
                            <li><a class="dropdown-item" href="{% url 'exams:paper_template_list' %}"><i class="bi bi-file-earmark-text me-2"></i>出卷模板</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{% url 'llm:ai_questions' %}"><i class="bi bi-magic me-2"></i>AI自动出题</a></li>
                        </ul>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.resolver_match.namespace == 'courses' %}active{% endif %}"
                           href="{% url 'courses:list' %}">
                            <i class="bi bi-book me-1"></i>课程管理
                        </a>
                    </li>
                    {% else %}
                    <!-- 学员菜单 -->
                    <li class="nav-item">
                        <a class="nav-link {% if request.resolver_match.url_name == 'dashboard' %}active{% endif %}"
                           href="{% url 'users:dashboard' %}">
                            <i class="bi bi-house-door me-1"></i>首页
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.resolver_match.namespace == 'courses' %}active{% endif %}"
                           href="{% url 'courses:list' %}">
                            <i class="bi bi-book me-1"></i>课程中心
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.resolver_match.namespace == 'exams' %}active{% endif %}"
                           href="{% url 'exams:list' %}">
                            <i class="bi bi-pencil-square me-1"></i>在线考试
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.resolver_match.namespace == 'plans' %}active{% endif %}"
                           href="{% url 'plans:my_tasks' %}">
                            <i class="bi bi-list-task me-1"></i>我的培训
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.resolver_match.namespace == 'training_matrix' %}active{% endif %}"
                           href="{% url 'training_matrix:my_matrix' %}">
                            <i class="bi bi-grid-3x3-gap-fill me-1"></i>培训矩阵
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.resolver_match.namespace == 'logs' and request.resolver_match.url_name == 'learning_log' %}active{% endif %}"
                           href="{% url 'logs:learning_log' %}">
                            <i class="bi bi-clock-history me-1"></i>学习记录
                        </a>
                    </li>
                    {% endif %}
                    {% if user.is_authenticated and not user.is_staff %}
                    <li class="nav-item">
                        <a class="nav-link {% if request.resolver_match.namespace == 'certificates' %}active{% endif %}"
                           href="{% url 'certificates:list' %}">
                            <i class="bi bi-award me-1"></i>我的证书
                        </a>
                    </li>
                    {% endif %}
                </ul>

                <!-- 右侧用户信息 -->
                <ul class="navbar-nav">
                    {% if user.is_authenticated %}
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle user-dropdown-toggle" href="#"
                           id="userDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                            <span class="user-avatar">{{ user.get_full_name|default:user.username|first }}</span>
                            <span class="d-none d-md-inline">{{ user.get_full_name|default:user.username }}</span>
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                            <li class="px-3 py-2">
                                <small class="text-muted" style="font-size:0.7rem;">当前登录</small>
                                <div class="fw-semibold" style="font-size:0.85rem;">{{ user.username }}</div>
                                {% if user.is_staff %}
                                <span class="badge" style="background:#FEF2F2;color:#DC2626;font-size:0.65rem;margin-top:4px;">管理员</span>
                                {% endif %}
                            </li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{% url 'users:profile' %}"><i class="bi bi-person me-2"></i>个人资料</a></li>
                            <li><a class="dropdown-item" href="{% url 'users:password_reset' %}"><i class="bi bi-key me-2"></i>修改密码</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="{% url 'users:logout' %}"><i class="bi bi-box-arrow-right me-2"></i>退出登录</a></li>
                        </ul>
                    </li>
                    {% else %}
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'users:login' %}">
                            <i class="bi bi-box-arrow-in-right me-1"></i>登录
                        </a>
                    </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>
```

- [ ] **Step 3: 更新消息提示区域**

```html
    <!-- 消息提示 -->
    {% if messages %}
    <div class="container mt-3 message-container">
        {% for message in messages %}
        <div class="alert alert-{{ message.tags }} alert-dismissible fade show d-flex align-items-center" role="alert">
            {% if message.tags == 'success' %}
                <i class="bi bi-check-circle-fill me-2"></i>
            {% elif message.tags == 'error' %}
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
            {% elif message.tags == 'warning' %}
                <i class="bi bi-exclamation-circle-fill me-2"></i>
            {% elif message.tags == 'info' %}
                <i class="bi bi-info-circle-fill me-2"></i>
            {% endif %}
            <div class="flex-grow-1">{{ message }}</div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="关闭"></button>
        </div>
        {% endfor %}
    </div>
    {% endif %}
```

- [ ] **Step 4: 更新页脚**

```html
    <!-- 页脚 -->
    <footer class="site-footer mt-auto">
        <div class="container">
            <div class="row align-items-center py-4">
                <div class="col-md-6 text-center text-md-start">
                    <p class="mb-1">
                        <i class="bi bi-mortarboard-fill me-1" style="color:var(--brand-teal);"></i>
                        <strong>{{ SYSTEM_NAME }}</strong>
                    </p>
                    <p class="mb-0 text-muted small">&copy; {% now "Y" %} {{ SYSTEM_NAME }}. All rights reserved.</p>
                </div>
                <div class="col-md-6 text-center text-md-end mt-2 mt-md-0">
                    <a href="{% url 'users:dashboard' %}" class="text-decoration-none me-3">首页</a>
                    <a href="{% url 'courses:list' %}" class="text-decoration-none me-3">课程中心</a>
                    <a href="{% url 'exams:list' %}" class="text-decoration-none me-3">考试中心</a>
                    <a href="{% url 'logs:learning_log' %}" class="text-decoration-none">学习记录</a>
                </div>
            </div>
        </div>
    </footer>
```

- [ ] **Step 5: 更新底部脚本**

```html
    <!-- 回到顶部 -->
    <button class="scroll-top btn btn-primary shadow" title="回到顶部" aria-label="回到顶部">
        <i class="bi bi-chevron-up"></i>
    </button>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- 自定义JS -->
    <script src="{% static 'js/main.js' %}"></script>

    {% block extra_js %}{% endblock %}
</body>
</html>
```

- [ ] **Step 6: 验证模板无语法错误**

Run: `cd /workspace/training_system && python manage.py check --deploy 2>&1 | head -5`
Expected: 无模板语法错误

- [ ] **Step 7: 提交**

```bash
git add templates/base.html
git commit -m "feat(ui): redesign navigation bar and footer

- Dark navy brand navigation with PV logo
- User avatar with gradient background
- Restructured dropdown menus with icons
- Refined footer with brand color accent"
```

---

### 任务 3: 重写登录页面

**Files:**
- Modify: `templates/registration/login.html`

- [ ] **Step 1: 重写登录页面样式和结构**

```html
{% extends "base.html" %}
{% load widget_tweaks %}

{% block title %}用户登录 - {{ SYSTEM_NAME }}{% endblock %}

{% block extra_css %}
<style>
    .login-page {
        min-height: calc(100vh - 56px);
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #0A1628 0%, #132347 50%, #1A3A6B 100%);
        margin: calc(-1 * var(--space-4)) calc(-1 * 3rem) 0;
        padding: 2rem;
        position: relative;
        overflow: hidden;
    }
    .login-page::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 600px;
        height: 600px;
        background: radial-gradient(circle, rgba(13,148,136,0.08) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    .login-card {
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(0,0,0,0.4);
        max-width: 420px;
        width: 100%;
        background: #fff;
        position: relative;
        z-index: 1;
    }
    .login-card .card-header {
        background: linear-gradient(135deg, #0A1628 0%, #132347 100%);
        color: #fff;
        text-align: center;
        padding: 2rem 1.5rem 1.5rem;
        border-bottom: none;
    }
    .login-card .card-header .login-logo {
        width: 56px;
        height: 56px;
        background: linear-gradient(135deg, #0D9488, #5EE4D0);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem;
        font-size: 1.5rem;
        font-weight: 700;
        color: #fff;
    }
    .login-card .card-header h3 {
        margin-bottom: 0.25rem;
        font-weight: 700;
        font-size: 1.15rem;
    }
    .login-card .card-header p {
        margin-bottom: 0;
        opacity: 0.6;
        font-size: 0.85rem;
    }
    .login-card .card-body {
        padding: 2rem 1.5rem;
    }
    .login-card .form-label {
        font-weight: 500;
        color: var(--text-primary);
        font-size: 0.85rem;
        margin-bottom: 6px;
    }
    .login-card .form-control {
        padding: 10px 12px;
        border-radius: 8px;
        border: 1.5px solid var(--border-color);
        font-size: 0.875rem;
        transition: all 0.2s ease;
    }
    .login-card .form-control:focus {
        border-color: var(--brand-teal);
        box-shadow: 0 0 0 3px rgba(13,148,136,0.12);
    }
    .login-card .input-group-text {
        border-radius: 8px 0 0 8px;
        border: 1.5px solid var(--border-color);
        border-right: none;
        background: var(--bg-subtle);
        color: var(--text-tertiary);
    }
    .login-card .input-group .form-control {
        border-radius: 0 8px 8px 0;
    }
    .login-card .btn-login {
        padding: 10px;
        font-size: 0.95rem;
        font-weight: 600;
        border-radius: 8px;
        letter-spacing: 1px;
        background: var(--brand-teal);
        border-color: var(--brand-teal);
        transition: all 0.2s ease;
    }
    .login-card .btn-login:hover {
        background: #0F766E;
        border-color: #0F766E;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(13,148,136,0.3);
    }
    .login-error {
        border-radius: 8px;
        font-size: 0.85rem;
    }
    .login-footer {
        text-align: center;
        padding: 0 1.5rem 1.5rem;
    }
    .login-footer a {
        color: var(--brand-teal);
        text-decoration: none;
        font-size: 0.85rem;
    }
    .login-footer a:hover {
        text-decoration: underline;
    }
    @media (max-width: 576px) {
        .login-page { margin: calc(-1 * var(--space-4)) calc(-1rem) 0; padding: 1rem; }
        .login-card .card-header { padding: 1.5rem 1rem 1rem; }
        .login-card .card-body { padding: 1.5rem 1rem; }
    }
</style>
{% endblock %}

{% block content %}
<div class="login-page">
    <div class="login-card">
        <div class="card-header">
            <div class="login-logo">PV</div>
            <h3>{{ SYSTEM_NAME }}</h3>
            <p>请登录您的账号以继续</p>
        </div>

        <div class="card-body">
            <form method="post" id="loginForm" novalidate>
                {% csrf_token %}

                {% if form.errors %}
                <div class="alert alert-danger login-error d-flex align-items-center mb-3" role="alert">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>
                    <div>
                        {% if form.non_field_errors %}
                            {% for error in form.non_field_errors %}
                                <div>{{ error }}</div>
                            {% endfor %}
                        {% elif form.errors %}
                            <div>用户名或密码错误，请重新输入。</div>
                        {% endif %}
                    </div>
                </div>
                {% endif %}

                {% if next and not form.errors %}
                <div class="alert alert-info login-error d-flex align-items-center mb-3" role="alert" style="border-left-color:var(--brand-teal);">
                    <i class="bi bi-info-circle-fill me-2"></i>
                    <div>请先登录以访问该页面。</div>
                </div>
                {% endif %}

                <div class="mb-3">
                    <label for="id_username" class="form-label">
                        <i class="bi bi-person me-1"></i>用户名
                    </label>
                    <div class="input-group">
                        <span class="input-group-text"><i class="bi bi-person-fill"></i></span>
                        {{ form.username|attr:"class:form-control"|attr:"placeholder:请输入用户名"|attr:"autocomplete:username"|attr:"required" }}
                    </div>
                </div>

                <div class="mb-4">
                    <label for="id_password" class="form-label">
                        <i class="bi bi-lock me-1"></i>密码
                    </label>
                    <div class="input-group">
                        <span class="input-group-text"><i class="bi bi-lock-fill"></i></span>
                        {{ form.password|attr:"class:form-control"|attr:"placeholder:请输入密码"|attr:"autocomplete:current-password"|attr:"required" }}
                        <button class="btn btn-outline-secondary" type="button" id="togglePassword" title="显示/隐藏密码">
                            <i class="bi bi-eye"></i>
                        </button>
                    </div>
                </div>

                <button type="submit" class="btn btn-primary btn-login w-100">
                    <i class="bi bi-box-arrow-in-right me-1"></i>登 录
                </button>
            </form>
        </div>

        <div class="login-footer">
            <a href="{% url 'users:password_reset' %}">
                <i class="bi bi-key me-1"></i>忘记密码？
            </a>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    var toggleBtn = document.getElementById('togglePassword');
    var passwordInput = document.getElementById('id_password');
    if (toggleBtn && passwordInput) {
        toggleBtn.addEventListener('click', function() {
            var type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            var icon = this.querySelector('i');
            icon.classList.toggle('bi-eye');
            icon.classList.toggle('bi-eye-slash');
        });
    }
    var usernameInput = document.getElementById('id_username');
    if (usernameInput) usernameInput.focus();
});
</script>
{% endblock %}
```

- [ ] **Step 2: 提交**

```bash
git add templates/registration/login.html
git commit -m "feat(ui): redesign login page

- Dark navy gradient background with brand ambiance
- PV logo badge in brand teal gradient
- Refined form controls with teal focus state
- Professional card design with subtle shadow"
```

---

### 任务 4: 重写学员仪表盘

**Files:**
- Modify: `templates/users/dashboard.html`

- [ ] **Step 1: 重写仪表盘模板内容**

```html
{% extends "base.html" %}

{% block title %}控制台 - {{ SYSTEM_NAME }}{% endblock %}

{% block content %}
<!-- 欢迎信息 -->
<div class="row mb-4">
    <div class="col-12">
        <div class="page-header border-0 mb-0 p-0">
            <div class="d-flex flex-column flex-md-row justify-content-md-between align-items-md-start">
                <div>
                    <h4 class="mb-1">
                        <span style="color:var(--brand-teal);">欢迎回来，</span>{{ user.get_full_name|default:user.username }}
                    </h4>
                    <p class="text-muted mb-0">
                        <i class="bi bi-calendar3 me-1"></i>今天是 {% now "Y年m月d日" %}，{% now "l" %}
                    </p>
                </div>
                <div class="mt-2 mt-md-0">
                    <a href="{% url 'courses:list' %}" class="btn btn-primary btn-sm me-1">
                        <i class="bi bi-book me-1"></i>浏览课程
                    </a>
                    <a href="{% url 'plans:my_tasks' %}" class="btn btn-outline-primary btn-sm">
                        <i class="bi bi-list-task me-1"></i>我的任务
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- 统计卡片 -->
<div class="row g-3 mb-4">
    <div class="col-6 col-lg">
        <div class="stat-card">
            <div class="stat-icon blue"><i class="bi bi-book"></i></div>
            <div class="stat-value">{{ pending_course_count }}</div>
            <div class="stat-label">待完成课程</div>
            <div class="stat-trend">门课程等待学习</div>
        </div>
    </div>
    <div class="col-6 col-lg">
        <div class="stat-card bg-primary">
            <div class="stat-icon"><i class="bi bi-check-circle"></i></div>
            <div class="stat-value">{{ completed_course_count }}</div>
            <div class="stat-label">已完成课程</div>
            <div class="stat-trend" style="color:rgba(255,255,255,0.6);">门课程已结业</div>
        </div>
    </div>
    <div class="col-6 col-lg">
        <div class="stat-card">
            <div class="stat-icon amber"><i class="bi bi-pencil-square"></i></div>
            <div class="stat-value">{{ pending_exam_count }}</div>
            <div class="stat-label">待考试</div>
            <div class="stat-trend" style="color:var(--color-amber);">场考试待参加</div>
        </div>
    </div>
    <div class="col-6 col-lg">
        <div class="stat-card">
            <div class="stat-icon teal"><i class="bi bi-award"></i></div>
            <div class="stat-value">{{ completed_exam_count }}</div>
            <div class="stat-label">已完成考试</div>
            <div class="stat-trend" style="color:var(--brand-teal);">场考试已完成</div>
        </div>
    </div>
    <div class="col-6 col-lg">
        <div class="stat-card">
            <div class="stat-icon slate"><i class="bi bi-clock-history"></i></div>
            <div class="stat-value">{{ total_learning_hours }}</div>
            <div class="stat-label">累计学习时长</div>
            <div class="stat-trend" style="color:#475569;">小时</div>
        </div>
    </div>
</div>

<!-- 快捷操作 -->
<div class="row mb-4">
    <div class="col-12">
        <div class="card">
            <div class="card-body">
                <h6 class="text-muted mb-3" style="font-size:0.78rem;">
                    <i class="bi bi-lightning me-1" style="color:var(--brand-teal);"></i>快捷操作
                </h6>
                <div class="row g-3">
                    <div class="col-6 col-sm-4 col-md-3 col-lg-2">
                        <a href="{% url 'courses:list' %}" class="quick-action">
                            <div class="quick-action-icon" style="color:var(--color-blue);background:var(--color-blue-bg);"><i class="bi bi-book"></i></div>
                            <span class="quick-action-label">课程中心</span>
                        </a>
                    </div>
                    <div class="col-6 col-sm-4 col-md-3 col-lg-2">
                        <a href="{% url 'exams:list' %}" class="quick-action">
                            <div class="quick-action-icon" style="color:var(--color-green);background:var(--color-green-bg);"><i class="bi bi-pencil-square"></i></div>
                            <span class="quick-action-label">在线考试</span>
                        </a>
                    </div>
                    <div class="col-6 col-sm-4 col-md-3 col-lg-2">
                        <a href="{% url 'plans:my_tasks' %}" class="quick-action">
                            <div class="quick-action-icon" style="color:var(--color-amber);background:var(--color-amber-bg);"><i class="bi bi-list-task"></i></div>
                            <span class="quick-action-label">我的任务</span>
                        </a>
                    </div>
                    <div class="col-6 col-sm-4 col-md-3 col-lg-2">
                        <a href="{% url 'plans:list' %}" class="quick-action">
                            <div class="quick-action-icon" style="color:var(--brand-teal);background:#F0FDFA;"><i class="bi bi-clipboard2-check"></i></div>
                            <span class="quick-action-label">培训计划</span>
                        </a>
                    </div>
                    <div class="col-6 col-sm-4 col-md-3 col-lg-2">
                        <a href="{% url 'logs:learning_log' %}" class="quick-action">
                            <div class="quick-action-icon" style="color:#475569;background:#F1F5F9;"><i class="bi bi-clock-history"></i></div>
                            <span class="quick-action-label">学习记录</span>
                        </a>
                    </div>
                    <div class="col-6 col-sm-4 col-md-3 col-lg-2">
                        <a href="{% url 'users:profile' %}" class="quick-action">
                            <div class="quick-action-icon" style="color:var(--color-purple);background:var(--color-purple-bg);"><i class="bi bi-person"></i></div>
                            <span class="quick-action-label">个人资料</span>
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- 最近学习记录 & 待完成任务 -->
<div class="row g-3">
    <div class="col-lg-8">
        <div class="card h-100">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                    <i class="bi bi-clock-history me-1" style="color:var(--color-blue);"></i>最近学习记录
                </h5>
                {% if recent_logs %}
                <a href="{% url 'logs:learning_log' %}" class="btn btn-sm btn-outline-primary">
                    查看全部 <i class="bi bi-arrow-right ms-1"></i>
                </a>
                {% endif %}
            </div>
            <div class="card-body">
                {% if recent_logs %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr><th>操作类型</th><th>课程/考试</th><th>学习时长</th><th>时间</th></tr>
                        </thead>
                        <tbody>
                            {% for log in recent_logs %}
                            <tr>
                                <td>
                                    {% if log.action == 'view' %}
                                        <span class="badge" style="background:var(--color-blue-bg);color:var(--color-blue);">
                                            <i class="bi bi-eye me-1"></i>{{ log.get_action_display }}
                                        </span>
                                    {% elif log.action == 'study' %}
                                        <span class="badge" style="background:var(--color-green-bg);color:var(--color-green);">
                                            <i class="bi bi-book me-1"></i>{{ log.get_action_display }}
                                        </span>
                                    {% elif log.action == 'exam' %}
                                        <span class="badge" style="background:var(--color-amber-bg);color:var(--color-amber);">
                                            <i class="bi bi-pencil me-1"></i>{{ log.get_action_display }}
                                        </span>
                                    {% elif log.action == 'complete' %}
                                        <span class="badge" style="background:var(--color-green-bg);color:var(--color-green);">
                                            <i class="bi bi-check me-1"></i>{{ log.get_action_display }}
                                        </span>
                                    {% else %}
                                        <span class="badge" style="background:#F1F5F9;color:#475569;">{{ log.get_action_display }}</span>
                                    {% endif %}
                                </td>
                                <td>
                                    {% if log.course %}
                                        <a href="{% url 'courses:detail' log.course.pk %}" class="text-decoration-none fw-medium" style="color:var(--text-primary);">
                                            {{ log.course.title }}
                                        </a>
                                    {% elif log.exam %}
                                        <a href="{% url 'exams:detail' log.exam.pk %}" class="text-decoration-none fw-medium" style="color:var(--text-primary);">
                                            {{ log.exam.title }}
                                        </a>
                                    {% else %}
                                        <span class="text-muted">--</span>
                                    {% endif %}
                                </td>
                                <td>
                                    {% if log.duration %}
                                        {{ log.duration|floatformat:0 }}秒
                                    {% else %}
                                        <span class="text-muted">--</span>
                                    {% endif %}
                                </td>
                                <td><small class="text-muted">{{ log.created_at|date:"Y-m-d H:i" }}</small></td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="empty-state">
                    <div class="empty-icon"><i class="bi bi-journal-bookmark"></i></div>
                    <h5>暂无学习记录</h5>
                    <p>开始您的第一门课程，学习记录将在这里展示。</p>
                    <a href="{% url 'courses:list' %}" class="btn btn-primary btn-sm mt-2">
                        <i class="bi bi-book me-1"></i>浏览课程
                    </a>
                </div>
                {% endif %}
            </div>
        </div>
    </div>

    <div class="col-lg-4">
        <div class="card h-100">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                    <i class="bi bi-list-check me-1" style="color:var(--color-amber);"></i>待完成任务
                </h5>
                {% if pending_tasks %}
                <a href="{% url 'plans:my_tasks' %}" class="btn btn-sm btn-outline-primary">
                    查看全部 <i class="bi bi-arrow-right ms-1"></i>
                </a>
                {% endif %}
            </div>
            <div class="card-body p-0">
                {% if pending_tasks %}
                <div class="list-group list-group-flush">
                    {% for assignment in pending_tasks %}
                    <div class="task-item">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1 me-2">
                                <div class="task-title">
                                    <a href="{% url 'plans:detail' assignment.task.plan.pk %}" class="text-decoration-none">
                                        {{ assignment.task.title }}
                                    </a>
                                </div>
                                <div class="task-meta">
                                    <i class="bi bi-collection me-1"></i>{{ assignment.task.plan.title }}
                                </div>
                                {% if assignment.task.deadline %}
                                <div class="task-deadline {% if assignment.task.deadline < today %}overdue{% endif %}">
                                    <i class="bi bi-calendar-event me-1"></i>
                                    截止：{{ assignment.task.deadline|date:"Y-m-d" }}
                                </div>
                                {% endif %}
                            </div>
                            <span class="badge flex-shrink-0" style="{% if assignment.status == 'pending' %}background:var(--color-amber-bg);color:var(--color-amber){% elif assignment.status == 'in_progress' %}background:var(--color-blue-bg);color:var(--color-blue){% elif assignment.status == 'completed' %}background:var(--color-green-bg);color:var(--color-green){% else %}background:#F1F5F9;color:#475569{% endif %}">
                                {{ assignment.get_status_display }}
                            </span>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <div class="empty-state">
                    <div class="empty-icon"><i class="bi bi-emoji-smile"></i></div>
                    <h5>暂无待完成任务</h5>
                    <p>所有任务已完成，继续加油！</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 2: 验证仪表盘渲染正常**

Run: `cd /workspace/training_system && python manage.py check`
Expected: System check identified no issues (0 silenced)

- [ ] **Step 3: 提交**

```bash
git add templates/users/dashboard.html
git commit -m "feat(ui): redesign student dashboard

- Redesigned stat cards with colored icons
- Updated quick actions with brand color accents
- Refined learning records table and task list
- Empty state improvements"
```

---

### 任务 5: 批量更新 P1 模板样式

**Files:**
- Modify: `templates/courses/course_list.html`
- Modify: `templates/exams/exam_list.html`
- Modify: `templates/plans/my_tasks.html`
- 以及其他 P1 优先级模板

- [ ] **Step 1: 批量替换所有模板中的 Bootstrap 默认类引用**

所有模板中需要替换的样式类：
- 将 `btn-primary` 按钮中的 `bg-primary` 徽章 → 适配新徽章样式
- 将 `class="badge bg-*"` → `class="badge"` 配合内联 style 或新 CSS 变量

- [ ] **Step 2: 更新课程列表页**

在 `templates/courses/course_list.html` 中，找到所有徽章标签并替换：
```html
<!-- 替换前 -->
<span class="badge bg-primary">...</span>
<span class="badge bg-success">...</span>
<span class="badge bg-warning text-dark">...</span>

<!-- 替换后 -->
<span class="badge" style="background:var(--color-blue-bg);color:var(--color-blue);">...</span>
<span class="badge" style="background:var(--color-green-bg);color:var(--color-green);">...</span>
<span class="badge" style="background:var(--color-amber-bg);color:var(--color-amber);">...</span>
```

- [ ] **Step 3: 更新考试列表页**

同上，查找 `templates/exams/exam_list.html` 中的徽章标签并替换。

- [ ] **Step 4: 更新任务列表页**

同上，查找 `templates/plans/my_tasks.html` 中的徽章标签并替换。

- [ ] **Step 5: 提交**

```bash
git add templates/courses/course_list.html templates/exams/exam_list.html templates/plans/my_tasks.html
git commit -m "feat(ui): update P1 template badges to brand colors

- Replace Bootstrap default badge colors with brand palette
- Consistent color coding across course, exam, and task pages"
```

---

### 任务 6: 批量更新剩余 P2 模板

**Files:**
- Modify: 所有剩余模板中的徽章、按钮、卡片样式

- [ ] **Step 1: 全局搜索并替换徽章样式**

```bash
cd /workspace/training_system
grep -rn 'badge bg-' templates/ --include="*.html" | grep -v '.pyc'
```

对每个匹配的文件，使用 `sed` 或手动替换：
- `badge bg-primary` → `badge` with `style="background:var(--color-blue-bg);color:var(--color-blue);"`
- `badge bg-success` → `badge` with `style="background:var(--color-green-bg);color:var(--color-green);"`
- `badge bg-warning text-dark` → `badge` with `style="background:var(--color-amber-bg);color:var(--color-amber);"`
- `badge bg-danger` → `badge` with `style="background:var(--color-red-bg);color:var(--color-red);"`
- `badge bg-info` → `badge` with `style="background:#F0FDFA;color:var(--brand-teal);"`
- `badge bg-secondary` → `badge` with `style="background:#F1F5F9;color:#475569;"`

- [ ] **Step 2: 提交**

```bash
git add templates/
git commit -m "feat(ui): update P2 template badges to brand colors

- Batch replace all Bootstrap badge classes with brand palette
- Consistent color system across all 80+ templates"
```

---

### 任务 7: 最终验证和预览

- [ ] **Step 1: 运行 Django 检查**

```bash
cd /workspace/training_system && python manage.py check
```
Expected: System check identified no issues (0 silenced)

- [ ] **Step 2: 启动开发服务器并手动验证**

```bash
cd /workspace/training_system && python manage.py runserver 0.0.0.0:8000
```

- [ ] **Step 3: 验证关键页面**
  - 登录页：http://localhost:8000/login/
  - 仪表盘：http://localhost:8000/dashboard/
  - 课程列表：http://localhost:8000/courses/
  - 考试列表：http://localhost:8000/exams/

- [ ] **Step 4: 提交最终版本**

```bash
git add -A
git commit -m "feat(ui): complete Fortune 500 design system implementation

- Full brand color system with navy + teal palette
- Inter + Noto Sans SC typography
- Redesigned navigation, login, dashboard
- Unified card, table, button, form styles
- Batch badge update across all templates"
```

---

## 自审清单

- [x] 所有步骤包含实际代码，无"TBD"或"TODO"
- [x] CSS 变量名在 style.css 和模板中一致
- [x] 文件路径精确
- [x] 覆盖设计文档中所有组件规范
- [x] 包含验证步骤
- [x] 每个任务都有独立提交信息