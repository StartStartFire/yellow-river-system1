<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { leafletLayer, LineSymbolizer } from 'protomaps-leaflet'
import { reservoirPoints, mapLayers } from '@/mock/home'

const pointsData = reservoirPoints.data
const layersData = mapLayers.data

const mapContainer = ref<HTMLDivElement | null>(null)
let map: L.Map | null = null
let markerGroup: L.LayerGroup | null = null
let riverLayer: ReturnType<typeof leafletLayer> | null = null
const activeLayers = ref<Record<string, boolean>>({})
const layerControlOpen = ref(false)

const props = defineProps<{
  selectedId: string | null
}>()

const emit = defineEmits<{
  (e: 'select-reservoir', id: string): void
  (e: 'clear-selected'): void
}>()

// 初始化图层状态
layersData.forEach((layer) => {
  activeLayers.value[layer.id] = layer.visible
})

const initMap = () => {
  if (!mapContainer.value) return

  // 确保容器有尺寸
  const rect = mapContainer.value.getBoundingClientRect()
  if (rect.width === 0 || rect.height === 0) {
    // 容器还没渲染完成，稍后重试
    setTimeout(() => initMap(), 100)
    return
  }

  if (map) {
    map.remove()
    map = null
  }

  map = L.map(mapContainer.value, {
    center: [36.2, 102.8],
    zoom: 7,
    zoomControl: false,
    attributionControl: false,
  })

  // Esri 卫星影像
  L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    {
      maxZoom: 18,
      attribution: 'Esri',
    }
  ).addTo(map)

  // 叠加地名标签
  L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
    {
      maxZoom: 18,
      opacity: 0.5,
    }
  ).addTo(map)

  // 黄河河网 PMTiles 矢量瓦片
  riverLayer = leafletLayer({
    url: '/static/river_network.pmtiles',
    paintRules: [
      {
        dataLayer: 'rivers',
        symbolizer: new LineSymbolizer({
          color: 'rgba(0, 180, 255, 0.7)',
          width: 1.2,
        }),
      },
    ],
  })
  riverLayer.addTo(map)

  addReservoirMarkers()

  // 根据当前图层状态初始化显隐
  if (!activeLayers.value['reservoir'] && markerGroup) {
    map.removeLayer(markerGroup)
  }
  if (!activeLayers.value['river'] && riverLayer) {
    map.removeLayer(riverLayer)
  }

  // 强制地图重新计算大小
  setTimeout(() => {
    map?.invalidateSize()
  }, 200)
}

const addReservoirMarkers = () => {
  if (!map) return
  if (markerGroup) {
    map.removeLayer(markerGroup)
  }
  markerGroup = L.layerGroup()

  pointsData.forEach((point) => {
    const icon = L.divIcon({
      className: 'reservoir-marker',
      html: `
        <div class="marker-pulse ${point.status}"></div>
        <div class="marker-outer ${point.status}"></div>
        <div class="marker-inner ${point.status}"></div>
        <div class="marker-label-text">${point.name}</div>
      `,
      iconSize: [100, 50],
      iconAnchor: [50, 25],
    })

    const marker = L.marker([point.lat, point.lng], { icon })
    marker.on('click', () => {
      if (!map) return

      emit('select-reservoir', point.id)
      // 直接弹出水库信息窗口
      map.closePopup()
      const popupContent = `
        <div class="map-popup">
          <div class="popup-header">${point.name}</div>
          <div class="popup-body">
            <div class="popup-row"><span>坝前水位</span><span>${point.waterLevel} m</span></div>
            <div class="popup-row"><span>尾水位</span><span>${point.tailwaterLevel} m</span></div>
            <div class="popup-row"><span>库容</span><span>${point.storage} 亿m³</span></div>
            <div class="popup-row"><span>库容率</span><span>${point.storageRate}%</span></div>
            <div class="popup-row"><span>入库流量</span><span>${point.inflow} m³/s</span></div>
            <div class="popup-row"><span>出库流量</span><span>${point.outflow} m³/s</span></div>
            <div class="popup-row"><span>机组过流</span><span>${point.turbineFlow} m³/s</span></div>
            <div class="popup-row"><span>更新时间</span><span>${point.updateTime}</span></div>
          </div>
        </div>
      `
      L.popup({
        className: 'reservoir-popup',
        closeButton: true,
        closeOnClick: false,
        offset: [0, -20],
      })
        .setLatLng([point.lat, point.lng])
        .setContent(popupContent)
        .openOn(map)
      map.flyTo([point.lat, point.lng], 9, { duration: 1 })
    })
    marker.addTo(markerGroup!)
  })
  markerGroup!.addTo(map)
}

// 从左侧面板选中水库时弹出 popup
watch(
  () => props.selectedId,
  (id) => {
    if (!map || !id) return
    const point = pointsData.find((p) => p.id === id)
    if (!point) return

    map.closePopup()

    const popupContent = `
      <div class="map-popup">
        <div class="popup-header">${point.name}</div>
        <div class="popup-body">
          <div class="popup-row"><span>坝前水位</span><span>${point.waterLevel} m</span></div>
          <div class="popup-row"><span>尾水位</span><span>${point.tailwaterLevel} m</span></div>
          <div class="popup-row"><span>库容</span><span>${point.storage} 亿m³</span></div>
          <div class="popup-row"><span>库容率</span><span>${point.storageRate}%</span></div>
          <div class="popup-row"><span>入库流量</span><span>${point.inflow} m³/s</span></div>
          <div class="popup-row"><span>出库流量</span><span>${point.outflow} m³/s</span></div>
          <div class="popup-row"><span>机组过流</span><span>${point.turbineFlow} m³/s</span></div>
          <div class="popup-row"><span>更新时间</span><span>${point.updateTime}</span></div>
        </div>
      </div>
    `

    L.popup({
      className: 'reservoir-popup',
      closeButton: true,
      closeOnClick: false,
      offset: [0, -20],
    })
      .setLatLng([point.lat, point.lng])
      .setContent(popupContent)
      .openOn(map)

    // 飞到选中水库
    map.flyTo([point.lat, point.lng], 9, { duration: 1 })
  }
)

const handleZoomIn = () => map?.zoomIn()
const handleZoomOut = () => map?.zoomOut()
const handleReset = () => map?.setView([36.2, 102.8], 7)

const toggleLayer = (id: string) => {
  activeLayers.value[id] = !activeLayers.value[id]
  const visible = activeLayers.value[id]

  if (!map) return

  if (id === 'reservoir') {
    if (visible && markerGroup && !map.hasLayer(markerGroup)) {
      markerGroup.addTo(map)
    } else if (!visible && markerGroup && map.hasLayer(markerGroup)) {
      map.removeLayer(markerGroup)
    }
  } else if (id === 'river') {
    if (visible && riverLayer && !map.hasLayer(riverLayer)) {
      riverLayer.addTo(map)
    } else if (!visible && riverLayer && map.hasLayer(riverLayer)) {
      map.removeLayer(riverLayer)
    }
  }
}

onMounted(() => {
  // 先等 DOM 彻底渲染
  setTimeout(() => initMap(), 300)
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<template>
  <div class="map-panel">
    <div
      class="map-header"
      style="background: rgba(6, 30, 70, 0.85); border: 1px solid rgba(50, 150, 255, 0.35); border-radius: 12px 12px 0 0; border-bottom: 1px solid rgba(50, 150, 255, 0.2);"
    >
      <div class="map-header-inner">
        <span class="map-title">黄河上游流域地图</span>
      </div>
    </div>
    <div class="map-body">
      <div ref="mapContainer" class="map-container"></div>

      <!-- 图层控制 -->
      <div
        class="layer-control"
        style="background: rgba(6, 30, 70, 0.9); border: 1px solid rgba(50, 150, 255, 0.3); border-radius: 8px;"
      >
        <div
          class="layer-control-header"
          @click="layerControlOpen = !layerControlOpen"
        >
          <span class="text-xs font-medium text-tech-text">图层控制</span>
          <span class="layer-toggle-icon" :class="{ rotated: layerControlOpen }">▶</span>
        </div>
        <div v-show="layerControlOpen" class="layer-control-body">
          <div v-for="layer in layersData" :key="layer.id" class="flex items-center justify-between py-0.5">
            <span class="text-xs text-tech-muted">{{ layer.name }}</span>
            <input
              type="checkbox"
              :checked="activeLayers[layer.id]"
              @change="toggleLayer(layer.id)"
              class="layer-toggle"
            />
          </div>
        </div>
      </div>

      <!-- 工具栏 -->
      <div
        class="map-toolbar"
        style="background: rgba(6, 30, 70, 0.9); border: 1px solid rgba(50, 150, 255, 0.3); border-radius: 8px;"
      >
        <button @click="handleReset" class="toolbar-btn">全域</button>
        <button class="toolbar-btn">上游</button>
        <button class="toolbar-btn">中游</button>
        <button class="toolbar-btn">下游</button>
        <span class="toolbar-divider"></span>
        <button @click="handleZoomIn" class="toolbar-btn">缩放+</button>
        <button @click="handleZoomOut" class="toolbar-btn">缩放-</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.map-panel {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  min-height: 0;
}

.map-header {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  flex-shrink: 0;
}

.map-header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.map-title {
  font-size: 14px;
  font-weight: 600;
  color: #e0e6ed;
  letter-spacing: 0.5px;
}

.map-body {
  position: relative;
  flex: 1;
  min-height: 0;
  border-left: 1px solid rgba(50, 150, 255, 0.35);
  border-right: 1px solid rgba(50, 150, 255, 0.35);
  border-bottom: 1px solid rgba(50, 150, 255, 0.35);
  border-radius: 0 0 12px 12px;
  overflow: hidden;
}

.map-container {
  width: 100%;
  height: 100%;
  min-height: 200px;
}

/* 图层控制 */
.layer-control {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 1000;
  padding: 12px;
  min-width: 100px;
}

.layer-toggle {
  accent-color: #00afff;
}

.layer-control-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
}

.layer-control-header:hover {
  opacity: 0.8;
}

.layer-toggle-icon {
  font-size: 10px;
  color: #00afff;
  transition: transform 0.25s ease;
  line-height: 1;
}

.layer-toggle-icon.rotated {
  transform: rotate(90deg);
}

.layer-control-body {
  margin-top: 8px;
}

/* 工具栏 */
.map-toolbar {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
}

.toolbar-btn {
  background: none;
  border: none;
  color: #c0c8d4;
  font-size: 12px;
  padding: 4px 10px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.toolbar-btn:hover {
  background: rgba(0, 175, 255, 0.15);
  color: #00d4ff;
}

.toolbar-divider {
  width: 1px;
  height: 16px;
  background: rgba(50, 150, 255, 0.3);
  margin: 0 4px;
}
</style>

<style>
/* 水库 marker 全局样式 */
.reservoir-marker {
  background: none !important;
  border: none !important;
}

.marker-pulse {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(0, 175, 255, 0.2);
  animation: markerPulse 2s ease-in-out infinite;
  pointer-events: none;
}

.marker-pulse.warning {
  background: rgba(255, 170, 0, 0.2);
}

.marker-pulse.abnormal {
  background: rgba(255, 77, 79, 0.2);
}

.marker-outer {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(0, 175, 255, 0.3);
  border: 2px solid rgba(0, 229, 255, 0.6);
  pointer-events: none;
}

.marker-outer.warning {
  background: rgba(255, 170, 0, 0.3);
  border-color: rgba(255, 204, 51, 0.6);
}

.marker-outer.abnormal {
  background: rgba(255, 77, 79, 0.3);
  border-color: rgba(255, 120, 117, 0.6);
}

.marker-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #00afff;
  box-shadow: 0 0 8px rgba(0, 175, 255, 0.8);
  pointer-events: none;
}

.marker-inner.warning {
  background: #ffaa00;
  box-shadow: 0 0 8px rgba(255, 170, 0, 0.8);
}

.marker-inner.abnormal {
  background: #ff4d4f;
  box-shadow: 0 0 8px rgba(255, 77, 79, 0.8);
}

@keyframes markerPulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.6;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.4);
    opacity: 0.2;
  }
}

.marker-label-text {
  position: absolute;
  bottom: -18px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 11px;
  color: #fff;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.9), 0 0 8px rgba(0, 0, 0, 0.6);
  white-space: nowrap;
  font-weight: 500;
  pointer-events: none;
}

/* Leaflet popup 深色主题 */
.reservoir-popup .leaflet-popup-content-wrapper {
  background: rgba(6, 30, 70, 0.95);
  border: 1px solid rgba(0, 170, 255, 0.4);
  border-radius: 8px;
  backdrop-filter: blur(6px);
  color: #e0e6ed;
  box-shadow: 0 0 20px rgba(0, 160, 255, 0.2);
}

.reservoir-popup .leaflet-popup-content {
  margin: 10px 14px;
  min-width: 200px;
}

.reservoir-popup .leaflet-popup-tip {
  background: rgba(6, 30, 70, 0.95);
  border: 1px solid rgba(0, 170, 255, 0.4);
}

.reservoir-popup .leaflet-popup-close-button {
  color: #7a8fa3 !important;
  font-size: 18px !important;
  top: 6px !important;
  right: 6px !important;
}

.reservoir-popup .leaflet-popup-close-button:hover {
  color: #e0e6ed !important;
}

.map-popup .popup-header {
  font-size: 14px;
  font-weight: 600;
  color: #00d4ff;
  padding-bottom: 8px;
  margin-bottom: 8px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.25);
}

.map-popup .popup-row {
  display: flex;
  justify-content: space-between;
  padding: 2px 0;
  font-size: 12px;
}

.map-popup .popup-row span:first-child {
  color: #7a8fa3;
}

.map-popup .popup-row span:last-child {
  color: #00d4ff;
  font-family: 'DIN Alternate', 'Roboto Mono', monospace;
}
</style>