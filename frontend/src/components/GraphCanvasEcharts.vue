<template>
  <div class="graph-card">
    <div class="graph-toolbar">
      <el-tag type="success">ECharts Graph</el-tag>
      <span>支持拖拽、缩放与邻接高亮</span>
    </div>
    <div v-if="nodes.length" ref="chartRef" class="graph-stage graph-host"></div>
    <div v-else class="graph-stage">
      <div class="graph-placeholder">
        <h3>暂无图谱数据</h3>
        <p>请先确认后端服务已启动，并且 `/api/graph/all` 可以返回节点与关系。</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import * as echarts from "echarts";
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps({
  nodes: {
    type: Array,
    default: () => [],
  },
  links: {
    type: Array,
    default: () => [],
  },
  activeNodeId: {
    type: String,
    default: "",
  },
  recommendedNodeIds: {
    type: Array,
    default: () => [],
  },
  learningPathNodeIds: {
    type: Array,
    default: () => [],
  },
  weakPointNodeIds: {
    type: Array,
    default: () => [],
  },
  defaultTargetId: {
    type: String,
    default: "",
  },
  statusMap: {
    type: Object,
    default: () => ({}),
  },
});
const emit = defineEmits(["node-select"]);

const chartRef = ref(null);
let chartInstance = null;
const layoutCache = new Map();
let cachedSignature = "";
let pendingSignature = "";

const categoryPalette = {
  基础概念: "#bc6c25",
  数字素养: "#4d908e",
  算法模型: "#577590",
  伦理素养: "#b56576",
  应用实践: "#6a994e",
};

const relationTextMap = {
  PREREQUISITE_OF: "前置依赖",
  RELATED_TO: "相关知识",
  BELONGS_TO: "归属分类",
};

const statusPalette = {
  2: "#6a994e",
  1: "#dda15e",
  0: "#c7c4bd",
};

const graphSignature = computed(() => {
  const nodeIds = props.nodes.map((node) => node.id).sort().join("|");
  const linkIds = props.links
    .map((link) => `${link.source}>${link.target}:${link.type}`)
    .sort()
    .join("|");
  return `${nodeIds}::${linkIds}`;
});

const chartNodes = computed(() =>
  props.nodes.map((node) => {
    const hasStatusData = Object.keys(props.statusMap || {}).length > 0;
    const nodeStatus = props.statusMap[node.id] ?? 0;
    const isActive = props.activeNodeId === node.id;
    const isTarget = props.defaultTargetId === node.id;
    const isPathNode = props.learningPathNodeIds.includes(node.id);
    const isRecommended = props.recommendedNodeIds.includes(node.id);
    const isWeakPoint = props.weakPointNodeIds.includes(node.id);
    const isMastered = nodeStatus === 2;

    let borderColor = "rgba(255, 255, 255, 0.85)";
    let borderWidth = 1.5;
    let shadowBlur = 8;
    let shadowColor = "rgba(47, 36, 24, 0.18)";
    let symbol = "circle";
    let symbolSize = 34 + (node.difficulty || 1) * 5;

    if (isWeakPoint) {
      borderColor = "#b56576";
      borderWidth = 3;
      shadowBlur = 14;
      shadowColor = "rgba(181, 101, 118, 0.28)";
      symbol = "roundRect";
    }
    if (isRecommended) {
      borderColor = "#dda15e";
      borderWidth = 3.5;
      shadowBlur = 16;
      shadowColor = "rgba(221, 161, 94, 0.3)";
      symbolSize += 2;
    }
    if (isPathNode) {
      borderColor = "#bc6c25";
      borderWidth = 4;
      shadowBlur = 18;
      shadowColor = "rgba(188, 108, 37, 0.32)";
      symbolSize += 4;
    }
    if (isTarget) {
      borderColor = "#8f4d14";
      borderWidth = 5;
      shadowBlur = 22;
      shadowColor = "rgba(143, 77, 20, 0.38)";
      symbol = "diamond";
      symbolSize += 8;
    }
    if (isActive) {
      borderColor = "#2f2418";
      borderWidth = 5;
      shadowBlur = 24;
      shadowColor = "rgba(47, 36, 24, 0.3)";
      symbolSize += 4;
    }

    return {
      id: node.id,
      name: node.name,
      category: node.category || "未分类",
      symbol,
      symbolSize,
      value: node.description || node.name,
      draggable: true,
      itemStyle: {
        color: hasStatusData ? statusPalette[nodeStatus] || "#c7c4bd" : categoryPalette[node.category] || "#8f4d14",
        borderColor,
        borderWidth,
        shadowBlur,
        shadowColor,
        opacity: isMastered ? 0.88 : 1,
      },
      label: {
        show: true,
        color: "#2f2418",
        fontSize: isTarget ? 14 : 13,
        fontWeight: isTarget || isActive ? "bold" : "normal",
      },
      description: node.description || "暂无描述",
      difficulty: node.difficulty || "未知",
      estimatedMinutes: node.estimated_minutes || 0,
    };
  }),
);

const chartLinks = computed(() =>
  props.links.map((link) => {
    const pathNodes = new Set(props.learningPathNodeIds);
    const isPathEdge = pathNodes.has(link.source) && pathNodes.has(link.target) && link.type === "PREREQUISITE_OF";
    return {
      source: link.source,
      target: link.target,
      value: relationTextMap[link.type] || link.type,
      rawType: link.type,
      lineStyle: {
        color: link.type === "PREREQUISITE_OF" ? "#bc6c25" : "#8ab17d",
        width: isPathEdge ? 3.5 : link.type === "PREREQUISITE_OF" ? 2 : 1.5,
        curveness: 0.12,
        opacity: isPathEdge ? 1 : 0.9,
      },
    };
  }),
);

function renderChart() {
  if (!chartRef.value || !chartNodes.value.length) {
    if (chartInstance) {
      chartInstance.clear();
    }
    return;
  }

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value);
    chartInstance.on("click", (params) => {
      if (params.dataType === "node") {
        emit("node-select", params.data.id);
      }
    });
    chartInstance.on("finished", () => {
      persistLayout();
    });
  }

  const hasCompleteLayout =
    cachedSignature === graphSignature.value &&
    props.nodes.every((node) => layoutCache.has(node.id));
  const useForceLayout = !hasCompleteLayout;
  pendingSignature = graphSignature.value;
  const data = chartNodes.value.map((node) => {
    if (!useForceLayout) {
      const point = layoutCache.get(node.id);
      if (point) {
        return {
          ...node,
          x: point.x,
          y: point.y,
          fixed: true,
        };
      }
    }
    return node;
  });

  chartInstance.setOption(
    {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "item",
        backgroundColor: "rgba(47, 36, 24, 0.92)",
        borderWidth: 0,
        textStyle: {
          color: "#fffaf3",
        },
        formatter: (params) => {
          if (params.dataType === "edge") {
            return `关系类型：${params.data.value}`;
          }
          return [
            `<strong>${params.data.name}</strong>`,
            `分类：${params.data.category}`,
            `难度：${params.data.difficulty}`,
            `建议时长：${params.data.estimatedMinutes || "未设置"}${params.data.estimatedMinutes ? " 分钟" : ""}`,
            params.data.description,
          ].join("<br/>");
        },
      },
      animationDuration: 800,
      series: [
        {
          type: "graph",
          layout: useForceLayout ? "force" : "none",
          roam: true,
          draggable: true,
          data,
          links: chartLinks.value,
          force: useForceLayout
            ? {
                repulsion: 320,
                edgeLength: [100, 180],
                gravity: 0.06,
              }
            : undefined,
          edgeSymbol: ["none", "arrow"],
          edgeSymbolSize: [0, 8],
          edgeLabel: {
            show: true,
            formatter: (params) => params.data.value,
            color: "#6b5a45",
            fontSize: 10,
            backgroundColor: "rgba(255, 248, 240, 0.92)",
            borderRadius: 8,
            padding: [3, 6],
          },
          emphasis: {
            focus: "adjacency",
            label: {
              fontWeight: "bold",
            },
          },
          selectedMode: "single",
        },
      ],
    },
    true,
  );
}

function persistLayout() {
  if (!chartInstance || !props.nodes.length) {
    return;
  }

  const seriesModel = chartInstance.getModel()?.getSeriesByIndex(0);
  const data = seriesModel?.getData();
  if (!data) {
    return;
  }

  const nextLayout = new Map();
  data.each((index) => {
    const rawItem = data.getRawDataItem(index);
    const layout = data.getItemLayout(index);
    let x;
    let y;
    if (Array.isArray(layout)) {
      [x, y] = layout;
    } else if (layout && typeof layout === "object") {
      x = layout.x ?? layout[0];
      y = layout.y ?? layout[1];
    }

    if (rawItem?.id && typeof x === "number" && typeof y === "number") {
      nextLayout.set(rawItem.id, { x, y });
    }
  });

  if (nextLayout.size) {
    layoutCache.clear();
    nextLayout.forEach((value, key) => layoutCache.set(key, value));
    cachedSignature = pendingSignature || graphSignature.value;
  }
}

function resizeChart() {
  if (chartInstance) {
    chartInstance.resize();
  }
}

watch(
  () => [
    props.nodes,
    props.links,
    props.activeNodeId,
    props.recommendedNodeIds,
    props.learningPathNodeIds,
    props.weakPointNodeIds,
    props.defaultTargetId,
    props.statusMap,
  ],
  async () => {
    await nextTick();
    renderChart();
  },
  { deep: true },
);

onMounted(() => {
  renderChart();
  window.addEventListener("resize", resizeChart);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", resizeChart);
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
});
</script>
