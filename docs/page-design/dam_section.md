# 一、页面分层思路

建议页面里分成 4 层：

```text
1. 最底层：页面背景（深色底）
2. 第二层：动态水体层（蓝色水面，随水位变化）
3. 第三层：静态断面背景图（山体 + 坝体 + 库底轮廓，透明背景）
4. 最上层：标注层（当前水位线、特征水位线、文字、箭头）
```

也就是：

```text
页面容器
├─ 背景层
├─ 水体层（动态）
├─ 断面静态图层（你的透明 PNG / SVG）
└─ 标注图层（SVG）
```

------

# 二、为什么不能直接放一个蓝色矩形？

如果你直接在下面放一个蓝色 `div`，会有两个问题：

## 问题 1：水会出现在不该出现的地方

比如山坡上方、坝外侧、天空区域，都可能被蓝色矩形盖住。

## 问题 2：水面边界不自然

你想要的是“库区里的水位上涨/下降”，而不是一个纯矩形进度条。

------

# 三、正确做法：给水体加一个“裁剪区域”

最推荐的是：

## 方案 A：SVG + clipPath（推荐）

用一个 SVG 路径定义“库区可蓄水范围”，然后让蓝色水体只在这个范围里显示。

也就是：

- **静态断面图**：负责展示山体和坝体
- **水体遮罩路径**：负责定义“水能出现的范围”
- **蓝色矩形**：负责通过高度变化模拟水位

------

# 四、实现原理

假设你有：

- 最低高程：`2380`
- 最高高程：`2520`
- 当前水位：`2467.35`

你先把“真实高程”换算成“页面中的 Y 坐标”：

```ts
function levelToY(level: number, minLevel: number, maxLevel: number, chartHeight: number) {
  return chartHeight - ((level - minLevel) / (maxLevel - minLevel)) * chartHeight
}
```

比如：

```ts
const y = levelToY(2467.35, 2380, 2520, 400)
```

然后把蓝色水体矩形的：

- `y = 当前水位对应像素位置`
- `height = 底部高度 - y`

这样水面就会上下变化。

------

# 五、推荐结构（最实用）

如果你用 Vue 页面，可以这样组织：

```html
<div class="section-wrap">
  <!-- 水体层 -->
  <svg class="water-layer" viewBox="0 0 1600 500">
    <defs>
      <clipPath id="reservoirClip">
        <!-- 这个 path 定义库区可蓄水区域 -->
        <path d="M 120 160 
                 L 220 190
                 L 340 260
                 L 520 360
                 L 980 360
                 L 1120 300
                 L 1180 240
                 L 1180 360
                 L 120 360 Z" />
      </clipPath>
    </defs>

    <!-- 水体 -->
    <rect
      x="0"
      :y="waterY"
      width="1600"
      :height="500 - waterY"
      clip-path="url(#reservoirClip)"
      fill="rgba(40,140,255,0.65)"
    />
  </svg>

  <!-- 静态断面图 -->
  <img src="/images/reservoir-section-bg.png" class="section-bg" />

  <!-- 标注层 -->
  <svg class="label-layer" viewBox="0 0 1600 500">
    <line :y1="waterY" :y2="waterY" x1="120" x2="1180" stroke="#4da3ff" />
    <text x="130" :y="waterY - 8">当前水位 2467.35 m</text>
  </svg>
</div>
```

------

# 六、CSS 层级

```css
.section-wrap {
  position: relative;
  width: 100%;
  height: 500px;
  background: #061a3a;
  overflow: hidden;
}

.water-layer,
.label-layer,
.section-bg {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
}

.water-layer {
  z-index: 1;
}

.section-bg {
  z-index: 2;
  pointer-events: none;
}

.label-layer {
  z-index: 3;
  pointer-events: none;
}
```

------

# 七、你现在这张静态图在项目里怎么用？

你现在手上这张图：

- 山体是实心的
- 坝体是实心的
- 其他区域是透明的

这很好，它适合做**前景遮罩层**。

## 用法就是：

### 1）下面放蓝色动态水体

### 2）上面盖你的透明断面图

这样水就会看起来“在山体之间”。

但是还差一步：

## 你还需要一个“库区裁剪路径”

否则蓝色水可能会跑到不该显示的地方。

------

# 八、最简版本怎么做？

如果你现在只是想先把页面跑通，不追求很精细，可以先用：

## 简化版方案

- 水体先用一个蓝色矩形
- 手动控制它的：
  - left
  - width
  - top / height
- 然后把透明静态图盖上去

比如：

```html
<div class="section-wrap">
  <div class="water" :style="{ top: waterTop + 'px' }"></div>
  <img src="/images/section-bg.png" class="section-bg" />
</div>
.water {
  position: absolute;
  left: 130px;
  width: 980px;
  bottom: 60px;
  background: linear-gradient(to bottom, rgba(70,160,255,.8), rgba(20,90,200,.55));
  z-index: 1;
}
```

这种做法：

- 简单
- 快速
- 适合 mock 阶段

但缺点是：

- 水面边界不够精确
- 只能近似模拟

------

# 九、最终推荐方案

我建议你分两步走：

## 第一步：先做可跑通版

用：

- 透明静态断面图
- 一个蓝色水体矩形
- 一个当前水位线

先把交互跑通。

------

## 第二步：再升级成精细版

再补一个：

- `reservoir-mask.svg`
  或者
- `clipPath` 路径

让水严格限制在库区内部。

------

# 十、你现在最需要补的资源

为了让效果更好，我建议你再准备一个：

## **库区水体裁剪轮廓**

它不需要很复杂，只要是一条闭合路径，表示：

> 从左岸接触点 → 沿当前库底轮廓 → 到坝前边界 → 再封闭回去

文件名可以叫：

```text
reservoir-water-mask.svg
```

这个文件专门给水体裁剪用。

------

# 十一、最关键的一句话总结

你的这个断面图实现逻辑应该是：

> **透明静态断面图放上层，动态水体放下层，水体通过 SVG 的 clipPath 或 mask 限制在库区范围内，水位变化本质上就是调整蓝色水体的高度。**

