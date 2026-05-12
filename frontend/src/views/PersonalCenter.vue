<template>
  <AppShell>
    <div v-if="!currentUser" class="page-grid">
      <el-card>
        <template #header>个人中心</template>
        <el-empty description="请先登录后查看个人资料、学习进度和薄弱点分析。" />
      </el-card>
    </div>

    <div v-else-if="currentUser.role !== 'student'" class="page-grid dashboard-grid">
      <el-card class="profile-panel">
        <template #header>
          <div class="card-header-inline">
            <span>个人信息</span>
            <el-button type="primary" plain @click="openProfileDialog">编辑资料</el-button>
          </div>
        </template>
        <div class="profile-card">
          <div class="profile-hero">
            <div class="profile-avatar">{{ profileInitial }}</div>
            <div class="profile-meta">
              <h3>{{ currentUser.profile?.real_name || currentUser.username }}</h3>
              <p>{{ roleTextMap[currentUser.role] }}</p>
              <div class="tag-list">
                <el-tag effect="plain">{{ currentUser.username }}</el-tag>
                <el-tag effect="plain">{{ currentUser.profile?.school || "未设置学校" }}</el-tag>
              </div>
            </div>
          </div>
          <div class="detail-grid">
            <div><span class="detail-label">邮箱</span><strong>{{ currentUser.profile?.email || "未填写" }}</strong></div>
            <div><span class="detail-label">专业</span><strong>{{ currentUser.profile?.major || "未填写" }}</strong></div>
            <div><span class="detail-label">年级</span><strong>{{ currentUser.profile?.grade || "未填写" }}</strong></div>
            <div><span class="detail-label">班级</span><strong>{{ currentUser.profile?.class_name || "未填写" }}</strong></div>
          </div>
        </div>
      </el-card>

      <el-card>
        <template #header>角色提示</template>
        <div class="insight-list">
          <div class="insight-item">
            <span class="detail-label">当前角色</span>
            <strong>{{ roleTextMap[currentUser.role] }}</strong>
            <p v-if="currentUser.role === 'teacher'">教师主要在教师工作台中查看班级学习概况、管理节点讨论、使用快速回复模板并导出班级问答统计。</p>
            <p v-else>图谱运维官主要在图谱运维台中维护账号、处理协同事项、查看操作日志并配置系统参数。</p>
          </div>
        </div>
      </el-card>
    </div>

    <div v-else class="workspace-page">
      <el-tabs v-model="activeStudentTab" class="workspace-tabs">
        <el-tab-pane label="个人中心" name="profile">
          <el-card class="workspace-panel">
            <template #header>
              <div class="card-header-inline">
                <span>个人中心</span>
                <div class="card-header-actions">
                  <el-tag effect="plain" type="warning">资料完整度 {{ profileCompleteness }}%</el-tag>
                  <el-button type="primary" plain @click="openProfileDialog">编辑资料</el-button>
                </div>
              </div>
            </template>

            <div class="profile-card">
              <div class="profile-hero profile-hero-large">
                <div class="profile-avatar">{{ profileInitial }}</div>
                <div class="profile-meta">
                  <h3>{{ currentUser.profile?.real_name || currentUser.username }}</h3>
                  <p>学生 · {{ currentUser.profile?.school || "未设置学校" }}</p>
                  <div class="tag-list">
                    <el-tag type="success" effect="plain">{{ currentUser.username }}</el-tag>
                    <el-tag effect="plain">{{ currentUser.profile?.major || "未设置专业" }}</el-tag>
                    <el-tag effect="plain">{{ currentUser.profile?.class_name || "未设置班级" }}</el-tag>
                  </div>
                </div>
              </div>

              <div class="detail-grid wide-detail-grid">
                <div><span class="detail-label">邮箱</span><strong>{{ currentUser.profile?.email || "未填写" }}</strong></div>
                <div><span class="detail-label">年级</span><strong>{{ currentUser.profile?.grade || "未填写" }}</strong></div>
                <div><span class="detail-label">性别</span><strong>{{ currentUser.profile?.gender || "未填写" }}</strong></div>
                <div><span class="detail-label">年龄</span><strong>{{ currentUser.profile?.age || "未填写" }}</strong></div>
                <div><span class="detail-label">学号</span><strong>{{ currentUser.profile?.student_no || "未填写" }}</strong></div>
                <div><span class="detail-label">学习进度</span><strong>{{ analytics.progress_rate }}%</strong></div>
              </div>

              <div class="detail-section">
                <span class="detail-label">个人简介</span>
                <p class="detail-text">{{ currentUser.profile?.bio || "可在编辑资料中补充你的学习兴趣、课程目标或研究方向。" }}</p>
              </div>

              <div class="workflow-strip">
                <div class="workflow-step is-done">
                  <span>1</span>
                  <strong>图谱定位</strong>
                  <p>先在知识图谱选择当前学习目标。</p>
                </div>
                <div class="workflow-step" :class="{ 'is-done': analytics.recent_quiz_attempts.length }">
                  <span>2</span>
                  <strong>节点自测</strong>
                  <p>用测验结果判断是否真正掌握。</p>
                </div>
                <div class="workflow-step" :class="{ 'is-done': questionItems.length }">
                  <span>3</span>
                  <strong>提问互动</strong>
                  <p>把卡住的问题沉淀到节点论坛。</p>
                </div>
                <div class="workflow-step" :class="{ 'is-done': favoriteAnswerItems.length }">
                  <span>4</span>
                  <strong>复盘收藏</strong>
                  <p>收藏优秀回答并回到图谱继续推进。</p>
                </div>
              </div>
            </div>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="学习进度可视化" name="progress">
          <el-card class="workspace-panel">
            <template #header>
              <div class="card-header-inline">
                <span>学习进度可视化</span>
                <el-button type="primary" plain @click="handleExport">导出学习记录 CSV</el-button>
              </div>
            </template>

            <div class="student-progress-overview expanded-progress-overview">
              <div class="dashboard-ring-wrap">
                <el-progress type="dashboard" :percentage="analytics.progress_rate" :stroke-width="12" color="#bc6c25">
                  <template #default="{ percentage }">
                    <div class="dashboard-center">
                      <strong>{{ percentage }}%</strong>
                      <span>整体进度</span>
                    </div>
                  </template>
                </el-progress>
              </div>
              <div class="progress-breakdown">
                <div class="progress-side-stats">
                  <button type="button" class="mini-stat-card" @click="openNodeList('图谱全部节点', graphNodes)">
                    <span>节点总数</span>
                    <strong>{{ analytics.total_concepts }}</strong>
                  </button>
                  <button type="button" class="mini-stat-card" @click="openStatusNodeList(2)">
                    <span>已掌握</span>
                    <strong>{{ analytics.mastered_count }}</strong>
                  </button>
                  <button type="button" class="mini-stat-card" @click="openStatusNodeList(1)">
                    <span>学习中</span>
                    <strong>{{ analytics.in_progress_count }}</strong>
                  </button>
                  <button type="button" class="mini-stat-card" @click="openStatusNodeList(0)">
                    <span>未学</span>
                    <strong>{{ analytics.unlearned_count }}</strong>
                  </button>
                </div>
                <div
                  v-for="item in statusSummaryItems"
                  :key="item.status"
                  class="status-progress-row clickable-panel"
                  @click="openStatusNodeList(item.status)"
                >
                  <div class="card-header-inline">
                    <span>{{ item.label }}</span>
                    <strong>{{ item.count }} 个 · {{ item.ratio }}%</strong>
                  </div>
                  <el-progress :percentage="item.ratio" :stroke-width="12" :color="statusColorMap[item.status]" />
                  <p class="detail-text">{{ statusHintMap[item.status] }}</p>
                </div>
              </div>
            </div>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="按模块学习进度" name="modules">
          <el-card class="workspace-panel">
            <template #header>按模块学习进度</template>
            <div class="module-progress-grid expanded-module-grid">
              <div v-for="item in moduleProgressItems" :key="item.module_name" class="module-progress-item">
                <div class="card-header-inline">
                  <strong>{{ item.module_name }}</strong>
                  <span class="table-meta">{{ item.progress_rate }}%</span>
                </div>
                <el-progress :percentage="item.progress_rate" :stroke-width="12" color="#bc6c25" />
                <div class="tag-list top-gap">
                  <el-tag effect="plain" class="clickable-tag" @click="openModuleNodeList(item)">节点 {{ item.total_count }}</el-tag>
                  <el-tag type="success" effect="plain" class="clickable-tag" @click="openModuleNodeList(item, 2)">已掌握 {{ item.mastered_count }}</el-tag>
                  <el-tag type="warning" effect="plain" class="clickable-tag" @click="openModuleNodeList(item, 1)">学习中 {{ item.in_progress_count }}</el-tag>
                  <el-tag effect="plain" class="clickable-tag" @click="openModuleNodeList(item, 0)">未学 {{ item.unlearned_count }}</el-tag>
                </div>
                <p class="detail-text top-gap">{{ buildModuleSuggestion(item) }}</p>
              </div>
            </div>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="薄弱点分析" name="weak">
          <el-card class="workspace-panel">
            <template #header>薄弱点分析</template>
            <div v-if="analytics.weak_review_items.length" class="question-list">
              <div v-for="(item, index) in analytics.weak_review_items" :key="item.concept_id" class="question-card expanded-question-card">
                <div class="question-header">
                  <div>
                    <span class="path-step">复习优先级 {{ index + 1 }}</span>
                    <h3>{{ item.concept_name }}</h3>
                    <p>{{ item.module_name || "未分类模块" }}</p>
                  </div>
                  <el-tag type="danger" effect="plain">评分 {{ item.review_score }}</el-tag>
                </div>
                <div class="summary-row compact-summary">
                  <div class="summary-metric"><span>自测错误率</span><strong>{{ item.error_rate }}%</strong></div>
                  <div class="summary-metric"><span>相关提问</span><strong>{{ item.question_count }}</strong></div>
                  <div class="summary-metric"><span>错题数量</span><strong>{{ item.incorrect_count }}</strong></div>
                </div>
                <p class="detail-text top-gap">{{ item.reason }}</p>
                <div class="question-actions">
                  <el-button type="primary" plain @click="jumpToGraphNode(item.concept_id)">跳转到该节点学习</el-button>
                </div>
              </div>
            </div>
            <el-empty v-else description="当前还没有明显薄弱点，继续保持学习节奏。" />
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="最近自测记录" name="quiz">
          <el-card class="workspace-panel">
            <template #header>最近自测记录</template>
            <div v-if="analytics.recent_quiz_attempts.length" class="analytics-list">
              <div v-for="item in analytics.recent_quiz_attempts" :key="item.id" class="analytics-card">
                <div class="card-header-inline">
                  <div>
                    <strong>{{ item.concept_name }}</strong>
                    <p class="table-meta">{{ formatDate(item.create_time) }}</p>
                  </div>
                  <el-tag :type="item.score >= 80 ? 'success' : 'warning'" effect="plain">{{ item.score }} 分</el-tag>
                </div>
                <el-progress :percentage="item.score" :stroke-width="10" :color="item.score >= 80 ? '#6a994e' : '#dda15e'" />
                <p class="detail-text top-gap">{{ item.correct_answers }}/{{ item.total_questions }} 题正确 · 错误率 {{ 100 - item.accuracy }}%</p>
                <p class="detail-text">{{ item.score >= 80 ? "本节点可以进入巩固阶段，建议继续推进后续路径。" : "建议回看知识梳理和错题解释，再重新完成一次自测。" }}</p>
              </div>
            </div>
            <el-empty v-else description="完成节点自测后，这里会记录你的最新成绩。" />
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="我的提问" name="questions">
          <el-card class="workspace-panel">
            <template #header>我的提问</template>
            <div class="summary-row compact-summary">
              <div class="summary-metric"><span>提问总数</span><strong>{{ questionItems.length }}</strong></div>
              <div class="summary-metric"><span>已有回复</span><strong>{{ answeredQuestionCount }}</strong></div>
              <div class="summary-metric"><span>待讨论</span><strong>{{ pendingQuestionCount }}</strong></div>
            </div>
            <div v-if="questionItems.length" class="question-list top-gap">
              <div v-for="item in questionItems" :key="`my-${item.id}`" class="question-card">
                <div class="question-header">
                  <div>
                    <h3>{{ item.title }}</h3>
                    <p>{{ item.concept_name || "综合问题" }} · {{ formatDate(item.create_time) }}</p>
                  </div>
                  <el-tag :type="item.status === 'answered' ? 'success' : 'warning'" effect="plain">
                    {{ item.status === "answered" ? "已有回复" : "待讨论" }}
                  </el-tag>
                </div>
                <p class="detail-text">{{ item.description }}</p>
                <div v-if="item.teacher_reply" class="reply-card top-gap">
                  <span class="detail-label">教师回复</span>
                  <strong>{{ item.teacher_name || "任课教师" }}</strong>
                  <p>{{ item.teacher_reply }}</p>
                </div>
              </div>
            </div>
            <el-empty v-else description="你还没有节点提问记录，可在知识图谱节点论坛中发起问题。" />
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="收藏的优秀回答" name="favorites">
          <el-card class="workspace-panel">
            <template #header>收藏的优秀回答</template>
            <div v-if="favoriteAnswerItems.length" class="question-list">
              <div v-for="item in favoriteAnswerItems" :key="`favorite-${item.id}`" class="question-card">
                <div class="question-header">
                  <div>
                    <h3>{{ item.title }}</h3>
                    <p>{{ item.concept_name || "综合问题" }} · {{ item.teacher_name || "任课教师" }}</p>
                  </div>
                  <div class="tag-list">
                    <el-tag type="warning" effect="dark">教师置顶</el-tag>
                    <el-tag type="success" effect="plain">已收藏</el-tag>
                  </div>
                </div>
                <div v-if="getFavoriteAnswerText(item)" class="reply-card">
                  <span class="detail-label">收藏的回答</span>
                  <p>{{ getFavoriteAnswerText(item) }}</p>
                </div>
                <div class="question-actions">
                  <el-button v-if="item.concept_id" text type="primary" @click="jumpToGraphNode(item.concept_id)">回到节点复习</el-button>
                </div>
              </div>
            </div>
            <el-empty v-else description="你还没有收藏优秀回答，可在节点论坛中收藏教师置顶的问题。" />
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="学习记录时间线" name="timeline">
          <el-card class="workspace-panel">
            <template #header>学习记录时间线</template>
            <el-timeline>
              <el-timeline-item
                v-for="item in learningItems"
                :key="item.id"
                :timestamp="formatDate(item.update_time)"
                placement="top"
              >
                <div class="timeline-record-card">
                  <div class="card-header-inline">
                    <strong>{{ conceptNameMap[item.concept_id] || item.concept_id }}</strong>
                    <el-tag :type="statusTagTypeMap[item.status]" effect="plain">{{ statusTextMap[item.status] }}</el-tag>
                  </div>
                  <p class="detail-text">这条记录会影响图谱节点颜色、个人进度统计和后续推荐路径。</p>
                </div>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-if="!learningItems.length" description="还没有学习记录，先去知识图谱中标记几个节点吧。" />
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-dialog v-model="nodeListDialogVisible" :title="nodeListTitle" width="760px">
      <div v-if="nodeListItems.length" class="node-list-grid">
        <button
          v-for="node in nodeListItems"
          :key="node.id"
          type="button"
          class="node-list-card"
          @click="openNodeDetail(node)"
        >
          <div class="card-header-inline">
            <strong>{{ node.name }}</strong>
            <el-tag :type="statusTagTypeMap[getNodeStatus(node.id)]" effect="plain">{{ statusTextMap[getNodeStatus(node.id)] }}</el-tag>
          </div>
          <p>{{ node.description || "该节点暂未补充说明。" }}</p>
          <div class="tag-list">
            <el-tag effect="plain">{{ node.category || "未分类" }}</el-tag>
            <el-tag effect="plain">已学 {{ getNodeLearningTime(node.id).total_minutes }} 分钟</el-tag>
            <el-tag effect="plain">访问 {{ getNodeLearningTime(node.id).visit_count }} 次</el-tag>
          </div>
        </button>
      </div>
      <el-empty v-else description="当前筛选条件下没有节点。" />
    </el-dialog>

    <el-drawer v-model="nodeDetailDrawerVisible" :title="selectedDetailNode?.name || '节点详情'" size="50%" class="node-drawer">
      <div v-if="selectedDetailNode" class="node-detail drawer-node-detail">
        <div class="detail-header">
          <div>
            <h3>{{ selectedDetailNode.name }}</h3>
            <div class="tag-list top-gap">
              <el-tag>{{ selectedDetailNode.category || "未分类" }}</el-tag>
              <el-tag :type="statusTagTypeMap[getNodeStatus(selectedDetailNode.id)]" effect="plain">{{ statusTextMap[getNodeStatus(selectedDetailNode.id)] }}</el-tag>
            </div>
          </div>
          <el-button type="primary" plain @click="jumpToGraphNode(selectedDetailNode.id)">到知识图谱完整学习</el-button>
        </div>

        <p class="detail-text">{{ selectedDetailNode.description || "该知识点暂未补充说明。" }}</p>
        <div class="detail-grid">
          <div><span class="detail-label">难度</span><strong>{{ selectedDetailNode.difficulty || "未知" }}</strong></div>
          <div><span class="detail-label">建议学习时长</span><strong>{{ selectedDetailNode.estimated_minutes ? `${selectedDetailNode.estimated_minutes} 分钟` : "未设置" }}</strong></div>
          <div><span class="detail-label">累计学习时间</span><strong>{{ getNodeLearningTime(selectedDetailNode.id).total_minutes }} 分钟</strong></div>
          <div><span class="detail-label">最近学习</span><strong>{{ getNodeLearningTime(selectedDetailNode.id).latest_time ? formatDate(getNodeLearningTime(selectedDetailNode.id).latest_time) : "暂无记录" }}</strong></div>
        </div>

        <el-tabs class="node-tabs">
          <el-tab-pane label="知识梳理">
            <div class="detail-section detail-stack">
              <span class="detail-label">核心要点</span>
              <ul v-if="selectedDetailNode.key_points?.length" class="point-list">
                <li v-for="point in selectedDetailNode.key_points" :key="point">{{ point }}</li>
              </ul>
              <span v-else class="empty-hint">暂未整理核心要点</span>
            </div>
            <div class="detail-section detail-stack">
              <span class="detail-label">文字讲解</span>
              <p class="detail-text">{{ selectedDetailNode.text_material || "该节点暂未补充文字材料。" }}</p>
            </div>
            <div class="detail-section detail-stack">
              <span class="detail-label">学习提示</span>
              <ul v-if="selectedDetailNode.study_tips?.length" class="point-list">
                <li v-for="tip in selectedDetailNode.study_tips" :key="tip">{{ tip }}</li>
              </ul>
              <span v-else class="empty-hint">暂未配置学习提示</span>
            </div>
          </el-tab-pane>
          <el-tab-pane label="学习材料">
            <div class="detail-section detail-stack">
              <span class="detail-label">推荐材料</span>
              <p class="detail-text">{{ selectedDetailNode.text_material || "该节点暂未补充学习材料。" }}</p>
              <el-link v-if="selectedDetailNode.video_url" :href="selectedDetailNode.video_url" type="primary" target="_blank">{{ selectedDetailNode.video_title || "打开视频资源" }}</el-link>
            </div>
            <div class="detail-section detail-stack">
              <span class="detail-label">实践任务</span>
              <p class="detail-text">{{ selectedDetailNode.practice_task || "暂未配置练习任务。" }}</p>
            </div>
          </el-tab-pane>
          <el-tab-pane label="自测题">
            <div class="detail-section detail-stack">
              <span class="detail-label">自测概况</span>
              <p class="detail-text">该节点已配置 {{ selectedDetailNode.quiz?.length || 0 }} 道自测题。进入知识图谱节点详情后可以正式作答并记录成绩。</p>
              <el-button type="primary" plain @click="jumpToGraphNode(selectedDetailNode.id)">进入自测</el-button>
            </div>
          </el-tab-pane>
          <el-tab-pane label="节点论坛">
            <div class="detail-section detail-stack">
              <span class="detail-label">节点论坛入口</span>
              <p class="detail-text">节点论坛支持提问、回复、楼中楼评论、点赞和收藏教师置顶优秀回答。为了保持讨论上下文一致，请进入知识图谱中的完整节点详情操作。</p>
              <el-button type="primary" plain @click="jumpToGraphNode(selectedDetailNode.id)">打开节点论坛</el-button>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-drawer>

    <el-dialog v-model="profileDialogVisible" title="编辑个人信息" width="680px">
      <el-form label-width="96px" class="profile-form">
        <div class="auth-form-grid">
          <el-form-item label="姓名">
            <el-input v-model="profileForm.real_name" placeholder="请输入真实姓名或昵称" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="profileForm.email" placeholder="请输入常用邮箱" />
          </el-form-item>
          <el-form-item label="学校">
            <el-input v-model="profileForm.school" placeholder="如：某某大学" />
          </el-form-item>
          <el-form-item label="专业">
            <el-input v-model="profileForm.major" placeholder="如：教育技术学" />
          </el-form-item>
          <el-form-item label="年级">
            <el-input v-model="profileForm.grade" placeholder="如：2023级" />
          </el-form-item>
          <el-form-item label="性别">
            <el-select v-model="profileForm.gender" placeholder="请选择性别" clearable class="full-width">
              <el-option label="女" value="女" />
              <el-option label="男" value="男" />
              <el-option label="未填写" value="未填写" />
            </el-select>
          </el-form-item>
          <el-form-item label="年龄">
            <el-input v-model="profileForm.age" placeholder="如：20" />
          </el-form-item>
          <el-form-item label="学号 / 工号">
            <el-input v-model="profileForm.student_no" placeholder="请输入学号或工号" />
          </el-form-item>
          <el-form-item label="班级">
            <el-input v-model="profileForm.class_name" placeholder="如：人工智能1班" />
          </el-form-item>
          <el-form-item label="角色身份">
            <el-input :model-value="roleTextMap[currentUser.role]" disabled />
          </el-form-item>
        </div>
        <el-form-item label="个人简介">
          <el-input
            v-model="profileForm.bio"
            type="textarea"
            :rows="4"
            placeholder="可填写学习兴趣、研究方向或课程目标"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="profileDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="savingProfile" @click="handleProfileSave">保存资料</el-button>
        </div>
      </template>
    </el-dialog>
  </AppShell>
</template>

<script setup>
import { ElMessage } from "element-plus";
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";

import { fetchCurrentUser, updateCurrentUserProfile } from "../api/auth";
import { fetchGraphAll } from "../api/graph";
import { exportLearningRecordsCsv, fetchLearningAnalytics, fetchLearningQuestions, fetchLearningStatuses, fetchMyQuestions, recordNodeVisit } from "../api/learning";
import AppShell from "../components/AppShell.vue";
import { getAccessToken, getCurrentUser, saveSession } from "../utils/session";
import { roleTextMap } from "../utils/role";

const router = useRouter();
const currentUser = ref(getCurrentUser());
const activeStudentTab = ref("profile");
const learningItems = ref([]);
const graphNodes = ref([]);
const questionItems = ref([]);
const favoriteAnswerItems = ref([]);
const profileDialogVisible = ref(false);
const savingProfile = ref(false);
const analytics = ref({
  progress_rate: 0,
  total_concepts: 0,
  mastered_count: 0,
  in_progress_count: 0,
  unlearned_count: 0,
  status_progress: [],
  module_progress: [],
  weak_review_items: [],
  recent_quiz_attempts: [],
  node_learning_times: [],
});
const nodeListDialogVisible = ref(false);
const nodeListTitle = ref("");
const nodeListItems = ref([]);
const nodeDetailDrawerVisible = ref(false);
const selectedDetailNode = ref(null);
const detailVisitStartedAt = ref(0);

const profileForm = reactive({
  real_name: "",
  email: "",
  school: "",
  major: "",
  grade: "",
  gender: "",
  age: "",
  student_no: "",
  class_name: "",
  bio: "",
});

const profileFields = ["real_name", "email", "school", "major", "grade", "gender", "age", "student_no", "class_name", "bio"];
const statusTextMap = {
  0: "未学",
  1: "学习中",
  2: "已掌握",
};
const statusColorMap = {
  0: "#c7c4bd",
  1: "#dda15e",
  2: "#6a994e",
};
const statusHintMap = {
  0: "未学节点会成为后续路径中的主要增长空间，可优先关注影响节点较多的薄弱点。",
  1: "学习中节点适合安排近期复习和二次自测，是推荐路径中的推进重点。",
  2: "已掌握节点会提升后续节点准备度，也会让图谱路径更快向高阶内容推进。",
};
const statusTagTypeMap = {
  0: "info",
  1: "warning",
  2: "success",
};

const conceptNameMap = computed(() => Object.fromEntries(graphNodes.value.map((node) => [node.id, node.name])));
const learningStatusMap = computed(() => Object.fromEntries(learningItems.value.map((item) => [item.concept_id, Number(item.status)])));
const nodeLearningTimeMap = computed(() => Object.fromEntries((analytics.value.node_learning_times || []).map((item) => [item.concept_id, item])));
const profileInitial = computed(() => (currentUser.value?.profile?.real_name || currentUser.value?.username || "学").slice(0, 1));
const profileCompleteness = computed(() => {
  const profile = currentUser.value?.profile || {};
  const filledCount = profileFields.filter((field) => Boolean(profile[field])).length;
  return Math.round((filledCount / profileFields.length) * 100);
});
const statusSummaryItems = computed(() => {
  if (analytics.value.status_progress.length) return analytics.value.status_progress;
  const total = analytics.value.total_concepts || 1;
  return [
    { label: "已掌握", status: 2, count: analytics.value.mastered_count, ratio: Math.round((analytics.value.mastered_count / total) * 100) },
    { label: "学习中", status: 1, count: analytics.value.in_progress_count, ratio: Math.round((analytics.value.in_progress_count / total) * 100) },
    { label: "未学", status: 0, count: analytics.value.unlearned_count, ratio: Math.round((analytics.value.unlearned_count / total) * 100) },
  ];
});
const moduleProgressItems = computed(() => [...analytics.value.module_progress].sort((a, b) => a.progress_rate - b.progress_rate));
const answeredQuestionCount = computed(() => questionItems.value.filter((item) => item.status === "answered").length);
const pendingQuestionCount = computed(() => questionItems.value.filter((item) => item.status !== "answered").length);

function getNodeStatus(conceptId) {
  return learningStatusMap.value[conceptId] ?? 0;
}

function getNodeLearningTime(conceptId) {
  return nodeLearningTimeMap.value[conceptId] || {
    concept_id: conceptId,
    concept_name: conceptNameMap.value[conceptId] || conceptId,
    total_minutes: 0,
    visit_count: 0,
    average_minutes: 0,
    latest_time: null,
  };
}

function flattenComments(comments = []) {
  return comments.flatMap((comment) => [comment, ...flattenComments(comment.replies || [])]);
}

function getFavoriteAnswerText(item) {
  if (item.teacher_reply) return item.teacher_reply;
  const comments = flattenComments(item.comments || []);
  return (
    comments.find((comment) => comment.is_excellent)?.content ||
    comments.find((comment) => comment.author_role === "teacher")?.content ||
    ""
  );
}

function getNodesByStatus(status) {
  return graphNodes.value.filter((node) => getNodeStatus(node.id) === Number(status));
}

function getNodesByModule(moduleName, status = null) {
  return graphNodes.value.filter((node) => {
    const sameModule = (node.category || "未分类模块") === moduleName;
    return sameModule && (status === null || getNodeStatus(node.id) === Number(status));
  });
}

function openNodeList(title, nodes) {
  nodeListTitle.value = title;
  nodeListItems.value = [...nodes].sort((a, b) => a.name.localeCompare(b.name, "zh-CN"));
  nodeListDialogVisible.value = true;
}

function openStatusNodeList(status) {
  const label = statusTextMap[status] || "节点";
  openNodeList(`${label}节点`, getNodesByStatus(status));
}

function openModuleNodeList(item, status = null) {
  const label = status === null ? "全部节点" : `${statusTextMap[status]}节点`;
  openNodeList(`${item.module_name} · ${label}`, getNodesByModule(item.module_name, status));
}

async function openNodeDetail(node) {
  if (nodeDetailDrawerVisible.value && selectedDetailNode.value?.id !== node.id) {
    await finishDetailNodeVisit();
  }
  selectedDetailNode.value = node;
  nodeDetailDrawerVisible.value = true;
  detailVisitStartedAt.value = Date.now();
}

async function finishDetailNodeVisit() {
  if (!selectedDetailNode.value || !detailVisitStartedAt.value) return;
  const node = selectedDetailNode.value;
  const durationSeconds = Math.max(Math.round((Date.now() - detailVisitStartedAt.value) / 1000), 0);
  detailVisitStartedAt.value = 0;
  if (durationSeconds < 3) return;
  try {
    await recordNodeVisit(node.id, {
      concept_name: node.name,
      duration_seconds: Math.min(durationSeconds, 7200),
    });
    const { data } = await fetchLearningAnalytics();
    analytics.value = data;
  } catch (error) {
    console.error(error);
  }
}

watch(nodeDetailDrawerVisible, async (visible) => {
  if (!visible) {
    await finishDetailNodeVisit();
  }
});

function formatDate(value) {
  if (!value) return "";
  return new Date(value).toLocaleString("zh-CN", { hour12: false });
}

function buildModuleSuggestion(item) {
  if (item.progress_rate >= 80) return "该模块已经较稳定，可以通过项目任务或节点论坛回答他人问题来巩固。";
  if (item.in_progress_count > 0) return "该模块存在学习中节点，建议优先完成自测并把状态更新为已掌握。";
  return "该模块仍有较多未学节点，可从图谱页的优先学习节点进入。";
}

function fillProfileForm(userData = currentUser.value) {
  const profile = userData?.profile || {};
  profileFields.forEach((field) => {
    profileForm[field] = profile[field] || "";
  });
}

function openProfileDialog() {
  fillProfileForm();
  profileDialogVisible.value = true;
}

function buildProfilePayload() {
  return Object.fromEntries(
    profileFields.map((field) => {
      const value = typeof profileForm[field] === "string" ? profileForm[field].trim() : profileForm[field];
      return [field, value || null];
    }),
  );
}

async function handleProfileSave() {
  try {
    savingProfile.value = true;
    const { data } = await updateCurrentUserProfile(buildProfilePayload());
    currentUser.value = data;
    saveSession(getAccessToken(), data);
    fillProfileForm(data);
    profileDialogVisible.value = false;
    ElMessage.success("个人信息已更新。");
  } catch (error) {
    console.error(error);
    ElMessage.error("保存个人信息失败，请稍后重试。");
  } finally {
    savingProfile.value = false;
  }
}

function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  window.URL.revokeObjectURL(url);
}

async function handleExport() {
  try {
    const { data, headers } = await exportLearningRecordsCsv();
    const disposition = headers["content-disposition"] || "";
    const matched = disposition.match(/filename="(.+)"/);
    downloadBlob(data, matched?.[1] || "student-learning-records.csv");
    ElMessage.success("学习记录已导出。");
  } catch (error) {
    console.error(error);
    ElMessage.error("导出学习记录失败，请稍后重试。");
  }
}

function jumpToGraphNode(conceptId) {
  router.push({ path: "/graph", query: { focus: conceptId } });
}

async function loadDashboard() {
  if (!currentUser.value) {
    return;
  }

  const tasks = [fetchCurrentUser()];
  if (currentUser.value.role === "student") {
    tasks.push(
      fetchGraphAll(),
      fetchLearningStatuses(),
      fetchLearningAnalytics(),
      fetchMyQuestions(),
      fetchLearningQuestions({ favorites_only: true, featured_only: true }),
    );
  }

  const results = await Promise.allSettled(tasks);
  const [meResult, graphResult, statusResult, analyticsResult, questionResult, favoriteResult] = results;
  let failureCount = 0;

  if (meResult.status === "fulfilled") {
    currentUser.value = meResult.value.data;
    saveSession(getAccessToken(), meResult.value.data);
    fillProfileForm(meResult.value.data);
  } else {
    failureCount += 1;
  }

  if (currentUser.value.role === "student") {
    if (graphResult?.status === "fulfilled") {
      graphNodes.value = graphResult.value.data.nodes || [];
    } else {
      failureCount += 1;
    }

    if (statusResult?.status === "fulfilled") {
      learningItems.value = statusResult.value.data.items || [];
    } else {
      failureCount += 1;
    }

    if (analyticsResult?.status === "fulfilled") {
      analytics.value = analyticsResult.value.data;
    } else {
      failureCount += 1;
    }

    if (questionResult?.status === "fulfilled") {
      questionItems.value = questionResult.value.data.items || [];
    } else {
      failureCount += 1;
    }

    if (favoriteResult?.status === "fulfilled") {
      favoriteAnswerItems.value = favoriteResult.value.data.items || [];
    } else {
      failureCount += 1;
    }
  }

  if (failureCount === tasks.length) {
    throw new Error("dashboard-load-failed");
  }
  if (failureCount > 0) {
    ElMessage.warning("个人中心有部分数据暂未刷新成功，已先展示可用内容。");
  }
}

onMounted(async () => {
  if (!currentUser.value) {
    return;
  }

  try {
    await loadDashboard();
  } catch (error) {
    console.error(error);
    ElMessage.error("个人中心数据加载失败，请稍后重试。");
  }
});
</script>
