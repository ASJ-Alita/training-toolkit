"""
SQLAlchemy ORM 模型 - 扩展
Kirkpatrick 评估 + RAG 知识库
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Evaluation(Base):
    """柯氏四级评估记录"""
    __tablename__ = "evaluations"

    id = Column(String(50), primary_key=True, index=True)
    course_name = Column(String(100), nullable=False, index=True)
    department = Column(String(50), default="")
    train_date = Column(String(10), default="")
    trainee_name = Column(String(50), default="匿名")
    # Level 1: 反应层（JSON 字符串存储各题得分）
    level1_data = Column(Text, default="{}")  # {"L1Q1": 4, "L1Q2": 5, ...}
    level1_avg = Column(Float, default=0)
    # Level 2: 学习层（前/后测得分百分比）
    l2_pre_score = Column(Float, default=0)
    l2_post_score = Column(Float, default=0)
    # Level 3: 行为层（JSON 字符串）
    level3_data = Column(Text, default="{}")  # {"L3Q1": 3, ...}
    level3_avg = Column(Float, default=0)
    # Level 4: 结果层（JSON 字符串，含 ROI 指标）
    level4_data = Column(Text, default="{}")  # {"L4M1": 15.0, ...}
    created_at = Column(String(20), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class Document(Base):
    """已上传文档"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    file_type = Column(String(10), default="")
    chunks_count = Column(Integer, default=0)
    status = Column(String(20), default="processing")  # processing / completed / failed
    created_at = Column(String(20), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class ChatMessage(Base):
    """RAG 问答对话历史"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), nullable=False, index=True)
    role = Column(String(10), nullable=False)  # user / assistant
    content = Column(Text, nullable=False)
    sources = Column(Text, default="[]")  # JSON 数组
    created_at = Column(String(20), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
