<template>
  <div class="auth-page">
    <div class="auth-panel auth-panel-wide">
      <div class="auth-copy">
        <p class="eyebrow">Create Account</p>
        <h1>创建你的学习档案</h1>
        <p>
          完整填写注册信息后，系统会在个人中心展示基础资料，并结合知识图谱生成学习画像。
        </p>
      </div>

      <el-card class="auth-card">
        <template #header>学生注册</template>
        <el-form label-position="top" @submit.prevent="handleRegister">
          <div class="auth-form-grid">
            <el-form-item label="用户名">
              <el-input v-model="registerForm.username" placeholder="至少 3 位字符" />
            </el-form-item>
            <el-form-item label="角色">
              <el-select v-model="registerForm.role" class="full-width">
                <el-option label="学生" value="student" />
                <el-option label="教师" value="teacher" />
                <el-option label="图谱运维官" value="admin" />
              </el-select>
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="registerForm.password" type="password" show-password placeholder="至少 4 位字符" />
            </el-form-item>
            <el-form-item label="确认密码">
              <el-input v-model="registerForm.confirmPassword" type="password" show-password placeholder="请再次输入密码" />
            </el-form-item>
            <el-form-item label="真实姓名">
              <el-input v-model="registerForm.real_name" placeholder="例如：张三" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="registerForm.email" placeholder="例如：student@example.com" />
            </el-form-item>
            <el-form-item label="学校">
              <el-input v-model="registerForm.school" placeholder="例如：某某大学" />
            </el-form-item>
            <el-form-item label="专业">
              <el-input v-model="registerForm.major" placeholder="例如：教育技术学" />
            </el-form-item>
            <el-form-item label="年级">
              <el-input v-model="registerForm.grade" placeholder="例如：2023级" />
            </el-form-item>
            <el-form-item label="学号 / 工号">
              <el-input v-model="registerForm.student_no" placeholder="用于展示在个人中心" />
            </el-form-item>
            <el-form-item label="班级">
              <el-input v-model="registerForm.class_name" placeholder="例如：数媒 1 班" />
            </el-form-item>
            <el-form-item label="个人简介">
              <el-input v-model="registerForm.bio" placeholder="可填写研究兴趣、学习目标等" />
            </el-form-item>
          </div>
          <div class="auth-links">
            <router-link to="/login">返回登录</router-link>
            <router-link to="/forgot-password">忘记密码</router-link>
          </div>
          <el-button type="primary" class="full-width" :loading="registerLoading" @click="handleRegister">注册并登录</el-button>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ElMessage } from "element-plus";
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { loginUser, registerUser } from "../api/auth";
import { getApiErrorMessage } from "../utils/apiError";
import { saveSession } from "../utils/session";
import { getDefaultRouteByRole } from "../utils/role";

const router = useRouter();
const registerLoading = ref(false);
const registerForm = reactive({
  username: "",
  password: "",
  confirmPassword: "",
  role: "student",
  real_name: "",
  email: "",
  school: "",
  major: "",
  grade: "",
  student_no: "",
  class_name: "",
  bio: "",
});

async function handleRegister() {
  const username = registerForm.username.trim();
  const password = registerForm.password.trim();

  if (!username || !password) {
    ElMessage.warning("请完整填写用户名和密码。");
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

  if (password !== registerForm.confirmPassword.trim()) {
    ElMessage.warning("两次输入的密码不一致。");
    return;
  }

  try {
    registerLoading.value = true;
    await registerUser({
      username,
      password,
      role: registerForm.role,
      profile: {
        real_name: registerForm.real_name.trim() || null,
        email: registerForm.email.trim() || null,
        school: registerForm.school.trim() || null,
        major: registerForm.major.trim() || null,
        grade: registerForm.grade.trim() || null,
        student_no: registerForm.student_no.trim() || null,
        class_name: registerForm.class_name.trim() || null,
        bio: registerForm.bio.trim() || null,
      },
    });
    const { data } = await loginUser({ username, password });
    saveSession(data.access_token, data.user);
    ElMessage.success("注册并登录成功，正在进入对应工作台。");
    router.push(getDefaultRouteByRole(data.user.role));
  } catch (error) {
    console.error(error);
    ElMessage.error(getApiErrorMessage(error, "注册失败，请稍后重试。"));
  } finally {
    registerLoading.value = false;
  }
}
</script>
