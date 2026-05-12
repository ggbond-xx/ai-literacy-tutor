<template>
  <el-container class="shell">
    <el-header class="shell-header">
      <div class="brand">基于知识图谱的《人工智能与数字素养》助学系统</div>
      <el-menu mode="horizontal" :default-active="activePath" router class="nav-menu">
        <el-menu-item v-for="item in navItems" :key="item.path" :index="item.path">{{ item.label }}</el-menu-item>
      </el-menu>
      <div class="header-actions">
        <template v-if="currentUser">
          <el-badge :value="notificationState.unreadCount" :hidden="notificationState.unreadCount === 0" class="notification-badge">
            <el-button plain @click="notificationDrawerVisible = true">消息中心</el-button>
          </el-badge>
          <div class="user-badge">
            <strong>{{ displayName }}</strong>
            <span>{{ roleLabel }}</span>
          </div>
          <el-button text @click="handleLogout">退出登录</el-button>
        </template>
        <el-button v-else text @click="router.push('/login')">登录 / 注册</el-button>
      </div>
    </el-header>
    <el-main class="shell-main">
      <slot />
    </el-main>

    <el-drawer v-model="notificationDrawerVisible" title="消息中心" size="380px">
      <div class="detail-stack">
        <div class="card-header-inline">
          <span class="detail-label">未读消息 {{ notificationState.unreadCount }} 条</span>
          <el-button text type="primary" :disabled="notificationState.unreadCount === 0" @click="handleReadAll">
            全部标记已读
          </el-button>
        </div>
        <div v-if="notificationState.items.length" class="notification-list">
          <div
            v-for="item in notificationState.items"
            :key="item.id"
            class="notification-card"
            :class="{ 'is-unread': !item.is_read }"
            @click="handleNotificationClick(item)"
          >
            <div class="card-header-inline">
              <strong>{{ item.title }}</strong>
              <el-tag v-if="!item.is_read" size="small" type="danger" effect="plain">未读</el-tag>
            </div>
            <p>{{ item.content }}</p>
            <div class="card-header-inline">
              <el-tag size="small" effect="plain">{{ notificationCategoryText[item.category] || item.category }}</el-tag>
              <span class="table-meta">{{ formatDate(item.create_time) }}</span>
            </div>
          </div>
        </div>
        <el-empty v-else description="当前没有新的站内消息。" />
      </div>
    </el-drawer>
  </el-container>
</template>

<script setup>
import { ElMessage } from "element-plus";
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { fetchNotifications, markAllNotificationsRead, markNotificationRead } from "../api/notifications";
import { clearSession, getCurrentUser } from "../utils/session";
import { roleTextMap } from "../utils/role";

const route = useRoute();
const router = useRouter();
const activePath = computed(() => route.path);
const currentUser = ref(getCurrentUser());
const notificationDrawerVisible = ref(false);
const notificationState = reactive({
  unreadCount: 0,
  items: [],
});

const roleLabel = computed(() => roleTextMap[currentUser.value?.role] || "游客");
const displayName = computed(() => currentUser.value?.profile?.real_name || currentUser.value?.username || "游客");
const notificationCategoryText = {
  discussion: "讨论动态",
  coordination: "协同事项",
  system: "系统通知",
};

const navItems = computed(() => {
  if (!currentUser.value) {
    return [
      { path: "/", label: "首页" },
      { path: "/graph", label: "图谱浏览" },
    ];
  }

  const items = [{ path: "/graph", label: "知识图谱" }];
  if (currentUser.value.role === "student") {
    items.push({ path: "/personal", label: "个人中心" });
  }
  if (currentUser.value.role === "teacher") {
    items.push({ path: "/teacher", label: "教师工作台" });
  }
  if (currentUser.value.role === "admin") {
    items.push({ path: "/admin", label: "图谱运维台" });
  }
  return items;
});

function syncCurrentUser() {
  currentUser.value = getCurrentUser();
  if (currentUser.value) {
    loadNotifications();
  } else {
    notificationState.unreadCount = 0;
    notificationState.items = [];
  }
}

function formatDate(value) {
  return value ? new Date(value).toLocaleString("zh-CN", { hour12: false }) : "";
}

async function loadNotifications() {
  if (!currentUser.value) {
    return;
  }
  try {
    const { data } = await fetchNotifications();
    notificationState.unreadCount = data.unread_count || 0;
    notificationState.items = data.items || [];
  } catch (error) {
    console.error(error);
  }
}

async function handleReadAll() {
  try {
    await markAllNotificationsRead();
    await loadNotifications();
    ElMessage.success("已全部标记为已读。");
  } catch (error) {
    console.error(error);
    ElMessage.error("更新消息状态失败，请稍后重试。");
  }
}

async function handleNotificationClick(item) {
  try {
    if (!item.is_read) {
      await markNotificationRead(item.id);
      await loadNotifications();
    }
    notificationDrawerVisible.value = false;
    if (item.link) {
      router.push(item.link);
    }
  } catch (error) {
    console.error(error);
    ElMessage.error("打开消息失败，请稍后重试。");
  }
}

function handleLogout() {
  clearSession();
  currentUser.value = null;
  notificationState.unreadCount = 0;
  notificationState.items = [];
  router.push("/");
}

onMounted(() => {
  window.addEventListener("session-updated", syncCurrentUser);
  if (currentUser.value) {
    loadNotifications();
  }
});

onBeforeUnmount(() => {
  window.removeEventListener("session-updated", syncCurrentUser);
});
</script>
