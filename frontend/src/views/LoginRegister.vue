<template>
  <AppShell>
    <div class="page-grid two-column">
      <el-card>
        <template #header>登录</template>
        <el-form label-position="top" @submit.prevent="handleLogin">
          <el-form-item label="用户名">
            <el-input v-model="loginForm.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="loginForm.password" type="password" show-password placeholder="至少 4 位字符" />
          </el-form-item>
          <el-button type="primary" class="full-width" :loading="loginLoading" @click="handleLogin">登录</el-button>
        </el-form>
      </el-card>
      <el-card>
        <template #header>注册</template>
        <el-form label-position="top" @submit.prevent="handleRegister">
          <el-form-item label="用户名">
            <el-input v-model="registerForm.username" placeholder="至少 3 位字符" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="registerForm.password" type="password" show-password placeholder="至少 4 位字符" />
          </el-form-item>
          <el-form-item label="角色">
            <el-select v-model="registerForm.role" class="full-width">
              <el-option label="学生" value="student" />
              <el-option label="教师" value="teacher" />
              <el-option label="图谱运维官" value="admin" />
            </el-select>
          </el-form-item>
          <el-button type="success" class="full-width" :loading="registerLoading" @click="handleRegister">注册并登录</el-button>
        </el-form>
      </el-card>
    </div>
  </AppShell>
</template>

<script setup>
import { ElMessage } from "element-plus";
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { loginUser, registerUser } from "../api/auth";
import AppShell from "../components/AppShell.vue";
import { getApiErrorMessage } from "../utils/apiError";
import { saveSession } from "../utils/session";

const router = useRouter();
const loginLoading = ref(false);
const registerLoading = ref(false);
const loginForm = reactive({
  username: "",
  password: "",
});

const registerForm = reactive({
  username: "",
  password: "",
  role: "student",
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
    ElMessage.success("登录成功，正在进入知识图谱。");
    router.push("/graph");
  } catch (error) {
    console.error(error);
    ElMessage.error(getApiErrorMessage(error, "登录失败，请检查用户名和密码。"));
  } finally {
    loginLoading.value = false;
  }
}

async function handleRegister() {
  const username = registerForm.username.trim();
  const password = registerForm.password.trim();

  if (!username || !password) {
    ElMessage.warning("请完整填写注册信息。");
    return;
  }

  if (username.length < 3) {
    ElMessage.warning("用户名至少需要 3 位字符。");
    return;
  }

  if (password.length < 4) {
    ElMessage.warning("密码至少需要 4 位字符。");
    return;
  }

  try {
    registerLoading.value = true;
    await registerUser({
      username,
      password,
      role: registerForm.role,
    });
    const { data } = await loginUser({ username, password });
    saveSession(data.access_token, data.user);
    ElMessage.success("注册并登录成功，正在进入知识图谱。");
    router.push("/graph");
  } catch (error) {
    console.error(error);
    ElMessage.error(getApiErrorMessage(error, "注册失败，请稍后重试。"));
  } finally {
    registerLoading.value = false;
  }
}
</script>
