"""
Pydantic 请求/响应 Schema
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


# ==================== Student ====================

class StudentCreate(BaseModel):
    name: str
    dept: str = ""
    position: str = ""
    email: str = ""

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    dept: Optional[str] = None
    position: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None

class StudentOut(BaseModel):
    id: str
    name: str
    dept: str = ""
    position: str = ""
    email: str = ""
    status: str = "active"
    created_at: str = ""

    class Config:
        from_attributes = True


# ==================== Training ====================

class TrainingCreate(BaseModel):
    name: str
    topic: str = ""
    start_date: str = ""
    end_date: str = ""
    max_score: float = 100

class TrainingUpdate(BaseModel):
    name: Optional[str] = None
    topic: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    max_score: Optional[float] = None
    status: Optional[str] = None

class TrainingOut(BaseModel):
    id: str
    name: str
    topic: str = ""
    start_date: str = ""
    end_date: str = ""
    max_score: float = 100
    status: str = "active"
    created_at: str = ""

    class Config:
        from_attributes = True


# ==================== Record ====================

class RecordCreate(BaseModel):
    student_id: str
    training_id: str
    type: str  # pre / post / milestone
    score: float
    notes: str = ""

class RecordOut(BaseModel):
    id: str
    student_id: str
    training_id: str
    type: str
    score: float
    notes: str = ""
    date: str = ""
    created_at: str = ""
    student: Optional[StudentOut] = None
    training: Optional[TrainingOut] = None

    class Config:
        from_attributes = True


# ==================== Stats / Dashboard ====================

class DashboardStats(BaseModel):
    active_students: int = 0
    active_trainings: int = 0
    total_records: int = 0
    avg_improvement: float = 0.0

class TrainingStats(BaseModel):
    total_students: int = 0
    pre_avg: float = 0.0
    post_avg: float = 0.0
    improvement: float = 0.0
    improvement_pct: float = 0.0
    qualified_rate: float = 0.0

class StudentProgress(BaseModel):
    training: TrainingOut
    pre_score: float = 0.0
    post_score: float = 0.0
    improvement: float = 0.0
    improvement_pct: float = 0.0
