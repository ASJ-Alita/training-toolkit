"""
学员管理 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4

from app.core.database import get_db
from app.models.models import Student as StudentModel
from app.models.schemas import StudentCreate, StudentUpdate, StudentOut

router = APIRouter(prefix="/api/students", tags=["学员管理"])


@router.get("", response_model=list[StudentOut])
def list_students(db: Session = Depends(get_db)):
    """获取所有学员"""
    return db.query(StudentModel).all()


@router.get("/{student_id}", response_model=StudentOut)
def get_student(student_id: str, db: Session = Depends(get_db)):
    """获取单个学员"""
    student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")
    return student


@router.post("", response_model=StudentOut, status_code=201)
def create_student(data: StudentCreate, db: Session = Depends(get_db)):
    """添加学员"""
    student = StudentModel(id=str(uuid4())[:8], **data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.put("/{student_id}", response_model=StudentOut)
def update_student(student_id: str, data: StudentUpdate, db: Session = Depends(get_db)):
    """更新学员信息"""
    student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(student, k, v)
    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}", status_code=204)
def delete_student(student_id: str, db: Session = Depends(get_db)):
    """删除学员（级联删除相关记录）"""
    student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")
    db.delete(student)
    db.commit()
