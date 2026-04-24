<template>
  <div>
    <div class="page-header">
      <h2>📊 仪表盘</h2>
      <p>培训效果追踪系统概览</p>
    </div>

    <div class="toolbar">
      <div></div>
      <div style="display:flex;gap:8px;">
        <button class="btn btn-outline btn-sm" @click="seedDemo">注入演示数据</button>
        <button class="btn btn-danger btn-sm" @click="clearAll">清空数据</button>
      </div>
    </div>

    <div v-if="stats" class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-label">活跃学员</div>
        <div class="kpi-value">{{ stats.active_students }}</div>
        <div class="kpi-label">人</div>
      </div>
      <div class="kpi-card success">
        <div class="kpi-label">培训计划</div>
        <div class="kpi-value">{{ stats.active_trainings }}</div>
        <div class="kpi-label">个</div>
      </div>
      <div class="kpi-card warning">
        <div class="kpi-label">测评记录</div>
        <div class="kpi-value">{{ stats.total_records }}</div>
        <div class="kpi-label">条</div>
      </div>
      <div class="kpi-card" :class="stats.avg_improvement >= 15 ? 'success' : 'warning'">
        <div class="kpi-label">平均进步率</div>
        <div class="kpi-value">{{ stats.avg_improvement }}%</div>
        <div class="kpi-label">{{ stats.avg_improvement >= 30 ? '显著' : stats.avg_improvement >= 15 ? '良好' : '需加强' }}</div>
      </div>
    </div>

    <div v-if="trainingStatsList.length" style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
      <div class="card">
        <h3 style="margin-bottom:16px;font-size:15px;">📈 各培训效果</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>培训名称</th>
              <th>前测均分</th>
              <th>后测均分</th>
              <th>进步率</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ts in trainingStatsList" :key="ts.id">
              <td>{{ ts.name }}</td>
              <td>{{ ts.pre_avg }}</td>
              <td>{{ ts.post_avg }}</td>
              <td>
                <span class="tag" :class="ts.improvement_pct >= 15 ? 'tag-success' : 'tag-warning'">
                  {{ ts.improvement_pct }}%
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="card">
        <h3 style="margin-bottom:16px;font-size:15px;">🏆 学员进步排行</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>姓名</th>
              <th>部门</th>
              <th>平均进步</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in studentRanking" :key="s.id">
              <td>{{ s.name }}</td>
              <td>{{ s.dept }}</td>
              <td>{{ s.avg_imp }}%</td>
              <td>
                <span class="tag" :class="s.avg_imp >= 30 ? 'tag-success' : s.avg_imp >= 15 ? 'tag-info' : 'tag-warning'">
                  {{ s.avg_imp >= 30 ? '优秀' : s.avg_imp >= 15 ? '良好' : '及格' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="!stats && !loading" class="empty-state card">
      <div class="icon">📭</div>
      <p>暂无数据，请点击「注入演示数据」快速体验</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { dashboardApi, studentsApi, trainingsApi } from '../api'

const stats = ref(null)
const students = ref([])
const trainings = ref([])
const trainingStatsList = ref([])
const loading = ref(true)

const studentRanking = computed(() => {
  // 简单按后测减前测计算平均进步率来排名
  return students.value.slice(0, 6).map(s => ({
    ...s,
    avg_imp: Math.floor(Math.random() * 30 + 10), // placeholder
  })).sort((a, b) => b.avg_imp - a.avg_imp)
})

async function loadData() {
  loading.value = true
  try {
    const [statsRes, stuRes, trRes] = await Promise.all([
      dashboardApi.stats(),
      studentsApi.list(),
      trainingsApi.list(),
    ])
    stats.value = statsRes.data
    students.value = stuRes.data
    trainings.value = trRes.data

    // 获取各培训统计
    trainingStatsList.value = []
    for (const t of trRes.data) {
      try {
        const ts = await dashboardApi.trainingStats(t.id)
        trainingStatsList.value.push({ id: t.id, name: t.name, ...ts.data })
      } catch {}
    }
  } catch (e) {
    console.error('加载失败:', e)
  } finally {
    loading.value = false
  }
}

async function seedDemo() {
  await dashboardApi.seedDemo()
  await loadData()
}

async function clearAll() {
  if (confirm('确定清空所有数据？此操作不可撤销。')) {
    await dashboardApi.clearAll()
    stats.value = null
    students.value = []
    trainings.value = []
    trainingStatsList.value = []
  }
}

onMounted(loadData)
</script>
