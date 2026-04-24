<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <h1>Training Toolkit</h1>
        <p>企业培训效果追踪系统</p>
      </div>

      <!-- 登录 / 注册 切换 -->
      <div class="tab-bar">
        <button :class="{ active: mode === 'login' }" @click="mode = 'login'">登录</button>
        <button :class="{ active: mode === 'register' }" @click="mode = 'register'">注册</button>
      </div>

      <!-- 错误提示 -->
      <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>

      <!-- 登录表单 -->
      <form v-if="mode === 'login'" @submit.prevent="handleLogin">
        <div class="form-group">
          <label>用户名</label>
          <input v-model="form.username" type="text" placeholder="请输入用户名" required autocomplete="username" />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="form.password" type="password" placeholder="请输入密码" required autocomplete="current-password" />
        </div>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? '登录中...' : '登 录' }}
        </button>
      </form>

      <!-- 注册表单 -->
      <form v-else @submit.prevent="handleRegister">
        <div class="form-group">
          <label>用户名 <span class="hint">（字母/数字/下划线）</span></label>
          <input v-model="form.username" type="text" placeholder="3-50位" required pattern="[a-zA-Z0-9_]{3,50}" autocomplete="username" />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="form.password" type="password" placeholder="至少4位" required minlength="4" autocomplete="new-password" />
        </div>
        <div class="form-group">
          <label>昵称</label>
          <input v-model="form.display_name" type="text" placeholder="选填" />
        </div>
        <div class="form-group">
          <label>角色</label>
          <select v-model="form.role">
            <option value="student">学员</option>
            <option value="admin">管理员</option>
          </select>
        </div>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? '注册中...' : '注 册' }}
        </button>
      </form>

      <!-- 默认账号提示 -->
      <div class="hint-box">
        <p><strong>默认管理员</strong>：admin / admin123</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const mode = ref('login')
const loading = ref(false)
const errorMsg = ref('')

const form = reactive({
  username: '',
  password: '',
  display_name: '',
  role: 'student',
})

async function handleLogin() {
  errorMsg.value = ''
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    router.push('/')
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  errorMsg.value = ''
  loading.value = true
  try {
    await auth.register({ ...form })
    // 注册成功后自动登录
    await auth.login(form.username, form.password)
    router.push('/')
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  padding: 20px;
}

.login-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 420px;
  padding: 40px 36px;
}

.login-header {
  text-align: center;
  margin-bottom: 28px;
}

.login-header h1 {
  font-size: 24px;
  color: #1a1a2e;
  margin: 0 0 4px;
}

.login-header p {
  font-size: 14px;
  color: #888;
  margin: 0;
}

.tab-bar {
  display: flex;
  border-bottom: 2px solid #eee;
  margin-bottom: 24px;
}

.tab-bar button {
  flex: 1;
  padding: 10px;
  border: none;
  background: none;
  font-size: 15px;
  color: #999;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
}

.tab-bar button.active {
  color: #4361ee;
  border-bottom-color: #4361ee;
  font-weight: 600;
}

.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  font-size: 13px;
  color: #555;
  margin-bottom: 6px;
  font-weight: 500;
}

.form-group .hint {
  font-size: 11px;
  color: #aaa;
  font-weight: 400;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #4361ee;
  box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.1);
}

.btn-primary {
  width: 100%;
  padding: 12px;
  background: #4361ee;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #3a56d4;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-msg {
  background: #fff2f2;
  color: #e74c3c;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 16px;
}

.hint-box {
  margin-top: 20px;
  padding: 12px;
  background: #f8f9ff;
  border-radius: 8px;
  text-align: center;
}

.hint-box p {
  margin: 0;
  font-size: 13px;
  color: #666;
}
</style>
