"""
SQLAlchemy ORM 模型
从原始 JSON 数据结构迁移到关系型数据库
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class Student(Base):
    """学员"""
    __tablename__ = "students"

    id = Column(String(8), primary_key=True, index=True)
    name = Column(String(50), nullable=False, index=True)
    dept = Column(String(50), default="")
    position = Column(String(50), default="")
    email = Column(String(100), default="")
    status = Column(String(10), default="active")
    created_at = Column(String(10), default=lambda: datetime.now().strftime("%Y-%m-%d"))

    records = relationship("Record", back_populates="student", cascade="all, delete-orphan")


class Training(Base):
    """培训计划"""
    __tablename__ = "trainings"

    id = Column(String(8), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    topic = Column(String(100), default="")
    start_date = Column(String(10), default="")
    end_date = Column(String(10), default="")
    max_score = Column(Float, default=100)
    status = Column(String(10), default="active")
    created_at = Column(String(10), default=lambda: datetime.now().strftime("%Y-%m-%d"))

    records = relationship("Record", back_populates="training", cascade="all, delete-orphan")


class Record(Base):
    """测评记录"""
    __tablename__ = "records"

    id = Column(String(8), primary_key=True, index=True)
    student_id = Column(String(8), ForeignKey("students.id"), nullable=False, index=True)
    training_id = Column(String(8), ForeignKey("trainings.id"), nullable=False, index=True)
    type = Column(String(10), nullable=False)  # pre / post / milestone
    score = Column(Float, nullable=False)
    notes = Column(Text, default="")
    date = Column(String(10), default=lambda: datetime.now().strftime("%Y-%m-%d"))
    created_at = Column(String(20), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))

    student = relationship("Student", back_populates="records")
    training = relationship("Training", back_populates="records")
