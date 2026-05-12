<template>
  <AppShell>
    <div class="workspace-page">
      <el-tabs v-model="activeAdminTab" class="workspace-tabs">
        <el-tab-pane label="账号管理" name="users">
          <el-card class="workspace-panel admin-user-card">
            <template #header>
              <div class="card-header-inline">
                <span>账号管理</span>
                <el-button type="primary" plain @click="openCreateDialog">新增账号</el-button>
              </div>
            </template>

            <div class="summary-row">
              <div class="summary-metric clickable-metric" :class="{ 'is-active-filter': adminUserRoleFilter === 'all' }" @click="adminUserRoleFilter = 'all'"><span>总用户数</span><strong>{{ overview.total_users }}</strong></div>
              <div class="summary-metric clickable-metric" :class="{ 'is-active-filter': adminUserRoleFilter === 'student' }" @click="adminUserRoleFilter = 'student'"><span>学生数</span><strong>{{ overview.role_counts.student || 0 }}</strong></div>
              <div class="summary-metric clickable-metric" :class="{ 'is-active-filter': adminUserRoleFilter === 'teacher' }" @click="adminUserRoleFilter = 'teacher'"><span>教师数</span><strong>{{ overview.role_counts.teacher || 0 }}</strong></div>
              <div class="summary-metric clickable-metric" :class="{ 'is-active-filter': adminUserRoleFilter === 'admin' }" @click="adminUserRoleFilter = 'admin'"><span>图谱运维官</span><strong>{{ overview.role_counts.admin || 0 }}</strong></div>
            </div>

            <el-table :data="filteredAdminUsers" size="small" empty-text="暂无用户数据">
              <el-table-column label="账号" min-width="150">
                <template #default="{ row }">
                  <strong>{{ row.profile?.real_name || row.username }}</strong>
                  <p class="table-meta">{{ row.username }}</p>
                </template>
              </el-table-column>
              <el-table-column label="角色" width="130">
                <template #default="{ row }">
                  <el-tag effect="plain">{{ roleTextMap[row.role] || row.role }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="班级 / 学校" min-width="190">
                <template #default="{ row }">
                  {{ row.profile?.class_name || row.class_id || "未设置班级" }}
                  <p class="table-meta">{{ row.profile?.school || "未设置学校" }}</p>
                </template>
              </el-table-column>
              <el-table-column label="性别 / 年龄" width="130">
                <template #default="{ row }">
                  {{ row.profile?.gender || "未填" }}
                  <p class="table-meta">{{ row.profile?.age ? `${row.profile.age} 岁` : "未填年龄" }}</p>
                </template>
              </el-table-column>
              <el-table-column label="学习与问答" min-width="180">
                <template #default="{ row }">
                  <div v-if="row.role === 'student'">
                    <el-progress :percentage="row.progress_rate" :stroke-width="8" color="#bc6c25" />
                    <p class="table-meta">待跟进问题 {{ row.pending_question_count }}</p>
                  </div>
                  <span v-else class="table-meta">管理类账号</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="180">
                <template #default="{ row }">
                  <el-button text type="primary" @click="openEditDialog(row)">编辑</el-button>
                  <el-button text type="danger" @click="handleUserDelete(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="图谱与讨论统计" name="stats">
          <el-card class="workspace-panel">
            <template #header>图谱与讨论统计</template>
            <div class="summary-row">
              <div class="summary-metric"><span>图谱节点</span><strong>{{ overview.graph_stats.node_count }}</strong></div>
              <div class="summary-metric"><span>图谱关系</span><strong>{{ overview.graph_stats.relation_count }}</strong></div>
              <div class="summary-metric"><span>置顶讨论</span><strong>{{ overview.question_governance.featured_question_count }}</strong></div>
              <div class="summary-metric"><span>优秀评论</span><strong>{{ overview.question_governance.excellent_comment_count }}</strong></div>
            </div>
            <div class="detail-section top-gap">
              <span class="detail-label">课程模块分布</span>
              <div class="tag-list top-gap">
                <el-tag v-for="(count, category) in overview.graph_stats.category_breakdown" :key="category" effect="plain">
                  {{ category }} · {{ count }}
                </el-tag>
              </div>
            </div>
            <div class="analytics-list top-gap">
              <div v-for="item in overview.question_governance.top_concepts" :key="item.concept_name" class="analytics-card">
                <div class="card-header-inline">
                  <strong>{{ item.concept_name }}</strong>
                  <el-tag effect="plain">提问 {{ item.question_count }}</el-tag>
                </div>
                <el-progress :percentage="governanceConceptPercent(item.question_count)" :stroke-width="10" color="#bc6c25" />
              </div>
            </div>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="讨论治理" name="discussion">
          <el-card class="workspace-panel admin-discussion-card">
            <template #header>讨论治理</template>
            <div class="admin-discussion-list">
              <div v-for="item in overview.recent_questions" :key="item.id" class="thread-card">
                <div class="question-header">
                  <div>
                    <h3>{{ item.title }}</h3>
                    <p>{{ item.student_name }} · {{ item.concept_name || "综合问题" }} · {{ formatDate(item.create_time) }}</p>
                  </div>
                  <div class="tag-list">
                    <el-tag v-if="item.is_featured" type="warning" effect="dark">教师置顶</el-tag>
                    <el-tag effect="plain">{{ item.comment_count }} 条评论</el-tag>
                  </div>
                </div>
                <p class="detail-text">{{ item.description }}</p>
                <div class="question-actions">
                  <el-button text type="danger" @click="handleQuestionDelete(item)">删除问题</el-button>
                </div>
                <ThreadCommentTree
                  v-if="item.comments.length"
                  :comments="item.comments"
                  :can-reply="false"
                  :can-like="false"
                  :can-moderate-delete="true"
                  @moderate-delete="handleCommentDelete"
                />
              </div>
              <el-empty v-if="!overview.recent_questions.length" description="当前暂无可治理的讨论内容" />
            </div>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="图谱审核发布" name="graph-review">
          <el-card class="workspace-panel">
            <template #header>
              <div class="card-header-inline">
                <span>教师图谱变更审核</span>
                <el-tag type="warning" effect="plain">审核通过后会发布到学生端图谱</el-tag>
              </div>
            </template>

            <div v-if="overview.graph_change_requests.length" class="insight-list">
              <div v-for="item in overview.graph_change_requests" :key="item.id" class="graph-review-card">
                <div class="card-header-inline">
                  <div>
                    <strong>{{ item.summary }}</strong>
                    <p class="table-meta">{{ item.teacher_name }} · {{ graphActionTextMap[item.action] || item.action }} · {{ formatDate(item.create_time) }}</p>
                  </div>
                  <el-tag :type="graphChangeStatusTypeMap[item.status] || 'info'" effect="plain">{{ graphChangeStatusTextMap[item.status] || item.status }}</el-tag>
                </div>

                <div class="graph-review-grid top-gap">
                  <div class="detail-section">
                    <span class="detail-label">节点基础信息</span>
                    <h3>{{ item.node.name }}</h3>
                    <p class="detail-text">{{ item.node.description || "暂无节点简介" }}</p>
                    <div class="tag-list">
                      <el-tag effect="plain">{{ item.node.category || "未分类" }}</el-tag>
                      <el-tag effect="plain">难度 {{ item.node.difficulty || "-" }}</el-tag>
                      <el-tag effect="plain">{{ item.node.estimated_minutes || "-" }} 分钟</el-tag>
                    </div>
                  </div>

                  <div class="detail-section">
                    <span class="detail-label">关系变更预览</span>
                    <div class="tag-list">
                      <el-tag v-for="name in item.prerequisite_names" :key="`p-${item.id}-${name}`" effect="plain">前置：{{ name }}</el-tag>
                      <el-tag v-for="name in item.next_names" :key="`n-${item.id}-${name}`" effect="plain">后续：{{ name }}</el-tag>
                      <el-tag v-for="name in item.related_names" :key="`r-${item.id}-${name}`" effect="plain">相关：{{ name }}</el-tag>
                    </div>
                    <p v-if="!item.prerequisite_names.length && !item.next_names.length && !item.related_names.length" class="detail-text">本次申请未修改节点关系。</p>
                  </div>
                </div>

                <el-collapse class="top-gap">
                  <el-collapse-item title="查看知识梳理、学习材料和自测题详情">
                    <div class="graph-review-grid">
                      <div class="detail-section">
                        <span class="detail-label">知识梳理</span>
                        <ul class="compact-list">
                          <li v-for="point in item.node.key_points" :key="point">{{ point }}</li>
                        </ul>
                        <p v-if="!item.node.key_points.length" class="detail-text">暂无知识梳理要点。</p>
                      </div>
                      <div class="detail-section">
                        <span class="detail-label">学习材料</span>
                        <p class="detail-text">{{ item.node.text_material || "暂无学习材料说明。" }}</p>
                      </div>
                      <div class="detail-section">
                        <span class="detail-label">资源链接</span>
                        <div class="tag-list">
                          <el-tag v-for="link in item.node.resource_links" :key="link.url" effect="plain">{{ link.label }}</el-tag>
                        </div>
                        <p v-if="!item.node.resource_links.length" class="detail-text">暂无资源链接。</p>
                      </div>
                      <div class="detail-section">
                        <span class="detail-label">自测题</span>
                        <p class="detail-text">共 {{ item.node.quiz.length }} 道题，审核时重点检查题干、选项和答案序号是否匹配。</p>
                      </div>
                    </div>
                  </el-collapse-item>
                </el-collapse>

                <div v-if="item.status === 'pending'" class="graph-review-actions">
                  <el-input
                    v-model="graphReviewDrafts[item.id]"
                    type="textarea"
                    :rows="3"
                    placeholder="填写审核意见，例如：已检查节点关系和自测题，允许发布；或说明驳回原因"
                  />
                  <div class="question-actions">
                    <el-button type="danger" plain @click="handleGraphChangeReview(item, 'rejected')">驳回修改</el-button>
                    <el-button type="success" @click="handleGraphChangeReview(item, 'approved')">审核通过并发布</el-button>
                  </div>
                </div>
                <p v-else-if="item.review_note" class="detail-text">审核意见：{{ item.review_note }}</p>
              </div>
            </div>
            <el-empty v-else description="当前没有教师提交的图谱变更申请。" />
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="教师协同事项" name="coordination">
          <el-card class="workspace-panel">
            <template #header>教师协同事项</template>
            <div class="insight-list">
              <div v-for="item in overview.coordination_requests" :key="item.id" class="insight-item">
                <div class="card-header-inline">
                  <div>
                    <strong>{{ item.title }}</strong>
                    <p class="table-meta">{{ item.teacher_name }} · {{ item.type }} · {{ formatDate(item.create_time) }}</p>
                  </div>
                  <el-tag :type="coordinationStatusTypeMap[item.status] || 'info'" effect="plain">{{ coordinationStatusTextMap[item.status] || item.status }}</el-tag>
                </div>
                <p>{{ item.description }}</p>
                <el-input
                  v-model="coordinationReplyDrafts[item.id]"
                  type="textarea"
                  :rows="3"
                  :placeholder="item.admin_reply || '填写图谱运维官处理意见或系统协同回复'"
                />
                <div class="question-actions">
                  <el-button plain type="primary" @click="handleCoordinationUpdate(item, 'processing')">标记处理中</el-button>
                  <el-button type="success" @click="handleCoordinationUpdate(item, 'resolved')">回复并办结</el-button>
                </div>
                <p v-if="item.admin_reply" class="detail-text">当前回复：{{ item.admin_reply }}</p>
              </div>
              <el-empty v-if="!overview.coordination_requests.length" description="当前没有待处理的教师协同事项" />
            </div>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="推荐算法参数" name="settings">
          <el-card class="workspace-panel">
            <template #header>推荐算法参数</template>
            <el-form label-width="140px" class="settings-form">
              <el-form-item label="推荐知识点数量"><el-input-number v-model="settingsForm.recommendation_limit" :min="1" :max="12" /></el-form-item>
              <el-form-item label="薄弱点数量"><el-input-number v-model="settingsForm.weak_point_limit" :min="1" :max="10" /></el-form-item>
              <el-form-item label="路径长度上限"><el-input-number v-model="settingsForm.path_limit" :min="1" :max="12" /></el-form-item>
              <el-form-item label="已掌握权重"><el-input-number v-model="settingsForm.mastery_weight" :min="0.5" :max="2" :step="0.1" /></el-form-item>
              <el-form-item label="学习中权重"><el-input-number v-model="settingsForm.in_progress_weight" :min="0.1" :max="1" :step="0.1" /></el-form-item>
            </el-form>
            <div class="detail-section">
              <span class="detail-label">参数影响</span>
              <p class="detail-text">保存后会影响学生图谱页顶部的推荐学习路径、优先学习节点和薄弱点排序，也会影响教师端学生学习概况中的当前目标。</p>
            </div>
            <div class="question-actions">
              <el-button type="primary" :loading="savingSettings" @click="handleSettingsSave">保存参数</el-button>
            </div>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="操作日志" name="logs">
          <el-card class="workspace-panel">
            <template #header>运维操作日志</template>
            <div v-if="overview.operation_logs.length" class="insight-list">
              <div v-for="item in overview.operation_logs" :key="item.id" class="insight-item">
                <div class="card-header-inline">
                  <strong>{{ item.action }}</strong>
                  <el-tag effect="plain">{{ item.actor_name }}</el-tag>
                </div>
                <p>{{ item.description }}</p>
                <p class="table-meta">{{ formatDate(item.create_time) }} · {{ item.target_type }} {{ item.target_id || "" }}</p>
              </div>
            </div>
            <el-empty v-else description="当前还没有操作日志。" />
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-dialog v-model="createDialogVisible" title="新增账号" width="680px">
      <el-form label-width="92px">
        <div class="admin-inline-form">
          <el-form-item label="用户名"><el-input v-model="createForm.username" /></el-form-item>
          <el-form-item label="密码"><el-input v-model="createForm.password" show-password /></el-form-item>
          <el-form-item label="角色">
            <el-select v-model="createForm.role" class="full-width">
              <el-option label="学生" value="student" />
              <el-option label="教师" value="teacher" />
              <el-option label="图谱运维官" value="admin" />
            </el-select>
          </el-form-item>
          <el-form-item label="班级编号"><el-input-number v-model="createForm.class_id" :min="1" :max="99" /></el-form-item>
          <el-form-item label="姓名"><el-input v-model="createForm.real_name" /></el-form-item>
          <el-form-item label="学校"><el-input v-model="createForm.school" /></el-form-item>
          <el-form-item label="专业"><el-input v-model="createForm.major" /></el-form-item>
          <el-form-item label="年级"><el-input v-model="createForm.grade" /></el-form-item>
          <el-form-item label="性别">
            <el-select v-model="createForm.gender" class="full-width" clearable>
              <el-option label="女" value="女" />
              <el-option label="男" value="男" />
              <el-option label="未填写" value="未填写" />
            </el-select>
          </el-form-item>
          <el-form-item label="年龄"><el-input v-model="createForm.age" placeholder="如：20" /></el-form-item>
          <el-form-item label="班级名称"><el-input v-model="createForm.class_name" /></el-form-item>
        </div>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="creatingUser" @click="handleUserCreate">创建账号</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="userDialogVisible" title="编辑账号" width="680px">
      <el-form label-width="96px">
        <div class="admin-inline-form">
          <el-form-item label="用户名"><el-input :model-value="activeUser?.username || ''" disabled /></el-form-item>
          <el-form-item label="重置密码">
            <el-input v-model="userForm.password" show-password placeholder="留空则不修改密码" />
          </el-form-item>
          <el-form-item label="角色">
            <el-select v-model="userForm.role" class="full-width">
              <el-option label="学生" value="student" />
              <el-option label="教师" value="teacher" />
              <el-option label="图谱运维官" value="admin" />
            </el-select>
          </el-form-item>
          <el-form-item label="班级编号"><el-input-number v-model="userForm.class_id" :min="1" :max="99" /></el-form-item>
          <el-form-item label="姓名"><el-input v-model="userForm.real_name" /></el-form-item>
          <el-form-item label="学校"><el-input v-model="userForm.school" /></el-form-item>
          <el-form-item label="专业"><el-input v-model="userForm.major" /></el-form-item>
          <el-form-item label="年级"><el-input v-model="userForm.grade" /></el-form-item>
          <el-form-item label="性别">
            <el-select v-model="userForm.gender" class="full-width" clearable>
              <el-option label="女" value="女" />
              <el-option label="男" value="男" />
              <el-option label="未填写" value="未填写" />
            </el-select>
          </el-form-item>
          <el-form-item label="年龄"><el-input v-model="userForm.age" placeholder="如：20" /></el-form-item>
          <el-form-item label="班级名称"><el-input v-model="userForm.class_name" /></el-form-item>
        </div>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="userDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="savingUser" @click="handleUserSave">保存修改</el-button>
        </div>
      </template>
    </el-dialog>
  </AppShell>
</template>

<script setup>
import { ElMessage, ElMessageBox } from "element-plus";
import { computed, onMounted, reactive, ref } from "vue";

import {
  createManagedUser,
  deleteManagedComment,
  deleteManagedQuestion,
  deleteManagedUser,
  fetchAdminOverview,
  reviewGraphChangeRequest,
  updateCoordinationRequest,
  updateManagedUser,
  updateRecommendationSettings,
} from "../api/admin";
import AppShell from "../components/AppShell.vue";
import ThreadCommentTree from "../components/ThreadCommentTree.vue";
import { roleTextMap } from "../utils/role";

const overview = ref({
  total_users: 0,
  role_counts: {},
  graph_stats: {
    node_count: 0,
    relation_count: 0,
    category_breakdown: {},
  },
  pending_question_count: 0,
  pending_coordination_count: 0,
  pending_graph_change_count: 0,
  question_governance: {
    featured_question_count: 0,
    favorite_answer_count: 0,
    answered_question_count: 0,
    excellent_comment_count: 0,
    comment_like_count: 0,
    top_concepts: [],
  },
  recommendation_settings: {
    recommendation_limit: 6,
    weak_point_limit: 5,
    path_limit: 6,
    mastery_weight: 1,
    in_progress_weight: 0.5,
  },
  users: [],
  recent_questions: [],
  coordination_requests: [],
  graph_change_requests: [],
  operation_logs: [],
});
const activeAdminTab = ref("users");
const adminUserRoleFilter = ref("all");
const userDialogVisible = ref(false);
const createDialogVisible = ref(false);
const savingUser = ref(false);
const savingSettings = ref(false);
const creatingUser = ref(false);
const activeUser = ref(null);
const userForm = reactive({
  role: "student",
  class_id: 1,
  password: "",
  real_name: "",
  school: "",
  major: "",
  grade: "",
  gender: "",
  age: "",
  class_name: "",
});
const createForm = reactive({
  username: "",
  password: "",
  role: "student",
  class_id: 1,
  real_name: "",
  school: "",
  major: "",
  grade: "",
  gender: "",
  age: "",
  class_name: "",
});
const coordinationReplyDrafts = reactive({});
const graphReviewDrafts = reactive({});
const settingsForm = reactive({
  recommendation_limit: 6,
  weak_point_limit: 5,
  path_limit: 6,
  mastery_weight: 1,
  in_progress_weight: 0.5,
});
const coordinationStatusTextMap = {
  pending: "待处理",
  processing: "处理中",
  resolved: "已办结",
};
const coordinationStatusTypeMap = {
  pending: "warning",
  processing: "primary",
  resolved: "success",
};
const graphActionTextMap = {
  create_node: "新增节点",
  update_node: "修改节点",
};
const graphChangeStatusTextMap = {
  pending: "待审核",
  approved: "已发布",
  rejected: "已驳回",
};
const graphChangeStatusTypeMap = {
  pending: "warning",
  approved: "success",
  rejected: "danger",
};
const maxGovernanceQuestionCount = computed(() => Math.max(...overview.value.question_governance.top_concepts.map((item) => item.question_count), 1));
const filteredAdminUsers = computed(() => {
  if (adminUserRoleFilter.value === "all") return overview.value.users;
  return overview.value.users.filter((item) => item.role === adminUserRoleFilter.value);
});

function governanceConceptPercent(count) {
  return Math.round((count / maxGovernanceQuestionCount.value) * 100);
}

function formatDate(value) {
  return value ? new Date(value).toLocaleString("zh-CN", { hour12: false }) : "";
}

function syncSettingsForm() {
  Object.assign(settingsForm, overview.value.recommendation_settings || {});
}

function resetCreateForm() {
  Object.assign(createForm, {
    username: "",
    password: "",
    role: "student",
    class_id: 1,
    real_name: "",
    school: "",
    major: "",
    grade: "",
    gender: "",
    age: "",
    class_name: "",
  });
}

function openCreateDialog() {
  resetCreateForm();
  createDialogVisible.value = true;
}

function openEditDialog(row) {
  activeUser.value = row;
  userForm.role = row.role;
  userForm.class_id = row.class_id || 1;
  userForm.password = "";
  userForm.real_name = row.profile?.real_name || "";
  userForm.school = row.profile?.school || "";
  userForm.major = row.profile?.major || "";
  userForm.grade = row.profile?.grade || "";
  userForm.gender = row.profile?.gender || "";
  userForm.age = row.profile?.age || "";
  userForm.class_name = row.profile?.class_name || "";
  userDialogVisible.value = true;
}

async function loadOverview() {
  const { data } = await fetchAdminOverview();
  overview.value = data;
  Object.assign(
    coordinationReplyDrafts,
    Object.fromEntries((data.coordination_requests || []).map((item) => [item.id, item.admin_reply || ""])),
  );
  Object.assign(
    graphReviewDrafts,
    Object.fromEntries((data.graph_change_requests || []).map((item) => [item.id, item.review_note || ""])),
  );
  syncSettingsForm();
}

async function handleUserCreate() {
  if (createForm.username.trim().length < 3 || createForm.password.trim().length < 4) {
    ElMessage.warning("用户名至少 3 位，密码至少 4 位。");
    return;
  }

  try {
    creatingUser.value = true;
    await createManagedUser({ ...createForm, username: createForm.username.trim(), password: createForm.password.trim() });
    createDialogVisible.value = false;
    ElMessage.success("账号已创建。");
    await loadOverview();
  } catch (error) {
    console.error(error);
    ElMessage.error("创建账号失败，请稍后重试。");
  } finally {
    creatingUser.value = false;
  }
}

async function handleUserSave() {
  if (!activeUser.value) {
    return;
  }

  try {
    savingUser.value = true;
    await updateManagedUser(activeUser.value.id, {
      role: userForm.role,
      class_id: userForm.class_id,
      password: userForm.password.trim() || null,
      real_name: userForm.real_name.trim() || null,
      school: userForm.school.trim() || null,
      major: userForm.major.trim() || null,
      grade: userForm.grade.trim() || null,
      gender: userForm.gender.trim() || null,
      age: userForm.age.trim() || null,
      class_name: userForm.class_name.trim() || null,
    });
    userDialogVisible.value = false;
    ElMessage.success("账号资料已更新。");
    await loadOverview();
  } catch (error) {
    console.error(error);
    ElMessage.error("保存用户信息失败，请稍后重试。");
  } finally {
    savingUser.value = false;
  }
}

async function handleUserDelete(row) {
  try {
    await ElMessageBox.confirm(`确认删除账号 ${row.username} 吗？`, "删除账号", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
    });
    await deleteManagedUser(row.id);
    ElMessage.success("账号已删除。");
    await loadOverview();
  } catch (error) {
    if (error === "cancel") {
      return;
    }
    console.error(error);
    ElMessage.error("删除账号失败，请稍后重试。");
  }
}

async function handleQuestionDelete(item) {
  try {
    await ElMessageBox.confirm("删除后该问题及其讨论将一并移除，是否继续？", "删除讨论", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
    });
    await deleteManagedQuestion(item.id);
    ElMessage.success("问题已删除。");
    await loadOverview();
  } catch (error) {
    if (error === "cancel") {
      return;
    }
    console.error(error);
    ElMessage.error("删除问题失败，请稍后重试。");
  }
}

async function handleCommentDelete(comment) {
  try {
    await ElMessageBox.confirm("确认删除这条评论吗？", "删除评论", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
    });
    await deleteManagedComment(comment.id);
    ElMessage.success("评论已删除。");
    await loadOverview();
  } catch (error) {
    if (error === "cancel") {
      return;
    }
    console.error(error);
    ElMessage.error("删除评论失败，请稍后重试。");
  }
}

async function handleCoordinationUpdate(item, status) {
  const reply = (coordinationReplyDrafts[item.id] || "").trim();
  if (status === "resolved" && reply.length < 2) {
    ElMessage.warning("办结协同事项前，请至少填写 2 个字的处理回复。");
    return;
  }

  try {
    await updateCoordinationRequest(item.id, {
      status,
      admin_reply: reply || null,
    });
    ElMessage.success(status === "resolved" ? "协同事项已办结。" : "已更新为处理中。");
    await loadOverview();
  } catch (error) {
    console.error(error);
    ElMessage.error("更新协同事项失败，请稍后重试。");
  }
}

async function handleGraphChangeReview(item, status) {
  const reviewNote = (graphReviewDrafts[item.id] || "").trim();
  if (status === "rejected" && reviewNote.length < 2) {
    ElMessage.warning("驳回申请时请填写原因，方便教师继续修改。");
    return;
  }

  try {
    await reviewGraphChangeRequest(item.id, {
      status,
      review_note: reviewNote || null,
    });
    ElMessage.success(status === "approved" ? "图谱变更已审核通过并发布。" : "图谱变更申请已驳回。");
    await loadOverview();
  } catch (error) {
    console.error(error);
    ElMessage.error("审核图谱变更失败，请稍后重试。");
  }
}

async function handleSettingsSave() {
  try {
    savingSettings.value = true;
    await updateRecommendationSettings({ ...settingsForm });
    ElMessage.success("推荐参数已更新，学生端和教师端会使用新的配置。");
    await loadOverview();
  } catch (error) {
    console.error(error);
    ElMessage.error("保存推荐参数失败，请稍后重试。");
  } finally {
    savingSettings.value = false;
  }
}

onMounted(async () => {
  try {
    await loadOverview();
  } catch (error) {
    console.error(error);
    ElMessage.error("图谱运维台数据加载失败，请稍后重试。");
  }
});
</script>
