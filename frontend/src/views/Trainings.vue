<template>
  <div>
    <div class="page-header">
      <h2>📚 培训管理</h2>
      <p>管理培训计划</p>
    </div>

    <div class="toolbar">
      <input
        v-model="search"
        type="text"
        placeholder="搜索培训名称 / 主题..."
        style="padding:8px 14px;border:1px solid var(--border);border-radius:8px;width:260px;font-size:13px;"
      />
      <button class="btn btn-primary" @click="openModal()">＋ 添加培训</button>
    </div>

    <div class="card">
      <table v-if="filtered.length" class="data-table">
        <thead>
          <tr>
            <th>培训名称</th>
            <th>主题</th>
            <th>起止日期</th>
            <th>满分</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in filtered" :key="t.id">
            <td><strong>{{ t.name }}</strong></td>
            <td>{{ t.topic || '-' }}</td>
            <td>{{ t.start_date || '-' }} ~ {{ t.end_date || '-' }}</td>
            <td>{{ t.max_score }}</td>
            <td>
              <span class="tag" :class="t.status === 'active' ? 'tag-success' : 'tag-warning'">
                {{ t.status === 'active' ? '进行中' : '已结束' }}
              </span>
            </td>
            <td>
              <button class="btn btn-outline btn-sm" @click="openModal(t)">编辑</button>
              <button class="btn btn-danger btn-sm" @click="handleDelete(t)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state">
        <div class="icon">📭</div>
        <p>暂无培训数据</p>
      </div>
    </div>

    <!-- 模态框 -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editing ? '编辑培训' : '添加培训' }}</h3>
          <button class="modal-close" @click="showModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>培训名称 *</label>
            <input v-model="form.name" placeholder="如：2024年Q1新员工入职培训" />
          </div>
          <div class="form-group">
            <label>培训主题</label>
            <input v-model="form.topic" placeholder="如：新员工入职培训" />
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
            <div class="form-group">
              <label>开始日期</label>
              <input v-model="form.start_date" type="date" />
            </div>
            <div class="form-group">
              <label>结束日期</label>
              <input v-model="form.end_date" type="date" />
            </div>
          </div>
          <div class="form-group">
            <label>满分</label>
            <input v-model.number="form.max_score" type="number" min="1" max="200" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showModal = false">取消</button>
          <button class="btn btn-primary" @click="handleSave">{{ editing ? '保存' : '添加' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { trainingsApi } from '../api'

const trainings = ref([])
const search = ref('')
const showModal = ref(false)
const editing = ref(null)
const form = ref({ name: '', topic: '', start_date: '', end_date: '', max_score: 100 })

const filtered = computed(() => {
  if (!search.value) return trainings.value
  const q = search.value.toLowerCase()
  return trainings.value.filter(t =>
    t.name.toLowerCase().includes(q) || (t.topic || '').toLowerCase().includes(q)
  )
})

async function load() {
  const { data } = await trainingsApi.list()
  trainings.value = data
}

function openModal(training = null) {
  editing.value = training
  if (training) {
    form.value = { name: training.name, topic: training.topic, start_date: training.start_date, end_date: training.end_date, max_score: training.max_score }
  } else {
    form.value = { name: '', topic: '', start_date: '', end_date: '', max_score: 100 }
  }
  showModal.value = true
}

async function handleSave() {
  if (!form.value.name.trim()) return alert('请输入培训名称')
  if (editing.value) {
    await trainingsApi.update(editing.value.id, form.value)
  } else {
    await trainingsApi.create(form.value)
  }
  showModal.value = false
  await load()
}

async function handleDelete(training) {
  if (!confirm(`确定删除培训「${training.name}」？相关测评记录也将被删除。`)) return
  await trainingsApi.delete(training.id)
  await load()
}

onMounted(load)
</script>
