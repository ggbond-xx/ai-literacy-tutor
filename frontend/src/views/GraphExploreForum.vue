<template>
  <AppShell>
    <div class="page-grid graph-page graph-page-v2">
      <div v-if="isStudent" class="graph-top-grid-v2">
        <el-card class="graph-top-card">
          <template #header>
            <div class="card-header-inline">
              <span>推荐学习路径</span>
              <el-tag type="warning" effect="plain">当前目标：{{ overview.default_target?.name || "等待推荐" }}</el-tag>
            </div>
          </template>
          <div class="detail-stack">
            <div class="detail-section detail-stack">
              <span class="detail-label">学习目标</span>
              <el-select
                :model-value="manualTargetId || overview.default_target?.id || ''"
                placeholder="选择优先攻克的知识点"
                filterable
                clearable
                class="full-width"
                @change="handleTargetSelect"
              >
                <el-option v-for="node in targetOptions" :key="node.id" :label="node.name" :value="node.id" />
              </el-select>
              <p class="detail-text">系统会结合掌握状态、前置依赖和薄弱点自动生成学习顺序。</p>
            </div>

            <div v-if="overview.learning_path.length" class="path-list compact-path-list">
              <div v-for="item in overview.learning_path" :key="item.step" class="path-card compact-path-card">
                <div class="path-header">
                  <div>
                    <span class="path-step">Step {{ item.step }}</span>
                    <h3>{{ item.concept.name }}</h3>
                  </div>
                  <el-tag effect="plain">{{ statusTextMap[item.concept.status] }}</el-tag>
                </div>
                <p>{{ item.reason }}</p>
                <div class="question-actions">
                  <el-button type="primary" plain @click="focusNode(item.concept.id)">查看节点</el-button>
                </div>
              </div>
            </div>
            <el-empty v-else description="先标记几个节点的学习状态，系统会自动生成推荐路径。" />
          </div>
        </el-card>

        <el-card class="graph-top-card">
          <template #header>
            <div class="card-header-inline">
              <span>优先学习节点</span>
              <el-tag type="success" effect="plain">进度 {{ progressRate }}%</el-tag>
            </div>
          </template>
          <div class="detail-stack">
            <div class="recommend-grid compact-recommend-grid">
              <div v-for="item in overview.recommended_concepts" :key="item.id" class="recommend-card">
                <div class="path-header">
                  <div>
                    <span class="path-step">优先节点</span>
                    <h3>{{ item.name }}</h3>
                  </div>
                  <el-tag type="success" effect="plain">准备度 {{ Math.round(item.readiness * 100) }}%</el-tag>
                </div>
                <p>{{ item.description || "建议先完成这一节点，再继续推进当前目标。" }}</p>
                <div class="tag-list">
                  <el-tag effect="plain">{{ statusTextMap[item.status] }}</el-tag>
                  <el-tag effect="plain">前置 {{ item.prerequisite_count }}</el-tag>
                  <el-tag effect="plain">影响 {{ item.blocked_count }}</el-tag>
                </div>
                <div class="question-actions">
                  <el-button type="primary" plain @click="focusNode(item.id)">查看节点</el-button>
                  <el-button plain @click="applyTargetSelection(item.id)">设为目标</el-button>
                </div>
              </div>
            </div>

            <div class="detail-section detail-stack">
              <span class="detail-label">薄弱点分析</span>
              <el-table :data="overview.weak_points" size="small" empty-text="当前暂无明显薄弱点">
                <el-table-column label="知识点" min-width="120">
                  <template #default="{ row }">
                    <el-button text type="primary" @click="focusNode(row.concept.id)">{{ row.concept.name }}</el-button>
                  </template>
                </el-table-column>
                <el-table-column label="影响节点数" width="110">
                  <template #default="{ row }">{{ row.impact_count }}</template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-card>
      </div>

      <div class="graph-panel-v2">
        <GraphCanvasEcharts
          :nodes="filteredNodes"
          :links="filteredLinks"
          :active-node-id="selectedNode?.id || ''"
          :recommended-node-ids="recommendedNodeIds"
          :learning-path-node-ids="learningPathNodeIds"
          :weak-point-node-ids="weakPointNodeIds"
          :default-target-id="overview.default_target?.id || ''"
          :status-map="statusMap"
          @node-select="handleNodeSelect"
        />

        <div class="graph-console-overlay">
          <div class="graph-console-card">
            <div class="graph-console-title">图谱控制台</div>
            <el-input v-model="keyword" placeholder="搜索知识点" clearable />
            <div class="metric"><span>节点总数</span><strong>{{ graph.nodes.length }}</strong></div>
            <div class="metric"><span>关系总数</span><strong>{{ graph.links.length }}</strong></div>
            <div class="metric"><span>学习进度</span><strong>{{ progressRate }}%</strong></div>
            <el-progress :percentage="progressRate" :stroke-width="10" color="#bc6c25" />
            <el-alert v-if="errorMessage" :title="errorMessage" type="warning" :closable="false" show-icon class="spaced" />
            <el-alert
              v-else-if="isStudent && overview.default_target"
              :title="`当前推荐目标：${overview.default_target.name}`"
              type="success"
              :closable="false"
              show-icon
              class="spaced"
            />
            <el-alert
              v-else-if="!currentUser"
              title="游客模式下可浏览整体图谱，点击节点后需先登录才能查看节点详情。"
              type="info"
              :closable="false"
              show-icon
              class="spaced"
            />
            <p v-else class="detail-text top-gap">点击图谱中的节点，可打开节点详情与讨论区。</p>
          </div>
        </div>
        <div class="graph-panel-caption">支持拖拽、缩放、关系标签与路径高亮</div>
      </div>

      <el-card v-if="!isStudent" class="graph-hint-card">
        <template #header>图谱使用说明</template>
        <div class="insight-list">
          <div class="insight-item">
            <span class="detail-label">当前页面职责</span>
            <strong>围绕知识点结构、前置关系、学习材料与讨论互动进行探索</strong>
            <p>学生可以在这里完成学习、讨论与自测；教师和图谱运维官更适合把这里作为图谱浏览与课程核对页面。</p>
          </div>
        </div>
      </el-card>
    </div>

    <el-drawer v-model="nodeDrawerVisible" :title="selectedNode?.name || '节点详情'" size="50%" class="node-drawer">
      <div v-if="selectedNode" class="node-detail drawer-node-detail">
        <div class="detail-header">
          <div>
            <h3>{{ selectedNode.name }}</h3>
            <div class="tag-list top-gap">
              <el-tag>{{ selectedNode.category || "未分类" }}</el-tag>
              <el-tag v-if="isTargetNode(selectedNode.id)" type="warning" effect="dark">当前目标</el-tag>
              <el-tag v-else-if="isPathNode(selectedNode.id)" type="warning" effect="plain">路径节点</el-tag>
              <el-tag v-if="isWeakPointNode(selectedNode.id)" type="danger" effect="plain">薄弱点</el-tag>
              <el-tag v-if="isRecommendedNode(selectedNode.id)" type="success" effect="plain">优先学习</el-tag>
            </div>
          </div>
        </div>

        <p class="detail-text">{{ selectedNode.description || "该知识点暂未补充说明。" }}</p>

        <div class="detail-grid">
          <div><span class="detail-label">难度</span><strong>{{ selectedNode.difficulty || "未知" }}</strong></div>
          <div><span class="detail-label">当前状态</span><strong>{{ statusTextMap[currentStatus] }}</strong></div>
          <div><span class="detail-label">建议学习时长</span><strong>{{ selectedNode.estimated_minutes ? `${selectedNode.estimated_minutes} 分钟` : "未设置" }}</strong></div>
          <div><span class="detail-label">内容来源</span><strong>{{ originTextMap[selectedNode.origin] || "课程目录" }}</strong></div>
        </div>

        <div v-if="isTeacher" v-loading="loadingTeacherConceptAnalytics" class="detail-section detail-stack teacher-node-analytics">
          <div class="detail-inline">
            <div>
              <span class="detail-label">教师节点统计</span>
              <strong>按班级查看该节点掌握情况与学习热度</strong>
            </div>
            <el-tag type="primary" effect="plain">点击 {{ teacherConceptAnalytics.click_count }} 次</el-tag>
          </div>
          <div class="summary-row compact-summary">
            <div class="summary-metric"><span>平均学习时间</span><strong>{{ teacherConceptAnalytics.average_learning_minutes }} 分钟</strong></div>
            <div class="summary-metric"><span>节点提问</span><strong>{{ teacherConceptAnalytics.question_count }}</strong></div>
            <div class="summary-metric"><span>待跟进</span><strong>{{ teacherConceptAnalytics.pending_question_count }}</strong></div>
          </div>
          <div v-if="teacherConceptAnalytics.class_stats.length" class="teacher-node-class-list">
            <div v-for="item in teacherConceptAnalytics.class_stats" :key="item.class_name" class="analytics-card">
              <div class="card-header-inline">
                <strong>{{ item.class_name }}</strong>
                <el-tag effect="plain">{{ item.student_count }} 人</el-tag>
              </div>
              <div class="status-progress-stack">
                <div>
                  <span>已掌握 {{ item.mastered_count }} 人 · {{ item.mastered_percentage }}%</span>
                  <el-progress :percentage="item.mastered_percentage" :stroke-width="8" color="#6a994e" />
                </div>
                <div>
                  <span>学习中 {{ item.in_progress_count }} 人 · {{ item.in_progress_percentage }}%</span>
                  <el-progress :percentage="item.in_progress_percentage" :stroke-width="8" color="#f4a261" />
                </div>
                <div>
                  <span>未学 {{ item.unlearned_count }} 人 · {{ item.unlearned_percentage }}%</span>
                  <el-progress :percentage="item.unlearned_percentage" :stroke-width="8" color="#adb5bd" />
                </div>
              </div>
              <el-collapse class="top-gap">
                <el-collapse-item title="查看学生名单">
                  <div class="tag-list">
                    <el-tag v-for="stu in item.students_mastered" :key="`m-${item.class_name}-${stu.user_id}`" type="success" effect="plain">{{ stu.display_name }}</el-tag>
                    <el-tag v-for="stu in item.students_in_progress" :key="`p-${item.class_name}-${stu.user_id}`" type="warning" effect="plain">{{ stu.display_name }}</el-tag>
                    <el-tag v-for="stu in item.students_unlearned" :key="`u-${item.class_name}-${stu.user_id}`" effect="plain">{{ stu.display_name }}</el-tag>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>
          </div>
          <el-empty v-else description="当前还没有该节点的班级统计数据。" />
        </div>

        <el-form-item v-if="isStudent && currentUser" label="掌握程度" class="status-editor">
          <el-radio-group :model-value="currentStatus" :disabled="savingStatus" @change="handleStatusChange">
            <el-radio-button :label="0">未学</el-radio-button>
            <el-radio-button :label="1">学习中</el-radio-button>
            <el-radio-button :label="2">已掌握</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <div v-if="isStudent && currentUser" class="node-actions">
          <el-button type="primary" plain @click="applyTargetSelection(selectedNode.id)">
            {{ isTargetNode(selectedNode.id) ? "刷新当前目标路径" : "设为学习目标" }}
          </el-button>
          <el-button v-if="manualTargetId && isTargetNode(selectedNode.id)" text type="primary" @click="resetTargetSelection">恢复系统推荐</el-button>
        </div>
        <div class="detail-section detail-stack">
          <span class="detail-label">前置知识点</span>
          <div class="tag-list">
            <el-tag v-for="item in prerequisiteNodes" :key="item.id" effect="plain" class="clickable-tag" @click="focusNode(item.id)">{{ item.name }}</el-tag>
            <span v-if="!prerequisiteNodes.length" class="empty-hint">暂无前置依赖</span>
          </div>
        </div>

        <div class="detail-section detail-stack">
          <span class="detail-label">可解锁知识点</span>
          <div class="tag-list">
            <el-tag v-for="item in unlockedNodes" :key="item.id" type="success" effect="plain" class="clickable-tag" @click="focusNode(item.id)">{{ item.name }}</el-tag>
            <span v-if="!unlockedNodes.length" class="empty-hint">暂无后续知识点</span>
          </div>
        </div>

        <el-tabs v-model="detailTab" class="node-tabs">
          <el-tab-pane label="知识梳理" name="outline">
            <div class="detail-section detail-stack">
              <span class="detail-label">核心要点</span>
              <ul v-if="selectedNode.key_points?.length" class="point-list">
                <li v-for="point in selectedNode.key_points" :key="point">{{ point }}</li>
              </ul>
              <span v-else class="empty-hint">暂未整理核心要点</span>
            </div>
            <div class="detail-section detail-stack">
              <span class="detail-label">文字讲解</span>
              <p class="detail-text">{{ selectedNode.text_material || "该节点暂未补充文字材料。" }}</p>
            </div>
            <div class="detail-section detail-stack">
              <span class="detail-label">学习提示</span>
              <ul v-if="selectedNode.study_tips?.length" class="point-list">
                <li v-for="tip in selectedNode.study_tips" :key="tip">{{ tip }}</li>
              </ul>
              <span v-else class="empty-hint">暂未配置学习提示</span>
            </div>
            <div class="detail-section detail-stack">
              <span class="detail-label">常见误区</span>
              <ul v-if="selectedNode.common_mistakes?.length" class="point-list">
                <li v-for="mistake in selectedNode.common_mistakes" :key="mistake">{{ mistake }}</li>
              </ul>
              <span v-else class="empty-hint">暂未整理常见误区</span>
            </div>
          </el-tab-pane>

          <el-tab-pane label="学习材料" name="resource">
            <div class="resource-panel-grid">
              <div class="detail-section detail-stack">
                <span class="detail-label">图示材料</span>
                <el-image v-if="selectedNode.image_url" :src="selectedNode.image_url" :preview-src-list="[selectedNode.image_url]" fit="cover" class="material-image" />
                <span v-else class="empty-hint">暂未配置图示材料</span>
              </div>
              <div class="detail-section detail-stack">
                <span class="detail-label">推荐视频</span>
                <el-link v-if="selectedNode.video_url" :href="selectedNode.video_url" type="primary" target="_blank">{{ selectedNode.video_title || "打开视频资源" }}</el-link>
                <p class="detail-text">建议先阅读知识梳理，再结合图示和视频完成理解与复盘。</p>
                <span v-if="!selectedNode.video_url" class="empty-hint">暂未配置视频材料</span>
              </div>
            </div>
            <div class="detail-section detail-stack">
              <span class="detail-label">课堂练习任务</span>
              <p class="detail-text">{{ selectedNode.practice_task || "暂未配置练习任务。" }}</p>
            </div>
          </el-tab-pane>

          <el-tab-pane label="自测题" name="quiz">
            <div v-if="selectedNode.quiz?.length" class="quiz-list">
              <div class="detail-section detail-stack quiz-intro">
                <span class="detail-label">自测说明</span>
                <p class="detail-text">达到 80 分以上时，可以直接将当前节点标记为“已掌握”。</p>
              </div>
              <div v-for="(question, questionIndex) in selectedNode.quiz" :key="`${selectedNode.id}-${questionIndex}`" class="quiz-card">
                <div class="quiz-title">{{ questionIndex + 1 }}. {{ question.question }}</div>
                <el-radio-group :model-value="activeQuizAnswers[questionIndex]" class="quiz-options" @change="(value) => updateQuizAnswer(questionIndex, value)">
                  <el-radio v-for="(option, optionIndex) in question.options" :key="`${selectedNode.id}-${questionIndex}-${optionIndex}`" :label="optionIndex" class="quiz-option">{{ option }}</el-radio>
                </el-radio-group>
                <div v-if="activeQuizResult" class="quiz-feedback">
                  <el-tag :type="activeQuizResult.details[questionIndex]?.is_correct ? 'success' : 'danger'" effect="plain">
                    {{ activeQuizResult.details[questionIndex]?.is_correct ? '回答正确' : `正确答案：${question.options[question.answer_index]}` }}
                  </el-tag>
                  <p>{{ question.explanation }}</p>
                </div>
              </div>
              <div class="quiz-actions">
                <el-button type="primary" @click="submitQuiz">提交自测</el-button>
                <el-button @click="resetQuiz">重新作答</el-button>
                <el-button v-if="activeQuizResult && activeQuizResult.score >= 80 && currentUser && currentStatus !== 2" type="success" plain @click="markCurrentNodeMastered">测试通过，标记为已掌握</el-button>
              </div>
              <div v-if="activeQuizResult" class="quiz-summary">
                <div class="summary-metric"><span>正确题数</span><strong>{{ activeQuizResult.correct }}/{{ activeQuizResult.total }}</strong></div>
                <div class="summary-metric"><span>测验得分</span><strong>{{ activeQuizResult.score }} 分</strong></div>
                <div class="summary-metric"><span>学习建议</span><strong>{{ activeQuizResult.score >= 80 ? '可以继续进阶' : '建议回看材料' }}</strong></div>
              </div>
            </div>
            <el-empty v-else description="该节点暂未配置自测题。" />
          </el-tab-pane>

          <el-tab-pane label="节点论坛" name="forum">
            <div class="detail-stack">
              <div class="detail-section detail-stack">
                <div class="detail-inline">
                  <div>
                    <span class="detail-label">节点讨论区</span>
                    <strong>围绕当前知识点发起问题、回复评论、沉淀优秀讨论</strong>
                  </div>
                  <el-button v-if="currentUser?.role === 'student'" type="primary" plain @click="openQuestionDialog">针对节点提问</el-button>
                </div>
                <p class="detail-text">学生负责发起问题，任何已登录用户都可以参与回复；评论支持点赞，评论作者可以删除自己的内容，教师可以置顶讨论并将优质回复设为优秀评论。</p>
              </div>

              <div v-loading="loadingNodeQuestions" class="thread-list">
                <template v-if="currentUser">
                  <div v-for="thread in orderedNodeQuestions" :key="thread.id" class="thread-card">
                    <div class="question-header">
                      <div>
                        <h3>{{ thread.title }}</h3>
                        <p>{{ thread.student_name }} · {{ formatDate(thread.create_time) }}</p>
                      </div>
                      <div class="tag-list">
                        <el-tag v-if="thread.is_featured" type="warning" effect="dark">教师置顶</el-tag>
                        <el-tag effect="plain">{{ thread.comment_count }} 条评论</el-tag>
                      </div>
                    </div>
                    <p class="detail-text">{{ thread.description }}</p>
                    <div class="question-actions">
                      <el-button text type="primary" @click="openReplyComposer(thread)">{{ activeReplyQuestionId === thread.id ? '收起回复' : '回复讨论' }}</el-button>
                      <el-button v-if="isStudent && thread.is_featured" plain type="success" @click="handleQuestionFavorite(thread)">
                        {{ thread.is_favorited ? '取消收藏' : '收藏优秀回答' }}
                      </el-button>
                      <el-button v-if="isTeacher" plain type="warning" @click="handleQuestionFeature(thread)">{{ thread.is_featured ? '取消置顶' : '置顶讨论' }}</el-button>
                    </div>
                    <div v-if="activeReplyQuestionId === thread.id" class="reply-composer">
                      <div v-if="replyContext.parentCommentId" class="detail-text reply-context-line">正在回复：{{ replyContext.targetName }}</div>
                      <el-input v-model="replyDrafts[thread.id]" type="textarea" :rows="3" placeholder="围绕当前节点补充你的理解、答疑建议或实践经验" />
                      <div class="dialog-footer">
                        <el-button @click="closeReplyComposer">取消</el-button>
                        <el-button type="primary" :loading="submittingCommentId === thread.id" @click="handleCommentSubmit(thread)">发布回复</el-button>
                      </div>
                    </div>

                    <div v-if="thread.comments.length" class="thread-comment-list">
                      <ThreadCommentTree
                        :comments="thread.comments"
                        :current-user-id="currentUser?.id || null"
                        :can-reply="Boolean(currentUser)"
                        :can-like="Boolean(currentUser)"
                        :is-teacher="isTeacher"
                        @reply="(comment) => openReplyComposer(thread, comment)"
                        @like="handleCommentLike"
                        @delete="handleCommentDelete"
                        @feature="handleCommentFeature"
                      />
                    </div>
                    <el-empty v-else description="这个讨论还没有回复，欢迎补充你的理解或问题。" />
                  </div>
                  <el-empty v-if="!orderedNodeQuestions.length" description="当前节点还没有讨论，欢迎发起第一条问题。" />
                </template>
                <el-empty v-else description="登录后可参与节点讨论、点赞评论与记录学习状态。" />
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      <el-empty v-else description="点击图谱中的节点，查看该知识点的学习详情与讨论区。" />
    </el-drawer>

    <el-dialog v-model="questionDialogVisible" title="围绕当前节点提问" width="640px">
      <div v-if="selectedNode" class="reply-preview">
        <h3>{{ selectedNode.name }}</h3>
        <p class="detail-text">{{ selectedNode.description || "请结合当前知识点描述你的困惑或讨论主题。" }}</p>
      </div>
      <el-form label-width="88px">
        <el-form-item label="问题标题"><el-input v-model="questionForm.title" placeholder="例如：为什么这个知识点会影响后续学习路径？" /></el-form-item>
        <el-form-item label="问题描述">
          <el-input v-model="questionForm.description" type="textarea" :rows="5" placeholder="说明你当前卡住的地方、已经尝试过的方法，或希望大家重点讨论的部分" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="questionDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="savingQuestion" @click="handleQuestionSubmit">提交问题</el-button>
        </div>
      </template>
    </el-dialog>
  </AppShell>
</template>

<script setup>
import { ElMessage, ElMessageBox } from "element-plus";
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { fetchGraphAll } from "../api/graph";
import { createQuestion, createQuestionComment, deleteQuestionComment, fetchLearningQuestions, fetchLearningStatuses, recordNodeVisit, submitQuizAttempt, toggleQuestionCommentLike, toggleQuestionFavorite, updateLearningStatus } from "../api/learning";
import { fetchRecommendOverview } from "../api/recommend";
import { featureTeacherComment, featureTeacherQuestion, fetchTeacherConceptAnalytics } from "../api/teacher";
import AppShell from "../components/AppShell.vue";
import GraphCanvasEcharts from "../components/GraphCanvasEcharts.vue";
import ThreadCommentTree from "../components/ThreadCommentTree.vue";
import { getCurrentUser } from "../utils/session";

const router = useRouter();
const route = useRoute();
const keyword = ref("");
const errorMessage = ref("");
const currentUser = ref(getCurrentUser());
const selectedNodeId = ref("");
const nodeDrawerVisible = ref(false);
const manualTargetId = ref("");
const statusMap = ref({});
const savingStatus = ref(false);
const questionDialogVisible = ref(false);
const savingQuestion = ref(false);
const loadingNodeQuestions = ref(false);
const activeReplyQuestionId = ref("");
const submittingCommentId = ref(0);
const detailTab = ref("outline");
const nodeQuestions = ref([]);
const loadingTeacherConceptAnalytics = ref(false);
const teacherConceptAnalytics = ref(createEmptyTeacherConceptAnalytics());
const quizAnswers = ref({});
const quizResults = ref({});
const activeVisitNodeId = ref("");
const activeVisitStartedAt = ref(0);
const replyDrafts = reactive({});
const replyContext = reactive({
  questionId: 0,
  parentCommentId: null,
  targetName: "",
});
const graph = reactive({ nodes: [], links: [] });
const questionForm = reactive({ title: "", description: "" });

const statusTextMap = { 0: "未学", 1: "学习中", 2: "已掌握" };
const originTextMap = { neo4j: "图数据库", catalog: "课程目录补充" };

function createEmptyOverview() {
  return { progress_rate: 0, total_concepts: 0, mastered_count: 0, in_progress_count: 0, unlearned_count: 0, recommended_concepts: [], weak_points: [], default_target: null, learning_path: [] };
}

function createEmptyTeacherConceptAnalytics() {
  return {
    concept_id: "",
    concept_name: "",
    category: "",
    click_count: 0,
    average_learning_minutes: 0,
    question_count: 0,
    pending_question_count: 0,
    featured_question_count: 0,
    class_stats: [],
    recent_questions: [],
  };
}

const overview = ref(createEmptyOverview());
const isStudent = computed(() => currentUser.value?.role === "student");
const isTeacher = computed(() => currentUser.value?.role === "teacher");
const nodeMap = computed(() => new Map(graph.nodes.map((node) => [node.id, node])));
const recommendedNodeIds = computed(() => overview.value.recommended_concepts.map((item) => item.id));
const learningPathNodeIds = computed(() => overview.value.learning_path.map((item) => item.concept.id));
const weakPointNodeIds = computed(() => overview.value.weak_points.map((item) => item.concept.id));
const selectedNode = computed(() => nodeMap.value.get(selectedNodeId.value) || null);
const targetOptions = computed(() => graph.nodes.filter((node) => (statusMap.value[node.id] ?? 0) !== 2 || node.id === manualTargetId.value).sort((a, b) => a.name.localeCompare(b.name, "zh-CN")));
const filteredNodes = computed(() => !keyword.value ? graph.nodes : graph.nodes.filter((node) => [node.name, node.category, node.description, node.text_material, node.practice_task, ...(node.study_tips || []), ...(node.common_mistakes || []), ...(node.key_points || [])].filter(Boolean).some((text) => text.includes(keyword.value))));
const filteredLinks = computed(() => {
  const visible = new Set(filteredNodes.value.map((node) => node.id));
  return graph.links.filter((link) => visible.has(link.source) && visible.has(link.target));
});
const currentStatus = computed(() => selectedNode.value ? statusMap.value[selectedNode.value.id] ?? 0 : 0);
const prerequisiteNodes = computed(() => !selectedNode.value ? [] : graph.links.filter((link) => link.type === "PREREQUISITE_OF" && link.target === selectedNode.value.id).map((link) => nodeMap.value.get(link.source)).filter(Boolean));
const unlockedNodes = computed(() => !selectedNode.value ? [] : graph.links.filter((link) => link.type === "PREREQUISITE_OF" && link.source === selectedNode.value.id).map((link) => nodeMap.value.get(link.target)).filter(Boolean));
const progressRate = computed(() => {
  if (!graph.nodes.length) return 0;
  const score = graph.nodes.reduce((total, node) => total + (statusMap.value[node.id] === 2 ? 1 : statusMap.value[node.id] === 1 ? 0.5 : 0), 0);
  return Math.round((score / graph.nodes.length) * 100);
});
const activeQuizAnswers = computed(() => selectedNode.value ? quizAnswers.value[selectedNode.value.id] || [] : []);
const activeQuizResult = computed(() => selectedNode.value ? quizResults.value[selectedNode.value.id] || null : null);
const orderedNodeQuestions = computed(() => [...nodeQuestions.value].sort((a, b) => (a.is_featured === b.is_featured ? new Date(b.create_time) - new Date(a.create_time) : a.is_featured ? -1 : 1)));

function formatDate(value) {
  return value ? new Date(value).toLocaleString("zh-CN", { hour12: false }) : "";
}

async function finishNodeVisit() {
  if (!activeVisitNodeId.value || !activeVisitStartedAt.value || !currentUser.value) return;
  const node = nodeMap.value.get(activeVisitNodeId.value);
  const durationSeconds = Math.max(Math.round((Date.now() - activeVisitStartedAt.value) / 1000), 0);
  activeVisitNodeId.value = "";
  activeVisitStartedAt.value = 0;
  if (!node || durationSeconds < 3) return;
  try {
    await recordNodeVisit(node.id, {
      concept_name: node.name,
      duration_seconds: Math.min(durationSeconds, 7200),
    });
    if (isTeacher.value) {
      await loadTeacherConceptAnalytics(node.id);
    }
  } catch (error) {
    console.error(error);
  }
}

function beginNodeVisit(node) {
  if (!currentUser.value || !node) return;
  activeVisitNodeId.value = node.id;
  activeVisitStartedAt.value = Date.now();
}

watch(nodeDrawerVisible, async (visible) => {
  if (!visible) {
    await finishNodeVisit();
  }
});

watch(filteredNodes, (nodes) => {
  if (!nodes.length) {
    selectedNodeId.value = "";
    nodeDrawerVisible.value = false;
    return;
  }
  if (!selectedNodeId.value || !nodes.some((node) => node.id === selectedNodeId.value)) {
    selectedNodeId.value = nodes[0].id;
  }
}, { immediate: true });

watch(selectedNode, async (node) => {
  detailTab.value = "outline";
  closeReplyComposer();
  if (!node) {
    nodeQuestions.value = [];
    teacherConceptAnalytics.value = createEmptyTeacherConceptAnalytics();
    return;
  }
  const quizLength = node.quiz?.length || 0;
  if (!quizAnswers.value[node.id] || quizAnswers.value[node.id].length !== quizLength) {
    quizAnswers.value = { ...quizAnswers.value, [node.id]: Array(quizLength).fill(null) };
  }
  await loadNodeQuestions(node.id);
  if (isTeacher.value) {
    await loadTeacherConceptAnalytics(node.id);
  }
}, { immediate: true });

function isRecommendedNode(nodeId) { return recommendedNodeIds.value.includes(nodeId); }
function isPathNode(nodeId) { return learningPathNodeIds.value.includes(nodeId); }
function isWeakPointNode(nodeId) { return weakPointNodeIds.value.includes(nodeId); }
function isTargetNode(nodeId) { return overview.value.default_target?.id === nodeId; }
function focusNode(nodeId, { syncRoute = true } = {}) {
  const node = nodeMap.value.get(nodeId);
  if (nodeDrawerVisible.value && activeVisitNodeId.value && activeVisitNodeId.value !== nodeId) {
    finishNodeVisit();
  }
  selectedNodeId.value = nodeId;
  if (currentUser.value) {
    nodeDrawerVisible.value = true;
    beginNodeVisit(node);
  }
  if (syncRoute) {
    router.replace({ path: "/graph", query: { ...route.query, focus: nodeId } });
  }
}
async function handleNodeSelect(nodeId) {
  selectedNodeId.value = nodeId;
  if (!currentUser.value) {
    nodeDrawerVisible.value = false;
    try {
      await ElMessageBox.confirm(
        "游客模式可以浏览图谱整体结构。登录后才可查看节点详情、学习材料、自测题和节点论坛，是否前往登录？",
        "请先登录",
        {
          confirmButtonText: "前往登录",
          cancelButtonText: "继续浏览",
          type: "info",
        },
      );
      router.push("/login");
    } catch (error) {
      if (error !== "cancel") {
        console.error(error);
      }
    }
    return;
  }
  focusNode(nodeId);
}
function closeReplyComposer() {
  activeReplyQuestionId.value = "";
  replyContext.questionId = 0;
  replyContext.parentCommentId = null;
  replyContext.targetName = "";
}

function openReplyComposer(thread, comment = null) {
  if (!currentUser.value) {
    ElMessage.warning("请先登录后再参与讨论。");
    return;
  }
  const nextParentCommentId = comment?.id ?? null;
  const isSameComposer =
    activeReplyQuestionId.value === thread.id &&
    replyContext.parentCommentId === nextParentCommentId;
  if (isSameComposer) {
    closeReplyComposer();
    return;
  }
  activeReplyQuestionId.value = thread.id;
  replyContext.questionId = thread.id;
  replyContext.parentCommentId = nextParentCommentId;
  replyContext.targetName = comment?.author_name || "";
}

function openQuestionDialog() {
  if (!selectedNode.value || currentUser.value?.role !== "student") return;
  questionForm.title = "";
  questionForm.description = "";
  questionDialogVisible.value = true;
}

async function loadGraph() {
  try {
    const { data } = await fetchGraphAll();
    graph.nodes = data.nodes;
    graph.links = data.links;
    if (graph.nodes.length && !selectedNodeId.value) selectedNodeId.value = graph.nodes[0].id;
  } catch (error) {
    errorMessage.value = "暂未连接到后端图谱接口，请检查 FastAPI 服务与代理配置。";
    console.error(error);
  }
}

async function loadLearningStatuses() {
  if (!currentUser.value) {
    statusMap.value = {};
    return;
  }
  try {
    const { data } = await fetchLearningStatuses();
    statusMap.value = data.status_map || {};
  } catch (error) {
    console.error(error);
    ElMessage.warning("学习状态加载失败，稍后仍可继续浏览知识图谱。");
  }
}

async function loadRecommendGuidance(targetConceptId = manualTargetId.value || undefined) {
  if (!isStudent.value) {
    overview.value = createEmptyOverview();
    return;
  }
  try {
    const { data } = await fetchRecommendOverview(targetConceptId);
    overview.value = data;
  } catch (error) {
    console.error(error);
    ElMessage.warning("个性化导学暂未刷新成功，已先展示图谱浏览功能。");
  }
}

async function loadNodeQuestions(conceptId = selectedNode.value?.id) {
  if (!conceptId || !currentUser.value) {
    nodeQuestions.value = [];
    return;
  }
  try {
    loadingNodeQuestions.value = true;
    const { data } = await fetchLearningQuestions({ concept_id: conceptId });
    nodeQuestions.value = data.items || [];
  } catch (error) {
    console.error(error);
    nodeQuestions.value = [];
  } finally {
    loadingNodeQuestions.value = false;
  }
}

async function loadTeacherConceptAnalytics(conceptId = selectedNode.value?.id) {
  if (!conceptId || !isTeacher.value) {
    teacherConceptAnalytics.value = createEmptyTeacherConceptAnalytics();
    return;
  }
  try {
    loadingTeacherConceptAnalytics.value = true;
    const { data } = await fetchTeacherConceptAnalytics(conceptId);
    teacherConceptAnalytics.value = data;
  } catch (error) {
    console.error(error);
    teacherConceptAnalytics.value = createEmptyTeacherConceptAnalytics();
  } finally {
    loadingTeacherConceptAnalytics.value = false;
  }
}

async function applyTargetSelection(nodeId) {
  if (!isStudent.value || !nodeId) return;
  manualTargetId.value = nodeId;
  focusNode(nodeId);
  await loadRecommendGuidance(nodeId);
  ElMessage.success("学习目标已更新，推荐路径已重新计算。");
}

async function resetTargetSelection() {
  manualTargetId.value = "";
  await loadRecommendGuidance();
  ElMessage.success("已恢复系统自动推荐目标。");
}

async function handleTargetSelect(nodeId) {
  if (!nodeId) {
    await resetTargetSelection();
    return;
  }
  await applyTargetSelection(nodeId);
}

async function handleQuestionSubmit() {
  const title = questionForm.title.trim();
  const description = questionForm.description.trim();
  if (!selectedNode.value || !currentUser.value || currentUser.value.role !== "student") {
    ElMessage.warning("只有学生可以围绕当前节点发起问题。");
    return;
  }
  if (title.length < 2 || description.length < 5) {
    ElMessage.warning("请完整填写问题标题和描述。");
    return;
  }
  try {
    savingQuestion.value = true;
    await createQuestion({ concept_id: selectedNode.value.id, concept_name: selectedNode.value.name, title, description });
    questionDialogVisible.value = false;
    ElMessage.success("问题已发布，其他同学和老师都可以继续回复。");
    await loadNodeQuestions(selectedNode.value.id);
  } catch (error) {
    console.error(error);
    ElMessage.error("提交问题失败，请稍后重试。");
  } finally {
    savingQuestion.value = false;
  }
}

async function handleCommentSubmit(thread) {
  const content = (replyDrafts[thread.id] || "").trim();
  if (!currentUser.value) {
    ElMessage.warning("请先登录后再参与讨论。");
    return;
  }
  if (content.length < 2) {
    ElMessage.warning("回复内容至少需要 2 个字。");
    return;
  }
  try {
    submittingCommentId.value = thread.id;
    await createQuestionComment(thread.id, content, replyContext.questionId === thread.id ? replyContext.parentCommentId : null);
    replyDrafts[thread.id] = "";
    closeReplyComposer();
    await loadNodeQuestions(selectedNode.value?.id);
    ElMessage.success("回复已发布。");
  } catch (error) {
    console.error(error);
    ElMessage.error("发布回复失败，请稍后重试。");
  } finally {
    submittingCommentId.value = 0;
  }
}

async function handleQuestionFeature(thread) {
  if (!isTeacher.value) return;
  try {
    await featureTeacherQuestion(thread.id, !thread.is_featured);
    await loadNodeQuestions(selectedNode.value?.id);
    ElMessage.success(thread.is_featured ? "已取消置顶。" : "已置顶该讨论。");
  } catch (error) {
    console.error(error);
    ElMessage.error("更新置顶状态失败，请稍后重试。");
  }
}

async function handleQuestionFavorite(thread) {
  if (!isStudent.value) return;
  try {
    const { data } = await toggleQuestionFavorite(thread.id);
    await loadNodeQuestions(selectedNode.value?.id);
    ElMessage.success(data.is_favorited ? "已收藏优秀回答，可在个人中心查看。" : "已取消收藏。");
  } catch (error) {
    console.error(error);
    ElMessage.error("收藏失败：只有教师置顶且已有回复沉淀的问题可以收藏。");
  }
}

async function handleCommentFeature(comment) {
  if (!isTeacher.value) return;
  try {
    await featureTeacherComment(comment.id, !comment.is_excellent);
    await loadNodeQuestions(selectedNode.value?.id);
    ElMessage.success(comment.is_excellent ? "已取消优秀评论。" : "已设为优秀评论。");
  } catch (error) {
    console.error(error);
    ElMessage.error("更新优秀评论失败，请稍后重试。");
  }
}

async function handleCommentLike(comment) {
  if (!currentUser.value) {
    ElMessage.warning("请先登录后再点赞。");
    return;
  }
  try {
    await toggleQuestionCommentLike(comment.id);
    await loadNodeQuestions(selectedNode.value?.id);
  } catch (error) {
    console.error(error);
    ElMessage.error("点赞失败，请稍后重试。");
  }
}

async function handleCommentDelete(comment) {
  try {
    await ElMessageBox.confirm("删除后该评论将不再展示，是否继续？", "删除评论", { type: "warning", confirmButtonText: "删除", cancelButtonText: "取消" });
    await deleteQuestionComment(comment.id);
    await loadNodeQuestions(selectedNode.value?.id);
    ElMessage.success("评论已删除。");
  } catch (error) {
    if (error === "cancel") return;
    console.error(error);
    ElMessage.error("删除评论失败，请稍后重试。");
  }
}

async function handleStatusChange(nextStatus) {
  if (!selectedNode.value || !currentUser.value) {
    ElMessage.info("请先登录后再记录掌握情况。");
    return;
  }
  try {
    savingStatus.value = true;
    await updateLearningStatus(selectedNode.value.id, Number(nextStatus));
    statusMap.value = { ...statusMap.value, [selectedNode.value.id]: Number(nextStatus) };
    if (isStudent.value) await loadRecommendGuidance();
    ElMessage.success(`已更新为“${statusTextMap[nextStatus]}”`);
  } catch (error) {
    console.error(error);
    ElMessage.error("保存学习状态失败，请检查登录状态或稍后重试。");
  } finally {
    savingStatus.value = false;
  }
}

function updateQuizAnswer(questionIndex, optionIndex) {
  if (!selectedNode.value) return;
  const nodeId = selectedNode.value.id;
  const nextAnswers = [...(quizAnswers.value[nodeId] || [])];
  nextAnswers[questionIndex] = optionIndex;
  quizAnswers.value = { ...quizAnswers.value, [nodeId]: nextAnswers };
}

function resetQuiz() {
  if (!selectedNode.value) return;
  const nodeId = selectedNode.value.id;
  quizAnswers.value = { ...quizAnswers.value, [nodeId]: Array(selectedNode.value.quiz?.length || 0).fill(null) };
  quizResults.value = { ...quizResults.value, [nodeId]: null };
}

async function submitQuiz() {
  if (!selectedNode.value?.quiz?.length) return;
  const nodeId = selectedNode.value.id;
  const answers = quizAnswers.value[nodeId] || [];
  if (answers.some((value) => value === null || value === undefined)) {
    ElMessage.warning("请先完成全部题目后再提交。");
    return;
  }
  let correct = 0;
  const details = selectedNode.value.quiz.map((question, index) => {
    const isCorrect = answers[index] === question.answer_index;
    if (isCorrect) correct += 1;
    return { selected_index: answers[index], is_correct: isCorrect };
  });
  const total = selectedNode.value.quiz.length;
  const score = Math.round((correct / total) * 100);
  quizResults.value = { ...quizResults.value, [nodeId]: { total, correct, score, details } };
  try {
    await submitQuizAttempt(nodeId, {
      concept_name: selectedNode.value.name,
      total_questions: total,
      correct_answers: correct,
      score,
    });
  } catch (error) {
    console.error(error);
  }
  ElMessage.success(`自测完成，当前得分 ${score} 分。`);
}

async function markCurrentNodeMastered() {
  await handleStatusChange(2);
}

onMounted(async () => {
  await loadGraph();
  await loadLearningStatuses();
  await loadRecommendGuidance();
  if (route.query.focus) {
    focusNode(String(route.query.focus), { syncRoute: false });
  }
});

watch(
  () => route.query.focus,
  (focusId) => {
    if (!focusId) {
      return;
    }
    if (graph.nodes.some((node) => node.id === focusId)) {
      focusNode(String(focusId), { syncRoute: false });
    }
  },
);
</script>
