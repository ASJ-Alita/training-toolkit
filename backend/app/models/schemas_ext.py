"""
Pydantic Schemas - 扩展
Kirkpatrick 评估 + RAG 知识库
"""

from pydantic import BaseModel
from typing import Optional


# ── Kirkpatrick 评估 ──────────────────────────────────────────────────────

class EvaluationCreate(BaseModel):
    course_name: str
    department: str = ""
    train_date: str = ""
    trainee_name: str = "匿名"
    level1: dict = {}          # {"L1Q1": 4, ...}
    level1_avg: float = 0
    l2_pre_score: float = 0
    l2_post_score: float = 0
    level3: dict = {}          # {"L3Q1": 3, ...}
    level3_avg: float = 0
    level4: dict = {}          # {"L4M1": 15.0, ...}


class EvaluationResponse(BaseModel):
    id: str
    course_name: str
    department: str
    train_date: str
    trainee_name: str
    level1_avg: float
    l2_pre_score: float
    l2_post_score: float
    level3_avg: float
    level4_data: dict
    created_at: str

    class Config:
        from_attributes = True


class EvalStatsResponse(BaseModel):
    total: int = 0
    level1: dict = {}
    level2: dict = {}
    level3: dict = {}
    level4: dict = {}


# ── Kirkpatrick 问卷配置 ─────────────────────────────────────────────────

LEVEL1_QUESTIONS = [
    {"id": "L1Q1", "text": "本次培训内容对我的工作有实际帮助", "category": "内容价值"},
    {"id": "L1Q2", "text": "培训内容的难度与我的需求匹配", "category": "内容价值"},
    {"id": "L1Q3", "text": "讲师讲解清晰，互动积极", "category": "讲师表现"},
    {"id": "L1Q4", "text": "讲师具备丰富的实战经验", "category": "讲师表现"},
    {"id": "L1Q5", "text": "培训时间安排合理", "category": "组织安排"},
    {"id": "L1Q6", "text": "培训场地/线上环境良好", "category": "组织安排"},
    {"id": "L1Q7", "text": "培训材料和课件质量高", "category": "教学资源"},
    {"id": "L1Q8", "text": "整体上我对本次培训感到满意", "category": "总体满意度"},
]

LEVEL2_QUESTIONS = [
    {"id": "L2Q1", "text": "柯氏四级评估模型中，'行为层'对应的是？",
     "options": ["A. 学员对培训的满意度", "B. 知识技能的掌握程度",
                 "C. 工作中行为改变的应用", "D. 业务结果的改善"],
     "answer": "C", "category": "方法论知识"},
    {"id": "L2Q2", "text": "以下哪种方式最能评估培训的'学习层'效果？",
     "options": ["A. 满意度问卷", "B. 前后测对比", "C. 绩效指标分析", "D. 上级访谈"],
     "answer": "B", "category": "方法论知识"},
    {"id": "L2Q3", "text": "ROI（培训投资回报率）属于柯氏模型的哪一层？",
     "options": ["A. 反应层", "B. 学习层", "C. 行为层", "D. 结果层"],
     "answer": "D", "category": "方法论知识"},
    {"id": "L2Q4", "text": "设计培训评估体系时，最关键的首要步骤是？",
     "options": ["A. 制作问卷", "B. 明确培训目标", "C. 收集数据", "D. 撰写报告"],
     "answer": "B", "category": "实操技能"},
    {"id": "L2Q5", "text": "以下哪种评估方式适合评估'行为层'？",
     "options": ["A. 知识测验", "B. 学员反馈表", "C. 360°行为观察", "D. 财务数据分析"],
     "answer": "C", "category": "实操技能"},
]

LEVEL3_QUESTIONS = [
    {"id": "L3Q1", "text": "培训中学到的方法，我已在工作中实际应用", "category": "知识应用"},
    {"id": "L3Q2", "text": "我能将培训内容分享或指导给同事", "category": "知识传播"},
    {"id": "L3Q3", "text": "培训改变了我处理某类问题的方式", "category": "行为改变"},
    {"id": "L3Q4", "text": "上级对我培训后的工作表现变化给予了认可", "category": "外部认可"},
    {"id": "L3Q5", "text": "我有计划继续深化培训中学到的技能", "category": "持续学习"},
    {"id": "L3Q6", "text": "应用培训内容时遇到的障碍已基本克服", "category": "障碍消除"},
]

LEVEL4_METRICS = [
    {"id": "L4M1", "text": "培训后团队工作效率提升（%）", "unit": "%", "benchmark": 10},
    {"id": "L4M2", "text": "培训后错误率/返工率降低（%）", "unit": "%", "benchmark": 15},
    {"id": "L4M3", "text": "员工技能达标率提升（%）", "unit": "%", "benchmark": 20},
    {"id": "L4M4", "text": "员工留存率变化（%）", "unit": "%", "benchmark": 5},
    {"id": "L4M5", "text": "培训总投入（元）", "unit": "元", "benchmark": 0},
    {"id": "L4M6", "text": "因培训带来的估算收益（元）", "unit": "元", "benchmark": 0},
]

COURSE_TEMPLATES = [
    "管理技能提升培训", "销售技巧培训", "Python/AI技术培训",
    "沟通表达培训", "项目管理培训", "企业文化与价值观培训",
    "新员工入职培训", "安全合规培训", "自定义课程",
]

DEPARTMENT_LIST = [
    "人力资源部", "销售部", "技术研发部", "市场营销部", "财务部",
    "运营部", "客服部", "行政部", "培训中心", "其他",
]


# ── RAG 知识库 ───────────────────────────────────────────────────────────

class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    chunks_count: int
    status: str


class KBStatsResponse(BaseModel):
    total_documents: int = 0
    total_chunks: int = 0
    sources: list = []
    llm_provider: str = ""


class ChatRequest(BaseModel):
    question: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    answer: str
    sources: list = []
    question: str = ""


class LLMConfigRequest(BaseModel):
    llm_provider: str = "siliconflow"
    api_key: str = ""


# ── RAG 配置 ─────────────────────────────────────────────────────────────

LLM_PROVIDERS = {
    "siliconflow": {
        "name": "硅基流动 DeepSeek-V3（推荐）",
        "chat_url": "https://api.siliconflow.cn/v1/chat/completions",
        "model": "deepseek-ai/DeepSeek-V3",
        "temperature": 0.3,
        "max_tokens": 2000,
    },
    "openai": {
        "name": "OpenAI GPT-4o-mini",
        "chat_url": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "max_tokens": 2000,
    },
    "zhihui": {
        "name": "智谱 GLM-4-flash",
        "chat_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "model": "glm-4-flash",
        "temperature": 0.3,
        "max_tokens": 2000,
    },
}

SILICONFLOW_EMBED = {
    "name": "BAAI/bge-m3",
    "url": "https://api.siliconflow.cn/v1/embeddings",
    "dimension": 1024,
}

CHUNK_SIZE = 400
CHUNK_OVERLAP = 80
TOP_K = 5
SIMILARITY_THRESHOLD = 0.3
