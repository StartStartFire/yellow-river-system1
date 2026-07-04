<script setup lang="ts">
/**
 * BaseChart — 通用 ECharts 图表容器
 *
 * 封装 ECharts 初始化、ResizeObserver 自适应、组件卸载自动 dispose。
 * 父组件只需提供 option 即可，无需手动管理 ECharts 生命周期。
 *
 * 用法：
 * ```vue
 * <BaseChart :option="chartOption" />
 * ```
 */
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

interface Props {
  /** ECharts option 对象，变化时自动 setOption */
  option: echarts.EChartsOption
  /** 是否在 setOption 时使用 notMerge（替换而非合并），默认 true */
  notMerge?: boolean
  /** 初始化延迟（ms），用于等待 flex 布局完成，默认 200 */
  initDelay?: boolean
  /** 最小高度（px），默认 0 */
  minHeight?: number
}

const props = withDefaults(defineProps<Props>(), {
  notMerge: true,
  initDelay: true,
  minHeight: 0,
})

const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

/** 初始化 ECharts 实例 */
const initChart = () => {
  if (!chartRef.value) return

  // 确保容器有尺寸
  const rect = chartRef.value.getBoundingClientRect()
  if (rect.width === 0 || rect.height === 0) {
    setTimeout(() => initChart(), 100)
    return
  }

  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  if (props.option) {
    chart.setOption(props.option, { notMerge: props.notMerge })
    chart.resize()
  }
}

/** 更新 option */
const updateChart = () => {
  if (!chart || !props.option) return
  chart.setOption(props.option, { notMerge: props.notMerge })
  chart.resize()
}

// 监听 option 变化自动更新
watch(() => props.option, () => {
  updateChart()
}, { deep: true })

onMounted(() => {
  const delay = props.initDelay ? 200 : 0
  setTimeout(() => {
    initChart()
    if (chartRef.value) {
      resizeObserver = new ResizeObserver(() => chart?.resize())
      resizeObserver.observe(chartRef.value)
    }
  }, delay)
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  if (chart) {
    chart.dispose()
    chart = null
  }
})

/** 暴露 chart 实例，供父组件需要时直接操作（如特殊 resize） */
defineExpose({
  getChart: () => chart,
  resize: () => chart?.resize(),
})
</script>

<template>
  <div
    ref="chartRef"
    class="base-chart"
    :style="{ minHeight: minHeight ? minHeight + 'px' : undefined }"
  ></div>
</template>

<style scoped>
.base-chart {
  width: 100%;
  height: 100%;
}
</style>
