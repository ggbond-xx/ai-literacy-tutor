<template>
  <AppShell>
    <div class="page-grid dashboard-grid">
      <el-card class="hero-summary">
        <template #header>教师工作台总览</template>
        <div class="summary-row">
          <div class="summary-metric">
            <span>学生人数</span>
            <strong>{{ overview.total_students }}</strong>
          </div>
          <div class="summary-metric">
            <span>平均进度</span>
            <strong>{{ overview.average_progress_rate }}%</strong>
          </div>
          <div class="summary-metric">
            <span>待回复问题</span>
            <strong>{{ overview.pending_question_count }}</strong>
          </div>
          <div class="summary-metric">
            <span>已掌握知识点累计</span>
            <strong>{{ overview.mastered_concepts_total }}</strong>
          </div>
          <div class="summary-metric">
            <span>优秀问答置顶数</span>
            <strong>{{ overview.featured_question_count }}</strong>
          </div>
        </div>
      </el-card>

      <el-card>
        <template #header>班级学习进度概览</template>
        <el-table :data="overview.student_progress" size="small" empty-text="当前暂无学生学习数据">
          <el-table-column label="学生" min-width="120">
            <template #default="{ row }">
              <strong>{{ row.display_name }}</strong>
              <p class="table-meta">{{ row.username }}</p>
            </template>
          </el-table-column>
          <el-table-column label="班级" min-width="100">
            <template #default="{ row }">{{ row.profile?.class_name || row.class_id || "未设置" }}</template>
          </el-table-column>
          <el-table-column label="总体进度" min-width="160">
            <template #default="{ row }">
              <el-progress :percentage="row.progress_rate" :stroke-width="10" color="#bc6c25" />
            </template>
          </el-table-column>
          <el-table-column label="当前目标" min-width="140">
            <template #default="{ row }">{{ row.current_target || "暂无" }}</template>
          </el-table-column>
          <el-table-column label="薄弱点" min-width="140">
            <template #default="{ row }">{{ row.weak_point || "暂无" }}</template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card>
        <template #header>学生问题回复</template>
        <div class="detail-section detail-stack">
          <span class="detail-label">按知识点筛选问题</span>
          <el-select v-model="activeConceptFilter" class="full-width" clearable placeholder="全部知识点">
            <el-option
              v-for="item in overview.concept_question_stats"
              :key="item.concept_name"
              :label="`${item.concept_name}（${item.question_count}）`"
              :value="item.concept_name"
            />
          </el-select>
        </div>
        <div v-if="filteredQuestions.length" class="question-list">
          <div v-for="item in filteredQuestions" :key="item.id" class="question-card">
            <div class="question-header">
              <div>
                <h3>{{ item.title }}</h3>
                <p>
                  <el-button text type="primary" @click="openStudentSnapshot(item)">{{ item.student_name }}</el-button>
                  · {{ item.concept_name || "综合问题" }} · {{ formatDate(item.create_time) }}
                </p>
              </div>
              <div class="tag-list">
                <el-tag :type="item.status === 'answered' ? 'success' : 'warning'" effect="plain">
                  {{ item.status === "answered" ? "已回复" : "待回复" }}
                </el-tag>
                <el-tag v-if="item.is_featured" type="warning" effect="dark">教师置顶</el-tag>
              </div>
            </div>
            <p class="detail-text">{{ item.description }}</p>
            <div v-if="item.teacher_reply" class="reply-card">
              <span class="detail-label">已回复内容</span>
              <p>{{ item.teacher_reply }}</p>
            </div>
            <div class="question-actions">
              <el-button text type="primary" @click="openStudentSnapshot(item)">查看提问者学习情况</el-button>
              <el-button type="primary" plain @click="openReplyDialog(item)">
                {{ item.status === "answered" ? "更新回复" : "立即回复" }}
              </el-button>
              <el-button
                v-if="item.teacher_reply"
                plain
                type="warning"
                @click="handleFeatureToggle(item)"
              >
                {{ item.is_featured ? "取消置顶" : "置顶优秀问答" }}
              </el-button>
            </div>
          </div>
        </div>
        <el-empty
          v-else
          :description="overview.recent_questions.length ? '当前筛选条件下没有问题。' : '当前还没有学生提问。'"
        />
      </el-card>

      <el-card>
        <template #header>教学关注点</template>
        <div class="insight-list">
          <div class="insight-item">
            <span class="detail-label">本页职责</span>
            <strong>查看学习进度、识别薄弱点、回复学生问题</strong>
            <p>教师工作台聚焦教学干预，帮助你快速掌握学生整体画像，并基于问题反馈做针对性辅导。</p>
          </div>
          <div class="insight-item">
            <span class="detail-label">与学生的交互</span>
            <strong>学生在知识图谱的节点下提问，教师在这里按知识点回复和置顶</strong>
            <p>教师回复完成后，可将优秀问答置顶，学生能在对应节点下看到并收藏优秀回答。</p>
          </div>
        </div>
      </el-card>
    </div>

    <el-dialog v-model="replyDialogVisible" title="回复学生问题" width="640px">
      <div v-if="activeQuestion" class="reply-preview">
        <h3>{{ activeQuestion.title }}</h3>
        <p class="detail-text">{{ activeQuestion.description }}</p>
      </div>
      <el-input
        v-model="replyForm.teacher_reply"
        type="textarea"
        :rows="6"
        placeholder="请给出针对性的解答、补充学习建议或推荐学生回看的知识点"
      />
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="replyDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="replying" @click="handleReplySubmit">保存回复</el-button>
        </div>
      </template>
    </el-dialog>

    <el-drawer v-model="studentDrawerVisible" title="学生学习情况" size="420px">
      <div v-if="studentSnapshot" class="insight-list">
        <div class="insight-item">
          <span class="detail-label">学生信息</span>
          <strong>{{ studentSnapshot.student.display_name }}</strong>
          <p>{{ studentSnapshot.student.username }} · {{ studentSnapshot.student.profile?.class_name || studentSnapshot.student.class_id || "未设置班级" }}</p>
        </div>
        <div class="summary-row compact-summary">
          <div class="summary-metric">
            <span>总体进度</span>
            <strong>{{ studentSnapshot.student.progress_rate }}%</strong>
          </div>
          <div class="summary-metric">
            <span>当前目标</span>
            <strong>{{ studentSnapshot.student.current_target || "暂无" }}</strong>
          </div>
          <div class="summary-metric">
            <span>优秀问答数</span>
            <strong>{{ studentSnapshot.featured_answer_count }}</strong>
          </div>
        </div>
        <div class="detail-section detail-stack">
          <span class="detail-label">最近学习记录</span>
          <el-timeline>
            <el-timeline-item
              v-for="item in studentSnapshot.recent_statuses"
              :key="`${item.concept_id}-${item.update_time}`"
              :timestamp="formatDate(item.update_time)"
              placement="top"
            >
              <strong>{{ item.concept_name }}</strong>
              <p>{{ statusTextMap[item.status] }}</p>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-drawer>
  </AppShell>
</template>

<script setup>
import { ElMessage } from "element-plus";
import { computed, onMounted, reactive, ref } from "vue";

import { fetchStudentSnapshot, featureTeacherQuestion, fetchTeacherOverview, replyTeacherQuestion } from "../api/teacher";
import AppShell from "../components/AppShell.vue";

const overview = ref({
  total_students: 0,
  average_progress_rate: 0,
  mastered_concepts_total: 0,
  pending_question_count: 0,
  answered_question_count: 0,
  featured_question_count: 0,
  student_progress: [],
  recent_questions: [],
  concept_question_stats: [],
});

const replyDialogVisible = ref(false);
const replying = ref(false);
const activeQuestion = ref(null);
const activeConceptFilter = ref("");
const studentDrawerVisible = ref(false);
const studentSnapshot = ref(null);
const replyForm = reactive({
  teacher_reply: "",
});
const statusTextMap = {
  0: "未学",
  1: "学习中",
  2: "已掌握",
};

const filteredQuestions = computed(() => {
  if (!activeConceptFilter.value) {
    return overview.value.recent_questions;
  }
  return overview.value.recent_questions.filter((item) => (item.concept_name || "综合问题") === activeConceptFilter.value);
});

function formatDate(value) {
  if (!value) {
    return "";
  }
  return new Date(value).toLocaleString("zh-CN", { hour12: false });
}

function openReplyDialog(item) {
  activeQuestion.value = item;
  replyForm.teacher_reply = item.teacher_reply || "";
  replyDialogVisible.value = true;
}

async function loadOverview() {
  const { data } = await fetchTeacherOverview();
  overview.value = data;
}

async function openStudentSnapshot(item) {
  try {
    const { data } = await fetchStudentSnapshot(item.student_id);
    studentSnapshot.value = data;
    studentDrawerVisible.value = true;
  } catch (error) {
    console.error(error);
    ElMessage.error("加载学生学习情况失败，请稍后重试。");
  }
}

async function handleReplySubmit() {
  if (!activeQuestion.value || replyForm.teacher_reply.trim().length < 2) {
    ElMessage.warning("请填写具体回复内容。");
    return;
  }

  try {
    replying.value = true;
    await replyTeacherQuestion(activeQuestion.value.id, replyForm.teacher_reply.trim());
    replyDialogVisible.value = false;
    ElMessage.success("回复已保存，学生会在个人中心看到你的反馈。");
    await loadOverview();
  } catch (error) {
    console.error(error);
    ElMessage.error("保存回复失败，请稍后重试。");
  } finally {
    replying.value = false;
  }
}

async function handleFeatureToggle(item) {
  try {
    await featureTeacherQuestion(item.id, !item.is_featured);
    ElMessage.success(item.is_featured ? "已取消置顶。" : "已置顶为优秀问答。");
    await loadOverview();
  } catch (error) {
    console.error(error);
    ElMessage.error("更新置顶状态失败，请稍后重试。");
  }
}

onMounted(async () => {
  try {
    await loadOverview();
  } catch (error) {
    console.error(error);
    ElMessage.error("教师工作台数据加载失败，请稍后重试。");
  }
});
</script>
