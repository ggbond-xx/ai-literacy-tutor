<template>
  <div class="thread-comment-tree">
    <div v-for="comment in comments" :key="comment.id" class="thread-comment">
      <div class="thread-comment-header">
        <div>
          <strong>{{ comment.author_name }}</strong>
          <span class="thread-comment-meta">
            · {{ roleTextMap[comment.author_role] || comment.author_role }} · {{ formatDate(comment.create_time) }}
          </span>
        </div>
        <div class="tag-list">
          <el-tag v-if="comment.is_excellent" type="success" effect="dark">优秀评论</el-tag>
          <el-tag v-if="comment.author_role === 'teacher'" effect="plain">教师</el-tag>
        </div>
      </div>

      <p class="detail-text">
        <span v-if="comment.reply_to_author_name" class="reply-target">回复 {{ comment.reply_to_author_name }}：</span>
        {{ comment.content }}
      </p>

      <div class="question-actions compact-thread-actions">
        <el-button v-if="canReply" text type="primary" @click="$emit('reply', comment)">回复</el-button>
        <el-button
          v-if="canLike && currentUserId !== comment.author_id"
          text
          type="primary"
          @click="$emit('like', comment)"
        >
          {{ comment.is_liked ? "取消点赞" : "点赞" }} {{ comment.like_count }}
        </el-button>
        <span v-else class="thread-like-count">点赞 {{ comment.like_count }}</span>
        <el-button v-if="comment.can_delete" text type="danger" @click="$emit('delete', comment)">删除</el-button>
        <el-button
          v-if="canModerateDelete && !comment.can_delete"
          text
          type="danger"
          @click="$emit('moderate-delete', comment)"
        >
          管理删除
        </el-button>
        <el-button
          v-if="isTeacher"
          text
          type="success"
          @click="$emit('feature', comment)"
        >
          {{ comment.is_excellent ? "取消优秀" : "设为优秀评论" }}
        </el-button>
      </div>

      <div v-if="comment.replies?.length" class="thread-comment-children">
        <ThreadCommentTree
          :comments="comment.replies"
          :current-user-id="currentUserId"
          :can-reply="canReply"
          :can-like="canLike"
          :is-teacher="isTeacher"
          :can-moderate-delete="canModerateDelete"
          @reply="$emit('reply', $event)"
          @like="$emit('like', $event)"
          @delete="$emit('delete', $event)"
          @moderate-delete="$emit('moderate-delete', $event)"
          @feature="$emit('feature', $event)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { roleTextMap } from "../utils/role";

defineOptions({
  name: "ThreadCommentTree",
});

defineProps({
  comments: {
    type: Array,
    default: () => [],
  },
  currentUserId: {
    type: Number,
    default: null,
  },
  canReply: {
    type: Boolean,
    default: false,
  },
  canLike: {
    type: Boolean,
    default: false,
  },
  canModerateDelete: {
    type: Boolean,
    default: false,
  },
  isTeacher: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["reply", "like", "delete", "moderate-delete", "feature"]);

function formatDate(value) {
  if (!value) {
    return "";
  }
  return new Date(value).toLocaleString("zh-CN", { hour12: false });
}
</script>
