<template>
  <div class="graph-card">
    <div class="graph-toolbar">
      <el-tag type="success">图谱画布预留区</el-tag>
      <span>后续可接入 ECharts Graph 或 AntV G6</span>
    </div>
    <div class="graph-stage">
      <div class="graph-placeholder">
        <h3>知识图谱可视化区域</h3>
        <p>当前已完成接口与页面结构，下一步可在此处挂载图谱渲染实例。</p>
        <p>节点数：{{ nodes.length }}，关系数：{{ links.length }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  nodes: {
    type: Array,
    default: () => [],
  },
  links: {
    type: Array,
    default: () => [],
  },
});
</script>
