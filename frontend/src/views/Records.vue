<template>
  <div>
    <div class="page-header">
      <h2>📝 测评记录</h2>
      <p>管理培训前后测及里程碑记录</p>
    </div>

    <div class="toolbar">
      <div style="display:flex;gap:12px;">
        <select v-model="filterStudent" style="padding:8px 12px;border:1px solid var(--border);border-radius:8px;font-size:13px;">
          <option value="">全部学员</option>
          <option v-for="s in students" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
        <select v-model="filterTraining" style="padding:8px 12px;border:1px solid var(--border);border-radius:8px;font-size:13px;">
          <option value="">全部培训</option>
          <option v-for="t in trainings" :key="t.id" :value="t.id">{{ t.name }}</option>
        </select>
      </div>
      <button class="btn btn-primary" @click="openModal()">＋ 添加记录</button>
    </div>

    <div class="card">
      <table v-if="records.length" class="data-table">
        <thead>
          <tr>
            <th>学员</th>
            <th>培训</th>
            <th>类型</th>
            <th>成绩</th>
            <th>备注</th>
            <th>日期</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in records" :key="r.id">
            <td>{{ r.student?.name || r.student_id }}</td>
            <td>{{ r.training?.name || r.training_id }}</td>
            <td>
              <span class="tag" :class="r.type === 'pre' ? 'tag-info' : r.type === 'post' ? 'tag-success' : 'tag-warning'">
                {{ r.type === 'pre' ? '前测' : r.type === 'post' ? '后测' : '里程碑' }}
              </span>
            </td>
            <td><strong>{{ r.score }}</strong></td>
            <td>{{ r.notes || '-' }}</td>
            <td>{{ r.date }}</td>
            <td>
              <button class="btn btn-danger btn-sm" @click="handleDelete(r)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state">
        <div class="icon">📭</div>
        <p>暂无测评记录</p>
      </div>
    </div>

    <!-- 模态框 -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>添加测评记录</h3>
          <button class="modal-close" @click="showModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>学员 *</label>
            <select v-model="form.student_id">
              <option value="">请选择学员</option>
              <option v-for="s in students" :key="s.id" :value="s.id">{{ s.name }} ({{ s.dept }})</option>
            </select>
          </div>
          <div class="form-group">
            <label>培训 *</label>
            <select v-model="form.training_id">
              <option value="">请选择培训</option>
              <option v-for="t in trainings" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
            <div class="form-group">
              <label>记录类型 *</label>
              <select v-model="form.type">
                <option value="pre">前测</option>
                <option value="post">后测</option>
                <option value="milestone">里程碑</option>
              </select>
            </div>
            <div class="form-group">
              <label>成绩 *</label>
              <input v-model.number="form.score" type="number" min="0" max="200" placeholder="0-100" />
            </div>
          </div>
          <div class="form-group">
            <label>备注</label>
            <textarea v-model="form.notes" rows="2" placeholder="可选备注信息..."></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showModal = false">取消</button>
          <button class="btn btn-primary" @click="handleSave">添加</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { recordsApi, studentsApi, trainingsApi } from '../api'

const records = ref([])
const students = ref([])
const trainings = ref([])
const filterStudent = ref('')
const filterTraining = ref('')
const showModal = ref(false)
const form = ref({ student_id: '', training_id: '', type: 'pre', score: '', notes: '' })

async function load() {
  const params = {}
  if (filterStudent.value) params.student_id = filterStudent.value
  if (filterTraining.value) params.training_id = filterTraining.value
  const { data } = await recordsApi.list(params)
  records.value = data
}

async function loadOptions() {
  const [s, t] = await Promise.all([studentsApi.list(), trainingsApi.list()])
  students.value = s.data
  trainings.value = t.data
}

watch(filterStudent, load)
watch(filterTraining, load)

function openModal() {
  form.value = { student_id: '', training_id: '', type: 'pre', score: '', notes: '' }
  showModal.value = true
}

async function handleSave() {
  if (!form.value.student_id || !form.value.training_id) return alert('请选择学员和培训')
  if (form.value.score === '' || form.value.score < 0) return alert('请输入有效成绩')
  await recordsApi.create({ ...form.value, score: Number(form.value.score) })
  showModal.value = false
  await load()
}

async function handleDelete(record) {
  if (!confirm('确定删除该测评记录？')) return
  await recordsApi.delete(record.id)
  await load()
}

onMounted(() => {
  loadOptions()
  load()
})
</script>
