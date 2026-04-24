"""
测评记录管理 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from app.core.database import get_db
from app.models.models import Record as RecordModel, Student, Training
from app.models.schemas import RecordCreate, RecordOut

router = APIRouter(prefix="/api/records", tags=["测评记录"])


@router.get("", response_model=list[RecordOut])
def list_records(
    student_id: str = None,
    training_id: str = None,
    db: Session = Depends(get_db),
):
    """获取测评记录（可按学员/培训筛选）"""
    query = db.query(RecordModel)
    if student_id:
        query = query.filter(RecordModel.student_id == student_id)
    if training_id:
        query = query.filter(RecordModel.training_id == training_id)
    return query.all()


@router.post("", response_model=RecordOut, status_code=201)
def create_record(data: RecordCreate, db: Session = Depends(get_db)):
    """添加测评记录"""
    if not db.query(Student).filter(Student.id == data.student_id).first():
        raise HTTPException(status_code=404, detail="学员不存在")
    if not db.query(Training).filter(Training.id == data.training_id).first():
        raise HTTPException(status_code=404, detail="培训计划不存在")

    now = datetime.now()
    record = RecordModel(
        id=str(uuid4())[:8],
        **data.model_dump(),
        date=now.strftime("%Y-%m-%d"),
        created_at=now.strftime("%Y-%m-%d %H:%M"),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: str, db: Session = Depends(get_db)):
    """删除测评记录"""
    record = db.query(RecordModel).filter(RecordModel.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(record)
    db.commit()
