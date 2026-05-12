<template>
  <AppShell>
    <div class="page-grid graph-page">
      <div class="page-grid graph-layout">
        <el-card class="side-panel">
        <template #header>图谱控制台</template>
        <el-input v-model="keyword" placeholder="搜索知识点" clearable />
        <el-divider />
        <div class="metric">
          <span>节点总数</span>
          <strong>{{ graph.nodes.length }}</strong>
        </div>
        <div class="metric">
          <span>关系总数</span>
          <strong>{{ graph.links.length }}</strong>
        </div>
        <div class="metric">
          <span>学习进度</span>
          <strong>{{ progressRate }}%</strong>
        </div>
        <el-progress :percentage="progressRate" :stroke-width="10" color="#bc6c25" />
        <el-alert
          v-if="errorMessage"
          :title="errorMessage"
          type="warning"
          :closable="false"
          show-icon
          class="spaced"
        />
        <el-alert
          v-else-if="!currentUser"
          title="登录后可标记知识点掌握状态，并在图谱下方查看个性化学习导航。"
          type="info"
          :closable="false"
          show-icon
          class="spaced"
        />
        <el-alert
          v-else-if="isStudent && overview.default_target"
          :title="`当前推荐目标：${overview.default_target.name}`"
          type="success"
          :closable="false"
          show-icon
          class="spaced"
        />
        <el-divider />
        <div v-if="isStudent && currentUser && graph.nodes.length" class="detail-section detail-stack compact-panel">
          <div class="detail-inline">
            <div>
              <span class="detail-label">学习目标</span>
              <strong>{{ manualTargetId ? "手动设定中" : "系统智能推荐" }}</strong>
            </div>
            <el-button v-if="manualTargetId" text type="primary" @click="resetTargetSelection">恢复推荐</el-button>
          </div>
          <el-select
            :model-value="manualTargetId || overview.default_target?.id || ''"
            placeholder="选择希望优先攻克的知识点"
            filterable
            clearable
            @change="handleTargetSelect"
          >
            <el-option
              v-for="node in targetOptions"
              :key="node.id"
              :label="node.name"
              :value="node.id"
            />
          </el-select>
          <p class="detail-text">切换学习目标后，系统会重新生成推荐路径，并在图谱中高亮优先学习节点。</p>
        </div>
        <el-divider />
        <div v-if="selectedNode" class="node-detail">
          <div class="detail-header">
            <div>
              <h3>{{ selectedNode.name }}</h3>
              <div class="tag-list top-gap">
                <el-tag>{{ selectedNode.category || "未分类" }}</el-tag>
                <el-tag v-if="isTargetNode(selectedNode.id)" type="warning" effect="dark">当前推荐目标</el-tag>
                <el-tag v-else-if="isPathNode(selectedNode.id)" type="warning" effect="plain">推荐路径节点</el-tag>
                <el-tag v-if="isWeakPointNode(selectedNode.id)" type="danger" effect="plain">薄弱点</el-tag>
                <el-tag v-if="isRecommendedNode(selectedNode.id)" type="success" effect="plain">优先学习</el-tag>
              </div>
            </div>
          </div>
          <p class="detail-text">{{ selectedNode.description || "该知识点暂未填写说明。" }}</p>
          <div class="detail-grid">
            <div>
              <span class="detail-label">难度</span>
              <strong>{{ selectedNode.difficulty || "未知" }}</strong>
            </div>
            <div>
              <span class="detail-label">当前状态</span>
              <strong>{{ statusTextMap[currentStatus] }}</strong>
            </div>
            <div>
              <span class="detail-label">建议学习时长</span>
              <strong>{{ selectedNode.estimated_minutes ? `${selectedNode.estimated_minutes} 分钟` : "未设置" }}</strong>
            </div>
            <div>
              <span class="detail-label">内容来源</span>
              <strong>{{ originTextMap[selectedNode.origin] || "课程目录" }}</strong>
            </div>
          </div>
          <el-form-item label="掌握程度" class="status-editor">
            <el-radio-group
              :model-value="currentStatus"
              :disabled="!currentUser || savingStatus"
              @change="handleStatusChange"
            >
              <el-radio-button :label="0">未学</el-radio-button>
              <el-radio-button :label="1">学习中</el-radio-button>
              <el-radio-button :label="2">已掌握</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <div v-if="isStudent && currentUser" class="node-actions">
            <el-button
              type="primary"
              plain
              @click="applyTargetSelection(selectedNode.id)"
            >
              {{ isTargetNode(selectedNode.id) ? "重新计算当前目标路径" : "设为学习目标" }}
            </el-button>
            <el-button v-if="manualTargetId && isTargetNode(selectedNode.id)" text type="primary" @click="resetTargetSelection">
              恢复系统推荐
            </el-button>
          </div>
          <div class="detail-section">
            <span class="detail-label">前置知识点</span>
            <div class="tag-list">
              <el-tag
                v-for="item in prerequisiteNodes"
                :key="item.id"
                effect="plain"
                class="clickable-tag"
                @click="focusNode(item.id)"
              >
                {{ item.name }}
              </el-tag>
              <span v-if="!prerequisiteNodes.length" class="empty-hint">暂无前置依赖</span>
            </div>
          </div>
          <div class="detail-section">
            <span class="detail-label">可解锁知识点</span>
            <div class="tag-list">
              <el-tag
                v-for="item in unlockedNodes"
                :key="item.id"
                type="success"
                effect="plain"
                class="clickable-tag"
                @click="focusNode(item.id)"
              >
                {{ item.name }}
              </el-tag>
              <span v-if="!unlockedNodes.length" class="empty-hint">暂无后续节点</span>
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
              <div class="detail-section detail-stack">
                <span class="detail-label">课堂练习任务</span>
                <p class="detail-text">{{ selectedNode.practice_task || "暂未配置实践任务。" }}</p>
              </div>
            </el-tab-pane>

            <el-tab-pane label="学习材料" name="resource">
              <div class="resource-panel-grid">
                <div class="detail-section detail-stack">
                  <span class="detail-label">图示材料</span>
                  <el-image
                    v-if="selectedNode.image_url"
                    :src="selectedNode.image_url"
                    :preview-src-list="[selectedNode.image_url]"
                    fit="cover"
                    class="material-image"
                  />
                  <span v-else class="empty-hint">暂未配置图示材料</span>
                </div>
                <div class="detail-section detail-stack">
                  <span class="detail-label">推荐视频</span>
                  <el-link
                    v-if="selectedNode.video_url"
                    :href="selectedNode.video_url"
                    type="primary"
                    target="_blank"
                  >
                    {{ selectedNode.video_title || "打开视频资源" }}
                  </el-link>
                  <p class="detail-text">建议先阅读“知识梳理”，再观看视频和图示材料，效果会更好。</p>
                  <span v-if="!selectedNode.video_url" class="empty-hint">暂未配置视频材料</span>
                </div>
              </div>
              <div class="detail-section detail-stack">
                <span class="detail-label">延伸资源</span>
                <div v-if="selectedNode.resource_links?.length" class="resource-list">
                  <el-link
                    v-for="resource in selectedNode.resource_links"
                    :key="resource.url"
                    :href="resource.url"
                    type="primary"
                    target="_blank"
                    class="resource-link"
                  >
                    {{ resource.label }}
                  </el-link>
                </div>
                <span v-else class="empty-hint">暂未配置外部资源</span>
              </div>
            </el-tab-pane>

            <el-tab-pane label="自测题" name="quiz">
              <div v-if="selectedNode.quiz?.length" class="quiz-list">
                <div class="detail-section detail-stack quiz-intro">
                  <span class="detail-label">自测说明</span>
                  <p class="detail-text">建议先完成知识梳理和学习材料，再进行自测。得分达到 80 分及以上时，可直接标记为“已掌握”。</p>
                </div>
                <div
                  v-for="(question, questionIndex) in selectedNode.quiz"
                  :key="question.question"
                  class="quiz-card"
                >
                  <div class="quiz-title">{{ questionIndex + 1 }}. {{ question.question }}</div>
                  <el-radio-group
                    :model-value="activeQuizAnswers[questionIndex]"
                    class="quiz-options"
                    @change="(value) => updateQuizAnswer(questionIndex, value)"
                  >
                    <el-radio
                      v-for="(option, optionIndex) in question.options"
                      :key="`${question.question}-${optionIndex}`"
                      :label="optionIndex"
                      class="quiz-option"
                    >
                      {{ option }}
                    </el-radio>
                  </el-radio-group>

                  <div v-if="activeQuizResult" class="quiz-feedback">
                    <el-tag :type="activeQuizResult.details[questionIndex]?.is_correct ? 'success' : 'danger'" effect="plain">
                      {{
                        activeQuizResult.details[questionIndex]?.is_correct
                          ? "回答正确"
                          : `正确答案：${question.options[question.answer_index]}`
                      }}
                    </el-tag>
                    <p>{{ question.explanation }}</p>
                  </div>
                </div>

                <div class="quiz-actions">
                  <el-button type="primary" @click="submitQuiz">提交自测</el-button>
                  <el-button @click="resetQuiz">重新作答</el-button>
                  <el-button
                    v-if="activeQuizResult && activeQuizResult.score >= 80 && currentUser && currentStatus !== 2"
                    type="success"
                    plain
                    @click="markCurrentNodeMastered"
                  >
                    测验通过，标记为已掌握
                  </el-button>
                </div>

                <div v-if="activeQuizResult" class="quiz-summary">
                  <div class="summary-metric">
                    <span>正确题数</span>
                    <strong>{{ activeQuizResult.correct }}/{{ activeQuizResult.total }}</strong>
                  </div>
                  <div class="summary-metric">
                    <span>测验得分</span>
                    <strong>{{ activeQuizResult.score }} 分</strong>
                  </div>
                  <div class="summary-metric">
                    <span>学习建议</span>
                    <strong>{{ activeQuizResult.score >= 80 ? "可以继续进阶" : "建议回看材料" }}</strong>
                  </div>
                </div>
              </div>
              <el-empty v-else description="该节点暂未配置自测题。" />
            </el-tab-pane>

            <el-tab-pane label="节点问答" name="question">
              <div class="detail-section detail-stack">
                <div class="detail-inline">
                  <div>
                    <span class="detail-label">节点互动说明</span>
                    <strong>围绕当前知识点发起问题、查看教师置顶的优秀回答</strong>
                  </div>
                  <el-button v-if="currentUser?.role === 'student'" type="primary" plain @click="openQuestionDialog">
                    针对该节点提问
                  </el-button>
                </div>
                <p class="detail-text">
                  {{
                    currentUser?.role === "student"
                      ? "你的提问会自动绑定到当前节点；教师回复并置顶后，其他学生也能在这里看到优秀问答。"
                      : "这里会展示与当前知识点相关的问答记录，方便从知识点维度观察学习难点。"
                  }}
                </p>
              </div>

              <div v-if="featuredNodeQuestions.length" class="question-list">
                <div v-for="item in featuredNodeQuestions" :key="`featured-${item.id}`" class="question-card">
                  <div class="question-header">
                    <div>
                      <h3>{{ item.title }}</h3>
                      <p>{{ item.student_name }} · {{ formatDate(item.create_time) }}</p>
                    </div>
                    <div class="tag-list">
                      <el-tag type="warning" effect="dark">教师置顶</el-tag>
                      <el-tag type="success" effect="plain">收藏 {{ item.favorite_count }}</el-tag>
                    </div>
                  </div>
                  <p class="detail-text">{{ item.description }}</p>
                  <div v-if="item.teacher_reply" class="reply-card">
                    <span class="detail-label">教师回复</span>
                    <strong>{{ item.teacher_name || "任课教师" }}</strong>
                    <p>{{ item.teacher_reply }}</p>
                  </div>
                  <div v-if="currentUser?.role === 'student'" class="question-actions">
                    <el-button type="primary" plain @click="handleFavoriteQuestion(item)">
                      {{ item.is_favorited ? "取消收藏" : "收藏优秀回答" }}
                    </el-button>
                  </div>
                </div>
              </div>

              <div v-if="personalNodeQuestions.length" class="question-list">
                <div v-for="item in personalNodeQuestions" :key="`mine-${item.id}`" class="question-card">
                  <div class="question-header">
                    <div>
                      <h3>{{ item.title }}</h3>
                      <p>我的提问 · {{ formatDate(item.create_time) }}</p>
                    </div>
                    <el-tag :type="item.status === 'answered' ? 'success' : 'warning'" effect="plain">
                      {{ item.status === "answered" ? "已回复" : "待回复" }}
                    </el-tag>
                  </div>
                  <p class="detail-text">{{ item.description }}</p>
                  <div v-if="item.teacher_reply" class="reply-card">
                    <span class="detail-label">教师回复</span>
                    <strong>{{ item.teacher_name || "任课教师" }}</strong>
                    <p>{{ item.teacher_reply }}</p>
                  </div>
                </div>
              </div>

              <el-empty
                v-if="!featuredNodeQuestions.length && !personalNodeQuestions.length"
                description="当前节点还没有问答记录，你可以先学习材料，再结合困惑向教师提问。"
              />
            </el-tab-pane>
          </el-tabs>
        </div>
        <el-empty v-else description="点击右侧图谱中的节点查看详情" />
      </el-card>

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
      </div>

      <div v-if="isStudent" class="page-grid graph-bottom-grid">
        <el-card class="graph-overview-card">
          <template #header>图谱导学总览</template>
          <div v-if="overview.default_target" class="graph-overview-grid">
            <div class="insight-list">
              <div class="insight-item">
                <span class="detail-label">当前推荐目标</span>
                <strong>{{ overview.default_target.name }}</strong>
                <p>{{ overview.default_target.description || "该目标知识点暂无说明。" }}</p>
                <div class="question-actions">
                  <el-button type="primary" plain @click="focusNode(overview.default_target.id)">在图谱中定位</el-button>
                  <el-button plain @click="detailTab = 'outline'">回到知识梳理</el-button>
                </div>
              </div>
              <div class="insight-item">
                <span class="detail-label">图谱阅读图例</span>
                <div class="tag-list">
                  <el-tag type="warning" effect="dark">金色菱形：当前目标</el-tag>
                  <el-tag type="warning" effect="plain">橙色描边：推荐路径</el-tag>
                  <el-tag type="success" effect="plain">绿色提示：优先学习</el-tag>
                  <el-tag type="danger" effect="plain">红色提示：薄弱点</el-tag>
                </div>
                <p>图中的箭头文字已经标出“前置依赖 / 相关知识”等关系，方便你直接顺着路径学习。</p>
              </div>
            </div>
            <div class="detail-section detail-stack">
              <span class="detail-label">图谱导学面板</span>
              <el-select
                :model-value="manualTargetId || overview.default_target?.id || ''"
                placeholder="切换推荐目标"
                filterable
                clearable
                @change="handleTargetSelect"
              >
                <el-option
                  v-for="node in targetOptions"
                  :key="node.id"
                  :label="node.name"
                  :value="node.id"
                />
              </el-select>
              <div class="compact-summary">
                <div class="summary-metric">
                  <span>进度</span>
                  <strong>{{ overview.progress_rate }}%</strong>
                </div>
                <div class="summary-metric">
                  <span>路径步数</span>
                  <strong>{{ overview.learning_path.length }}</strong>
                </div>
                <div class="summary-metric">
                  <span>薄弱点</span>
                  <strong>{{ overview.weak_points.length }}</strong>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="登录并标记学习状态后，这里会生成个性化图谱导航。" />
        </el-card>

        <el-card class="graph-path-card">
          <template #header>推荐学习路径</template>
          <el-empty v-if="!overview.learning_path.length" description="先去图谱中标记几个节点的掌握状态，这里会生成更合理的路径。" />
          <div v-else class="path-list">
            <div
              v-for="item in overview.learning_path"
              :key="item.step"
              class="path-card"
            >
              <div class="path-header">
                <div>
                  <span class="path-step">Step {{ item.step }}</span>
                  <h3>{{ item.concept.name }}</h3>
                </div>
                <el-tag effect="plain">{{ statusTextMap[item.concept.status] }}</el-tag>
              </div>
              <p>{{ item.reason }}</p>
              <div class="tag-list">
                <el-tag effect="plain">{{ item.concept.category || "未分类" }}</el-tag>
                <el-tag effect="plain">难度 {{ item.concept.difficulty || "-" }}</el-tag>
              </div>
              <div class="question-actions">
                <el-button type="primary" plain @click="focusNode(item.concept.id)">查看节点</el-button>
              </div>
            </div>
          </div>
          <div class="detail-section detail-stack path-note">
            <span class="detail-label">路径使用建议</span>
            <ul class="point-list">
              <li>优先完成当前目标前的未学节点，再进入后续知识点。</li>
              <li>每学完一个节点就更新掌握状态，推荐路径会自动刷新。</li>
              <li>先看知识梳理和材料，再做自测，80 分以上再继续下一步。</li>
            </ul>
          </div>
        </el-card>

        <el-card class="graph-focus-card">
          <template #header>优先学习节点</template>
          <div v-if="overview.recommended_concepts.length" class="detail-stack">
            <div class="recommend-grid">
              <div
                v-for="item in overview.recommended_concepts"
                :key="item.id"
                class="recommend-card"
              >
                <div class="path-header">
                  <div>
                    <span class="path-step">推荐节点</span>
                    <h3>{{ item.name }}</h3>
                  </div>
                  <el-tag type="success" effect="plain">准备度 {{ Math.round(item.readiness * 100) }}%</el-tag>
                </div>
                <p>{{ item.description || "该知识点暂无补充说明。" }}</p>
                <div class="tag-list">
                  <el-tag effect="plain">前置 {{ item.prerequisite_count }}</el-tag>
                  <el-tag effect="plain">影响 {{ item.blocked_count }}</el-tag>
                  <el-tag effect="plain">{{ statusTextMap[item.status] }}</el-tag>
                </div>
                <div class="question-actions">
                  <el-button type="primary" plain @click="focusNode(item.id)">定位节点</el-button>
                  <el-button plain @click="applyTargetSelection(item.id)">设为目标</el-button>
                </div>
              </div>
            </div>
            <div class="detail-section detail-stack">
              <span class="detail-label">薄弱点分析</span>
              <el-table :data="overview.weak_points" size="small" empty-text="暂无薄弱点数据">
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
          <el-empty v-else description="暂无个性化推荐，请先完成部分学习标记。" />
        </el-card>
      </div>

      <el-card v-else class="graph-hint-card">
        <template #header>图谱探索说明</template>
        <div class="insight-list">
          <div class="insight-item">
            <span class="detail-label">当前页面职责</span>
            <strong>围绕知识点结构、前置关系和学习材料展开探索</strong>
            <p>学生可以在这里看到个性化导学；教师和图谱运维官则更适合把这里作为知识结构浏览和课程内容核对页面。</p>
          </div>
        </div>
      </el-card>
    </div>

    <el-dialog v-model="questionDialogVisible" title="围绕当前节点提问" width="640px">
      <div v-if="selectedNode" class="reply-preview">
        <h3>{{ selectedNode.name }}</h3>
        <p class="detail-text">{{ selectedNode.description || "请结合当前知识点描述你的困惑。" }}</p>
      </div>
      <el-form label-width="88px">
        <el-form-item label="问题标题">
          <el-input v-model="questionForm.title" placeholder="例如：为什么这个知识点会影响后续路径推荐？" />
        </el-form-item>
        <el-form-item label="问题描述">
          <el-input
            v-model="questionForm.description"
            type="textarea"
            :rows="5"
            placeholder="说明你当前卡住的地方、已经尝试的方法，以及希望教师重点解答的部分"
          />
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
import { ElMessage } from "element-plus";
import { computed, onMounted, reactive, ref, watch } from "vue";

import { fetchGraphAll } from "../api/graph";
import { createQuestion, fetchLearningQuestions, fetchLearningStatuses, toggleQuestionFavorite, updateLearningStatus } from "../api/learning";
import { fetchRecommendOverview } from "../api/recommend";
import AppShell from "../components/AppShell.vue";
import GraphCanvasEcharts from "../components/GraphCanvasEcharts.vue";
import { getCurrentUser } from "../utils/session";

const keyword = ref("");
const errorMessage = ref("");
const currentUser = ref(getCurrentUser());
const selectedNodeId = ref("");
const manualTargetId = ref("");
const statusMap = ref({});
const savingStatus = ref(false);
const questionDialogVisible = ref(false);
const savingQuestion = ref(false);
const nodeQuestions = ref([]);
const detailTab = ref("outline");
const quizAnswers = ref({});
const quizResults = ref({});
const graph = reactive({
  nodes: [],
  links: [],
});

function createEmptyOverview() {
  return {
    progress_rate: 0,
    total_concepts: 0,
    mastered_count: 0,
    in_progress_count: 0,
    unlearned_count: 0,
    recommended_concepts: [],
    weak_points: [],
    default_target: null,
    learning_path: [],
  };
}

const overview = ref(createEmptyOverview());
const questionForm = reactive({
  title: "",
  description: "",
});

const statusTextMap = {
  0: "未学",
  1: "学习中",
  2: "已掌握",
};

const originTextMap = {
  neo4j: "图数据库",
  catalog: "课程目录补充",
};

const isStudent = computed(() => currentUser.value?.role === "student");
const nodeMap = computed(() => new Map(graph.nodes.map((node) => [node.id, node])));
const recommendedNodeIds = computed(() => overview.value.recommended_concepts.map((item) => item.id));
const learningPathNodeIds = computed(() => overview.value.learning_path.map((item) => item.concept.id));
const weakPointNodeIds = computed(() => overview.value.weak_points.map((item) => item.concept.id));
const targetOptions = computed(() =>
  graph.nodes
    .filter((node) => (statusMap.value[node.id] ?? 0) !== 2 || node.id === manualTargetId.value)
    .sort((left, right) => left.name.localeCompare(right.name, "zh-CN"))
);

const filteredNodes = computed(() => {
  if (!keyword.value) {
    return graph.nodes;
  }
  return graph.nodes.filter(
    (node) =>
      node.name.includes(keyword.value) ||
      (node.category && node.category.includes(keyword.value)) ||
      (node.description && node.description.includes(keyword.value)) ||
      (node.text_material && node.text_material.includes(keyword.value)) ||
      node.study_tips?.some((tip) => tip.includes(keyword.value)) ||
      node.common_mistakes?.some((mistake) => mistake.includes(keyword.value)) ||
      (node.practice_task && node.practice_task.includes(keyword.value)) ||
      node.key_points?.some((point) => point.includes(keyword.value))
  );
});

const filteredLinks = computed(() => {
  const visibleNodeIds = new Set(filteredNodes.value.map((node) => node.id));
  return graph.links.filter((link) => visibleNodeIds.has(link.source) && visibleNodeIds.has(link.target));
});

const selectedNode = computed(() => nodeMap.value.get(selectedNodeId.value) || null);

const currentStatus = computed(() => {
  if (!selectedNode.value) {
    return 0;
  }
  return statusMap.value[selectedNode.value.id] ?? 0;
});

const prerequisiteNodes = computed(() => {
  if (!selectedNode.value) {
    return [];
  }
  return graph.links
    .filter((link) => link.type === "PREREQUISITE_OF" && link.target === selectedNode.value.id)
    .map((link) => nodeMap.value.get(link.source))
    .filter(Boolean);
});

const unlockedNodes = computed(() => {
  if (!selectedNode.value) {
    return [];
  }
  return graph.links
    .filter((link) => link.type === "PREREQUISITE_OF" && link.source === selectedNode.value.id)
    .map((link) => nodeMap.value.get(link.target))
    .filter(Boolean);
});

const progressRate = computed(() => {
  if (!graph.nodes.length) {
    return 0;
  }
  const score = graph.nodes.reduce((total, node) => {
    const status = statusMap.value[node.id] ?? 0;
    if (status === 2) {
      return total + 1;
    }
    if (status === 1) {
      return total + 0.5;
    }
    return total;
  }, 0);
  return Math.round((score / graph.nodes.length) * 100);
});

const activeQuizAnswers = computed(() => {
  if (!selectedNode.value) {
    return [];
  }
  return quizAnswers.value[selectedNode.value.id] || [];
});

const activeQuizResult = computed(() => {
  if (!selectedNode.value) {
    return null;
  }
  return quizResults.value[selectedNode.value.id] || null;
});

const featuredNodeQuestions = computed(() => nodeQuestions.value.filter((item) => item.is_featured));
const personalNodeQuestions = computed(() => {
  if (!currentUser.value) {
    return [];
  }
  return nodeQuestions.value.filter((item) => item.student_id === currentUser.value.id && !item.is_featured);
});

function formatDate(value) {
  if (!value) {
    return "";
  }
  return new Date(value).toLocaleString("zh-CN", { hour12: false });
}

watch(
  filteredNodes,
  (nodes) => {
    if (!nodes.length) {
      selectedNodeId.value = "";
      return;
    }
    if (!selectedNodeId.value || !nodes.some((node) => node.id === selectedNodeId.value)) {
      selectedNodeId.value = nodes[0].id;
    }
  },
  { immediate: true }
);

watch(
  selectedNode,
  async (node) => {
    detailTab.value = "outline";
    if (!node) {
      nodeQuestions.value = [];
      return;
    }

    const quizLength = node.quiz?.length || 0;
    const existingAnswers = quizAnswers.value[node.id];
    if (!existingAnswers || existingAnswers.length !== quizLength) {
      quizAnswers.value = {
        ...quizAnswers.value,
        [node.id]: Array(quizLength).fill(null),
      };
    }

    await loadNodeQuestions(node.id);
  },
  { immediate: true }
);

function isRecommendedNode(nodeId) {
  return recommendedNodeIds.value.includes(nodeId);
}

function isPathNode(nodeId) {
  return learningPathNodeIds.value.includes(nodeId);
}

function isWeakPointNode(nodeId) {
  return weakPointNodeIds.value.includes(nodeId);
}

function isTargetNode(nodeId) {
  return overview.value.default_target?.id === nodeId;
}

function focusNode(nodeId) {
  selectedNodeId.value = nodeId;
}

function openQuestionDialog() {
  if (!selectedNode.value) {
    return;
  }
  questionForm.title = "";
  questionForm.description = "";
  questionDialogVisible.value = true;
}

async function loadGraph() {
  try {
    const { data } = await fetchGraphAll();
    graph.nodes = data.nodes;
    graph.links = data.links;
    if (graph.nodes.length && !selectedNodeId.value) {
      selectedNodeId.value = graph.nodes[0].id;
    }
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
    const { data } = await fetchLearningQuestions({ concept_id: conceptId });
    nodeQuestions.value = data.items || [];
  } catch (error) {
    console.error(error);
    nodeQuestions.value = [];
  }
}

async function applyTargetSelection(nodeId) {
  if (!isStudent.value || !nodeId) {
    return;
  }

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
    ElMessage.warning("只有学生可以围绕当前节点提问。");
    return;
  }
  if (title.length < 2 || description.length < 5) {
    ElMessage.warning("请完整填写问题标题和描述。");
    return;
  }

  try {
    savingQuestion.value = true;
    await createQuestion({
      concept_id: selectedNode.value.id,
      concept_name: selectedNode.value.name,
      title,
      description,
    });
    questionDialogVisible.value = false;
    ElMessage.success("问题已提交，教师会在对应知识点下看到你的提问。");
    await loadNodeQuestions(selectedNode.value.id);
  } catch (error) {
    console.error(error);
    ElMessage.error("提交问题失败，请稍后重试。");
  } finally {
    savingQuestion.value = false;
  }
}

async function handleFavoriteQuestion(question) {
  try {
    const { data } = await toggleQuestionFavorite(question.id);
    nodeQuestions.value = nodeQuestions.value.map((item) =>
      item.id === question.id
        ? {
            ...item,
            is_favorited: data.is_favorited,
            favorite_count: data.favorite_count,
          }
        : item
    );
    ElMessage.success(data.is_favorited ? "已收藏优秀回答。" : "已取消收藏。");
  } catch (error) {
    console.error(error);
    ElMessage.error("收藏操作失败，请稍后重试。");
  }
}

function handleNodeSelect(nodeId) {
  selectedNodeId.value = nodeId;
}

async function handleStatusChange(nextStatus) {
  if (!selectedNode.value || !currentUser.value) {
    ElMessage.info("请先登录后再记录掌握情况。");
    return;
  }

  try {
    savingStatus.value = true;
    await updateLearningStatus(selectedNode.value.id, Number(nextStatus));
    statusMap.value = {
      ...statusMap.value,
      [selectedNode.value.id]: Number(nextStatus),
    };
    if (isStudent.value) {
      await loadRecommendGuidance();
    }
    ElMessage.success(`已更新为“${statusTextMap[nextStatus]}”`);
  } catch (error) {
    console.error(error);
    ElMessage.error("保存学习状态失败，请检查登录状态或稍后重试。");
  } finally {
    savingStatus.value = false;
  }
}

function updateQuizAnswer(questionIndex, optionIndex) {
  if (!selectedNode.value) {
    return;
  }

  const nodeId = selectedNode.value.id;
  const nextAnswers = [...(quizAnswers.value[nodeId] || [])];
  nextAnswers[questionIndex] = optionIndex;
  quizAnswers.value = {
    ...quizAnswers.value,
    [nodeId]: nextAnswers,
  };
}

function resetQuiz() {
  if (!selectedNode.value) {
    return;
  }

  const nodeId = selectedNode.value.id;
  quizAnswers.value = {
    ...quizAnswers.value,
    [nodeId]: Array(selectedNode.value.quiz?.length || 0).fill(null),
  };
  quizResults.value = {
    ...quizResults.value,
    [nodeId]: null,
  };
}

function submitQuiz() {
  if (!selectedNode.value?.quiz?.length) {
    return;
  }

  const nodeId = selectedNode.value.id;
  const answers = quizAnswers.value[nodeId] || [];
  if (answers.some((value) => value === null || value === undefined)) {
    ElMessage.warning("请先完成全部题目后再提交。");
    return;
  }

  let correct = 0;
  const details = selectedNode.value.quiz.map((question, index) => {
    const isCorrect = answers[index] === question.answer_index;
    if (isCorrect) {
      correct += 1;
    }
    return {
      selected_index: answers[index],
      is_correct: isCorrect,
    };
  });

  const total = selectedNode.value.quiz.length;
  const score = Math.round((correct / total) * 100);
  quizResults.value = {
    ...quizResults.value,
    [nodeId]: {
      total,
      correct,
      score,
      details,
    },
  };
  ElMessage.success(`自测完成，当前得分 ${score} 分。`);
}

async function markCurrentNodeMastered() {
  await handleStatusChange(2);
}

onMounted(async () => {
  await loadGraph();
  await loadLearningStatuses();
  await loadRecommendGuidance();
});
</script>
