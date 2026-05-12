<template>
  <AppShell>
    <section class="hero">
      <div>
        <p class="eyebrow">Knowledge Graph Powered Learning</p>
        <h1>基于知识图谱的《人工智能与数字素养》助学系统</h1>
        <p class="hero-text">
          首页面向游客开放。你可以先进入知识图谱整体浏览课程结构，也可以登录后进入学生、教师或图谱运维官的专属工作空间。
        </p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="$router.push('/graph')">进入图谱浏览</el-button>
          <el-button size="large" @click="$router.push('/login')">登录 / 注册</el-button>
        </div>
      </div>
      <el-card class="highlight-card">
        <template #header>核心能力</template>
        <ul class="feature-list">
          <li>游客可浏览完整知识图谱结构与关系</li>
          <li>学生登录后可学习节点内容、参与讨论与自测</li>
          <li>教师可围绕学生问题、班级讨论与教学协同开展管理</li>
          <li>图谱运维官可处理账号、讨论治理与系统参数配置</li>
        </ul>
      </el-card>
    </section>
  </AppShell>
</template>

<script setup>
import AppShell from "../components/AppShell.vue";
</script>
