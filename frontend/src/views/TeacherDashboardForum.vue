<template>
  <AppShell>
    <div class="workspace-page teacher-dashboard-v2">
      <el-tabs v-model="activeTeacherTab" class="workspace-tabs">
        <el-tab-pane label="教师工作台" name="overview">
          <el-card class="workspace-panel">
            <template #header>
              <div class="card-header-inline">
                <span>教师工作台</span>
                <el-button type="primary" plain @click="handleExport">导出班级问答统计 CSV</el-button>
              </div>
            </template>

            <div class="summary-row teacher-summary-row">
              <div class="summary-metric clickable-metric" @click="openTeacherDetail('全部学生名单', overview.student_progress, 'students')"><span>学生人数</span><strong>{{ overview.total_students }}</strong></div>
              <div class="summary-metric"><span>平均进度</span><strong>{{ overview.average_progress_rate }}%</strong></div>
              <div class="summary-metric"><span>平均每人掌握节点数</span><strong>{{ overview.class_overview.average_mastered_count }}</strong></div>
              <div class="summary-metric clickable-metric" @click="jumpToQuestionList('pending')"><span>待跟进问题</span><strong>{{ overview.pending_question_count }}</strong></div>
            </div>
            <div class="summary-row teacher-summary-row">
              <div class="summary-metric clickable-metric" @click="openAllMasteredConcepts"><span>全班已掌握节点次</span><strong>{{ overview.mastered_concepts_total }}</strong></div>
              <div class="summary-metric"><span>已回复问题</span><strong>{{ overview.answered_question_count }}</strong></div>
              <div class="summary-metric clickable-metric" @click="jumpToQuestionList('featured')"><span>置顶讨论</span><strong>{{ overview.featured_question_count }}</strong></div>
              <div class="summary-metric"><span>图谱待审</span><strong>{{ pendingGraphChangeCount }}</strong></div>
            </div>

            <div class="analytics-list top-gap">
              <div v-for="classItem in overview.class_overviews" :key="classItem.class_name" class="analytics-card teacher-class-card">
                <div class="card-header-inline">
                  <strong>{{ classItem.class_name }}</strong>
                  <div class="tag-list">
                    <el-tag effect="plain">{{ classItem.student_count }} 人</el-tag>
                    <el-tag type="primary" effect="plain">平均进度 {{ classItem.average_progress_rate }}%</el-tag>
                  </div>
                </div>
                <div class="summary-row compact-summary">
                  <div class="summary-metric clickable-metric" @click="openTeacherDetail(`${classItem.class_name}学生名单`, classItem.students, 'students')">
                    <span>学生</span><strong>{{ classItem.student_count }}</strong>
                  </div>
                  <div class="summary-metric clickable-metric" @click="openClassConcepts(classItem, 'mastered')">
                    <span>已掌握节点次</span><strong>{{ classItem.mastered_concepts_total }}</strong>
                  </div>
                  <div class="summary-metric clickable-metric" @click="jumpToQuestionList('pending', classItem)">
                    <span>待跟进</span><strong>{{ classItem.pending_question_count }}</strong>
                  </div>
                </div>
                <div class="question-actions">
                  <el-button text type="primary" @click="openTeacherDetail(`${classItem.class_name}学生名单`, classItem.students, 'students')">查看学生</el-button>
                  <el-button text type="primary" @click="openClassConcepts(classItem, 'unlearned')">未学较多节点</el-button>
                  <el-button text type="primary" @click="openClassConcepts(classItem, 'inProgress')">学习中较多节点</el-button>
                  <el-button text type="primary" @click="openClassConcepts(classItem, 'mastered')">已掌握较多节点</el-button>
                </div>
                <div class="status-progress-stack">
                  <div v-for="statusItem in classItem.status_distribution" :key="`${classItem.class_name}-${statusItem.status}`">
                    <span>{{ statusItem.label }} {{ statusItem.count }} 次 · {{ statusItem.percentage }}%</span>
                    <el-progress :percentage="statusItem.percentage" :stroke-width="8" :color="statusColorMap[statusItem.status]" />
                  </div>
                </div>
                <div class="three-status-columns top-gap">
                  <div>
                    <span class="detail-label">未学较多</span>
                    <el-tag v-for="node in classItem.top_unlearned_concepts.slice(0, 4)" :key="`u-${classItem.class_name}-${node.concept_id}`" effect="plain">
                      {{ node.concept_name }} {{ node.unlearned_count }}
                    </el-tag>
                  </div>
                  <div>
                    <span class="detail-label">学习中较多</span>
                    <el-tag v-for="node in classItem.top_in_progress_concepts.slice(0, 4)" :key="`p-${classItem.class_name}-${node.concept_id}`" type="warning" effect="plain">
                      {{ node.concept_name }} {{ node.in_progress_count }}
                    </el-tag>
                  </div>
                  <div>
                    <span class="detail-label">已掌握较多</span>
                    <el-tag v-for="node in classItem.top_mastered_concepts.slice(0, 4)" :key="`m-${classItem.class_name}-${node.concept_id}`" type="success" effect="plain">
                      {{ node.concept_name }} {{ node.mastered_count }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>

            <div class="workflow-strip top-gap">
              <div class="workflow-step is-done">
                <span>1</span>
                <strong>观察班级</strong>
                <p>查看平均进度和高频提问节点。</p>
              </div>
              <div class="workflow-step" :class="{ 'is-done': overview.pending_question_count > 0 || overview.answered_question_count > 0 }">
                <span>2</span>
                <strong>跟进学生</strong>
                <p>从学生快照定位个人薄弱环节。</p>
              </div>
              <div class="workflow-step" :class="{ 'is-done': overview.featured_question_count > 0 }">
                <span>3</span>
                <strong>沉淀讨论</strong>
                <p>置顶问题并设置优秀评论。</p>
              </div>
              <div class="workflow-step" :class="{ 'is-done': overview.coordination_requests.length > 0 }">
                <span>4</span>
                <strong>协同运维</strong>
                <p>向图谱运维官提交资源和系统事项。</p>
              </div>
            </div>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="图谱节点分析" name="node-analysis">
          <el-card class="workspace-panel">
            <template #header>
              <div class="card-header-inline">
                <span>图谱节点分析</span>
                <div class="teacher-thread-filters">
                  <el-select v-model="activeFactorKey" class="teacher-filter-select" placeholder="选择分析维度">
                    <el-option
                      v-for="item in overview.learning_factor_analysis"
                      :key="item.factor_key"
                      :label="item.factor_label"
                      :value="item.factor_key"
                    />
                  </el-select>
                  <el-select v-model="activeVennStatus" class="teacher-filter-select" placeholder="选择学习程度">
                    <el-option label="已掌握节点" :value="2" />
                    <el-option label="学习中节点" :value="1" />
                    <el-option label="未学节点" :value="0" />
                  </el-select>
                </div>
              </div>
            </template>

            <section v-if="activeFactorAnalysis" class="node-analysis-brief">
              <div>
                <span class="detail-label">当前分析口径</span>
                <h3>{{ activeFactorAnalysis.factor_label }} · {{ statusTextMap[activeVennStatus] }}节点</h3>
                <p class="detail-text">{{ activeFactorAnalysis.description }}</p>
              </div>
              <button type="button" class="node-brief-metric" @click="openTeacherDetail(`共同${statusTextMap[activeVennStatus]}节点`, factorVennSets.common, 'concepts')">
                <span>共同节点</span>
                <strong>{{ factorVennSets.common.length }}</strong>
              </button>
              <button type="button" class="node-brief-metric" @click="openNodeAnalysisDetail(`${statusTextMap[activeVennStatus]}节点明细`, activeStatusAnalysisNodes)">
                <span>相关节点</span>
                <strong>{{ activeStatusAnalysisNodes.length }}</strong>
              </button>
              <button type="button" class="node-brief-metric" @click="openNodeAnalysisDetail('需要重点关注的节点', focusAnalysisNodes)">
                <span>重点关注</span>
                <strong>{{ focusAnalysisNodes.length }}</strong>
              </button>
            </section>

            <section v-if="activeFactorAnalysis" class="detail-section detail-stack">
              <div class="card-header-inline">
                <div>
                  <span class="detail-label">分组掌握结构</span>
                  <p class="detail-text">比较不同分组在当前学习程度下涉及哪些节点，点击分组卡片可查看该组薄弱节点明细。</p>
                </div>
              </div>
              <div class="node-group-board">
                <button
                  v-for="group in activeFactorAnalysis.groups"
                  :key="group.group_key"
                  type="button"
                  class="node-group-card"
                  @click="openFactorGroupDetail(group)"
                >
                  <div class="card-header-inline">
                    <strong>{{ group.group_label }}</strong>
                    <el-tag effect="plain">{{ group.student_count }} 人</el-tag>
                  </div>
                  <div class="node-group-main">
                    <strong>{{ getGroupConceptsByStatus(group, activeVennStatus).length }}</strong>
                    <span>{{ statusTextMap[activeVennStatus] }}节点</span>
                  </div>
                  <el-progress :percentage="getGroupStatusPercentage(group, activeVennStatus)" :stroke-width="10" :color="statusColorMap[activeVennStatus]" />
                  <p class="detail-text">人均节点学习时间 {{ group.average_learning_minutes }} 分钟</p>
                  <div class="tag-list top-gap">
                    <el-tag
                      v-for="node in getGroupConceptsByStatus(group, activeVennStatus).slice(0, 4)"
                      :key="`${group.group_key}-${activeVennStatus}-${node.concept_id}`"
                      effect="plain"
                      @click.stop="openTeacherDetail(`${group.group_label}${statusTextMap[activeVennStatus]}节点`, [node], 'concepts')"
                    >
                      {{ node.concept_name }}
                    </el-tag>
                  </div>
                </button>
              </div>
            </section>

            <section v-if="activeFactorAnalysis" class="node-difference-grid">
              <div class="detail-section detail-stack">
                <div class="card-header-inline">
                  <div>
                    <span class="detail-label">共同节点</span>
                    <p class="detail-text">所有分组都处于“{{ statusTextMap[activeVennStatus] }}”的节点，适合统一安排课堂活动。</p>
                  </div>
                  <el-tag effect="plain">{{ factorVennSets.common.length }} 个</el-tag>
                </div>
                <div class="node-chip-list">
                  <el-tag
                    v-for="node in factorVennSets.common"
                    :key="node.concept_id"
                    class="clickable-tag"
                    effect="plain"
                    @click="openTeacherDetail(`共同${statusTextMap[activeVennStatus]}节点`, [node], 'concepts')"
                  >
                    {{ node.concept_name }}
                  </el-tag>
                  <el-empty v-if="!factorVennSets.common.length" description="当前筛选下暂无共同节点。" />
                </div>
              </div>
              <div class="detail-section detail-stack">
                <span class="detail-label">差异节点</span>
                <div class="node-diff-list">
                  <button
                  v-for="group in activeFactorAnalysis.groups"
                  :key="group.group_key"
                  type="button"
                    class="node-diff-card"
                    @click="openTeacherDetail(`${group.group_label}${statusTextMap[activeVennStatus]}差异节点`, getGroupUniqueConcepts(group), 'concepts')"
                >
                  <div class="card-header-inline">
                    <strong>{{ group.group_label }}</strong>
                      <el-tag effect="plain">{{ getGroupUniqueConcepts(group).length }} 个</el-tag>
                  </div>
                    <p class="detail-text">{{ previewConceptNames(getGroupUniqueConcepts(group)) }}</p>
                  </button>
                </div>
              </div>
            </section>

            <section class="detail-section detail-stack">
              <div class="card-header-inline">
                <div>
                  <span class="detail-label">节点诊断列表</span>
                  <p class="detail-text">按当前学习程度筛选节点，综合查看掌握结构、问题热度、点击次数和平均学习时长。</p>
                </div>
                <el-tag type="primary" effect="plain">{{ activeStatusAnalysisNodes.length }} 个节点</el-tag>
              </div>
              <div class="node-diagnosis-grid">
                <button
                  v-for="node in activeStatusAnalysisNodes.slice(0, 12)"
                  :key="node.concept_id"
                  type="button"
                  class="node-diagnosis-card"
                  @click="openNodeAnalysisDetail(`${node.concept_name} 节点明细`, [node])"
                >
                  <div class="card-header-inline">
                    <strong>{{ node.concept_name }}</strong>
                    <el-tag :type="node.pending_count > 0 ? 'warning' : node.risk_score >= 60 ? 'danger' : 'success'" effect="plain">
                      风险 {{ node.risk_score }}
                    </el-tag>
                  </div>
                  <div class="node-diagnosis-meta">
                    <span>{{ statusTextMap[activeVennStatus] }} {{ getNodeStatusCount(node, activeVennStatus) }} 人</span>
                    <span>提问 {{ node.question_count }}</span>
                    <span>平均 {{ node.average_learning_minutes }} 分</span>
                  </div>
                  <el-progress :percentage="getNodeStatusPercentage(node, activeVennStatus)" :stroke-width="9" :color="statusColorMap[activeVennStatus]" />
                  <p class="detail-text">{{ node.risk_reason }}</p>
                </button>
              </div>
            </section>

            <section class="node-analysis-two-column">
              <div class="detail-section detail-stack">
                <span class="detail-label">节点难度判断</span>
                <p class="detail-text">以平均学习时长和未学比例判断节点是否需要拆分材料、增加案例或调整前置依赖。</p>
                <div class="node-chip-list">
                  <el-tag
                    v-for="node in slowLearningNodes.slice(0, 8)"
                    :key="`slow-${node.concept_id}`"
                    effect="plain"
                    class="clickable-tag"
                    @click="openNodeAnalysisDetail('高耗时节点', [node])"
                  >
                    {{ node.concept_name }} · {{ node.average_learning_minutes }} 分
                  </el-tag>
                </div>
              </div>
              <div class="detail-section detail-stack">
                <span class="detail-label">讨论跟进入口</span>
                <p class="detail-text">待跟进节点应优先进入“节点讨论管理”，通过回复、置顶和优秀评论沉淀公共答案。</p>
                  <div class="tag-list top-gap">
                    <el-tag
                    v-for="node in pendingQuestionNodes.slice(0, 8)"
                    :key="`pending-${node.concept_id}`"
                      effect="plain"
                    class="clickable-tag"
                    @click="jumpToQuestionList('pending')"
                    >
                    {{ node.concept_name }} · 待跟进{{ node.pending_count }}
                    </el-tag>
                  </div>
              </div>
            </section>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="学生学习情况" name="students">
          <el-card class="workspace-panel">
            <template #header>学生学习情况</template>
            <el-table :data="overview.student_progress" size="small" empty-text="当前暂无学生学习数据">
              <el-table-column label="学生" min-width="140">
                <template #default="{ row }">
                  <el-button text type="primary" @click="openStudentSnapshot(row)">{{ row.display_name }}</el-button>
                  <p class="table-meta">{{ row.username }}</p>
                </template>
              </el-table-column>
              <el-table-column label="进度" min-width="180">
                <template #default="{ row }">
                  <el-progress :percentage="row.progress_rate" :stroke-width="8" color="#bc6c25" />
                </template>
              </el-table-column>
              <el-table-column label="当前目标" min-width="150">
                <template #default="{ row }">{{ row.current_target || "等待推荐" }}</template>
              </el-table-column>
              <el-table-column label="薄弱点" min-width="150">
                <template #default="{ row }">{{ row.weak_point || "暂无明显薄弱点" }}</template>
              </el-table-column>
              <el-table-column label="提问 / 待跟进" min-width="130">
                <template #default="{ row }">{{ row.question_count }} / {{ row.pending_question_count }}</template>
              </el-table-column>
              <el-table-column label="操作" width="140">
                <template #default="{ row }">
                  <el-button type="primary" plain @click="openStudentSnapshot(row)">查看快照</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="节点讨论管理" name="threads">
          <el-card class="workspace-panel teacher-thread-card">
            <template #header>
              <div class="card-header-inline">
                <span>节点讨论管理</span>
                <div class="teacher-thread-filters">
                  <el-segmented v-model="questionFilterMode" :options="questionFilterOptions" />
                  <el-select v-model="activeConceptFilter" clearable placeholder="全部知识点" class="teacher-filter-select">
                    <el-option
                      v-for="item in overview.concept_question_stats"
                      :key="item.concept_name"
                      :label="`${item.concept_name}（${item.question_count}）`"
                      :value="item.concept_name"
                    />
                  </el-select>
                </div>
              </div>
            </template>

            <div v-if="filteredQuestions.length" class="thread-list">
              <div v-for="item in filteredQuestions" :key="item.id" class="thread-card">
                <div class="question-header">
                  <div>
                    <h3>{{ item.title }}</h3>
                    <p>
                      <el-button text type="primary" @click="openStudentSnapshot(item)">{{ item.student_name }}</el-button>
                      · {{ item.concept_name || "综合问题" }} · {{ formatDate(item.create_time) }}
                    </p>
                  </div>
                  <div class="tag-list">
                    <el-tag :type="item.status === 'answered' ? 'success' : 'warning'" effect="plain">{{ item.status === "answered" ? "已有回复" : "待讨论" }}</el-tag>
                    <el-tag v-if="item.is_featured" type="warning" effect="dark">教师置顶</el-tag>
                    <el-tag effect="plain">{{ item.comment_count }} 条评论</el-tag>
                  </div>
                </div>

                <p class="detail-text">{{ item.description }}</p>

                <div class="question-actions">
                  <el-button text type="primary" @click="openStudentSnapshot(item)">查看提问者学习情况</el-button>
                  <el-button type="primary" plain @click="openReplyComposer(item)">{{ activeReplyQuestionId === item.id ? "收起回复框" : "参与回复" }}</el-button>
                  <el-button plain type="warning" @click="handleFeatureToggle(item)">{{ item.is_featured ? "取消置顶" : "置顶讨论" }}</el-button>
                </div>

                <div v-if="activeReplyQuestionId === item.id" class="reply-composer">
                  <div v-if="replyContext.parentCommentId" class="detail-text reply-context-line">正在回复：{{ replyContext.targetName }}</div>
                  <div class="tag-list top-gap">
                    <el-tag
                      v-for="template in overview.quick_reply_templates"
                      :key="template.id"
                      effect="plain"
                      class="clickable-tag"
                      @click="applyTemplate(item.id, template)"
                    >
                      {{ template.title }}
                    </el-tag>
                  </div>
                  <el-input v-model="replyDrafts[item.id]" type="textarea" :rows="3" placeholder="围绕当前节点补充解释、学习建议或进一步追问" class="top-gap" />
                  <div class="dialog-footer">
                    <el-button @click="closeReplyComposer">取消</el-button>
                    <el-button type="primary" :loading="replyingQuestionId === item.id" @click="handleReplySubmit(item)">发布回复</el-button>
                  </div>
                </div>

                <div v-if="item.comments.length" class="thread-comment-list">
                  <ThreadCommentTree
                    :comments="item.comments"
                    :current-user-id="currentUser?.id || null"
                    :can-reply="true"
                    :can-like="false"
                    :is-teacher="true"
                    @reply="(comment) => openReplyComposer(item, comment)"
                    @delete="handleCommentDelete"
                    @feature="handleCommentFeature"
                  />
                </div>
                <el-empty v-else description="当前讨论还没有评论，教师可以先补充第一条引导回复。" />
              </div>
            </div>
            <el-empty v-else :description="overview.recent_questions.length ? '当前筛选条件下没有问题。' : '当前还没有学生提问。'" />
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="图谱节点编辑" name="graph-editor">
          <el-card class="workspace-panel">
            <template #header>
              <div class="card-header-inline">
                <span>图谱节点编辑申请</span>
                <el-tag type="warning" effect="plain">提交后需图谱运维官审核发布</el-tag>
              </div>
            </template>

            <div class="workflow-strip top-gap">
              <div class="workflow-step is-done">
                <span>1</span>
                <strong>选择节点</strong>
                <p>新增或选择已有知识点，明确本次修改范围。</p>
              </div>
              <div class="workflow-step is-done">
                <span>2</span>
                <strong>补充内容</strong>
                <p>完善知识梳理、学习材料、资源链接和自测题。</p>
              </div>
              <div class="workflow-step">
                <span>3</span>
                <strong>设置关系</strong>
                <p>标注前置依赖、后续学习和相关知识点。</p>
              </div>
              <div class="workflow-step" :class="{ 'is-done': overview.graph_change_requests.length > 0 }">
                <span>4</span>
                <strong>等待发布</strong>
                <p>运维官审核通过后，学生端图谱立即读取新内容。</p>
              </div>
            </div>

            <div class="two-column workspace-two-column top-gap">
              <div class="detail-section detail-stack">
                <span class="detail-label">节点内容草稿</span>
                <el-form label-width="104px">
                  <el-form-item label="操作类型">
                    <el-radio-group v-model="graphChangeForm.action" @change="handleGraphActionChange">
                      <el-radio-button label="update_node">修改已有节点</el-radio-button>
                      <el-radio-button label="create_node">新增知识点</el-radio-button>
                    </el-radio-group>
                  </el-form-item>
                  <el-form-item v-if="graphChangeForm.action === 'update_node'" label="选择节点">
                    <el-select v-model="selectedGraphNodeName" filterable class="full-width" placeholder="选择要修改的知识点" @change="fillGraphFormFromNode">
                      <el-option v-for="node in graphNodes" :key="node.name" :label="node.name" :value="node.name" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="申请说明">
                    <el-input v-model="graphChangeForm.summary" placeholder="例如：补充机器学习节点的材料和自测题" />
                  </el-form-item>
                  <el-form-item label="节点名称">
                    <el-input v-model="graphChangeForm.node.name" :disabled="graphChangeForm.action === 'update_node'" />
                  </el-form-item>
                  <el-form-item label="所属模块">
                    <el-input v-model="graphChangeForm.node.category" placeholder="如：算法模型 / 数字素养 / 伦理素养" />
                  </el-form-item>
                  <el-form-item label="难度/时长">
                    <div class="inline-field-row">
                      <el-input-number v-model="graphChangeForm.node.difficulty" :min="1" :max="5" />
                      <el-input-number v-model="graphChangeForm.node.estimated_minutes" :min="5" :max="240" />
                    </div>
                  </el-form-item>
                  <el-form-item label="节点简介">
                    <el-input v-model="graphChangeForm.node.description" type="textarea" :rows="3" />
                  </el-form-item>
                  <el-form-item label="知识梳理">
                    <el-input v-model="graphDraftTexts.keyPoints" type="textarea" :rows="4" placeholder="每行一个核心要点，会显示在节点弹窗的知识梳理中" />
                  </el-form-item>
                  <el-form-item label="学习材料">
                    <el-input v-model="graphChangeForm.node.text_material" type="textarea" :rows="5" placeholder="面向学生的学习说明、案例、学习步骤或注意事项" />
                  </el-form-item>
                  <el-form-item label="视频材料">
                    <div class="stacked-fields">
                      <el-input v-model="graphChangeForm.node.video_title" placeholder="视频标题" />
                      <el-input v-model="graphChangeForm.node.video_url" placeholder="视频链接或检索链接" />
                    </div>
                  </el-form-item>
                  <el-form-item label="资源链接">
                    <el-input v-model="graphDraftTexts.resourceLinks" type="textarea" :rows="3" placeholder="每行：资源名称|https://example.com" />
                  </el-form-item>
                </el-form>
              </div>

              <div class="detail-section detail-stack">
                <span class="detail-label">关系与自测题</span>
                <el-form label-width="104px">
                  <el-form-item label="前置依赖">
                    <el-select v-model="graphChangeForm.prerequisite_names" multiple filterable class="full-width" placeholder="学习当前节点前建议掌握">
                      <el-option v-for="node in relationCandidateNodes" :key="`pre-${node.name}`" :label="node.name" :value="node.name" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="后续节点">
                    <el-select v-model="graphChangeForm.next_names" multiple filterable class="full-width" placeholder="掌握当前节点后推荐学习">
                      <el-option v-for="node in relationCandidateNodes" :key="`next-${node.name}`" :label="node.name" :value="node.name" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="相关节点">
                    <el-select v-model="graphChangeForm.related_names" multiple filterable class="full-width" placeholder="概念相近或可横向拓展的节点">
                      <el-option v-for="node in relationCandidateNodes" :key="`rel-${node.name}`" :label="node.name" :value="node.name" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="学习建议">
                    <el-input v-model="graphDraftTexts.studyTips" type="textarea" :rows="3" placeholder="每行一条学习建议" />
                  </el-form-item>
                  <el-form-item label="常见误区">
                    <el-input v-model="graphDraftTexts.commonMistakes" type="textarea" :rows="3" placeholder="每行一条常见误区" />
                  </el-form-item>
                  <el-form-item label="实践任务">
                    <el-input v-model="graphChangeForm.node.practice_task" type="textarea" :rows="3" />
                  </el-form-item>
                  <el-form-item label="自测题">
                    <el-input
                      v-model="graphDraftTexts.quiz"
                      type="textarea"
                      :rows="8"
                      placeholder="每行一题：题目|选项A|选项B|选项C|选项D|正确序号0-3|解析。判断题可写：题目|正确|错误|0|解析"
                    />
                  </el-form-item>
                </el-form>
                <div class="question-actions">
                  <el-button @click="resetGraphChangeForm">重置草稿</el-button>
                  <el-button type="primary" :loading="submittingGraphChange" @click="handleGraphChangeSubmit">提交审核</el-button>
                </div>
              </div>
            </div>
          </el-card>

          <el-card class="workspace-panel top-gap">
            <template #header>我的图谱变更申请</template>
            <div v-if="overview.graph_change_requests.length" class="insight-list">
              <div v-for="item in overview.graph_change_requests" :key="item.id" class="insight-item">
                <div class="card-header-inline">
                  <div>
                    <strong>{{ item.summary }}</strong>
                    <p class="table-meta">{{ item.node.name }} · {{ graphActionTextMap[item.action] || item.action }} · {{ formatDate(item.create_time) }}</p>
                  </div>
                  <el-tag :type="graphChangeStatusTypeMap[item.status] || 'info'" effect="plain">{{ graphChangeStatusTextMap[item.status] || item.status }}</el-tag>
                </div>
                <p>{{ item.node.description || "暂无节点简介" }}</p>
                <div class="tag-list">
                  <el-tag v-for="name in item.prerequisite_names" :key="`p-${item.id}-${name}`" effect="plain">前置：{{ name }}</el-tag>
                  <el-tag v-for="name in item.next_names" :key="`n-${item.id}-${name}`" effect="plain">后续：{{ name }}</el-tag>
                  <el-tag v-for="name in item.related_names" :key="`r-${item.id}-${name}`" effect="plain">相关：{{ name }}</el-tag>
                </div>
                <p v-if="item.review_note" class="detail-text">审核意见：{{ item.review_note }}</p>
              </div>
            </div>
            <el-empty v-else description="还没有提交图谱节点变更申请。" />
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="快速回复模板" name="templates">
          <el-card class="workspace-panel">
            <template #header>快速回复模板</template>
            <div class="two-column workspace-two-column">
              <div class="detail-section">
                <span class="detail-label">新增模板</span>
                <el-form label-width="72px">
                  <el-form-item label="模板名">
                    <el-input v-model="templateForm.title" placeholder="如：先看学习材料" />
                  </el-form-item>
                  <el-form-item label="内容">
                    <el-input v-model="templateForm.content" type="textarea" :rows="5" placeholder="如：请先查看当前节点学习材料中的第2节，再继续提问。" />
                  </el-form-item>
                </el-form>
                <div class="question-actions">
                  <el-button type="primary" :loading="creatingTemplate" @click="handleTemplateCreate">保存模板</el-button>
                </div>
              </div>

              <div class="detail-section">
                <span class="detail-label">我的模板</span>
                <div v-if="overview.quick_reply_templates.length" class="insight-list">
                  <div v-for="item in overview.quick_reply_templates" :key="item.id" class="insight-item">
                    <div class="card-header-inline">
                      <strong>{{ item.title }}</strong>
                      <el-button text type="danger" @click="handleTemplateDelete(item)">删除</el-button>
                    </div>
                    <p>{{ item.content }}</p>
                  </div>
                </div>
                <el-empty v-else description="还没有模板，可先新增几条常用回复。" />
              </div>
            </div>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="教师协同事项" name="coordination">
          <el-card class="workspace-panel">
            <template #header>教师与图谱运维官协同</template>
            <div class="two-column workspace-two-column">
              <div class="detail-section detail-stack">
                <span class="detail-label">发起协同事项</span>
                <el-form label-width="88px">
                  <el-form-item label="事项类型">
                    <el-select v-model="coordinationForm.type" class="full-width">
                      <el-option v-for="item in coordinationTypes" :key="item.value" :label="item.label" :value="item.value" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="事项标题"><el-input v-model="coordinationForm.title" placeholder="例如：申请扩充某个知识点材料或调整班级权限" /></el-form-item>
                  <el-form-item label="具体说明">
                    <el-input v-model="coordinationForm.description" type="textarea" :rows="5" placeholder="说明你的教学诉求、涉及对象和希望图谱运维官配合的处理方式" />
                  </el-form-item>
                </el-form>
                <div class="question-actions">
                  <el-button type="primary" :loading="submittingCoordination" @click="handleCoordinationSubmit">提交协同事项</el-button>
                </div>
              </div>

              <div class="detail-section detail-stack">
                <span class="detail-label">当前协同进度</span>
                <div v-if="overview.coordination_requests.length" class="insight-list">
                  <div v-for="item in overview.coordination_requests" :key="item.id" class="insight-item">
                    <div class="card-header-inline">
                      <strong>{{ item.title }}</strong>
                      <el-tag :type="coordinationStatusTypeMap[item.status] || 'info'" effect="plain">{{ coordinationStatusTextMap[item.status] || item.status }}</el-tag>
                    </div>
                    <p>{{ item.description }}</p>
                    <div class="tag-list">
                      <el-tag effect="plain">{{ item.type }}</el-tag>
                      <el-tag effect="plain">{{ formatDate(item.create_time) }}</el-tag>
                    </div>
                    <p v-if="item.admin_reply" class="detail-text">图谱运维官回复：{{ item.admin_reply }}</p>
                  </div>
                </div>
                <el-empty v-else description="当前还没有协同事项，可在左侧提交图谱维护、账号权限或系统支持需求。" />
              </div>
            </div>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="数据导出" name="export">
          <el-card class="workspace-panel">
            <template #header>教学数据导出</template>
            <div class="detail-section">
              <span class="detail-label">导出内容</span>
              <p class="detail-text">导出文件包含学生姓名、知识点、问题标题、处理状态、评论数量和置顶状态，可用于线下分析班级共性问题。</p>
              <div class="question-actions">
                <el-button type="primary" @click="handleExport">导出班级问答统计 CSV</el-button>
              </div>
            </div>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-drawer v-model="studentDrawerVisible" title="学生学习情况" size="620px">
      <div v-if="studentSnapshot" class="insight-list">
        <div class="insight-item">
          <span class="detail-label">学生信息</span>
          <strong>{{ studentSnapshot.student.display_name }}</strong>
          <p>{{ studentSnapshot.student.username }} · {{ studentSnapshot.student.profile?.class_name || studentSnapshot.student.class_id || "未设置班级" }}</p>
        </div>
        <div class="summary-row snapshot-summary-grid">
          <div class="summary-metric clickable-metric" @click="openTeacherDetail(`${studentSnapshot.student.display_name}已掌握节点`, studentSnapshot.mastered_statuses, 'statuses')"><span>已掌握节点</span><strong>{{ studentSnapshot.mastered_statuses.length }}</strong></div>
          <div class="summary-metric clickable-metric" @click="openTeacherDetail(`${studentSnapshot.student.display_name}学习中节点`, studentSnapshot.in_progress_statuses, 'statuses')"><span>学习中节点</span><strong>{{ studentSnapshot.in_progress_statuses.length }}</strong></div>
          <div class="summary-metric clickable-metric" @click="openTeacherDetail(`${studentSnapshot.student.display_name}未学节点`, studentSnapshot.unlearned_concepts, 'statuses')"><span>未学节点</span><strong>{{ studentSnapshot.unlearned_concepts.length }}</strong></div>
          <div class="summary-metric clickable-metric" @click="openTeacherDetail(`${studentSnapshot.student.display_name}全部提问`, studentSnapshot.recent_questions, 'questions')"><span>提问总数</span><strong>{{ studentSnapshot.total_question_count }}</strong></div>
          <div class="summary-metric clickable-metric" @click="openTeacherDetail(`${studentSnapshot.student.display_name}待跟进问题`, studentSnapshot.pending_questions, 'questions')"><span>待跟进问题</span><strong>{{ studentSnapshot.pending_question_count }}</strong></div>
          <div class="summary-metric clickable-metric" @click="openTeacherDetail(`${studentSnapshot.student.display_name}薄弱节点`, studentSnapshot.weak_statuses, 'statuses')"><span>薄弱节点</span><strong>{{ studentSnapshot.weak_statuses.length }}</strong></div>
        </div>
        <div class="detail-section detail-stack">
          <span class="detail-label">最近提问与讨论</span>
          <div v-if="studentSnapshot.recent_questions.length" class="insight-list">
            <div v-for="item in studentSnapshot.recent_questions" :key="item.id" class="insight-item">
              <strong>{{ item.title }}</strong>
              <p>{{ item.concept_name || "综合问题" }} · {{ formatDate(item.create_time) }}</p>
              <div class="tag-list">
                <el-tag effect="plain">{{ item.status === "answered" ? "已有回复" : "待讨论" }}</el-tag>
                <el-tag v-if="item.is_featured" type="warning" effect="plain">教师置顶</el-tag>
              </div>
            </div>
          </div>
          <el-empty v-else description="该学生近期还没有新的节点提问记录。" />
        </div>
      </div>
    </el-drawer>

    <el-dialog v-model="detailDialogVisible" :title="detailDialogTitle" width="860px" append-to-body class="teacher-detail-dialog">
      <div v-if="detailDialogType === 'students'" class="insight-list">
        <div v-for="item in detailDialogItems" :key="item.user_id" class="insight-item">
          <div class="card-header-inline">
            <div>
              <strong>{{ item.display_name }}</strong>
              <p class="table-meta">{{ item.username }} · {{ item.profile?.class_name || item.class_id || "未设置班级" }}</p>
            </div>
            <el-tag effect="plain">进度 {{ item.progress_rate }}%</el-tag>
          </div>
          <div class="question-actions">
            <el-button text type="primary" @click="openStudentSnapshot(item)">查看学习情况</el-button>
          </div>
        </div>
      </div>
      <div v-else-if="detailDialogType === 'concepts'" class="insight-list">
        <div v-for="item in detailDialogItems" :key="item.concept_id" class="insight-item">
          <div class="card-header-inline">
            <strong>{{ item.concept_name }}</strong>
            <div class="tag-list">
              <el-tag effect="plain">{{ item.category || "未分类" }}</el-tag>
              <el-tag v-if="item.risk_score !== undefined" type="danger" effect="plain">风险分 {{ item.risk_score }}</el-tag>
            </div>
          </div>
          <p class="detail-text">未学 {{ item.unlearned_count || 0 }} 人，学习中 {{ item.in_progress_count || 0 }} 人，已掌握 {{ item.mastered_count || 0 }} 人。</p>
          <div v-if="item.risk_score !== undefined" class="summary-row compact-summary top-gap">
            <div class="summary-metric"><span>提问次数</span><strong>{{ item.question_count }}</strong></div>
            <div class="summary-metric"><span>待跟进</span><strong>{{ item.pending_count }}</strong></div>
            <div class="summary-metric"><span>平均学习</span><strong>{{ item.average_learning_minutes }} 分</strong></div>
          </div>
          <p v-if="item.risk_reason" class="detail-text top-gap">{{ item.risk_reason }}</p>
        </div>
      </div>
      <div v-else-if="detailDialogType === 'questions'" class="insight-list">
        <div v-for="item in detailDialogItems" :key="item.id" class="insight-item">
          <div class="card-header-inline">
            <strong>{{ item.title }}</strong>
            <el-tag :type="item.status === 'answered' ? 'success' : 'warning'" effect="plain">{{ item.status === "answered" ? "已有回复" : "待跟进" }}</el-tag>
          </div>
          <p>{{ item.concept_name || "综合问题" }} · {{ item.student_name }} · {{ formatDate(item.create_time) }}</p>
          <div class="question-actions">
            <el-button text type="primary" @click="jumpToQuestion(item)">跳转到讨论管理</el-button>
          </div>
        </div>
      </div>
      <div v-else-if="detailDialogType === 'statuses'" class="tag-list">
        <el-tag v-for="item in detailDialogItems" :key="item.concept_id" effect="plain">{{ item.concept_name || item.concept_id }}</el-tag>
      </div>
      <el-empty v-if="!detailDialogItems.length" description="当前没有可展示的明细数据。" />
    </el-dialog>
  </AppShell>
</template>

<script setup>
import { ElMessage, ElMessageBox } from "element-plus";
import { computed, onMounted, reactive, ref } from "vue";

import { fetchGraphAll } from "../api/graph";
import { createQuestionComment, deleteQuestionComment } from "../api/learning";
import {
  createGraphChangeRequest,
  createQuickReplyTemplate,
  createTeacherCoordinationRequest,
  deleteQuickReplyTemplate,
  exportTeacherQuestionsCsv,
  fetchStudentSnapshot,
  featureTeacherComment,
  featureTeacherQuestion,
  fetchTeacherOverview,
} from "../api/teacher";
import AppShell from "../components/AppShell.vue";
import ThreadCommentTree from "../components/ThreadCommentTree.vue";
import { getCurrentUser } from "../utils/session";

const overview = ref({
  total_students: 0,
  average_progress_rate: 0,
  mastered_concepts_total: 0,
  pending_question_count: 0,
  answered_question_count: 0,
  featured_question_count: 0,
  pending_coordination_count: 0,
  student_progress: [],
  recent_questions: [],
  concept_question_stats: [],
  coordination_requests: [],
  class_overview: {
    average_mastered_count: 0,
    top_asked_concepts: [],
  },
  class_overviews: [],
  learning_factor_analysis: [],
  node_learning_analysis: [],
  quick_reply_templates: [],
  graph_change_requests: [],
});
const currentUser = ref(getCurrentUser());
const activeTeacherTab = ref("overview");
const activeConceptFilter = ref("");
const activeFactorKey = ref("gender");
const activeVennStatus = ref(2);
const questionFilterMode = ref("all");
const activeClassStudentIds = ref([]);
const activeReplyQuestionId = ref("");
const replyingQuestionId = ref(0);
const replyDrafts = reactive({});
const replyContext = ref({
  questionId: 0,
  parentCommentId: null,
  targetName: "",
});
const coordinationForm = ref({
  type: "图谱内容维护",
  title: "",
  description: "",
});
const templateForm = reactive({
  title: "",
  content: "",
});
const creatingTemplate = ref(false);
const studentDrawerVisible = ref(false);
const studentSnapshot = ref(null);
const detailDialogVisible = ref(false);
const detailDialogTitle = ref("");
const detailDialogType = ref("students");
const detailDialogItems = ref([]);
const submittingCoordination = ref(false);
const submittingGraphChange = ref(false);
const graphNodes = ref([]);
const graphLinks = ref([]);
const selectedGraphNodeName = ref("");
const graphDraftTexts = reactive({
  keyPoints: "",
  resourceLinks: "",
  studyTips: "",
  commonMistakes: "",
  quiz: "",
});
const graphChangeForm = reactive({
  action: "update_node",
  summary: "",
  target_concept_name: "",
  node: {
    name: "",
    description: "",
    category: "",
    difficulty: 2,
    estimated_minutes: 30,
    key_points: [],
    text_material: "",
    image_url: "",
    video_title: "",
    video_url: "",
    resource_links: [],
    study_tips: [],
    common_mistakes: [],
    practice_task: "",
    quiz: [],
  },
  prerequisite_names: [],
  next_names: [],
  related_names: [],
});
const coordinationTypes = [
  { label: "图谱内容维护", value: "图谱内容维护" },
  { label: "班级权限调整", value: "班级权限调整" },
  { label: "教学资源补充", value: "教学资源补充" },
  { label: "系统支持请求", value: "系统支持请求" },
];
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
const statusColorMap = {
  0: "#adb5bd",
  1: "#f4a261",
  2: "#6a994e",
};
const statusTextMap = {
  0: "未学",
  1: "学习中",
  2: "已掌握",
};
const questionFilterOptions = [
  { label: "全部", value: "all" },
  { label: "待跟进", value: "pending" },
  { label: "置顶", value: "featured" },
];
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

const filteredQuestions = computed(() => {
  let questions = overview.value.recent_questions;
  if (activeConceptFilter.value) {
    questions = questions.filter((item) => (item.concept_name || "综合问题") === activeConceptFilter.value);
  }
  if (questionFilterMode.value === "pending") {
    questions = questions.filter((item) => item.status === "pending");
  }
  if (questionFilterMode.value === "featured") {
    questions = questions.filter((item) => item.is_featured);
  }
  if (activeClassStudentIds.value.length) {
    const classIds = new Set(activeClassStudentIds.value);
    questions = questions.filter((item) => classIds.has(item.student_id));
  }
  return questions;
});
const maxConceptQuestionCount = computed(() => Math.max(...overview.value.concept_question_stats.map((item) => item.question_count), 1));
const pendingGraphChangeCount = computed(() => overview.value.graph_change_requests.filter((item) => item.status === "pending").length);
const relationCandidateNodes = computed(() => graphNodes.value.filter((item) => item.name !== graphChangeForm.node.name));
const highRiskNodes = computed(() => overview.value.node_learning_analysis.filter((item) => item.risk_score >= 55).slice(0, 8));
const topQuestionNodes = computed(() => overview.value.node_learning_analysis.filter((item) => item.question_count > 0).sort((a, b) => b.question_count - a.question_count).slice(0, 8));
const slowLearningNodes = computed(() => overview.value.node_learning_analysis.filter((item) => item.average_learning_minutes > 0).sort((a, b) => b.average_learning_minutes - a.average_learning_minutes).slice(0, 8));
const pendingQuestionNodes = computed(() => overview.value.node_learning_analysis.filter((item) => item.pending_count > 0).sort((a, b) => b.pending_count - a.pending_count).slice(0, 8));
const priorityNodeCards = computed(() => overview.value.node_learning_analysis.slice(0, 6));
const activeStatusAnalysisNodes = computed(() => overview.value.node_learning_analysis.filter((item) => getNodeStatusCount(item, activeVennStatus.value) > 0).sort((a, b) => b.risk_score - a.risk_score));
const focusAnalysisNodes = computed(() => activeStatusAnalysisNodes.value.filter((item) => item.risk_score >= 55 || item.pending_count > 0).slice(0, 10));
const activeFactorAnalysis = computed(() => {
  const items = overview.value.learning_factor_analysis || [];
  return items.find((item) => item.factor_key === activeFactorKey.value) || items[0] || null;
});
const factorVennSets = computed(() => {
  const groups = (activeFactorAnalysis.value?.groups || []).slice(0, 3).map((group) => ({
    ...group,
    concepts: getGroupConceptsByStatus(group, activeVennStatus.value),
  }));
  if (!groups.length) return { groups: [], common: [] };
  const commonNames = groups
    .map((group) => new Set(group.concepts.map((item) => item.concept_name)))
    .reduce((acc, set) => new Set([...acc].filter((name) => set.has(name))));
  const byName = new Map(groups.flatMap((group) => group.concepts.map((item) => [item.concept_name, item])));
  return {
    groups,
    common: [...commonNames].map((name) => byName.get(name)).filter(Boolean),
  };
});

function getGroupConceptsByStatus(group, status) {
  if (status === 2) return group.mastered_concepts || [];
  if (status === 1) return group.in_progress_concepts || [];
  return group.unlearned_concepts || [];
}

function getGroupStatusPercentage(group, status) {
  if (status === 2) return group.mastered_percentage || 0;
  if (status === 1) return group.in_progress_percentage || 0;
  return group.unlearned_percentage || 0;
}

function getNodeStatusCount(node, status) {
  if (status === 2) return node.mastered_count || 0;
  if (status === 1) return node.in_progress_count || 0;
  return node.unlearned_count || 0;
}

function getNodeStatusPercentage(node, status) {
  if (status === 2) return node.mastered_percentage || 0;
  if (status === 1) return node.in_progress_percentage || 0;
  return node.unlearned_percentage || 0;
}

function getGroupUniqueConcepts(group) {
  const commonNames = new Set(factorVennSets.value.common.map((item) => item.concept_name));
  return getGroupConceptsByStatus(group, activeVennStatus.value).filter((item) => !commonNames.has(item.concept_name));
}

function previewConceptNames(items = []) {
  if (!items.length) return "暂无共同节点";
  const names = items.map((item) => item.concept_name);
  return names.length > 3 ? `${names.slice(0, 3).join("、")}...` : names.join("、");
}

function formatConceptTooltip(items = []) {
  return items.length ? items.map((item) => item.concept_name).join("、") : "暂无节点";
}

function conceptQuestionPercent(count) {
  return Math.round((count / maxConceptQuestionCount.value) * 100);
}

function formatDate(value) {
  return value ? new Date(value).toLocaleString("zh-CN", { hour12: false }) : "";
}

function linesToList(value) {
  return value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

function linksFromText(value) {
  return linesToList(value)
    .map((line) => {
      const [label, url] = line.split("|").map((item) => item?.trim());
      return label && url ? { label, url } : null;
    })
    .filter(Boolean);
}

function quizFromText(value) {
  return linesToList(value)
    .map((line) => {
      const parts = line.split("|").map((item) => item.trim());
      if (parts.length >= 7) {
        const [question, ...rest] = parts;
        const explanation = rest.pop();
        const answerIndex = Number(rest.pop());
        const options = rest;
        return Number.isInteger(answerIndex) && options.length >= 2
          ? { question, options, answer_index: answerIndex, explanation }
          : null;
      }
      if (parts.length === 5) {
        const [question, optionA, optionB, answerIndexText, explanation] = parts;
        const answerIndex = Number(answerIndexText);
        return Number.isInteger(answerIndex)
          ? { question, options: [optionA, optionB], answer_index: answerIndex, explanation }
          : null;
      }
      return null;
    })
    .filter((item) => item && item.question && item.options.length >= 2 && item.answer_index >= 0 && item.answer_index < item.options.length);
}

function textFromList(list) {
  return (list || []).join("\n");
}

function textFromLinks(list) {
  return (list || []).map((item) => `${item.label}|${item.url}`).join("\n");
}

function textFromQuiz(list) {
  return (list || [])
    .map((item) => `${item.question}|${item.options.join("|")}|${item.answer_index}|${item.explanation || ""}`)
    .join("\n");
}

function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  window.URL.revokeObjectURL(url);
}

function closeReplyComposer() {
  activeReplyQuestionId.value = "";
  replyContext.value = {
    questionId: 0,
    parentCommentId: null,
    targetName: "",
  };
}

function openReplyComposer(question, comment = null) {
  const nextParentCommentId = comment?.id ?? null;
  const isSameComposer =
    activeReplyQuestionId.value === question.id &&
    replyContext.value.parentCommentId === nextParentCommentId;
  if (isSameComposer) {
    closeReplyComposer();
    return;
  }
  activeReplyQuestionId.value = question.id;
  replyContext.value = {
    questionId: question.id,
    parentCommentId: nextParentCommentId,
    targetName: comment?.author_name || "",
  };
}

function applyTemplate(questionId, template) {
  replyDrafts[questionId] = template.content;
}

function openTeacherDetail(title, items, type = "students") {
  detailDialogTitle.value = title;
  detailDialogItems.value = items || [];
  detailDialogType.value = type;
  detailDialogVisible.value = true;
}

function openNodeAnalysisDetail(title, items) {
  openTeacherDetail(title, items || [], "concepts");
}

function openQuestionConceptDetail(item) {
  const matched = overview.value.node_learning_analysis.find((node) => node.concept_name === item.concept_name);
  openNodeAnalysisDetail(`${item.concept_name} 提问明细`, matched ? [matched] : [{
    concept_name: item.concept_name,
    question_count: item.question_count,
    pending_count: item.pending_count,
  }]);
}

function openFactorGroupDetail(group) {
  openTeacherDetail(`${activeFactorAnalysis.value?.factor_label || "分组"}：${group.group_label}`, getGroupConceptsByStatus(group, activeVennStatus.value), "concepts");
}

function openClassConcepts(classItem, type) {
  const map = {
    unlearned: ["未学较多节点", classItem.top_unlearned_concepts],
    inProgress: ["学习中较多节点", classItem.top_in_progress_concepts],
    mastered: ["已掌握较多节点", classItem.top_mastered_concepts],
  };
  const [label, items] = map[type] || map.unlearned;
  openTeacherDetail(`${classItem.class_name}${label}`, items, "concepts");
}

function openAllMasteredConcepts() {
  const items = overview.value.class_overviews.flatMap((item) => item.top_mastered_concepts || []);
  openTeacherDetail("全班已掌握节点统计", items, "concepts");
}

function jumpToQuestionList(mode = "all", classItem = null) {
  questionFilterMode.value = mode;
  activeConceptFilter.value = "";
  activeClassStudentIds.value = classItem ? classItem.students.map((item) => item.user_id) : [];
  activeTeacherTab.value = "threads";
}

function jumpToQuestion(question) {
  detailDialogVisible.value = false;
  questionFilterMode.value = question.is_featured ? "featured" : question.status === "pending" ? "pending" : "all";
  activeConceptFilter.value = question.concept_name || "";
  activeClassStudentIds.value = [];
  activeTeacherTab.value = "threads";
}

async function loadOverview() {
  const { data } = await fetchTeacherOverview();
  overview.value = data;
  if (!overview.value.learning_factor_analysis?.some((item) => item.factor_key === activeFactorKey.value)) {
    activeFactorKey.value = overview.value.learning_factor_analysis?.[0]?.factor_key || "gender";
  }
}

async function loadGraphCatalog() {
  const { data } = await fetchGraphAll();
  graphNodes.value = [...(data.nodes || [])].sort((a, b) => a.name.localeCompare(b.name, "zh-CN"));
  graphLinks.value = data.links || [];
  if (!selectedGraphNodeName.value && graphNodes.value.length) {
    selectedGraphNodeName.value = graphNodes.value[0].name;
    fillGraphFormFromNode(selectedGraphNodeName.value);
  }
}

function resetGraphChangeForm() {
  Object.assign(graphChangeForm, {
    action: graphChangeForm.action,
    summary: "",
    target_concept_name: "",
    node: {
      name: "",
      description: "",
      category: "",
      difficulty: 2,
      estimated_minutes: 30,
      key_points: [],
      text_material: "",
      image_url: "",
      video_title: "",
      video_url: "",
      resource_links: [],
      study_tips: [],
      common_mistakes: [],
      practice_task: "",
      quiz: [],
    },
    prerequisite_names: [],
    next_names: [],
    related_names: [],
  });
  Object.assign(graphDraftTexts, {
    keyPoints: "",
    resourceLinks: "",
    studyTips: "",
    commonMistakes: "",
    quiz: "",
  });
  if (graphChangeForm.action === "update_node" && selectedGraphNodeName.value) {
    fillGraphFormFromNode(selectedGraphNodeName.value);
  }
}

function handleGraphActionChange() {
  selectedGraphNodeName.value = graphChangeForm.action === "update_node" ? selectedGraphNodeName.value : "";
  resetGraphChangeForm();
}

function fillGraphFormFromNode(nodeName) {
  const node = graphNodes.value.find((item) => item.name === nodeName);
  if (!node) return;
  graphChangeForm.target_concept_name = node.name;
  graphChangeForm.node = {
    name: node.name,
    description: node.description || "",
    category: node.category || "",
    difficulty: node.difficulty || 2,
    estimated_minutes: node.estimated_minutes || 30,
    key_points: node.key_points || [],
    text_material: node.text_material || "",
    image_url: node.image_url || "",
    video_title: node.video_title || "",
    video_url: node.video_url || "",
    resource_links: node.resource_links || [],
    study_tips: node.study_tips || [],
    common_mistakes: node.common_mistakes || [],
    practice_task: node.practice_task || "",
    quiz: node.quiz || [],
  };
  graphDraftTexts.keyPoints = textFromList(node.key_points);
  graphDraftTexts.resourceLinks = textFromLinks(node.resource_links);
  graphDraftTexts.studyTips = textFromList(node.study_tips);
  graphDraftTexts.commonMistakes = textFromList(node.common_mistakes);
  graphDraftTexts.quiz = textFromQuiz(node.quiz);

  const idToName = Object.fromEntries(graphNodes.value.map((item) => [item.id, item.name]));
  const nameToId = Object.fromEntries(graphNodes.value.map((item) => [item.name, item.id]));
  const nodeId = nameToId[node.name];
  graphChangeForm.prerequisite_names = graphLinks.value
    .filter((item) => item.type === "PREREQUISITE_OF" && item.target === nodeId)
    .map((item) => idToName[item.source])
    .filter(Boolean);
  graphChangeForm.next_names = graphLinks.value
    .filter((item) => item.type === "PREREQUISITE_OF" && item.source === nodeId)
    .map((item) => idToName[item.target])
    .filter(Boolean);
  graphChangeForm.related_names = graphLinks.value
    .filter((item) => item.type === "RELATED_TO" && (item.source === nodeId || item.target === nodeId))
    .map((item) => (item.source === nodeId ? idToName[item.target] : idToName[item.source]))
    .filter(Boolean);
}

function buildGraphChangePayload() {
  return {
    action: graphChangeForm.action,
    summary: graphChangeForm.summary.trim(),
    target_concept_name: graphChangeForm.action === "update_node" ? graphChangeForm.target_concept_name : null,
    node: {
      ...graphChangeForm.node,
      name: graphChangeForm.node.name.trim(),
      description: graphChangeForm.node.description?.trim() || null,
      category: graphChangeForm.node.category?.trim() || null,
      key_points: linesToList(graphDraftTexts.keyPoints),
      text_material: graphChangeForm.node.text_material?.trim() || null,
      image_url: graphChangeForm.node.image_url?.trim() || null,
      video_title: graphChangeForm.node.video_title?.trim() || null,
      video_url: graphChangeForm.node.video_url?.trim() || null,
      resource_links: linksFromText(graphDraftTexts.resourceLinks),
      study_tips: linesToList(graphDraftTexts.studyTips),
      common_mistakes: linesToList(graphDraftTexts.commonMistakes),
      practice_task: graphChangeForm.node.practice_task?.trim() || null,
      quiz: quizFromText(graphDraftTexts.quiz),
    },
    prerequisite_names: graphChangeForm.prerequisite_names,
    next_names: graphChangeForm.next_names,
    related_names: graphChangeForm.related_names,
  };
}

async function handleExport() {
  try {
    const { data, headers } = await exportTeacherQuestionsCsv();
    const disposition = headers["content-disposition"] || "";
    const matched = disposition.match(/filename="(.+)"/);
    downloadBlob(data, matched?.[1] || "teacher-class-question-stats.csv");
    ElMessage.success("班级问答统计已导出。");
  } catch (error) {
    console.error(error);
    ElMessage.error("导出班级问答统计失败，请稍后重试。");
  }
}

async function handleTemplateCreate() {
  const title = templateForm.title.trim();
  const content = templateForm.content.trim();
  if (title.length < 2 || content.length < 4) {
    ElMessage.warning("请完整填写模板名称和内容。");
    return;
  }

  try {
    creatingTemplate.value = true;
    await createQuickReplyTemplate({ title, content });
    templateForm.title = "";
    templateForm.content = "";
    ElMessage.success("快速回复模板已保存。");
    await loadOverview();
  } catch (error) {
    console.error(error);
    ElMessage.error("保存模板失败，请稍后重试。");
  } finally {
    creatingTemplate.value = false;
  }
}

async function handleTemplateDelete(item) {
  try {
    await ElMessageBox.confirm("确认删除这条快速回复模板吗？", "删除模板", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
    });
    await deleteQuickReplyTemplate(item.id);
    ElMessage.success("模板已删除。");
    await loadOverview();
  } catch (error) {
    if (error === "cancel") {
      return;
    }
    console.error(error);
    ElMessage.error("删除模板失败，请稍后重试。");
  }
}

async function handleCoordinationSubmit() {
  const title = coordinationForm.value.title.trim();
  const description = coordinationForm.value.description.trim();
  if (title.length < 2 || description.length < 5) {
    ElMessage.warning("请完整填写协同事项标题和说明。");
    return;
  }

  try {
    submittingCoordination.value = true;
    await createTeacherCoordinationRequest({
      type: coordinationForm.value.type,
      title,
      description,
    });
    coordinationForm.value = {
      type: "图谱内容维护",
      title: "",
      description: "",
    };
    ElMessage.success("协同事项已提交，图谱运维官处理后会回传到此页面。");
    await loadOverview();
  } catch (error) {
    console.error(error);
    ElMessage.error("提交协同事项失败，请稍后重试。");
  } finally {
    submittingCoordination.value = false;
  }
}

async function handleGraphChangeSubmit() {
  const payload = buildGraphChangePayload();
  if (payload.summary.length < 4 || payload.node.name.length < 1) {
    ElMessage.warning("请至少填写申请说明和节点名称。");
    return;
  }
  if (!payload.node.description && !payload.node.text_material && payload.node.key_points.length === 0) {
    ElMessage.warning("请至少补充节点简介、知识梳理或学习材料中的一项。");
    return;
  }

  try {
    submittingGraphChange.value = true;
    await createGraphChangeRequest(payload);
    ElMessage.success("图谱节点变更申请已提交，等待图谱运维官审核。");
    await Promise.all([loadOverview(), loadGraphCatalog()]);
  } catch (error) {
    console.error(error);
    ElMessage.error("提交图谱变更申请失败，请检查内容格式后重试。");
  } finally {
    submittingGraphChange.value = false;
  }
}

async function openStudentSnapshot(item) {
  try {
    const studentId = item.student_id || item.user_id;
    const { data } = await fetchStudentSnapshot(studentId);
    studentSnapshot.value = data;
    studentDrawerVisible.value = true;
  } catch (error) {
    console.error(error);
    ElMessage.error("加载学生学习情况失败，请稍后重试。");
  }
}

async function handleReplySubmit(item) {
  const content = (replyDrafts[item.id] || "").trim();
  if (content.length < 2) {
    ElMessage.warning("回复内容至少需要 2 个字。");
    return;
  }
  try {
    replyingQuestionId.value = item.id;
    await createQuestionComment(item.id, content, replyContext.value.questionId === item.id ? replyContext.value.parentCommentId : null);
    replyDrafts[item.id] = "";
    closeReplyComposer();
    ElMessage.success("回复已发布，学生会在对应节点论坛中看到。");
    await loadOverview();
  } catch (error) {
    console.error(error);
    ElMessage.error("发布回复失败，请稍后重试。");
  } finally {
    replyingQuestionId.value = 0;
  }
}

async function handleFeatureToggle(item) {
  try {
    await featureTeacherQuestion(item.id, !item.is_featured);
    ElMessage.success(item.is_featured ? "已取消置顶。" : "已置顶讨论。");
    await loadOverview();
  } catch (error) {
    console.error(error);
    ElMessage.error("更新置顶状态失败，请稍后重试。");
  }
}

async function handleCommentFeature(comment) {
  try {
    await featureTeacherComment(comment.id, !comment.is_excellent);
    ElMessage.success(comment.is_excellent ? "已取消优秀评论。" : "已设为优秀评论。");
    await loadOverview();
  } catch (error) {
    console.error(error);
    ElMessage.error("更新优秀评论失败，请稍后重试。");
  }
}

async function handleCommentDelete(comment) {
  try {
    await ElMessageBox.confirm("删除后这条评论及其楼中楼回复会一起移除，是否继续？", "删除评论", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
    });
    await deleteQuestionComment(comment.id);
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

onMounted(async () => {
  try {
    await Promise.all([loadOverview(), loadGraphCatalog()]);
  } catch (error) {
    console.error(error);
    ElMessage.error("教师工作台数据加载失败，请稍后重试。");
  }
});
</script>
