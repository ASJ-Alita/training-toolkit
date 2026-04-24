"""
柯氏四级评估 API
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import SessionLocal
from app.models.models_ext import Evaluation
from app.models.schemas_ext import (
    EvaluationCreate, EvaluationResponse, EvalStatsResponse,
    LEVEL1_QUESTIONS, LEVEL2_QUESTIONS, LEVEL3_QUESTIONS, LEVEL4_METRICS,
    COURSE_TEMPLATES, DEPARTMENT_LIST,
)

router = APIRouter(prefix="/api/evaluations", tags=["Kirkpatrick 评估"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── 问卷配置 ──────────────────────────────────────────────────────────────

@router.get("/config")
def get_eval_config():
    """获取问卷配置（题目、选项等）"""
    return {
        "level1_questions": LEVEL1_QUESTIONS,
        "level2_questions": LEVEL2_QUESTIONS,
        "level3_questions": LEVEL3_QUESTIONS,
        "level4_metrics": LEVEL4_METRICS,
        "course_templates": COURSE_TEMPLATES,
        "department_list": DEPARTMENT_LIST,
    }


# ── CRUD ──────────────────────────────────────────────────────────────────

@router.get("/")
def list_evaluations():
    """获取所有评估记录"""
    db = SessionLocal()
    try:
        evaluations = db.query(Evaluation).order_by(Evaluation.created_at.desc()).all()
        result = []
        for e in evaluations:
            import json
            l4 = json.loads(e.level4_data) if e.level4_data else {}
            result.append(EvaluationResponse(
                id=e.id,
                course_name=e.course_name,
                department=e.department,
                train_date=e.train_date,
                trainee_name=e.trainee_name,
                level1_avg=e.level1_avg,
                l2_pre_score=e.l2_pre_score,
                l2_post_score=e.l2_post_score,
                level3_avg=e.level3_avg,
                level4_data=l4,
                created_at=e.created_at,
            ))
        return result
    finally:
        db.close()


@router.get("/{eval_id}")
def get_evaluation(eval_id: str):
    """获取单条评估记录详情"""
    db = SessionLocal()
    try:
        e = db.query(Evaluation).filter(Evaluation.id == eval_id).first()
        if not e:
            raise HTTPException(status_code=404, detail="评估记录不存在")
        import json
        return {
            "id": e.id,
            "course_name": e.course_name,
            "department": e.department,
            "train_date": e.train_date,
            "trainee_name": e.trainee_name,
            "level1": json.loads(e.level1_data) if e.level1_data else {},
            "level1_avg": e.level1_avg,
            "l2_pre_score": e.l2_pre_score,
            "l2_post_score": e.l2_post_score,
            "level3": json.loads(e.level3_data) if e.level3_data else {},
            "level3_avg": e.level3_avg,
            "level4": json.loads(e.level4_data) if e.level4_data else {},
            "created_at": e.created_at,
        }
    finally:
        db.close()


@router.post("/")
def create_evaluation(data: EvaluationCreate):
    """创建评估记录"""
    db = SessionLocal()
    try:
        import json
        record_id = f"KP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        evaluation = Evaluation(
            id=record_id,
            course_name=data.course_name,
            department=data.department,
            train_date=data.train_date,
            trainee_name=data.trainee_name,
            level1_data=json.dumps(data.level1, ensure_ascii=False),
            level1_avg=data.level1_avg,
            l2_pre_score=data.l2_pre_score,
            l2_post_score=data.l2_post_score,
            level3_data=json.dumps(data.level3, ensure_ascii=False),
            level3_avg=data.level3_avg,
            level4_data=json.dumps(data.level4, ensure_ascii=False),
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        return {"id": record_id, "message": "评估数据已保存"}
    finally:
        db.close()


@router.delete("/{eval_id}")
def delete_evaluation(eval_id: str):
    """删除评估记录"""
    db = SessionLocal()
    try:
        e = db.query(Evaluation).filter(Evaluation.id == eval_id).first()
        if not e:
            raise HTTPException(status_code=404, detail="评估记录不存在")
        db.delete(e)
        db.commit()
        return {"message": "已删除"}
    finally:
        db.close()


@router.delete("/")
def clear_evaluations():
    """清空所有评估记录"""
    db = SessionLocal()
    try:
        db.query(Evaluation).delete()
        db.commit()
        return {"message": "所有评估记录已清空"}
    finally:
        db.close()


# ── 统计 ──────────────────────────────────────────────────────────────────

@router.get("/stats/summary")
def get_eval_stats():
    """计算评估统计数据"""
    db = SessionLocal()
    try:
        evaluations = db.query(Evaluation).all()
        if not evaluations:
            return {"total": 0, "level1": {}, "level2": {}, "level3": {}, "level4": {}}

        import json
        n = len(evaluations)

        # Level 1
        l1_scores = {}
        for e in evaluations:
            for qid, val in json.loads(e.level1_data).items():
                l1_scores.setdefault(qid, []).append(val)
        l1_avg = {qid: round(sum(v) / len(v), 2) for qid, v in l1_scores.items()}
        l1_total = round(sum(l1_avg.values()) / len(l1_avg), 2) if l1_avg else 0

        # Level 2
        pre_scores = [e.l2_pre_score for e in evaluations if e.l2_pre_score]
        post_scores = [e.l2_post_score for e in evaluations if e.l2_post_score]
        l2_pre_avg = round(sum(pre_scores) / len(pre_scores), 1) if pre_scores else 0
        l2_post_avg = round(sum(post_scores) / len(post_scores), 1) if post_scores else 0

        # Level 3
        l3_scores = {}
        for e in evaluations:
            for qid, val in json.loads(e.level3_data).items():
                l3_scores.setdefault(qid, []).append(val)
        l3_avg = {qid: round(sum(v) / len(v), 2) for qid, v in l3_scores.items()}
        l3_total = round(sum(l3_avg.values()) / len(l3_avg), 2) if l3_avg else 0

        # Level 4 ROI
        investments, benefits = [], []
        l4_metrics = {}
        for e in evaluations:
            l4 = json.loads(e.level4_data)
            inv = l4.get("L4M5", 0)
            ben = l4.get("L4M6", 0)
            if inv: investments.append(inv)
            if ben: benefits.append(ben)
            for mid in ["L4M1", "L4M2", "L4M3", "L4M4"]:
                v = l4.get(mid)
                if v is not None:
                    l4_metrics.setdefault(mid, []).append(v)

        total_invest = sum(investments)
        total_benefit = sum(benefits)
        roi = round((total_benefit - total_invest) / total_invest * 100, 1) if total_invest else 0
        l4_avg = {mid: round(sum(v) / len(v), 1) for mid, v in l4_metrics.items()}

        return {
            "total": n,
            "level1": {"avg_by_question": l1_avg, "total_avg": l1_total},
            "level2": {"pre_avg": l2_pre_avg, "post_avg": l2_post_avg, "improvement": round(l2_post_avg - l2_pre_avg, 1)},
            "level3": {"avg_by_question": l3_avg, "total_avg": l3_total},
            "level4": {"metrics_avg": l4_avg, "total_invest": total_invest, "total_benefit": total_benefit, "roi": roi},
        }
    finally:
        db.close()


# ── 演示数据 ──────────────────────────────────────────────────────────────

@router.post("/demo-data")
def inject_demo_data():
    """注入演示数据"""
    import random, json
    db = SessionLocal()
    try:
        db.query(Evaluation).delete()
        db.commit()

        courses = ["管理技能提升培训", "Python/AI技术培训", "沟通表达培训", "销售技巧培训"]
        depts = ["人力资源部", "技术研发部", "销售部", "市场营销部"]
        for i in range(8):
            l1 = {q["id"]: random.randint(3, 5) for q in LEVEL1_QUESTIONS}
            l3 = {q["id"]: random.randint(2, 5) for q in LEVEL3_QUESTIONS}
            eval_obj = Evaluation(
                id=f"KP-DEMO-{i+1:03d}",
                course_name=random.choice(courses),
                department=random.choice(depts),
                train_date=f"2026-04-{random.randint(10, 22):02d}",
                trainee_name=f"学员{i+1:02d}",
                level1_data=json.dumps(l1, ensure_ascii=False),
                level1_avg=round(sum(l1.values()) / len(l1), 2),
                l2_pre_score=random.randint(40, 65),
                l2_post_score=random.randint(70, 95),
                level3_data=json.dumps(l3, ensure_ascii=False),
                level3_avg=round(sum(l3.values()) / len(l3), 2),
                level4_data=json.dumps({
                    "L4M1": round(random.uniform(8, 20), 1),
                    "L4M2": round(random.uniform(10, 25), 1),
                    "L4M3": round(random.uniform(15, 30), 1),
                    "L4M4": round(random.uniform(3, 8), 1),
                    "L4M5": random.randint(20000, 80000),
                    "L4M6": random.randint(50000, 200000),
                }, ensure_ascii=False),
            )
            db.add(eval_obj)
        db.commit()
        return {"message": "已注入 8 条演示数据"}
    finally:
        db.close()
