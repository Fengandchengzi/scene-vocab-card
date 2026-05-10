---
name: scene-vocab-card
description: |
  为英语教材生成场景词汇卡海报。
  用户输入教材页面/截图/单词列表 → 输出一张主题海报（所有词汇标注在同一场景中）。
  输出：结构化 JSON（scene_label / scene_image_prompt / keywords / min_frames）+ 可选 PNG。
  触发词：场景词汇卡、scene vocab card、做场景卡、生成词汇场景、教材场景卡、做词汇海报
---

# 场景词汇卡生成器 (scene-vocab-card)

## 1. SKILL 概述

将英语教材内容转化为场景词汇卡海报——一个完整的主题场景，教材中所有目标词汇作为标签标注在画面中。

**三层结构：**
```
场景图 → 场景关键词标签 → 最小句子框架
```

**与 edu-ip-poster 的核心区别：**
- 无 IP 角色，使用通用插画风格（可切换 7 种 style_zone）
- 所有教材词汇出在同一张海报中，标签地位平等
- 输出结构化 JSON（前端消费 + 图像生成双用），不仅仅是一张 PNG

---

## 2. 输入规格

用户直接给教材页面，**所有词汇出在同一张海报中**：

1. **识别教材主题**：确定课文主题（如 Class Rules / Kitchen / Weather）
2. **提取目标词汇**：从教材页面提取核心词汇（5-8 个）
3. **设计统一场景**：围绕教材主题设计一个能容纳所有词汇的完整场景
   - 场景必须是具体可视化的（`课堂规则教室全景` ✓ / `课堂规则` ✗）
   - 每个词汇在场景中都有可指向的视觉元素
4. **生成单张海报 JSON**：所有词汇作为 keywords 数组中的标签，共享同一个 scene_image_prompt
5. **min_frames 覆盖多个词汇**：从教材核心句型中提取，不限于单个词

**典型输入形式：**
- 教材 PDF 页面截图
- 教材照片
- 手动输入的单词列表 + 主题

**可选参数：**

| 字段 | 说明 |
|---|---|
| `style_zone` | 风格区 prompt 文本。默认值见下方。可整体替换，参见 `references/style_zones.md` |

**默认 style_zone：**
```
modern educational illustration style, clean vector-based art with soft hand-drawn texture, gentle rounded shapes, warm and friendly color palette (muted terracotta, sage green, cream white, warm ochre), soft even lighting (no harsh shadows), subtle grain texture overlay, 4:3 ratio, no photorealistic elements, no dark or dramatic lighting, no cinematic atmosphere
```

**示例对话：**
```
用户：[上传教材 PDF 截图，内容是 Class Rules 课文]
skill：主题 → 课堂规则
      场景 → 教室全景（老师、举手学生、迟到学生、垃圾桶、灯开关）
      → 输出一张海报的 JSON，8 个标签分布在画面各处
```

---

## 3. 输出格式

```json
{
  "scene_label": "具体可视化场景中文标签（前端展示，不进图）",
  "scene_image_prompt": "按【四区结构】生成的完整 prompt（纯英文）",
  "keywords": [
    {
      "en": "英文名（进图标签）",
      "zh": "中文名（前端展示用，不进图）",
      "pos": "noun",
      "anchor_position": "8 个枚举之一"
    }
  ],
  "min_frames": [
    {
      "en": "教材核心句型",
      "zh": "中文翻译"
    }
  ]
}
```

**关键约定：**
- `scene_label` 是中文，给前端展示，**不进图**
- `keywords[].zh` 是中文，给前端展示，**不进图**
- `min_frames[].zh` 是中文翻译，**不进图**
- `scene_image_prompt` 和图中所有标签文字**只用英文**
- keywords 所有标签地位平等，没有主角/配角之分
- min_frames 来自教材原句，可覆盖多个不同词汇

---

## 4. scene_image_prompt 四区结构

必须按以下四区输出，每区用空行分隔。**所有文字（含标签）只用英文。**

### 【内容区】

1-2 句话。按 anchor_position 顺序描述：

- 主体角色的位置、外貌、动作
- 每个 keyword 的位置和外观

### 【风格区】

直接插入 `{style_zone}` 文本。参见 `references/style_zones.md`。

### 【标签区】

```
Label style: small rounded label with off-white background (#f5f0e8), warm dark brown text (#4a3728), sans-serif font (English bold), thin curved dark brown line (1-2px) connecting label to object.

Label list (English only):
- {anchor_position}: '{en}' → arrow points to [brief description]
- {anchor_position}: '{en}' → arrow points to [brief description]
...
```

按 anchor_position 顺序排列。

### 【避免项】

```
No photorealistic rendering, no Chinese characters anywhere in the image, no Western faces (East Asian anchor), no real brand logos, no anime/manga style, no frame borders, no watermark, no duplicate labels (each label word must appear exactly once in the image).
```

---

## 5. 硬约束

| # | 规则 |
|---|---|
| 1 | keywords 数组 **5-8 个**，必须是该场景里图中可识别的物件/动作/姿态 |
| 2 | scene_label 必须是**具体可视化场景**，不是抽象类别（`课堂规则教室全景` ✓ / `课堂规则` ✗） |
| 3 | keywords 每条必须填 anchor_position，不可留空，必须与内容区描述一致 |
| 4 | min_frames 2-3 条，每条不超过 5 词，以动词起头 |
| 5 | min_frames 来自教材核心句型，可覆盖不同词汇 |
| 6 | 图像里所有文字只用英文。中文不进图 |

---

## 6. 完整示例

### Class Rules 教材海报

**输入：**
```
用户上传教材截图：Unit 1 Class Rules 页面
包含词汇：chalkboard, clock, raise hand, trash can, clean floor, light switch, teacher, late
```

**输出：**
```json
{
  "scene_label": "课堂规则教室全景",
  "scene_image_prompt": "A bright elementary school classroom scene showing multiple activities: at the front a young East Asian teacher stands beside a green chalkboard pointing to a list; in the center a girl raises her hand while sitting at a neat desk; near the door a boy rushes in with a flustered look, a wall clock above reads 8:15; to the left another student drops crumpled paper into a green trash can beside tidy rows of desks with a shiny mopped floor; at the back wall a boy reaches up to flip a light switch near the doorframe; no food is visible on any desk.\n\nmodern educational illustration style, clean vector-based art with soft hand-drawn texture, gentle rounded shapes, warm and friendly color palette (muted terracotta, sage green, cream white, warm ochre), soft even lighting (no harsh shadows), subtle grain texture overlay, 4:3 ratio, no photorealistic elements, no dark or dramatic lighting, no cinematic atmosphere\n\nLabel style: small rounded label with off-white background (#f5f0e8), warm dark brown text (#4a3728), sans-serif font (English bold), thin curved dark brown line (1-2px) connecting label to object.\n\nLabel list (English only):\n- top-center: 'chalkboard' → arrow points to the green chalkboard with rule list\n- top-right: 'clock' → arrow points to the wall clock showing 8:15\n- middle-right: 'raise hand' → arrow points to the girl's raised hand\n- middle-left: 'trash can' → arrow points to the green trash can\n- bottom-center: 'clean floor' → arrow points to the shiny mopped floor\n- bottom-right: 'light switch' → arrow points to the boy reaching for the switch\n- top-left: 'teacher' → arrow points to the teacher at the front\n- bottom-left: 'late' → arrow points to the rushing boy with flustered expression\n\nNo photorealistic rendering, no Chinese characters anywhere in the image, no Western faces (East Asian anchor), no real brand logos, no anime/manga style, no frame borders, no watermark, no duplicate labels (each label word must appear exactly once in the image).",
  "keywords": [
    {"en": "chalkboard", "zh": "黑板", "pos": "noun", "anchor_position": "top-center"},
    {"en": "clock", "zh": "时钟", "pos": "noun", "anchor_position": "top-right"},
    {"en": "raise hand", "zh": "举手", "pos": "noun", "anchor_position": "middle-right"},
    {"en": "trash can", "zh": "垃圾桶", "pos": "noun", "anchor_position": "middle-left"},
    {"en": "clean floor", "zh": "干净的地板", "pos": "noun", "anchor_position": "bottom-center"},
    {"en": "light switch", "zh": "灯开关", "pos": "noun", "anchor_position": "bottom-right"},
    {"en": "teacher", "zh": "老师", "pos": "noun", "anchor_position": "top-left"},
    {"en": "late", "zh": "迟到", "pos": "noun", "anchor_position": "bottom-left"}
  ],
  "min_frames": [
    {"en": "raise your hand", "zh": "举手"},
    {"en": "keep the floor clean", "zh": "保持地板干净"},
    {"en": "don't be late", "zh": "不要迟到"}
  ]
}
```

---

## 7. 工作流

```
步骤 1  接收教材（PDF 页面 / 截图 / 单词列表）
   ↓
步骤 2  识别教材主题 + 提取目标词汇（5-8 个）
   ↓
步骤 3  设计统一场景（围绕教材主题，能容纳所有词汇的完整场景）
   ↓
步骤 4  为每个词汇分配 anchor_position（确保画面中有对应的视觉元素）
   ↓
步骤 5  从教材原句提取 min_frames（覆盖多个词汇）
   ↓
步骤 6  输出 JSON 草稿（不含 scene_image_prompt 完整文本）
   ↓
★ 确认点 1 ——「场景确认」
   │  向用户展示：
   │  · scene_label（场景名称）
   │  · keywords 表格（en / zh / anchor_position）
   │  · min_frames 列表
   │  用户可以：
   │  · ✅ 确认 → 继续
   │  · ✏️ 修改 → 增删词汇、调整场景、换 anchor_position、改 min_frames
   │  · 🔄 重新设计 → 返回步骤 3
   ↓
步骤 7  组装 scene_image_prompt（四区结构，纯英文）
   ↓
★ 确认点 2 ——「Prompt 确认」
   │  向用户展示：
   │  · 完整 scene_image_prompt 文本（四区结构）
   │  用户可以：
   │  · ✅ 确认 → 继续生成图片
   │  · ✏️ 修改 → 调整内容区描述、标签文字、风格区（可换 style_zone）
   │  · ⏭️ 跳过生图 → 只保留 JSON，不生成 PNG
   ↓
步骤 8  将 scene_image_prompt 写入临时文件
   ↓
步骤 9  调用脚本生成 PNG 图片
         → python3 ~/.claude/skills/scene-vocab-card/scripts/generate_image.py \
              --file /tmp/scene_vocab_prompt.txt \
              --type 场景词汇卡
         → 图片保存到 ~/scene-vocab-card/output/
```

---

## 8. 参考文件

| 文件 | 用途 |
|---|---|
| `references/scene_library.md` | 13 个场景模板（含 keyword 池和构图建议） |
| `references/style_zones.md` | 7 种风格区完整 prompt 文本 |
