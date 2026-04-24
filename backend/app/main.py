"""
Training Toolkit - FastAPI 主入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api.students import router as students_router
from app.api.trainings import router as trainings_router
from app.api.records import router as records_router
from app.api.dashboard import router as dashboard_router

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="企业培训效果追踪系统 API - FastAPI + SQLite",
)

# CORS 配置（开发环境允许前端跨域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(students_router)
app.include_router(trainings_router)
app.include_router(records_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }
