"""
Training Toolkit - FastAPI 主入口
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import engine, Base, get_db
from app.core.security import decode_access_token
from app.models.auth_models import User
from app.api.auth import router as auth_router
from app.api.students import router as students_router
from app.api.trainings import router as trainings_router
from app.api.records import router as records_router
from app.api.dashboard import router as dashboard_router
from app.api.evaluations import router as evaluations_router
from app.api.rag import router as rag_router

# 创建数据库表（含扩展模型）
from app.models.models_ext import Evaluation, Document, ChatMessage  # noqa: F401
from app.models.auth_models import User as _User  # noqa: F401 确保表被创建

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

# 注册路由 — 认证路由无需保护
app.include_router(auth_router)

# ---------- 受保护路由的认证依赖 ----------

_security_scheme = HTTPBearer(auto_error=False)


async def verify_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_security_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    """
    可选认证依赖：有 token 则验证，无 token 返回 None。
    用于允许部分公开端点 + 可选增强。
    """
    if not credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        return None
    user = db.query(User).filter(User.id == payload["sub"], User.is_active.is_(True)).first()
    return user


def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db),
) -> User:
    """强制认证依赖：必须携带有效 token"""
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
    user = db.query(User).filter(User.id == payload["sub"], User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")
    return user


# 注册受保护路由（全部需要认证）
app.include_router(students_router, dependencies=[Depends(require_auth)])
app.include_router(trainings_router, dependencies=[Depends(require_auth)])
app.include_router(records_router, dependencies=[Depends(require_auth)])
app.include_router(dashboard_router, dependencies=[Depends(require_auth)])
app.include_router(evaluations_router, dependencies=[Depends(require_auth)])
app.include_router(rag_router, dependencies=[Depends(require_auth)])


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }
