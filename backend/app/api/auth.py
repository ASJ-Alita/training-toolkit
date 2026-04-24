"""
认证 API — 登录 / 注册 / 修改密码 / 当前用户
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.models.auth_models import User
from app.models.auth_schemas import (
    LoginRequest,
    RegisterRequest,
    ChangePasswordRequest,
    TokenResponse,
    UserInfo,
)

router = APIRouter(prefix="/api/auth", tags=["认证"])
security_scheme = HTTPBearer()

# ---------- 管理员默认账号 ----------
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"


def _get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """依赖注入：从 JWT 获取当前用户，所有受保护路由共用"""
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效或过期的 token")
    user = db.query(User).filter(User.id == payload["sub"], User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")
    return user


def _ensure_admin_user(db: Session):
    """首次启动时自动创建默认管理员"""
    exists = db.query(User).filter(User.username == DEFAULT_ADMIN_USERNAME).first()
    if not exists:
        admin = User(
            id=str(uuid.uuid4()),
            username=DEFAULT_ADMIN_USERNAME,
            hashed_password=hash_password(DEFAULT_ADMIN_PASSWORD),
            display_name="系统管理员",
            role="admin",
        )
        db.add(admin)
        db.commit()


# ---------- 端点 ----------

@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """用户登录，返回 JWT"""
    _ensure_admin_user(db)
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已禁用")
    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(
        access_token=token,
        user=UserInfo(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            role=user.role,
            student_id=user.student_id or "",
        ),
    )


@router.post("/register", response_model=UserInfo)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """
    注册新用户。
    - admin 角色只能由已有 admin 创建
    - student 角色开放注册
    """
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")
    user = User(
        id=str(uuid.uuid4()),
        username=body.username,
        hashed_password=hash_password(body.password),
        display_name=body.display_name or body.username,
        role=body.role,
        student_id=body.student_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserInfo(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        role=user.role,
        student_id=user.student_id or "",
    )


@router.get("/me", response_model=UserInfo)
def get_me(current_user: User = Depends(_get_current_user)):
    """获取当前登录用户信息"""
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        display_name=current_user.display_name,
        role=current_user.role,
        student_id=current_user.student_id or "",
    )


@router.put("/password")
def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
):
    """修改当前用户密码"""
    if not verify_password(body.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码错误")
    current_user.hashed_password = hash_password(body.new_password)
    db.commit()
    return {"message": "密码修改成功"}


# ---------- 用户管理（仅管理员） ----------

@router.get("/users", response_model=list[UserInfo])
def list_users(
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
):
    """获取所有用户列表（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可访问")
    users = db.query(User).all()
    return [
        UserInfo(id=u.id, username=u.username, display_name=u.display_name, role=u.role, student_id=u.student_id or "")
        for u in users
    ]


@router.put("/users/{user_id}/toggle-active")
def toggle_user_active(
    user_id: str,
    current_user: User = Depends(_get_current_user),
    db: Session = Depends(get_db),
):
    """启用/禁用用户（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可访问")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    user.is_active = not user.is_active
    db.commit()
    return {"message": f"用户已{'启用' if user.is_active else '禁用'}"}
