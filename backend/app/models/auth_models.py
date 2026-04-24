"""
认证相关 SQLAlchemy ORM 模型
"""

from sqlalchemy import Column, String, Boolean, DateTime
from datetime import datetime, timezone

from app.core.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(128), nullable=False)
    display_name = Column(String(50), default="")
    role = Column(String(10), nullable=False, default="student")  # admin / student
    student_id = Column(String(8), default="", index=True)  # 学员角色关联的学员 ID
    is_active = Column(Boolean, default=True)
    created_at = Column(
        String(20),
        default=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
    )
