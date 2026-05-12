<template>
  <div class="auth-page">
    <div class="auth-panel">
      <div class="auth-copy">
        <p class="eyebrow">Password Help</p>
        <h1>找回密码</h1>
        <p>当前版本提供演示级功能，你可以通过图谱运维官重置账号密码，或重新注册新的演示账号。</p>
      </div>

      <el-card class="auth-card">
        <template #header>密码找回说明</template>
        <el-alert
          title="如需正式找回密码，可在后续版本接入邮箱验证码或图谱运维官审核流程。"
          type="info"
          :closable="false"
          show-icon
        />
        <div class="forgot-actions">
          <el-button type="primary" @click="router.push('/login')">返回登录</el-button>
          <el-button @click="router.push('/register')">去注册新账号</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();
</script>
