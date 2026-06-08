<script setup lang="ts">
import { announcement, weatherInfo } from '@/mock/home'

const announcementData = announcement.data
const weatherData = weatherInfo.data
</script>

<template>
  <div class="footer-bar"
    style="background: rgba(6, 30, 70, 0.85); border-top: 1px solid rgba(50, 150, 255, 0.25); backdrop-filter: blur(6px);">
    <!-- 通知公告 -->
    <div class="footer-section announcement-section">
      <span class="footer-label">通知公告</span>
      <div class="announcement-content">
        <span class="announcement-text">{{ announcementData.content }}</span>
      </div>
    </div>

    <!-- 天气 -->
    <div class="footer-section weather-section">
      <span class="footer-label">{{ weatherData.city }}</span>
      <span class="weather-info">{{ weatherData.weather }} {{ weatherData.temperature }} {{ weatherData.wind }}</span>
    </div>

    <!-- 退出系统 -->
    <div class="footer-section exit-section">
      <button class="exit-btn">退出系统</button>
    </div>
  </div>
</template>

<style scoped>
.footer-bar {
  display: flex;
  align-items: center;
  height: 36px;
  padding: 0 16px;
  gap: 24px;
}

.footer-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

.announcement-section {
  flex: 1;
  overflow: hidden;
}

.footer-label {
  font-size: 12px;
  color: #7a8fa3;
  white-space: nowrap;
}

.announcement-content {
  flex: 1;
  overflow: hidden;
}

.announcement-text {
  font-size: 12px;
  color: #c0c8d4;
  display: inline-block;
  white-space: nowrap;
  animation: scroll-text 20s linear infinite;
}

@keyframes scroll-text {
  0% { transform: translateX(100%); }
  100% { transform: translateX(-100%); }
}

.weather-info {
  font-size: 12px;
  color: #c0c8d4;
}

.exit-btn {
  background: none;
  border: 1px solid rgba(50, 150, 255, 0.3);
  color: #7a8fa3;
  font-size: 12px;
  padding: 2px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.exit-btn:hover {
  border-color: #ff4d4f;
  color: #ff4d4f;
}
</style>
