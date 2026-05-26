---
name: scene-vocab-card
description: |
  为英语教材生成场景词汇卡海报。
  用户输入教材页面/截图/单词列表 → 输出一张主题海报（所有词汇标注在同一场景中）。
  输出：结构化 JSON（scene_label / scene_image_prompt / keywords / min_frames）+ 可选 PNG。
  触发词：场景词汇卡、scene vocab card、做场景卡、生成词汇场景、教材场景卡、做词汇海报
---

# 场景词汇卡生成器 (scene-vocab-card)

## 1. 概述

将英语教材内容转化为场景词汇卡海报：场景图 → 关键词标签 → 最小句子框架。所有目标词汇标注在同一张海报的连续场景中，输出结构化 JSON + 可选 PNG。

---

## 2. 输出格式

```json
{
  "title": "海报标题（用户提供，可中英文，渲染在图片顶部）",
  "scene_label": "具体可视化场景中文标签（前端展示，不进图）",
  "scene_image_prompt": "按五区结构生成的完整 prompt",
  "keywords": [
    {
      "en": "英文标签（进图）",
      "zh": "中文（前端展示，不进图）",
      "pos": "noun",
      "anchor_position": "top-left | top-center | top-right | middle-left | middle-right | bottom-left | bottom-center | bottom-right"
    }
  ],
  "min_frames": [
    { "en": "教材核心句型", "zh": "中文翻译" }
  ]
}
```

---

## 3. scene_image_prompt 五区结构

每区用空行分隔。

### 【标题区】（有 title 时）

```
Title banner at the very top of the image: a prominent horizontal banner with text "{title}", bold stylized font, warm-toned decorative background ribbon.
```

### 【内容区】

描述**单一连续场景**，按纵深层次组织：

1. **远景**：天空、建筑轮廓、氛围光影渐变
2. **中景**（上中景 + 下中景）：主要角色和核心活动、环境道具穿插
3. **前景**：近处角色和细节元素、近大远小强化纵深

**必须遵守：**
- **纵深透视**：前景→中景→远景空间层次，不可平面排列
- **方向性光影**：写明光源方向和投影效果（如 warm golden-hour sunlight streams from the lower right casting long dramatic shadows）
- **场景密度**：用环境道具填满画面（花篮、灯笼、遮阳棚、推车、盆栽、气球、彩旗等）
- **角色动态**：夸张肢体动作和丰富表情，避免呆板站立
- **禁止格子拼贴**：所有元素在同一连续空间中

### 【风格区】

插入 style_zone 文本，见 `references/style_zones.md`。

### 【标签区】

```
Label style: small rounded label with off-white background (#f5f0e8), warm dark brown text (#4a3728), sans-serif font (English bold), thin curved dark brown line (1-2px) connecting label to object.

Label list (English only):
- '{en}' → arrow points to [brief description]
...
```

### 【避免项】

```
No photorealistic rendering, no Chinese characters in labels (Chinese allowed only in title banner), no real brand logos, no frame borders, no watermark, no duplicate labels (each label word must appear exactly once), no misspellings, no random extra words, no irrelevant decorative text, no grid or collage layout (all elements must exist in one continuous scene).
```

### 硬约束

| # | 规则 |
|---|---|
| 1 | scene_label 必须是具体可视化场景（`课堂规则教室全景` ✓ / `课堂规则` ✗） |
| 2 | keywords 每条必须填 anchor_position，与内容区描述一致 |
| 3 | 图中标签只用英文。标题横幅可用中文。除标题外中文不进图 |
| 4 | min_frames 2-3 条，不超过 5 词，动词起头，来自教材核心句型 |
| 5 | IP 安全与可读性规则详见 `references/style_zones.md` 通用风格原则 |

### 骨架示例

```
[标题区] Title banner ... "Unit 1 Class Rules" ...

[内容区] A single continuous classroom scene with depth perspective: far background ... middle ground ... foreground ... Warm morning light ...

[风格区] modern educational illustration style, ... 9:16 portrait ratio ...

[标签区] Label style: ... Label list: - 'chalkboard' → ... - 'clock' → ...

[避免项] No photorealistic rendering, ...
```

---

## 4. 工作流

**输入形式**：教材 PDF 截图 / 教材照片 / 单词列表 + 主题

**可选参数**：

| 字段 | 说明 |
|---|---|
| `title` | 海报标题，渲染在图片顶部横幅，可中英文 |
| `style_zone` | 风格区，10 种预设或自定义，默认 `default`，详见 `references/style_zones.md` |

**预设风格（主动展示给用户）**：

| # | 标签 | 中文名 | 适合 |
|---|---|---|---|
| 1 | `default` | 现代教育插画 | 通用 |
| 2 | `watercolor` | 柔和水彩 | 自然/季节 |
| 3 | `hand_painted_anime` | 手绘动画风 | 故事/冒险 |
| 4 | `line_drawing` | 黑白线描 | 科学/可涂色 |
| 5 | `pixel_art` | 像素画 | 游戏/科技 |
| 6 | `chinese_ink` | 中国水墨 | 传统文化 |
| 7 | `realistic` | 写实油画 | 历史/人文 |
| 8 | `crayon_journal` | 蜡笔手账风 | 低年级/日常 |
| 9 | `chibi_comic` | Q版漫画 | 对话/社交 |
| 10 | `infographic` | 信息图 | 流程/科普 |

自定义风格：用户描述任意风格 → 按通用原则生成英文 prompt。

**版式选择**（根据词汇语义自动推荐，用户可覆盖）：

| 版式 | 适用场景 |
|---|---|
| **全部融入一景** | 词汇属于同一生态（教室、厨房、公园、城市等），默认 |
| **一词一景** | 词汇是动作/运动/职业等各需独立小场景展示的概念 |

**语义聚类参考**（辅助场景匹配）：

| 词类 | 推荐场景 |
|---|---|
| 食物 | 厨房、市场、野餐、面包店、餐厅 |
| 动物 | 动物园、森林、动物救助站 |
| 运动/动作 | 运动场、操场、户外营地 |
| 颜色 | 画室、花园、教室色卡墙 |
| 自然/植物 | 花园、森林、温室 |
| 学校物品 | 教室、图书馆、书桌 |
| 交通/地点 | 城市地图、车站、机场 |
| 混合词汇 | 选择能自然容纳所有词汇的统一故事场景 |

**流程**：

```
步骤 1  接收教材 → 识别主题 + 提取词汇
   ↓
步骤 2  展示风格选项，用户选定 style_zone（不选 → default）
   ↓
步骤 3  选择版式 + 设计场景 + 分配 anchor_position + 提取 min_frames
   ↓
★ 确认点 1「场景确认」
   展示：风格、版式、scene_label、keywords 表格、min_frames
   用户可：✅ 确认 / ✏️ 修改 / 🎨 换风格 / 🔄 重新设计
   ↓
步骤 4  组装 scene_image_prompt（五区结构）
   ↓
★ 确认点 2「Prompt 确认」
   展示完整 prompt
   用户可：✅ 确认 / ✏️ 修改 / 🎨 换风格 / ⏭️ 跳过生图
   ↓
步骤 5  写入临时文件 → 调用生图脚本
         python3 ~/.claude/skills/scene-vocab-card/scripts/generate_image.py \
           --file /tmp/scene_vocab_prompt.txt --type 场景词汇卡
         → 保存到 ~/scene-vocab-card/output/
```

---

## 5. 参考文件

| 文件 | 用途 |
|---|---|
| `references/scene_library.md` | 13 个场景模板（keyword 池 + 构图建议） |
| `references/style_zones.md` | 10 种风格 prompt + 通用原则（IP 安全、可读性、避免项） |
