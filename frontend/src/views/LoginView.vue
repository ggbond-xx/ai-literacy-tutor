<template>
  <div class="auth-page">
    <div class="auth-panel">
      <div class="auth-copy">
        <p class="eyebrow">AI Literacy Tutor</p>
        <h1>欢迎回到助学系统</h1>
        <p>
          登录后可继续浏览知识图谱、记录掌握程度、查看薄弱点分析和个性化学习路径。
        </p>
      </div>

      <el-card class="auth-card">
        <template #header>账号登录</template>
        <el-form label-position="top" @submit.prevent="handleLogin">
          <el-form-item label="用户名">
            <el-input v-model="loginForm.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="loginForm.password" type="password" show-password placeholder="至少 4 位字符" />
          </el-form-item>
          <div class="auth-links">
            <router-link to="/forgot-password">找回密码</router-link>
            <router-link to="/register">立即注册</router-link>
          </div>
          <el-button type="primary" class="full-width" :loading="loginLoading" @click="handleLogin">登录</el-button>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ElMessage } from "element-plus";
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { loginUser } from "../api/auth";
import { getApiErrorMessage } from "../utils/apiError";
import { saveSession } from "../utils/session";
import { getDefaultRouteByRole } from "../utils/role";

const router = useRouter();
const loginLoading = ref(false);
const loginForm = reactive({
  username: "",
  password: "",
});

async function handleLogin() {
  const username = loginForm.username.trim();
  const password = loginForm.password.trim();

  if (!username || !password) {
    ElMessage.warning("请输入用户名和密码。");
    return;
  }

  if (password.length < 4) {
    ElMessage.warning("密码至少需要 4 位字符。");
    return;
  }

  try {
    loginLoading.value = true;
    const { data } = await loginUser({ username, password });
    saveSession(data.access_token, data.user);
    ElMessage.success("登录成功，正在进入对应工作台。");
    router.push(getDefaultRouteByRole(data.user.role));
  } catch (error) {
    console.error(error);
    ElMessage.error(getApiErrorMessage(error, "登录失败，请检查用户名和密码。"));
  } finally {
    loginLoading.value = false;
  }
}
</script>
