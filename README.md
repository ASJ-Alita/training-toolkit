<div align="center">

# 🏢 Training Toolkit

> 用 AI 重塑企业培训全流程 — Web 版

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Vue 3](https://img.shields.io/badge/Vue-3-4FC08D?style=flat-square&logo=vue.js)](https://vuejs.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite)](https://sqlite.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)](https://docs.docker.com/)
[![JWT](https://img.shields.io/badge/JWT-Auth-EA4335?style=flat-square)](#)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python)](#)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**企业培训效果追踪系统 Web 版** — FastAPI + Vue 3 + JWT 认证 + Docker 部署

从 tkinter 桌面端迁移到现代化 Web 架构，展示前后端分离、JWT 认证、RESTful API 设计、ORM 数据建模、Docker 容器化等工程能力。

</div>

---

## ✨ 功能特性

### 🔐 认证与权限
- **JWT 登录** — 基于 JSON Web Token 的无状态认证，24h 自动过期
- **角色区分** — 管理员（admin）/ 学员（student）两种角色
- **权限控制** — 学员管理、培训管理等敏感操作仅管理员可访问
- **用户管理** — 注册、登录、修改密码、启用/禁用用户
- **默认管理员** — 首次启动自动创建 `admin / admin123`

### 核心模块
- **📊 仪表盘** — 实时统计：活跃学员数、培训计划数、测评记录数、平均进步率
- **👥 学员管理** — CRUD 操作：添加、编辑、删除学员，搜索过滤（管理员）
- **📚 培训管理** — 管理培训计划：名称、主题、日期、满分（管理员）
- **📝 测评记录** — 记录前测/后测/里程碑成绩，按学员/培训筛选
- **📈 统计分析** — 自动计算进步率、达标率，可视化展示

### 🎓 柯氏四级评估（Kirkpatrick）
- **L1 反应层** — 8 道满意度量表（1-5 分），讲师/内容/组织多维度评分
- **L2 学习层** — 5 道知识测验题，前测/后测对比，自动计算进步率
- **L3 行为层** — 6 道行为追踪量表，30 天后评估知识迁移效果
- **L4 结果层** — ROI 计算、业务指标追踪（效率/错误率/留存率）
- **评估报告** — 自动生成可视化统计报告，含四级对比、AI 分析建议

### 🤖 RAG 知识库问答
- **文档管理** — 上传 PDF/TXT/DOCX，自动提取文本、智能分块、BGE-M3 向量化
- **智能问答** — 基于向量检索 + LLM 的 RAG 架构，回答附带参考来源
- **多模型支持** — 硅基流动 DeepSeek-V3 / OpenAI GPT-4o-mini / 智谱 GLM-4-flash

## 🏗️ 技术架构

```
training-toolkit/
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── main.py           # 应用入口 + 路由注册 + JWT 中间件
│   │   ├── api/              # RESTful API 路由
│   │   │   ├── auth.py       # 认证 API（登录/注册/用户管理）
│   │   │   ├── students.py   # 学员 API
│   │   │   ├── trainings.py  # 培训 API
│   │   │   ├── records.py    # 测评记录 API
│   │   │   ├── dashboard.py  # 仪表盘/统计 API
│   │   │   ├── evaluations.py # 柯氏评估 API
│   │   │   └── rag.py        # RAG 知识库 API
│   │   ├── models/           # 数据模型
│   │   │   ├── models.py      # SQLAlchemy ORM（核心）
│   │   │   ├── models_ext.py  # SQLAlchemy ORM（评估+RAG）
│   │   │   ├── auth_models.py # SQLAlchemy ORM（用户认证）
│   │   │   ├── schemas.py     # Pydantic Schema（核心）
│   │   │   ├── schemas_ext.py # Pydantic Schema（评估+RAG）
│   │   │   └── auth_schemas.py# Pydantic Schema（认证）
│   │   └── core/             # 核心配置
│   │       ├── config.py     # 应用配置（含 JWT 密钥）
│   │       ├── database.py   # 数据库连接
│   │       └── security.py   # JWT + bcrypt 工具
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.py                # 开发启动脚本
├── frontend/                 # Vue 3 前端
│   ├── src/
│   │   ├── views/            # 页面组件（7个模块，含 Login）
│   │   ├── stores/           # Pinia 状态管理（auth）
│   │   ├── api/              # Axios 封装（JWT 拦截器）
│   │   ├── router/           # Vue Router（路由守卫）
│   │   └── style.css         # 全局样式
│   ├── nginx.conf            # Nginx 配置（SPA + 反向代理）
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml        # 一键部署
└── README.md
```

### 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| 后端框架 | FastAPI | 高性能异步 API |
| ORM | SQLAlchemy | 关系型数据库映射 |
| 认证 | JWT + bcrypt | 无状态 Token 认证 |
| 数据校验 | Pydantic v2 | 请求/响应 Schema |
| 数据库 | SQLite | 轻量级文件数据库 |
| 前端框架 | Vue 3 + Pinia | 响应式 UI + 状态管理 |
| 路由 | Vue Router 4 | SPA 路由 + 守卫 |
| HTTP 客户端 | Axios | API 请求（自动携带 JWT） |
| 构建工具 | Vite | 前端构建 |
| 部署 | Docker + Nginx | 容器化一键部署 |

## 🚀 快速开始

### 方式一：Docker 一键部署（推荐）

```bash
# 克隆仓库
git clone https://github.com/ASJ-Alita/training-toolkit.git
cd training-toolkit

# 配置环境变量（可选，默认使用内置密钥）
cp backend/.env.example backend/.env
# 编辑 .env 修改 SECRET_KEY

# 启动
docker compose up -d

# 访问 http://localhost
# 默认账号：admin / admin123
```

### 方式二：本地开发

#### 1. 启动后端

```bash
cd backend
pip install -r requirements.txt
python run.py
```

后端运行在 http://127.0.0.1:8000

- API 文档：http://127.0.0.1:8000/docs

#### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://127.0.0.1:5173，开发模式下自动代理 API 到后端。

#### 3. 快速体验

1. 打开前端页面，使用 `admin / admin123` 登录
2. 进入仪表盘，点击「注入演示数据」
3. 管理员可浏览学员管理、培训管理等全部功能
4. 注册学员账号后可体验受限视图

## 📡 API 概览

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/login` | 用户登录（返回 JWT） |
| POST | `/api/auth/register` | 注册新用户 |
| GET | `/api/auth/me` | 获取当前用户信息 |
| PUT | `/api/auth/password` | 修改密码 |
| GET | `/api/auth/users` | 用户列表（管理员） |
| PUT | `/api/auth/users/{id}/toggle-active` | 启用/禁用用户（管理员） |

### 培训追踪
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/dashboard` | 仪表盘统计 |
| GET/POST | `/api/students` | 学员列表 / 添加学员 |
| PUT/DELETE | `/api/students/{id}` | 更新 / 删除学员 |
| GET/POST | `/api/trainings` | 培训列表 / 添加培训 |
| PUT/DELETE | `/api/trainings/{id}` | 更新 / 删除培训 |
| GET/POST | `/api/records` | 记录列表（可筛选） / 添加记录 |
| DELETE | `/api/records/{id}` | 删除记录 |
| POST | `/api/demo-data` | 注入演示数据 |

### 柯氏评估
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/evaluations/config` | 问卷配置（题目/选项） |
| GET/POST | `/api/evaluations/` | 评估列表 / 创建评估 |
| GET | `/api/evaluations/{id}` | 评估详情 |
| DELETE | `/api/evaluations/{id}` | 删除评估 |
| GET | `/api/evaluations/stats/summary` | 统计报告 |

### RAG 知识库
| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/rag/config` | 获取/更新 API 配置 |
| POST | `/api/rag/upload` | 上传文档 |
| GET | `/api/rag/documents` | 文档列表 |
| POST | `/api/rag/chat` | 智能问答 |
| DELETE | `/api/rag/clear` | 清空知识库 |

## 🔄 迁移说明

本项目从原始桌面应用迁移而来，整合为统一的 Web 平台：

| 原始项目 | 技术栈 | Web 模块 |
|----------|--------|---------|
| [training-tracker](https://github.com/ASJ-Alita/training-tracker) | tkinter + JSON | 学员/培训/记录/仪表盘 |
| [kirkpatrick-eval](https://github.com/ASJ-Alita/kirkpatrick-eval) | tkinter + JSON | 柯氏四级评估 |
| [rag-knowledge-base](https://github.com/ASJ-Alita/rag-knowledge-base) | Streamlit + FAISS | RAG 知识库问答 |

关键改进：
- **JSON 文件 → SQLite**：支持多用户并发
- **tkinter/Streamlit → Vue 3**：统一现代化 Web 界面
- **无认证 → JWT**：管理员/学员角色权限控制
- **单机 → Docker**：一键部署，环境隔离
- **复用业务逻辑**：统计分析、RAG 问答、评估算法完全保留

## 📄 License

MIT
