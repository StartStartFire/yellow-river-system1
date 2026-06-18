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

/** 高程 → SVG Y 坐标 (image 坐标系 0~654) */
const toY = (e: number) => ((elevMax.value - e) / ELEV_RANGE.value) * 654

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
// 水体仅在坝体上游侧（左侧）显示，坝面右侧为绝对边界。
const DAM_FACE_X = 1340
const TERRAIN_BOTTOM = 609
const reservoirClipPath = computed(() => {
  const crestY = toY(props.section.dam.crestElevation)
  const midLowY = toY(elevMin.value + 40)
  const bottomY = TERRAIN_BOTTOM + 30

  // 左岸沿山谷轮廓，右侧垂直切割在坝面
  const pts = [
    `M -80,${Math.max(0, crestY - 140).toFixed(1)}`,
    `L 40,${(crestY + 25).toFixed(1)}`,
    `L 180,${midLowY.toFixed(1)}`,
    `L 380,${toY(elevMin.value + 20).toFixed(1)}`,
    `L 660,${bottomY.toFixed(1)}`,
    // 河床底部到坝面位置
    `L ${DAM_FACE_X},${bottomY.toFixed(1)}`,
    // 垂直向上切割到坝顶（绝对边界，不让水体到下游）
    `L ${DAM_FACE_X},${Math.max(0, crestY - 140).toFixed(1)}`,
    'Z',
  ]
  return pts.join(' ')
})

// ========== 水面波动纹理 ==========
const wavePath1 = computed(() => {
  const wy = waterY.value
  const baseY = Math.min(wy + 6, 647)
  return `M 200 ${baseY} Q 260 ${baseY - 4} 320 ${baseY} T 440 ${baseY} T 560 ${baseY}`
})
const wavePath2 = computed(() => {
  const wy = waterY.value
  const baseY = Math.min(wy + 14, 647)
  return `M 250 ${baseY} Q 310 ${baseY - 3} 370 ${baseY} T 490 ${baseY}`
})
</script>

<template>
  <div class="section-graph">
    <PanelCard :title="section.title">
      <div class="graph-wrap">
        <!-- ===== 水体+背景共享容器：与 PNG 完全相同的位置和尺寸 ===== -->
        <div class="graph-visual">
          <!-- 水体层 (z-index: 1) -->
          <svg
            class="layer water-layer"
            :viewBox="`0 0 1672 654`"
            preserveAspectRatio="none"
          >
            <defs>
              <clipPath id="reservoirClip">
                <path :d="reservoirClipPath" />
              </clipPath>

              <linearGradient id="waterGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%"   stop-color="rgba(0, 160, 255, 0.60)" />
                <stop offset="40%"  stop-color="rgba(0, 110, 230, 0.55)" />
                <stop offset="100%" stop-color="rgba(0, 50, 160, 0.70)" />
              </linearGradient>

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
            <rect
              x="0"
              :y="Math.max(0, waterY)"
              width="1672"
              :height="TERRAIN_BOTTOM - Math.max(0, waterY)"
              fill="url(#deepGrad)"
              clip-path="url(#reservoirClip)"
            />
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

          <!-- 静态断面背景图 (z-index: 2) -->
          <img
            src="/map/section-bg.png"
            class="layer section-bg"
            alt="水库断面"
          />

          <!-- 标注层 (z-index: 3, 与水体/背景共享坐标空间) -->
          <svg
            class="layer label-layer"
            :viewBox="`0 0 1672 654`"
            preserveAspectRatio="none"
          >
          <defs>
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
            <line
              x1="0" y1="14" x2="0" y2="640"
              stroke="rgba(50,150,255,0.45)" stroke-width="4"
            />
            <template v-for="tk in elevationTicks" :key="'tk-' + tk.elev">
              <line
                :x1="0" :y1="tk.y" :x2="1670" :y2="tk.y"
                stroke="rgba(50,150,255,0.15)" stroke-width="2"
                stroke-dasharray="6,5"
              />
              <text
                :x="50" :y="tk.y + 5"
                fill="#5a7a9a" font-size="20" text-anchor="end"
                font-family="'DIN Alternate', 'Roboto Mono', monospace"
              >{{ tk.elev }}</text>
            </template>
          </g>

          <!-- ---- 当前水位高亮带 ---- -->
          <rect
            :x="55"
            :y="waterY - 3"
            width="1280"
            height="6"
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
            <line
              :x1="0" :y1="lv.y" :x2="1560" :y2="lv.y"
              :stroke="lv.color"
              :stroke-width="lv.isCurrent ? 3 : 2"
              :stroke-dasharray="lv.isCurrent ? 'none' : '12,6'"
              :filter="lv.isCurrent ? 'url(#currentGlow)' : 'none'"
              opacity="1"
            />
            <text
              :x="60" :y="lv.y - 8"
              :fill="lv.color"
              font-size="15" font-weight="550" opacity="0.95"
            >{{ lv.name }}</text>
            <text
              :x="1555" :y="lv.y - 8"
              :fill="lv.color"
              font-size="20" text-anchor="end"
              :font-weight="lv.isCurrent ? 700 : 500"
              font-family="'DIN Alternate', 'Roboto Mono', monospace"
            >{{ lv.value.toFixed(2) }} m</text>
          </g>

          <!-- ---- 坝顶标注（固定坐标，所有水库共用同一张 PNG，坝顶位置不变） ---- -->
          <g class="dam-label">
            <line
              x1="1295" y1="142" x2="1360" y2="142"
              stroke="rgba(150,180,210,0.50)" stroke-width="2"
            />
            <text
              x="1350" y="135"
              fill="#94A3B8" font-size="17" text-anchor="end" font-weight="600"
            >坝顶 {{ section.dam.crestElevation.toFixed(2) }}m</text>
          </g>

          <!-- ---- 入库流量 ---- -->
          <g class="flow-indicator inflow">
            <rect
              :x="110" :y="36"
              width="120" height="36" rx="6"
              fill="rgba(6,30,70,0.85)"
              stroke="rgba(0,229,255,0.30)" stroke-width="1"
            />
            <text
              :x="170" :y="53"
              fill="#00E5FF" font-size="20" text-anchor="middle" font-weight="600"
              font-family="'DIN Alternate', 'Roboto Mono', monospace"
            >{{ section.inflow }} m³/s</text>
            <text
              :x="170" :y="30"
              fill="#5a8aaa" font-size="17" text-anchor="middle"
            >入库流量</text>
          </g>

          <!-- ---- 出库流量 ---- -->
          <g class="flow-indicator outflow">
            <rect
              :x="1470" :y="36"
              width="120" height="36" rx="6"
              fill="rgba(6,30,70,0.85)"
              stroke="rgba(0,212,255,0.30)" stroke-width="1"
            />
            <text
              :x="1530" :y="53"
              fill="#00d4ff" font-size="20" text-anchor="middle" font-weight="600"
              font-family="'DIN Alternate', 'Roboto Mono', monospace"
            >{{ section.outflow }} m³/s</text>
            <text
              :x="1530" :y="30"
              fill="#5a8aaa" font-size="17" text-anchor="middle"
            >出库流量</text>
          </g>
        </svg>
        </div><!-- graph-visual end -->
      </div><!-- graph-wrap end -->

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
  width: 100%;
  max-width: 2200px;
  aspect-ratio: 1672 / 654;
  background: #061a3a;
  overflow: hidden;
  border-radius: 6px;
  flex-shrink: 0;
  margin: 0 auto;
}

/* 水体+背景共享容器：与 PNG 完全相同的位置和尺寸 */
.graph-visual {
  position: absolute;
  left: 38px;
  top: 0;
  width: calc(100% - 100px);
  height: 100%;
}

.graph-visual .layer {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.graph-visual .water-layer {
  z-index: 1;
}

.graph-visual .section-bg {
  z-index: 2;
  object-fit: fill;
}

.graph-visual .label-layer {
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
