<script setup lang="ts">
import { computed } from 'vue'
import PanelCard from '@/components/common/PanelCard.vue'
import type { ReservoirSection } from '@/mock/basicData'

interface Props {
  section: ReservoirSection
  showGlow?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showGlow: true,
})

// ========== 坐标系统 ==========
// 背景图 1672x940, 高程范围动态计算
const elevMin = computed(() => {
  const all = props.section.levels.map(l => l.value)
  all.push(props.section.currentLevel)
  all.push(props.section.dam.crestElevation)
  return Math.floor(Math.min(...all) / 20) * 20 - 20
})

const elevMax = computed(() => {
  const all = props.section.levels.map(l => l.value)
  all.push(props.section.currentLevel)
  all.push(props.section.dam.crestElevation)
  return Math.ceil(Math.max(...all) / 20) * 20 + 20
})

const ELEV_RANGE = computed(() => elevMax.value - elevMin.value)

/** 高程 → SVG Y 坐标 (image 坐标系 0~940) */
const toY = (e: number) => ((elevMax.value - e) / ELEV_RANGE.value) * 940

/** 当前水位 Y 坐标 */
const waterY = computed(() => toY(props.section.currentLevel))

// ========== 高程刻度 ==========
const elevationTicks = computed(() => {
  const step = 20
  const ticks: { elev: number; y: number }[] = []
  for (let e = elevMin.value; e <= elevMax.value; e += step) {
    ticks.push({ elev: e, y: toY(e) })
  }
  return ticks
})

// ========== 特征水位线 ==========
interface LevelLine {
  name: string
  value: number
  color: string
  y: number
  isCurrent: boolean
}

const levelLines = computed<LevelLine[]>(() => {
  const lines: LevelLine[] = props.section.levels.map(lv => ({
    name: lv.name,
    value: lv.value,
    color: lv.color,
    y: toY(lv.value),
    isCurrent: false,
  }))
  lines.push({
    name: '当前水位',
    value: props.section.currentLevel,
    color: '#00AFFF',
    y: toY(props.section.currentLevel),
    isCurrent: true,
  })
  return lines.sort((a, b) => b.value - a.value)
})

// ========== 库区水体裁剪路径 (clipPath) ==========
// 注意: 水体层在 PNG 下方 (z-index:1), PNG 会遮挡多余水体,
// 所以 clipPath 需比地形更宽, 确保水体填满山体透明区域
const TERRAIN_BOTTOM = 875
const reservoirClipPath = computed(() => {
  // 左岸线 (从坝顶左侧到河床底部, 向外扩展贴合山体)
  const leftPoints = [
    { x: 20,  y: toY(props.section.dam.crestElevation) - 50 },
    { x: 80,  y: toY(props.section.dam.crestElevation) + 10 },
    { x: 180, y: toY(elevMin.value + 80) },
    { x: 320, y: toY(elevMin.value + 50) },
    { x: 480, y: toY(elevMin.value + 20) },
    { x: 660, y: TERRAIN_BOTTOM },
  ]
  // 右岸线 (河床底部到坝顶右侧)
  const rightPoints = [
    { x: 1030, y: TERRAIN_BOTTOM },
    { x: 1120, y: toY(elevMin.value + 20) },
    { x: 1220, y: toY(elevMin.value + 50) },
    { x: 1320, y: toY(props.section.dam.crestElevation) + 10 },
    { x: 1380, y: toY(props.section.dam.crestElevation) - 50 },
  ]

  let d = `M ${leftPoints[0].x.toFixed(1)} ${leftPoints[0].y.toFixed(1)}`

  // 左岸
  for (let i = 1; i < leftPoints.length; i++) {
    const prev = leftPoints[i - 1]
    const p = leftPoints[i]
    d += ` C ${(prev.x + (p.x - prev.x) * 0.4).toFixed(1)} ${(prev.y + 8).toFixed(1)},`
    d += ` ${(prev.x + (p.x - prev.x) * 0.6).toFixed(1)} ${p.y.toFixed(1)},`
    d += ` ${p.x.toFixed(1)} ${p.y.toFixed(1)}`
  }

  // 河床底部连线
  d += ` L ${rightPoints[0].x.toFixed(1)} ${rightPoints[0].y.toFixed(1)}`

  // 右岸
  for (let i = 1; i < rightPoints.length; i++) {
    const prev = rightPoints[i - 1]
    const p = rightPoints[i]
    d += ` C ${(prev.x + (p.x - prev.x) * 0.4).toFixed(1)} ${prev.y.toFixed(1)},`
    d += ` ${(prev.x + (p.x - prev.x) * 0.6).toFixed(1)} ${(p.y + 8).toFixed(1)},`
    d += ` ${p.x.toFixed(1)} ${p.y.toFixed(1)}`
  }

  // 上方闭合
  d += ` L ${leftPoints[0].x.toFixed(1)} ${leftPoints[0].y.toFixed(1)} Z`
  return d
})

// ========== 水面波动纹理 ==========
const wavePath1 = computed(() => {
  const wy = waterY.value
  const baseY = Math.min(wy + 6, 930)
  return `M 200 ${baseY} Q 260 ${baseY - 4} 320 ${baseY} T 440 ${baseY} T 560 ${baseY}`
})
const wavePath2 = computed(() => {
  const wy = waterY.value
  const baseY = Math.min(wy + 14, 930)
  return `M 250 ${baseY} Q 310 ${baseY - 3} 370 ${baseY} T 490 ${baseY}`
})
</script>

<template>
  <div class="section-graph">
    <PanelCard :title="section.title">
      <div class="graph-wrap">
        <!-- ===== 水体层 (z-index: 1) ===== -->
        <svg
          class="layer water-layer"
          :viewBox="`0 0 1672 940`"
          preserveAspectRatio="xMidYMid slice"
        >
          <defs>
            <clipPath id="reservoirClip">
              <path :d="reservoirClipPath" />
            </clipPath>

            <!-- 水体渐变 -->
            <linearGradient id="waterGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%"   stop-color="rgba(0, 160, 255, 0.60)" />
              <stop offset="40%"  stop-color="rgba(0, 110, 230, 0.55)" />
              <stop offset="100%" stop-color="rgba(0, 50, 160, 0.70)" />
            </linearGradient>

            <!-- 水底渐变 -->
            <linearGradient id="deepGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%"   stop-color="rgba(0, 60, 180, 0.20)" />
              <stop offset="100%" stop-color="rgba(0, 20, 80, 0.40)" />
            </linearGradient>
          </defs>
          <rect
            x="0"
            :y="Math.max(0, waterY)"
            width="1672"
            :height="TERRAIN_BOTTOM - Math.max(0, waterY)"
            fill="url(#waterGrad)"
            clip-path="url(#reservoirClip)"
          />

          <!-- 水底深度渐变 -->
          <rect
            x="0"
            :y="Math.max(0, waterY)"
            width="1672"
            :height="TERRAIN_BOTTOM - Math.max(0, waterY)"
            fill="url(#deepGrad)"
            clip-path="url(#reservoirClip)"
          />

          <!-- 表面波纹 -->
          <path
            v-if="waterY > 10"
            :d="wavePath1"
            fill="none"
            stroke="rgba(255,255,255,0.20)"
            stroke-width="2"
            clip-path="url(#reservoirClip)"
          />
          <path
            v-if="waterY > 20"
            :d="wavePath2"
            fill="none"
            stroke="rgba(255,255,255,0.12)"
            stroke-width="1.5"
            clip-path="url(#reservoirClip)"
          />
        </svg>

        <!-- ===== 静态断面背景图 (z-index: 2) ===== -->
        <img
          src="/map/section-bg.png"
          class="layer section-bg"
          alt="水库断面"
        />

        <!-- ===== 标注层 (z-index: 3) ===== -->
        <svg
          class="layer label-layer"
          :viewBox="`0 0 1672 940`"
          preserveAspectRatio="xMidYMid slice"
        >
          <defs>
            <!-- 水位线发光 -->
            <filter id="levelGlow" x="-20%" y="-30%" width="140%" height="160%">
              <feGaussianBlur stdDeviation="2.5" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <filter id="currentGlow" x="-30%" y="-50%" width="160%" height="200%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          <!-- ---- 高程坐标轴 ---- -->
          <g class="axis-group">
            <!-- 轴主线 -->
            <line
              x1="55" y1="20" x2="55" y2="920"
              stroke="rgba(50,150,255,0.45)" stroke-width="2.5"
            />
            <text
              x="48" y="14" fill="#5a7a9a" font-size="22"
              text-anchor="end" font-weight="600"
            >高程(m)</text>

            <template v-for="tk in elevationTicks" :key="'tk-' + tk.elev">
              <!-- 横向虚线对齐线 (贯穿整个图表区) -->
              <line
                :x1="55" :y1="tk.y" :x2="1670" :y2="tk.y"
                stroke="rgba(50,150,255,0.15)" stroke-width="2"
                stroke-dasharray="6,5"
              />
              <!-- 刻度线 -->
              <line
                :x1="43" :y1="tk.y" :x2="55" :y2="tk.y"
                stroke="rgba(50,150,255,0.45)" stroke-width="2.5"
              />
              <!-- 刻度标签 -->
              <text
                :x="40" :y="tk.y + 7"
                fill="#5a7a9a" font-size="20" text-anchor="end"
                font-family="'DIN Alternate', 'Roboto Mono', monospace"
              >{{ tk.elev }}</text>
            </template>
          </g>

          <!-- ---- 当前水位高亮带 ---- -->
          <rect
            :x="55"
            :y="waterY - 4"
            width="1280"
            height="8"
            fill="url(#currentGlowGrad)"
            rx="2"
            opacity="0.9"
          />
          <defs>
            <linearGradient id="currentGlowGrad" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%"   stop-color="rgba(0, 175, 255, 0)" />
              <stop offset="15%"  stop-color="rgba(0, 175, 255, 0.20)" />
              <stop offset="50%"  stop-color="rgba(0, 175, 255, 0.35)" />
              <stop offset="85%"  stop-color="rgba(0, 175, 255, 0.20)" />
              <stop offset="100%" stop-color="rgba(0, 175, 255, 0)" />
            </linearGradient>
          </defs>

          <!-- ---- 特征水位线 ---- -->
          <g
            v-for="lv in levelLines"
            :key="lv.name"
            class="level-line-group"
          >
            <!-- 水位线从左侧刻度贯穿到右侧数值 -->
            <line
              :x1="55" :y1="lv.y" :x2="1560" :y2="lv.y"
              :stroke="lv.color"
              :stroke-width="lv.isCurrent ? 1 : 1"
              :stroke-dasharray="lv.isCurrent ? 'none' : '12,6'"
              :filter="lv.isCurrent ? 'url(#currentGlow)' : 'none'"
              opacity="1"
            />
            <!-- 左侧标签 -->
            <text
              :x="60" :y="lv.y - 12"
              :fill="lv.color"
              font-size="20"
              font-weight="600"
              opacity="0.95"
            >{{ lv.name }}</text>
            <!-- 右侧数值 -->
            <text
              :x="1555" :y="lv.y - 12"
              :fill="lv.color"
              font-size="20"
              text-anchor="end"
              :font-weight="lv.isCurrent ? 700 : 500"
              font-family="'DIN Alternate', 'Roboto Mono', monospace"
            >{{ lv.value.toFixed(2) }} m</text>
          </g>

          <!-- ---- 坝顶标注 ---- -->
          <g class="dam-label">
            <line
              :x1="1295" :y1="toY(section.dam.crestElevation)"
              :x2="1360" :y2="toY(section.dam.crestElevation)"
              stroke="rgba(150,180,210,0.50)" stroke-width="2"
            />
            <text
              :x="1350" :y="toY(section.dam.crestElevation) - 10"
              fill="#94A3B8" font-size="17" text-anchor="end" font-weight="600"
            >坝顶 {{ section.dam.crestElevation.toFixed(2) }}m</text>
          </g>

          <!-- ---- 入库流量 (仅数值, 无箭头) ---- -->
          <g class="flow-indicator inflow">
            <rect
              :x="110" :y="52"
              width="120" height="36" rx="6"
              fill="rgba(6,30,70,0.85)"
              stroke="rgba(0,229,255,0.30)"
              stroke-width="1"
            />
            <text
              :x="170" :y="76"
              fill="#00E5FF" font-size="20" text-anchor="middle" font-weight="600"
              font-family="'DIN Alternate', 'Roboto Mono', monospace"
            >{{ section.inflow }} m³/s</text>
            <text
              :x="170" :y="43"
              fill="#5a8aaa" font-size="17" text-anchor="middle"
            >入库流量</text>
          </g>

          <!-- ---- 出库流量 (仅数值, 无箭头) ---- -->
          <g class="flow-indicator outflow">
            <rect
              :x="1470" :y="52"
              width="120" height="36" rx="6"
              fill="rgba(6,30,70,0.85)"
              stroke="rgba(0,212,255,0.30)"
              stroke-width="1"
            />
            <text
              :x="1530" :y="76"
              fill="#00d4ff" font-size="20" text-anchor="middle" font-weight="600"
              font-family="'DIN Alternate', 'Roboto Mono', monospace"
            >{{ section.outflow }} m³/s</text>
            <text
              :x="1530" :y="43"
              fill="#5a8aaa" font-size="17" text-anchor="middle"
            >出库流量</text>
          </g>
        </svg>
      </div>

      <!-- 底部工程参数栏 -->
      <div class="params-bar">
        <div class="param-item">
          <span class="param-icon">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <rect x="1" y="1" width="12" height="12" rx="2" stroke="#00AFFF" stroke-width="1.2"/>
              <path d="M1 7h12" stroke="#00AFFF" stroke-width="1.2"/>
            </svg>
          </span>
          <span class="param-label">坝型</span>
          <span class="param-value">{{ section.dam.type }}</span>
        </div>
        <div class="param-divider"></div>
        <div class="param-item">
          <span class="param-label">坝顶高程</span>
          <span class="param-value">{{ section.dam.crestElevation.toFixed(2) }} m</span>
        </div>
        <div class="param-divider"></div>
        <div class="param-item">
          <span class="param-label">坝顶长度</span>
          <span class="param-value">{{ section.dam.crestLength.toFixed(2) }} m</span>
        </div>
        <div class="param-divider"></div>
        <div class="param-item">
          <span class="param-label">最大坝高</span>
          <span class="param-value">{{ section.dam.maxHeight.toFixed(2) }} m</span>
        </div>
      </div>
    </PanelCard>
  </div>
</template>

<style scoped>
.section-graph {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.graph-wrap {
  position: relative;
  width: 95%;
  max-width: 1600px;
  aspect-ratio: 1672 / 940;
  background: #061a3a;
  overflow: hidden;
  border-radius: 6px;
  flex-shrink: 0;
  margin: 0 auto;
}

/* 所有图层共用定位 */
.layer {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

/* 水体层 */
.water-layer {
  z-index: 1;
}

/* 静态断面图：向右偏移，避免与左侧刻度重叠 */
.section-bg {
  z-index: 2;
  left: 38px;
  width: calc(100% - 100px);
  object-fit: fill;
}

/* 标注层 */
.label-layer {
  z-index: 3;
}

/* 底部参数栏 */
.params-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 16px;
  margin-top: 10px;
  background: rgba(0, 175, 255, 0.05);
  border: 1px solid rgba(50, 150, 255, 0.2);
  border-radius: 8px;
  flex-shrink: 0;
  overflow-x: auto;
}

.param-item {
  display: flex;
  align-items: baseline;
  gap: 6px;
  white-space: nowrap;
}

.param-icon {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.param-label {
  font-size: 11px;
  color: #7a8fa3;
}

.param-value {
  font-size: 13px;
  font-weight: 600;
  color: #00d4ff;
  font-family: 'DIN Alternate', 'Roboto Mono', monospace;
}

.param-divider {
  width: 1px;
  height: 16px;
  background: rgba(50, 150, 255, 0.2);
  flex-shrink: 0;
}
</style>