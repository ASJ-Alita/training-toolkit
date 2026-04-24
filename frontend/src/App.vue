<template>
  <!-- 未登录 → 仅显示 Login 页面，不渲染侧边栏 -->
  <router-view v-if="!auth.isLoggedIn" />

  <!-- 已登录 → 侧边栏 + 主内容 -->
  <template v-else>
    <nav class="sidebar">
      <div class="sidebar-brand">
        <h1>Training Toolkit</h1>
        <p>企业培训效果追踪</p>
      </div>

      <div class="sidebar-nav">
        <router-link to="/">
          <span class="nav-icon">📊</span>
          <span>仪表盘</span>
        </router-link>

        <!-- 管理员菜单 -->
        <template v-if="auth.isAdmin">
          <router-link to="/students">
            <span class="nav-icon">👥</span>
            <span>学员管理</span>
          </router-link>
          <router-link to="/trainings">
            <span class="nav-icon">📚</span>
            <span>培训管理</span>
          </router-link>
        </template>

        <router-link to="/records">
          <span class="nav-icon">📝</span>
          <span>测评记录</span>
        </router-link>

        <div class="nav-divider"></div>

        <router-link to="/evaluation">
          <span class="nav-icon">🎓</span>
          <span>柯氏评估</span>
        </router-link>
        <router-link to="/knowledge-base">
          <span class="nav-icon">🤖</span>
          <span>知识库问答</span>
        </router-link>
      </div>

      <!-- 底部用户信息 -->
      <div class="sidebar-footer">
        <div class="user-info">
          <span class="user-avatar">{{ auth.displayName.charAt(0).toUpperCase() }}</span>
          <div class="user-detail">
            <span class="user-name">{{ auth.displayName }}</span>
            <span class="user-role">{{ auth.isAdmin ? '管理员' : '学员' }}</span>
          </div>
        </div>
        <button class="logout-btn" @click="handleLogout" title="退出登录">⏻</button>
      </div>
    </nav>

    <main class="main-content">
      <router-view />
    </main>
  </template>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const router = useRouter()
const auth = useAuthStore()

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>
