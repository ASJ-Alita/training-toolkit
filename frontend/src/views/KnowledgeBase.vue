<template>
  <div class="rag-page">
    <div class="page-header">
      <h1>📚 RAG 知识库问答</h1>
      <p>Retrieval-Augmented Generation · 基于检索增强的智能问答</p>
    </div>

    <div class="tab-bar">
      <button :class="['tab-btn', { active: activeTab === 'kb' }]" @click="activeTab = 'kb'">📂 知识库管理</button>
      <button :class="['tab-btn', { active: activeTab === 'qa' }]" @click="activeTab = 'qa'">💬 智能问答</button>
    </div>

    <!-- 知识库管理 -->
    <div v-if="activeTab === 'kb'" class="tab-content">
      <!-- API 设置 -->
      <div class="section">
        <div class="section-header">⚙️ API 设置</div>
        <div class="config-row">
          <div class="config-item">
            <label>选择大模型</label>
            <select v-model="ragConfig.llm_provider">
              <option v-for="(name, key) in ragConfig.llm_providers" :key="key" :value="key">{{ name }}</option>
            </select>
          </div>
          <div class="config-item">
            <label>API Key</label>
            <input type="password" v-model="ragConfig.api_key" placeholder="输入 API Key" />
          </div>
          <button class="btn btn-primary" @click="saveConfig">💾 保存配置</button>
        </div>
      </div>

      <!-- 上传文档 -->
      <div class="section">
        <div class="section-header">📤 上传文档到知识库</div>
        <div class="upload-area">
          <div class="upload-info">
            <p><strong>支持的格式：</strong>.txt / .pdf / .docx</p>
            <p><strong>处理流程：</strong>上传文件 → 文本提取 → 智能分块 → 向量化存储</p>
            <p><strong>分块设置：</strong>块大小 400 字符 / 重叠 80 字符 / BGE-M3 向量模型</p>
          </div>
          <div class="upload-box" @dragover.prevent @drop.prevent="handleDrop" @click="$refs.fileInput.click()">
            <input ref="fileInput" type="file" multiple accept=".txt,.pdf,.docx" style="display:none" @change="handleFiles" />
            <div class="upload-icon">📁</div>
            <p>拖拽文件到此处，或点击选择文件</p>
          </div>
          <div v-if="uploading" class="upload-progress">
            <div class="progress-bar"><div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div></div>
            <p>{{ uploadStatus }}</p>
          </div>
        </div>
      </div>

      <!-- 知识库状态 -->
      <div class="section">
        <div class="section-header">📊 知识库状态</div>
        <div class="stats-grid">
          <div class="stat-card"><div class="stat-value">{{ kbStats.total_documents || 0 }}</div><div class="stat-label">文档数</div></div>
          <div class="stat-card"><div class="stat-value">{{ kbStats.total_chunks || 0 }}</div><div class="stat-label">文本块</div></div>
          <div class="stat-card"><div class="stat-value">{{ kbStats.dimension || 1024 }}</div><div class="stat-label">向量维度</div></div>
          <div class="stat-card"><div class="stat-value">BGE-M3</div><div class="stat-label">向量模型</div></div>
        </div>
        <div class="clear-row">
          <button class="btn btn-danger" @click="clearKB" :disabled="!kbStats.total_documents">🗑️ 清空知识库</button>
        </div>
      </div>

      <!-- 文档列表 -->
      <div class="section">
        <div class="section-header">📄 已入库文档</div>
        <div v-if="documents.length > 0" class="doc-list">
          <div v-for="doc in documents" :key="doc.id" class="doc-item">
            <span class="doc-name">📄 {{ doc.filename }}</span>
            <span class="doc-info">{{ (doc.file_size / 1024).toFixed(1) }} KB · {{ doc.chunks_count }} 块 · {{ doc.created_at }}</span>
            <button class="btn btn-danger btn-sm" @click="deleteDoc(doc.id)">删除</button>
          </div>
        </div>
        <div v-else class="empty-hint">📭 知识库为空，请上传文档后开始问答</div>
      </div>
    </div>

    <!-- 智能问答 -->
    <div v-if="activeTab === 'qa'" class="tab-content">
      <!-- 配置提示 -->
      <div v-if="!ragConfig.api_key_set" class="warning-box">
        ⚠️ 请先在「知识库管理」中配置 API Key
      </div>

      <!-- 对话区域 -->
      <div class="chat-container" ref="chatContainer">
        <div v-for="(msg, idx) in messages" :key="idx" :class="['chat-msg', msg.role]">
          <div class="msg-bubble">
            <p v-html="formatAnswer(msg.content)"></p>
            <div v-if="msg.sources && msg.sources.length > 0" class="sources-section">
              <div class="sources-toggle" @click="toggleSources(idx)">
                📌 查看参考来源（{{ msg.sources.length }}条）
              </div>
              <div v-if="expandedSources.includes(idx)" class="sources-list">
                <div v-for="(s, si) in msg.sources" :key="si" class="source-card">
                  <div class="source-header">
                    <strong>来源{{ si + 1 }}</strong>：{{ s.source }} &nbsp;|&nbsp; 相关度：{{ (s.score * 100).toFixed(0) }}%
                  </div>
                  <div class="source-text">{{ s.text }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="loading" class="chat-msg assistant">
          <div class="msg-bubble typing">
            <span class="dot"></span><span class="dot"></span><span class="dot"></span>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <input v-model="question" @keyup.enter="sendQuestion" placeholder="输入您的问题..." :disabled="loading" />
        <button class="btn btn-primary" @click="sendQuestion" :disabled="loading || !question.trim()">🚀 提问</button>
        <button class="btn btn-gray" @click="clearChat">🗑️ 清空对话</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import api from '../api'

const activeTab = ref('kb')
const ragConfig = reactive({ llm_provider: 'siliconflow', llm_providers: {}, api_key: '', api_key_set: false })
const kbStats = ref({})
const documents = ref([])
const messages = ref([])
const question = ref('')
const loading = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')
const expandedSources = ref([])
const chatContainer = ref(null)

onMounted(async () => {
  await loadConfig()
  await loadKBStats()
  await loadDocuments()
  await loadChatHistory()
})

async function loadConfig() {
  const res = await api.get('/api/rag/config')
  Object.assign(ragConfig, res.data)
}

async function saveConfig() {
  await api.post('/api/rag/config', { llm_provider: ragConfig.llm_provider, api_key: ragConfig.api_key })
  alert('✅ 配置已保存')
  await loadConfig()
}

async function loadKBStats() {
  const res = await api.get('/api/rag/stats')
  kbStats.value = res.data
}

async function loadDocuments() {
  const res = await api.get('/api/rag/documents')
  documents.value = res.data
}

async function handleFiles(e) {
  const files = e.target.files || e.dataTransfer?.files
  if (!files || files.length === 0) return
  await uploadFiles(Array.from(files))
}

async function handleDrop(e) {
  const files = e.dataTransfer?.files
  if (files) await uploadFiles(Array.from(files))
}

async function uploadFiles(files) {
  uploading.value = true
  uploadProgress.value = 0
  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    uploadStatus.value = `正在处理：${file.name}（${i + 1}/${files.length}）`
    const formData = new FormData()
    formData.append('file', file)
    try {
      await api.post('/api/rag/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
      uploadProgress.value = Math.round((i + 1) / files.length * 100)
    } catch (err) {
      alert(`❌ ${file.name} 上传失败：${err.response?.data?.detail || err.message}`)
    }
  }
  uploading.value = false
  uploadStatus.value = ''
  await loadKBStats()
  await loadDocuments()
}

async function deleteDoc(id) {
  if (!confirm('确定删除该文档？')) return
  await api.delete(`/api/rag/documents/${id}`)
  await loadKBStats()
  await loadDocuments()
}

async function clearKB() {
  if (!confirm('⚠️ 确定要清空知识库吗？此操作不可恢复！')) return
  await api.delete('/api/rag/clear')
  await loadKBStats()
  await loadDocuments()
}

async function loadChatHistory() {
  try {
    const res = await api.get('/api/rag/chat/history/default')
    messages.value = res.data
  } catch { /* ignore */ }
}

async function sendQuestion() {
  if (!question.value.trim() || loading.value) return
  const q = question.value.trim()
  messages.value.push({ role: 'user', content: q })
  question.value = ''
  loading.value = true
  await nextTick()
  scrollToBottom()

  try {
    const res = await api.post('/api/rag/chat', { question: q, session_id: 'default' })
    messages.value.push({ role: 'assistant', content: res.data.answer, sources: res.data.sources })
  } catch (err) {
    messages.value.push({ role: 'assistant', content: `❌ 问答失败：${err.response?.data?.detail || err.message}`, sources: [] })
  }
  loading.value = false
  await nextTick()
  scrollToBottom()
}

async function clearChat() {
  messages.value = []
  try { await api.delete('/api/rag/chat/history/default') } catch { /* ignore */ }
}

function toggleSources(idx) {
  const i = expandedSources.value.indexOf(idx)
  if (i >= 0) expandedSources.value.splice(i, 1)
  else expandedSources.value.push(idx)
}

function scrollToBottom() {
  if (chatContainer.value) chatContainer.value.scrollTop = chatContainer.value.scrollHeight
}

function formatAnswer(text) {
  return text.replace(/\n/g, '<br>')
}
</script>

<style scoped>
.rag-page { padding: 0; }
.page-header { text-align: center; padding: 20px 0 16px; }
.page-header h1 { color: #1e293b; margin: 0; font-size: 24px; }
.page-header p { color: #64748b; margin: 4px 0 0; font-size: 13px; }

.tab-bar { display: flex; gap: 4px; background: #e2e8f0; border-radius: 10px; padding: 4px; margin-bottom: 20px; }
.tab-btn { flex: 1; padding: 10px; border: none; background: transparent; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; color: #64748b; transition: all .2s; }
.tab-btn.active { background: white; color: #4f46e5; box-shadow: 0 2px 8px rgba(0,0,0,.1); }

.section { background: white; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,.06); }
.section-header { font-weight: 600; font-size: 15px; color: #1e293b; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 2px solid #f1f5f9; }

.config-row { display: flex; align-items: flex-end; gap: 12px; flex-wrap: wrap; }
.config-item { display: flex; flex-direction: column; gap: 4px; }
.config-item label { font-size: 12px; color: #64748b; font-weight: 500; }
.config-item select, .config-item input { padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 13px; min-width: 180px; }

.upload-area { padding: 8px 0; }
.upload-info { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 16px; }
.upload-info p { font-size: 13px; color: #475569; }
.upload-box { border: 2px dashed #cbd5e1; border-radius: 12px; padding: 40px; text-align: center; cursor: pointer; transition: all .2s; }
.upload-box:hover { border-color: #4f46e5; background: #f5f3ff; }
.upload-icon { font-size: 40px; margin-bottom: 8px; }
.upload-box p { color: #64748b; font-size: 14px; }

.upload-progress { margin-top: 12px; }
.progress-bar { background: #e2e8f0; border-radius: 8px; height: 8px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #4f46e5, #7c3aed); border-radius: 8px; transition: width .3s; }
.upload-progress p { font-size: 12px; color: #64748b; margin-top: 6px; }

.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
.stat-card { background: #f8fafc; border-radius: 10px; padding: 16px; text-align: center; }
.stat-value { font-size: 28px; font-weight: 700; color: #1e293b; }
.stat-label { font-size: 12px; color: #94a3b8; margin-top: 4px; }
.clear-row { text-align: right; }

.doc-list { display: flex; flex-direction: column; gap: 6px; }
.doc-item { display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: #f8fafc; border-radius: 8px; }
.doc-name { flex: 1; font-size: 13px; font-weight: 500; }
.doc-info { font-size: 12px; color: #94a3b8; }

.empty-hint { text-align: center; padding: 30px; color: #94a3b8; font-size: 14px; }

.warning-box { background: #fef3c7; border: 1px solid #fbbf24; border-radius: 10px; padding: 14px 20px; color: #92400e; font-size: 14px; margin-bottom: 16px; }

.chat-container { background: white; border-radius: 12px; padding: 20px; min-height: 400px; max-height: 500px; overflow-y: auto; box-shadow: 0 1px 4px rgba(0,0,0,.06); margin-bottom: 12px; }

.chat-msg { display: flex; margin-bottom: 12px; }
.chat-msg.user { justify-content: flex-end; }
.chat-msg.assistant { justify-content: flex-start; }

.msg-bubble { max-width: 75%; padding: 12px 16px; border-radius: 16px; font-size: 14px; line-height: 1.6; }
.chat-msg.user .msg-bubble { background: #4f46e5; color: white; border-radius: 16px 4px 16px 16px; }
.chat-msg.assistant .msg-bubble { background: white; color: #1e293b; border: 1px solid #e2e8f0; border-radius: 16px 16px 4px 16px; }

.typing { padding: 16px 24px; display: flex; gap: 6px; }
.dot { width: 8px; height: 8px; background: #94a3b8; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out; }
.dot:nth-child(2) { animation-delay: .2s; }
.dot:nth-child(3) { animation-delay: .4s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0.6); } 40% { transform: scale(1); } }

.sources-section { margin-top: 8px; }
.sources-toggle { font-size: 12px; color: #4f46e5; cursor: pointer; padding: 4px 0; }
.sources-list { margin-top: 8px; }
.source-card { background: #f8fafc; border-radius: 8px; padding: 10px 14px; margin-bottom: 6px; border-left: 3px solid #94a3b8; }
.source-header { font-size: 12px; color: #475569; margin-bottom: 4px; }
.source-text { font-size: 12px; color: #64748b; line-height: 1.5; }

.chat-input-area { display: flex; gap: 8px; align-items: center; }
.chat-input-area input { flex: 1; padding: 12px 16px; border: 2px solid #e2e8f0; border-radius: 12px; font-size: 14px; outline: none; transition: border-color .2s; }
.chat-input-area input:focus { border-color: #4f46e5; }

.btn { padding: 8px 16px; border: none; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 500; transition: all .2s; }
.btn:disabled { opacity: .5; cursor: not-allowed; }
.btn-primary { background: #4f46e5; color: white; }
.btn-primary:hover { background: #4338ca; }
.btn-danger { background: #e74c3c; color: white; }
.btn-gray { background: #94a3b8; color: white; }
.btn-sm { padding: 4px 10px; font-size: 12px; }

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .upload-info { grid-template-columns: 1fr; }
  .msg-bubble { max-width: 90%; }
}
</style>
