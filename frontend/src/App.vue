<template>
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
      <router-link to="/students">
        <span class="nav-icon">👥</span>
        <span>学员管理</span>
      </router-link>
      <router-link to="/trainings">
        <span class="nav-icon">📚</span>
        <span>培训管理</span>
      </router-link>
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
  </nav>
  <main class="main-content">
    <router-view />
  </main>
</template>
