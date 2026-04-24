"""
培训计划管理 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4

from app.core.database import get_db
from app.models.models import Training as TrainingModel
from app.models.schemas import TrainingCreate, TrainingUpdate, TrainingOut

router = APIRouter(prefix="/api/trainings", tags=["培训管理"])


@router.get("", response_model=list[TrainingOut])
def list_trainings(db: Session = Depends(get_db)):
    """获取所有培训计划"""
    return db.query(TrainingModel).all()


@router.get("/{training_id}", response_model=TrainingOut)
def get_training(training_id: str, db: Session = Depends(get_db)):
    """获取单个培训计划"""
    training = db.query(TrainingModel).filter(TrainingModel.id == training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="培训计划不存在")
    return training


@router.post("", response_model=TrainingOut, status_code=201)
def create_training(data: TrainingCreate, db: Session = Depends(get_db)):
    """添加培训计划"""
    training = TrainingModel(id=str(uuid4())[:8], **data.model_dump())
    db.add(training)
    db.commit()
    db.refresh(training)
    return training


@router.put("/{training_id}", response_model=TrainingOut)
def update_training(training_id: str, data: TrainingUpdate, db: Session = Depends(get_db)):
    """更新培训计划"""
    training = db.query(TrainingModel).filter(TrainingModel.id == training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="培训计划不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(training, k, v)
    db.commit()
    db.refresh(training)
    return training


@router.delete("/{training_id}", status_code=204)
def delete_training(training_id: str, db: Session = Depends(get_db)):
    """删除培训计划（级联删除相关记录）"""
    training = db.query(TrainingModel).filter(TrainingModel.id == training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="培训计划不存在")
    db.delete(training)
    db.commit()
