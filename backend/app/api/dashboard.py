"""
仪表盘与统计 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
import random

from app.core.database import get_db
from app.models.models import Student, Training, Record
from app.models.schemas import DashboardStats, TrainingStats, StudentProgress, TrainingOut

router = APIRouter(prefix="/api", tags=["仪表盘"])


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(db: Session = Depends(get_db)):
    """仪表盘统计数据"""
    active_students = db.query(Student).filter(Student.status == "active").count()
    active_trainings = db.query(Training).filter(Training.status == "active").count()
    total_records = db.query(Record).count()

    improvements = []
    for t in db.query(Training).all():
        stats = _calc_training_stats(t.id, db)
        if stats and stats.improvement_pct != 0:
            improvements.append(stats.improvement_pct)

    avg_imp = sum(improvements) / len(improvements) if improvements else 0

    return DashboardStats(
        active_students=active_students,
        active_trainings=active_trainings,
        total_records=total_records,
        avg_improvement=round(avg_imp, 1),
    )


@router.get("/trainings/{training_id}/stats", response_model=TrainingStats)
def get_training_stats(training_id: str, db: Session = Depends(get_db)):
    """获取培训统计"""
    stats = _calc_training_stats(training_id, db)
    if not stats:
        raise HTTPException(status_code=404, detail="该培训暂无完整前后测数据")
    return stats


@router.get("/students/{student_id}/progress", response_model=list[StudentProgress])
def get_student_progress(student_id: str, db: Session = Depends(get_db)):
    """获取学员在所有培训中的进步情况"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")

    records = db.query(Record).filter(Record.student_id == student_id).all()

    progress = []
    for t in db.query(Training).all():
        pre = next((r for r in records if r.training_id == t.id and r.type == "pre"), None)
        post = next((r for r in records if r.training_id == t.id and r.type == "post"), None)
        if pre and post:
            improvement = post.score - pre.score
            improvement_pct = (improvement / pre.score * 100) if pre.score > 0 else 0
            progress.append(StudentProgress(
                training=TrainingOut.model_validate(t),
                pre_score=pre.score,
                post_score=post.score,
                improvement=round(improvement, 1),
                improvement_pct=round(improvement_pct, 1),
            ))
    return progress


@router.post("/demo-data", status_code=201)
def seed_demo_data(db: Session = Depends(get_db)):
    """注入演示数据（仅开发环境使用）"""
    if db.query(Student).count() > 0:
        return {"message": "数据库已有数据，跳过注入"}

    demo_students = [
        {"name": "张伟", "dept": "销售部", "position": "销售代表"},
        {"name": "李娜", "dept": "技术部", "position": "Java开发"},
        {"name": "王强", "dept": "市场部", "position": "市场专员"},
        {"name": "陈静", "dept": "人事部", "position": "HR主管"},
        {"name": "刘洋", "dept": "财务部", "position": "会计"},
        {"name": "赵敏", "dept": "销售部", "position": "销售经理"},
    ]

    student_objs = []
    for s in demo_students:
        obj = Student(
            id=str(uuid4())[:8],
            **s,
            created_at=datetime.now().strftime("%Y-%m-%d"),
        )
        db.add(obj)
        student_objs.append(obj)

    demo_trainings = [
        {"name": "2024年Q1新员工入职培训", "topic": "新员工入职培训",
         "start_date": "2024-01-15", "end_date": "2024-01-17"},
        {"name": "销售技能提升班", "topic": "销售技巧培训",
         "start_date": "2024-02-01", "end_date": "2024-02-03"},
        {"name": "数字化办公技能培训", "topic": "数字化技能培训",
         "start_date": "2024-03-10", "end_date": "2024-03-12"},
    ]

    training_objs = []
    for t in demo_trainings:
        obj = Training(
            id=str(uuid4())[:8],
            **t,
            created_at=datetime.now().strftime("%Y-%m-%d"),
        )
        db.add(obj)
        training_objs.append(obj)

    db.flush()

    for s in student_objs:
        for t in training_objs:
            pre_score = random.randint(40, 70)
            post_score = min(100, pre_score + random.randint(10, 35))
            db.add(Record(
                id=str(uuid4())[:8],
                student_id=s.id,
                training_id=t.id,
                type="pre",
                score=float(pre_score),
                date="2024-01-15",
                created_at="2024-01-15 09:00",
            ))
            db.add(Record(
                id=str(uuid4())[:8],
                student_id=s.id,
                training_id=t.id,
                type="post",
                score=float(post_score),
                date="2024-02-15",
                created_at="2024-02-15 16:00",
            ))

    db.commit()
    return {"message": f"已注入 {len(demo_students)} 名学员、{len(demo_trainings)} 个培训及测评记录"}


@router.delete("/clear-data", status_code=204)
def clear_all_data(db: Session = Depends(get_db)):
    """清空所有数据"""
    db.query(Record).delete()
    db.query(Student).delete()
    db.query(Training).delete()
    db.commit()


def _calc_training_stats(training_id: str, db: Session) -> TrainingStats | None:
    """计算单个培训的统计数据"""
    records = db.query(Record).filter(Record.training_id == training_id).all()
    pres = [r for r in records if r.type == "pre"]
    posts = [r for r in records if r.type == "post"]

    if not pres or not posts:
        return None

    pre_avg = sum(r.score for r in pres) / len(pres)
    post_avg = sum(r.score for r in posts) / len(posts)
    improvement = post_avg - pre_avg
    improvement_pct = (improvement / pre_avg * 100) if pre_avg > 0 else 0

    qualified = sum(1 for r in posts if r.score >= 75)
    qualified_rate = qualified / len(posts) * 100 if posts else 0

    return TrainingStats(
        total_students=len(pres),
        pre_avg=round(pre_avg, 1),
        post_avg=round(post_avg, 1),
        improvement=round(improvement, 1),
        improvement_pct=round(improvement_pct, 1),
        qualified_rate=round(qualified_rate, 1),
    )
