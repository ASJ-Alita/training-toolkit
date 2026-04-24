<template>
  <div>
    <div class="page-header">
      <h2>👥 学员管理</h2>
      <p>管理参训学员信息</p>
    </div>

    <div class="toolbar">
      <input
        v-model="search"
        type="text"
        placeholder="搜索学员姓名 / 部门..."
        style="padding:8px 14px;border:1px solid var(--border);border-radius:8px;width:260px;font-size:13px;"
      />
      <button class="btn btn-primary" @click="openModal()">＋ 添加学员</button>
    </div>

    <div class="card">
      <table v-if="filtered.length" class="data-table">
        <thead>
          <tr>
            <th>姓名</th>
            <th>部门</th>
            <th>岗位</th>
            <th>邮箱</th>
            <th>状态</th>
            <th>创建日期</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in filtered" :key="s.id">
            <td><strong>{{ s.name }}</strong></td>
            <td>{{ s.dept || '-' }}</td>
            <td>{{ s.position || '-' }}</td>
            <td>{{ s.email || '-' }}</td>
            <td>
              <span class="tag" :class="s.status === 'active' ? 'tag-success' : 'tag-warning'">
                {{ s.status === 'active' ? '活跃' : '停用' }}
              </span>
            </td>
            <td>{{ s.created_at }}</td>
            <td>
              <button class="btn btn-outline btn-sm" @click="openModal(s)">编辑</button>
              <button class="btn btn-danger btn-sm" @click="handleDelete(s)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state">
        <div class="icon">📭</div>
        <p>暂无学员数据</p>
      </div>
    </div>

    <!-- 添加/编辑模态框 -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editing ? '编辑学员' : '添加学员' }}</h3>
          <button class="modal-close" @click="showModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>姓名 *</label>
            <input v-model="form.name" placeholder="请输入学员姓名" />
          </div>
          <div class="form-group">
            <label>部门</label>
            <input v-model="form.dept" placeholder="如：销售部" />
          </div>
          <div class="form-group">
            <label>岗位</label>
            <input v-model="form.position" placeholder="如：销售代表" />
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input v-model="form.email" placeholder="name@company.com" />
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
import { studentsApi } from '../api'

const students = ref([])
const search = ref('')
const showModal = ref(false)
const editing = ref(null)
const form = ref({ name: '', dept: '', position: '', email: '' })

const filtered = computed(() => {
  if (!search.value) return students.value
  const q = search.value.toLowerCase()
  return students.value.filter(s =>
    s.name.toLowerCase().includes(q) || (s.dept || '').toLowerCase().includes(q)
  )
})

async function load() {
  const { data } = await studentsApi.list()
  students.value = data
}

function openModal(student = null) {
  editing.value = student
  if (student) {
    form.value = { name: student.name, dept: student.dept, position: student.position, email: student.email }
  } else {
    form.value = { name: '', dept: '', position: '', email: '' }
  }
  showModal.value = true
}

async function handleSave() {
  if (!form.value.name.trim()) return alert('请输入学员姓名')
  if (editing.value) {
    await studentsApi.update(editing.value.id, form.value)
  } else {
    await studentsApi.create(form.value)
  }
  showModal.value = false
  await load()
}

async function handleDelete(student) {
  if (!confirm(`确定删除学员「${student.name}」？相关测评记录也将被删除。`)) return
  await studentsApi.delete(student.id)
  await load()
}

onMounted(load)
</script>
