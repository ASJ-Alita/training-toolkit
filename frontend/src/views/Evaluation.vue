<template>
  <div class="eval-page">
    <div class="page-header">
      <h1>🎓 柯氏四级培训评估</h1>
      <p>Kirkpatrick Four-Level Training Evaluation</p>
    </div>

    <!-- Tab 切换 -->
    <div class="tab-bar">
      <button :class="['tab-btn', { active: activeTab === 'form' }]" @click="activeTab = 'form'">
        📝 填写问卷
      </button>
      <button :class="['tab-btn', { active: activeTab === 'data' }]" @click="activeTab = 'data'">
        📋 数据列表
      </button>
      <button :class="['tab-btn', { active: activeTab === 'report' }]" @click="activeTab = 'report'">
        📊 评估报告
      </button>
    </div>

    <!-- Tab 1: 问卷 -->
    <div v-if="activeTab === 'form'" class="tab-content">
      <!-- 基本信息 -->
      <div class="section">
        <div class="section-header l1">📌 基本信息</div>
        <div class="form-row">
          <label>课程名称</label>
          <select v-model="form.course_name">
            <option v-for="c in config.course_templates" :key="c">{{ c }}</option>
          </select>
          <label>部门</label>
          <select v-model="form.department">
            <option v-for="d in config.department_list" :key="d">{{ d }}</option>
          </select>
        </div>
        <div class="form-row">
          <label>培训日期</label>
          <input type="date" v-model="form.train_date" />
          <label>姓名</label>
          <input type="text" v-model="form.trainee_name" placeholder="可匿名" />
        </div>
      </div>

      <!-- Level 1 -->
      <div class="section">
        <div class="section-header l1">Level 1 · 反应层 — 培训结束后填写</div>
        <p class="section-hint">请为以下各项评分（1=非常不同意  5=非常同意）</p>
        <div class="rating-list">
          <div v-for="q in config.level1_questions" :key="q.id" class="rating-item">
            <span class="q-text">{{ q.text }}</span>
            <span class="q-category">{{ q.category }}</span>
            <div class="rating-stars">
              <button v-for="n in 5" :key="n"
                :class="['star', { active: (form.level1[q.id] || 3) >= n }]"
                @click="form.level1[q.id] = n">{{ n }}</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Level 2 -->
      <div class="section">
        <div class="section-header l2">Level 2 · 学习层 — 前测 & 后测</div>
        <div class="quiz-area">
          <div class="quiz-card" v-for="q in config.level2_questions" :key="q.id">
            <p class="quiz-text"><strong>{{ q.text }}</strong></p>
            <div class="quiz-options">
              <label v-for="opt in q.options" :key="opt" class="quiz-opt">
                <input type="radio" :name="q.id" :value="opt[0]"
                  v-model="quizAnswers[q.id]" />
                {{ opt }}
              </label>
            </div>
          </div>
          <div class="quiz-actions">
            <button class="btn btn-sm l2" @click="submitQuiz('pre')">
              ▶ 提交前测
            </button>
            <button class="btn btn-sm l2-green" @click="submitQuiz('post')">
              ▶ 提交后测
            </button>
          </div>
          <div class="quiz-scores">
            <span>前测：<strong :class="{ 'text-green': form.l2_pre_score > 0 }">{{ form.l2_pre_score > 0 ? form.l2_pre_score + '%' : '未完成' }}</strong></span>
            <span>后测：<strong :class="{ 'text-green': form.l2_post_score > 0 }">{{ form.l2_post_score > 0 ? form.l2_post_score + '%' : '未完成' }}</strong></span>
          </div>
        </div>
      </div>

      <!-- Level 3 -->
      <div class="section">
        <div class="section-header l3">Level 3 · 行为层 — 培训结束30天后填写</div>
        <p class="section-hint">请评估培训内容在实际工作中的应用情况（1=完全没有  5=总是）</p>
        <div class="rating-list">
          <div v-for="q in config.level3_questions" :key="q.id" class="rating-item">
            <span class="q-text">{{ q.text }}</span>
            <span class="q-category">{{ q.category }}</span>
            <div class="rating-stars">
              <button v-for="n in 5" :key="n"
                :class="['star', { active: (form.level3[q.id] || 3) >= n }]"
                @click="form.level3[q.id] = n">{{ n }}</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Level 4 -->
      <div class="section">
        <div class="section-header l4">Level 4 · 结果层 — 培训完成后业务指标变化</div>
        <p class="section-hint">请填写培训前后的业务指标变化，以及培训投入与估算收益</p>
        <div class="metric-list">
          <div v-for="m in config.level4_metrics" :key="m.id" class="metric-item">
            <span class="m-text">{{ m.text }}</span>
            <div class="m-input">
              <input type="number" v-model.number="form.level4[m.id]" />
              <span class="m-unit">{{ m.unit }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 提交 -->
      <div class="submit-area">
        <button class="btn btn-primary btn-lg" @click="submitEval">✅ 提交评估数据</button>
        <button class="btn btn-gray btn-lg" @click="resetForm">🔄 重置表单</button>
      </div>
    </div>

    <!-- Tab 2: 数据列表 -->
    <div v-if="activeTab === 'data'" class="tab-content">
      <div class="toolbar">
        <button class="btn btn-primary" @click="loadEvals">🔄 刷新</button>
        <button class="btn btn-green" @click="exportCSV">📤 导出CSV</button>
        <button class="btn btn-danger" @click="clearAll" :disabled="evaluations.length === 0">🗑️ 清空所有</button>
        <span class="record-count">共 {{ evaluations.length }} 条记录</span>
      </div>
      <div class="table-wrap">
        <table v-if="evaluations.length > 0">
          <thead>
            <tr>
              <th>记录ID</th><th>课程名称</th><th>部门</th><th>日期</th>
              <th>L1均分</th><th>L2前测%</th><th>L2后测%</th><th>L3均分</th><th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="e in evaluations" :key="e.id">
              <td>{{ e.id }}</td><td>{{ e.course_name }}</td><td>{{ e.department }}</td>
              <td>{{ e.train_date }}</td>
              <td><span class="badge l1">{{ e.level1_avg }}</span></td>
              <td>{{ e.l2_pre_score }}%</td>
              <td><span class="badge l2">{{ e.l2_post_score }}%</span></td>
              <td>{{ e.level3_avg }}</td>
              <td><button class="btn btn-danger btn-sm" @click="deleteEval(e.id)">删除</button></td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty-state">
          <p>📭 暂无评估数据</p>
          <button class="btn btn-purple" @click="injectDemo">🎭 注入演示数据</button>
        </div>
      </div>
    </div>

    <!-- Tab 3: 评估报告 -->
    <div v-if="activeTab === 'report'" class="tab-content">
      <div class="report-actions">
        <button class="btn btn-primary btn-lg" @click="loadReport">📊 生成评估报告</button>
        <button class="btn btn-purple btn-lg" @click="injectDemo">🎭 注入演示数据</button>
      </div>
      <div v-if="stats.total > 0" class="report-content">
        <!-- KPI 卡片 -->
        <div class="kpi-grid">
          <div class="kpi-card l1">
            <div class="kpi-label">L1 反应层满意度</div>
            <div class="kpi-value">{{ stats.level1?.total_avg || 0 }}<small>/5</small></div>
          </div>
          <div class="kpi-card l2">
            <div class="kpi-label">L2 学习层进步</div>
            <div class="kpi-value">+{{ stats.level2?.improvement || 0 }}<small>%</small></div>
          </div>
          <div class="kpi-card l3">
            <div class="kpi-label">L3 行为层应用度</div>
            <div class="kpi-value">{{ stats.level3?.total_avg || 0 }}<small>/5</small></div>
          </div>
          <div class="kpi-card l4">
            <div class="kpi-label">L4 培训ROI</div>
            <div class="kpi-value" :class="{ negative: (stats.level4?.roi || 0) < 0 }">
              {{ stats.level4?.roi || 0 }}<small>%</small>
            </div>
          </div>
        </div>

        <!-- L2 前后测对比 -->
        <div class="section">
          <div class="section-header l2">📝 L2 学习层 — 前测 vs 后测</div>
          <div class="compare-bar">
            <div class="compare-item">
              <span class="bar-label">前测均分</span>
              <div class="bar-track"><div class="bar-fill pre" :style="{ width: (stats.level2?.pre_avg || 0) + '%' }">{{ stats.level2?.pre_avg || 0 }}%</div></div>
            </div>
            <div class="compare-item">
              <span class="bar-label">后测均分</span>
              <div class="bar-track"><div class="bar-fill post" :style="{ width: (stats.level2?.post_avg || 0) + '%' }">{{ stats.level2?.post_avg || 0 }}%</div></div>
            </div>
          </div>
        </div>

        <!-- ROI 详情 -->
        <div class="section">
          <div class="section-header l4">💰 ROI 详情</div>
          <div class="roi-detail">
            <p>累计培训投入：<strong>¥{{ (stats.level4?.total_invest || 0).toLocaleString() }}</strong></p>
            <p>估算培训收益：<strong class="text-green">¥{{ (stats.level4?.total_benefit || 0).toLocaleString() }}</strong></p>
            <p>净收益：<strong :class="(stats.level4?.roi || 0) >= 0 ? 'text-green' : 'text-red'">
              ¥{{ ((stats.level4?.total_benefit || 0) - (stats.level4?.total_invest || 0)).toLocaleString() }}</strong></p>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <p>📭 暂无评估数据，请先填写问卷或注入演示数据</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import api from '../api'

const activeTab = ref('form')
const config = ref({})
const evaluations = ref([])
const stats = ref({})
const quizAnswers = reactive({})

const form = reactive({
  course_name: '管理技能提升培训',
  department: '人力资源部',
  train_date: new Date().toISOString().slice(0, 10),
  trainee_name: '匿名',
  level1: {},
  l2_pre_score: 0,
  l2_post_score: 0,
  level3: {},
  level4: {},
})

onMounted(async () => {
  const res = await api.get('/api/evaluations/config')
  config.value = res.data
  // 初始化默认值
  config.value.level1_questions?.forEach(q => { if (!form.level1[q.id]) form.level1[q.id] = 3 })
  config.value.level3_questions?.forEach(q => { if (!form.level3[q.id]) form.level3[q.id] = 3 })
  config.value.level4_metrics?.forEach(m => { if (!form.level4[m.id]) form.level4[m.id] = 0 })
  loadEvals()
})

async function loadEvals() {
  const res = await api.get('/api/evaluations/')
  evaluations.value = res.data
}

function submitQuiz(mode) {
  const questions = config.value.level2_questions || []
  let score = 0
  questions.forEach(q => {
    if (quizAnswers[q.id] === q.answer) score++
  })
  const pct = Math.round(score / questions.length * 100)
  if (mode === 'pre') form.l2_pre_score = pct
  else form.l2_post_score = pct
  alert(`${mode === 'pre' ? '前测' : '后测'}得分：${pct}%（${score}/${questions.length} 题正确）`)
}

async function submitEval() {
  const l1Vals = Object.values(form.level1)
  const l3Vals = Object.values(form.level3)
  const payload = {
    course_name: form.course_name,
    department: form.department,
    train_date: form.train_date,
    trainee_name: form.trainee_name || '匿名',
    level1: form.level1,
    level1_avg: l1Vals.length ? +(l1Vals.reduce((a, b) => a + b, 0) / l1Vals.length).toFixed(2) : 0,
    l2_pre_score: form.l2_pre_score,
    l2_post_score: form.l2_post_score,
    level3: form.level3,
    level3_avg: l3Vals.length ? +(l3Vals.reduce((a, b) => a + b, 0) / l3Vals.length).toFixed(2) : 0,
    level4: form.level4,
  }
  await api.post('/api/evaluations/', payload)
  alert('✅ 评估数据已保存！')
  resetForm()
  loadEvals()
}

function resetForm() {
  form.level1 = {}
  form.level3 = {}
  form.level4 = {}
  form.l2_pre_score = 0
  form.l2_post_score = 0
  config.value.level1_questions?.forEach(q => { form.level1[q.id] = 3 })
  config.value.level3_questions?.forEach(q => { form.level3[q.id] = 3 })
  config.value.level4_metrics?.forEach(m => { form.level4[m.id] = 0 })
}

async function deleteEval(id) {
  if (!confirm('确定要删除这条记录吗？')) return
  await api.delete(`/api/evaluations/${id}`)
  loadEvals()
}

async function clearAll() {
  if (!confirm('⚠️ 确定要清空所有评估数据吗？此操作不可恢复！')) return
  await api.delete('/api/evaluations/')
  loadEvals()
}

async function exportCSV() {
  // 简单前端 CSV 导出
  if (evaluations.value.length === 0) { alert('暂无数据'); return }
  const headers = ['记录ID', '课程名称', '部门', '日期', 'L1均分', 'L2前测%', 'L2后测%', 'L3均分']
  const rows = evaluations.value.map(e => [e.id, e.course_name, e.department, e.train_date, e.level1_avg, e.l2_pre_score, e.l2_post_score, e.level3_avg])
  const csv = '\uFEFF' + [headers, ...rows].map(r => r.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = `kirkpatrick_data_${Date.now()}.csv`; a.click()
  URL.revokeObjectURL(url)
}

async function injectDemo() {
  await api.post('/api/evaluations/demo-data')
  alert('✅ 已注入演示数据')
  loadEvals()
  loadReport()
}

async function loadReport() {
  const res = await api.get('/api/evaluations/stats/summary')
  stats.value = res.data
}
</script>

<style scoped>
.eval-page { padding: 0; }
.page-header { text-align: center; padding: 20px 0 16px; }
.page-header h1 { color: #1e293b; margin: 0; font-size: 24px; }
.page-header p { color: #64748b; margin: 4px 0 0; font-size: 13px; }

.tab-bar { display: flex; gap: 4px; background: #e2e8f0; border-radius: 10px; padding: 4px; margin-bottom: 20px; }
.tab-btn { flex: 1; padding: 10px; border: none; background: transparent; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; color: #64748b; transition: all .2s; }
.tab-btn.active { background: white; color: #1a237e; box-shadow: 0 2px 8px rgba(0,0,0,.1); }

.section { background: white; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,.06); }
.section-header { border-radius: 8px; padding: 10px 16px; margin: -20px -20px 16px; font-weight: 600; color: white; font-size: 14px; }
.section-header.l1 { background: #3498db; }
.section-header.l2 { background: #2ecc71; }
.section-header.l3 { background: #f39c12; }
.section-header.l4 { background: #9b59b6; }
.section-hint { color: #64748b; font-size: 13px; margin: 8px 0 12px; }

.form-row { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; flex-wrap: wrap; }
.form-row label { font-size: 13px; font-weight: 600; color: #475569; min-width: 70px; }
.form-row input, .form-row select { padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 13px; min-width: 140px; }

.rating-list { display: flex; flex-direction: column; gap: 6px; }
.rating-item { display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: #f8fafc; border-radius: 8px; }
.q-text { flex: 1; font-size: 13px; color: #334155; }
.q-category { font-size: 11px; color: #94a3b8; background: #f1f5f9; padding: 2px 8px; border-radius: 12px; }
.rating-stars { display: flex; gap: 4px; }
.star { width: 32px; height: 32px; border: 2px solid #e2e8f0; border-radius: 6px; background: white; cursor: pointer; font-size: 13px; font-weight: 600; color: #94a3b8; transition: all .15s; }
.star.active { border-color: #3498db; background: #3498db; color: white; }

.quiz-area { padding: 8px 0; }
.quiz-card { padding: 14px; margin-bottom: 12px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0; }
.quiz-text { font-size: 14px; color: #1e293b; margin-bottom: 10px; }
.quiz-options { display: flex; flex-wrap: wrap; gap: 12px; }
.quiz-opt { display: flex; align-items: center; gap: 6px; font-size: 13px; cursor: pointer; }
.quiz-opt input { accent-color: #2ecc71; }
.quiz-actions { display: flex; gap: 10px; margin: 16px 0; }
.quiz-scores { display: flex; gap: 20px; font-size: 14px; color: #64748b; }

.metric-list { display: flex; flex-direction: column; gap: 8px; }
.metric-item { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: #f8fafc; border-radius: 8px; }
.m-text { font-size: 13px; color: #334155; }
.m-input { display: flex; align-items: center; gap: 8px; }
.m-input input { width: 100px; padding: 6px 10px; border: 1px solid #e2e8f0; border-radius: 6px; text-align: right; font-size: 14px; }
.m-unit { font-size: 12px; color: #94a3b8; }

.submit-area { display: flex; gap: 12px; justify-content: center; padding: 24px 0; }

.toolbar { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
.record-count { margin-left: auto; font-size: 13px; color: #64748b; }

.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { background: #f1f5f9; padding: 10px 12px; text-align: left; font-weight: 600; color: #475569; white-space: nowrap; }
td { padding: 10px 12px; border-bottom: 1px solid #f1f5f9; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: 600; }
.badge.l1 { background: #dbeafe; color: #1d4ed8; }
.badge.l2 { background: #d1fae5; color: #065f46; }

.empty-state { text-align: center; padding: 60px 20px; color: #94a3b8; }
.empty-state p { font-size: 16px; margin-bottom: 16px; }

.report-actions { display: flex; gap: 12px; justify-content: center; margin-bottom: 24px; }

.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 20px; }
.kpi-card { background: white; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,.06); border-top: 4px solid; }
.kpi-card.l1 { border-color: #3498db; }
.kpi-card.l2 { border-color: #2ecc71; }
.kpi-card.l3 { border-color: #f39c12; }
.kpi-card.l4 { border-color: #9b59b6; }
.kpi-label { font-size: 12px; color: #94a3b8; margin-bottom: 8px; }
.kpi-value { font-size: 32px; font-weight: 700; color: #1e293b; }
.kpi-value.l2 { color: #2ecc71; }
.kpi-value.negative { color: #e74c3c; }
.kpi-value small { font-size: 14px; }

.compare-bar { display: flex; flex-direction: column; gap: 12px; padding: 8px 0; }
.compare-item { display: flex; align-items: center; gap: 12px; }
.bar-label { width: 70px; font-size: 13px; color: #475569; }
.bar-track { flex: 1; background: #f0f0f0; border-radius: 6px; height: 28px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 6px; display: flex; align-items: center; padding-left: 10px; font-size: 13px; font-weight: 600; color: white; transition: width .5s; }
.bar-fill.pre { background: #64748b; }
.bar-fill.post { background: #10b981; }

.roi-detail { display: flex; gap: 24px; flex-wrap: wrap; }
.roi-detail p { font-size: 14px; color: #475569; }

.btn { padding: 8px 16px; border: none; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 500; transition: all .2s; }
.btn:disabled { opacity: .5; cursor: not-allowed; }
.btn-primary { background: #1a237e; color: white; }
.btn-primary:hover { background: #283593; }
.btn-green { background: #2ecc71; color: white; }
.btn-danger { background: #e74c3c; color: white; }
.btn-gray { background: #94a3b8; color: white; }
.btn-purple { background: #9b59b6; color: white; }
.btn-sm { padding: 6px 12px; font-size: 12px; }
.btn-sm.l2 { background: #2ecc71; color: white; }
.btn-sm.l2-green { background: #27ae60; color: white; }
.btn-lg { padding: 12px 28px; font-size: 15px; font-weight: 600; }

.text-green { color: #27ae60; }
.text-red { color: #e74c3c; }

@media (max-width: 768px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .form-row { flex-direction: column; align-items: flex-start; }
}
</style>
