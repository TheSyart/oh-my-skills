---
name: ai-video-evaluator
description: |
  AI 视频内容质量评估与短视频解析工具。当用户需要：
  1) 解析/下载抖音、快手、小红书、B站视频链接
  2) 将视频语音转录为带时间戳的文本
  3) 提取视频标题、话题、直链等信息
  4) 判断 AI 视频内容质量高低、是否焦虑营销、是否空洞无意义
  5) 审查知识教学类视频中的概念错误、夸大断言或证据不足
  6) 生成带截图证据和字幕证据的 HTML 评估报告
  7) 处理任何短视频分享链接
  必须使用此 skill。skill 内置四个平台解析脚本、DashScope 转录脚本、ffmpeg 抽帧脚本和 HTML 评估报告模板。
---

# AI Video Evaluator

短视频解析、语音转文本和 AI 视频质量评估工作流。

Skill 目录结构：
```
ai-video-evaluator/
├── SKILL.md           # 本文件
├── .env               # DASHSCOPE_API_KEY 配置文件
├── assets/
│   ├── video_eval_report_template.html # 视频评估 HTML/PPT 风格模板
│   ├── transcript_glossary.json # 常见 ASR 专名纠错表
│   ├── platform-logos/ # 四个平台透明 PNG logo，用于报告平台标识
│   │   ├── logo-douyin.png
│   │   ├── logo-kuaishou.png
│   │   ├── logo-xiaohongshu.png
│   │   └── logo-bilibili.png
│   └── rating-badges/ # 一体化评分标识 PNG，不在 HTML 中叠字
│       ├── badge-hangbaole.png
│       ├── badge-haitingding.png
│       ├── badge-nengkankan.png
│       ├── badge-youdianxu.png
│       └── badge-lawangle.png
└── scripts/
    ├── parse.py       # 统一入口：自动检测平台并解析
    ├── douyin.py      # 抖音解析
    ├── kuaishou.py    # 快手解析
    ├── xhs.py         # 小红书解析
    ├── bilibili.py    # B站解析
    ├── transcribe.py  # 语音转文本
    ├── normalize_transcript.py # 字幕专名纠错/规范化
    └── capture_frames.py # 按时间点抽取视频截图
```

## 配置

转录功能需要阿里百炼 API Key；截图功能需要系统安装 `ffmpeg`。

1. 访问 https://dashscope.console.aliyun.com/ 创建 API Key
2. 填入 skill 目录下的 `.env` 文件：
   ```
   DASHSCOPE_API_KEY=sk-xxxxxxxx
   ```
3. 安装 `ffmpeg`。脚本会优先使用 PATH 中的 `ffmpeg`，也会自动探测常见 Homebrew 路径；仍找不到时可传 `--ffmpeg-bin` 或设置 `FFMPEG_BIN`。没有 `ffmpeg` 时，不要生成无截图的完整评估报告；应提示用户安装后重试。

## 用法

先设置 skill 路径，避免在不同工作目录下找不到脚本：

```bash
SKILL_DIR="$HOME/.codex/skills/ai-video-evaluator"
```

### 解析视频链接

统一入口（自动检测平台）：
```bash
python "$SKILL_DIR/scripts/parse.py" --url "<分享链接>"
```

或指定平台：
```bash
python "$SKILL_DIR/scripts/douyin.py" --url "<链接>"
python "$SKILL_DIR/scripts/kuaishou.py" --url "<链接>"
python "$SKILL_DIR/scripts/xhs.py" --url "<链接>"
python "$SKILL_DIR/scripts/bilibili.py" --url "<链接>"
```

**输出格式：**
```json
{
  "title": "视频标题",
  "topic": "#话题标签",
  "videoId": "视频ID",
  "url": "视频直链（MP4）",
  "platform": "douyin|kuaishou|xhs|bilibili"
}
```

### 语音转文本

```bash
python "$SKILL_DIR/scripts/transcribe.py" --url "<视频直链>"
```

**输出格式：**
```json
{
  "text": "完整转录文本",
  "sentences": [
    {"text": "第一句", "begin_time": 0, "end_time": 3500}
  ]
}
```

### 字幕纠错与专名规范化

转录完成后必须先纠错，再进入评估和报告生成：

```bash
python "$SKILL_DIR/scripts/normalize_transcript.py" \
  --input "<transcript.json>" \
  --out "<transcript.normalized.json>"
```

如发现视频特有误识别，使用 `--extra` 增补本次替换：

```bash
python "$SKILL_DIR/scripts/normalize_transcript.py" \
  --input "<transcript.json>" \
  --out "<transcript.normalized.json>" \
  --extra "cloud code=Claude Code" \
  --extra "open air=OpenAI"
```

**输出格式：**
```json
{
  "text": "纠错后的完整文本",
  "sentences": [
    {"text": "纠错后的句子", "begin_time": 0, "end_time": 3500}
  ],
  "corrections": [
    {"from": "cloud code", "to": "Claude Code", "type": "literal", "count": 2}
  ]
}
```

### 按字幕时间点抽帧

从字幕时间轴中选择证据时间点后抽帧：

```bash
python "$SKILL_DIR/scripts/capture_frames.py" \
  --video-url "<视频直链>" \
  --times "12.3,45.0,78.5" \
  --out-dir "<报告资源目录>"
```

如果 `ffmpeg` 不在 PATH 中：

```bash
python "$SKILL_DIR/scripts/capture_frames.py" \
  --video-url "<视频直链>" \
  --times "12.3,45.0,78.5" \
  --out-dir "<报告资源目录>" \
  --ffmpeg-bin "/path/to/ffmpeg"
```

**输出格式：**
```json
{
  "frames": [
    {"time": 12.3, "path": "/abs/path/frame_001_12.300s.jpg"}
  ]
}
```

## 典型工作流

1. **用户给分享链接 → 解析**
   ```bash
   python "$SKILL_DIR/scripts/parse.py" --url "<链接>"
   ```

2. **用户要视频文案 → 解析+转录**
   ```bash
   # 先解析
   result=$(python "$SKILL_DIR/scripts/parse.py" --url "<链接>")
   video_url=$(echo "$result" | python -c "import sys,json; print(json.load(sys.stdin)['url'])")

   # 再转录
   python "$SKILL_DIR/scripts/transcribe.py" --url "$video_url"
   ```

3. **用户要分析视频 → 解析+转录，然后分析**
   - 运行 parse.py 获取元数据
   - 运行 transcribe.py 获取文案
   - 结合 title/topic + transcript 进行内容分析

4. **用户要评估 AI 视频质量 → 解析+转录+抽帧+HTML 报告**
   - 运行 `parse.py` 获取标题、话题、视频 ID、平台、视频直链
   - 运行 `transcribe.py` 获取完整字幕和 `sentences`
   - 运行 `normalize_transcript.py` 生成纠错后的 transcript；之后所有证据引用都用纠错版本
   - 从字幕时间轴中选择 3-6 个证据时间点
   - 运行 `capture_frames.py` 抽取这些时间点的视频截图
   - 复制 `assets/video_eval_report_template.html` 生成 HTML 评估报告
   - 按平台复制一个 `assets/platform-logos/*.png` 到报告资源目录，并填入模板的 `{{PLATFORM_LOGO_SRC}}`
   - 按总分复制一个 `assets/rating-badges/*.png` 到报告资源目录，并填入模板的 `{{RATING_BADGE_SRC}}`
   - 截图和评分标识资源放在 HTML 同级或子目录中

## AI 视频质量评估规范

目标用户是普通观众。评估重点回答：这个视频值不值得看、是否单纯贩卖焦虑、是否空洞无意义、知识教学内容有没有明显概念错误。

### 字幕纠错规范

不要在报告里写“字幕包含少量同音和专有名词误识别”然后把问题丢给用户。必须先修字幕。

处理顺序：

1. 结合标题、话题、画面截图、上下文和领域常识列出专名：如 OpenAI、Codex、Claude Code、Anthropic、OpenClaw、Hermes、SDK、API、tool use、CLAUDE.md。
2. 运行 `normalize_transcript.py` 应用 `assets/transcript_glossary.json`。
3. 对仍明显错误的词，用 `--extra "错词=正词"` 重新生成一次 normalized transcript。
4. 报告中的字幕摘录、断言表、证据画廊一律使用 normalized transcript。
5. 如果某个词无法确定，不要硬改；写成“疑似 X”或在概念审查里说明不确定性。
6. 不要长篇展示原始 ASR 字幕。原始转录只作为内部工作文件；用户看到的是纠错后的短句证据和结构化摘要。

常见纠错方向：

- `open air`、`opai` → `OpenAI`
- `cloud code`、`cloucode` → `Claude Code`
- `cloud点md` → `CLAUDE.md`
- `sk` 在 SDK 语境下 → `SDK`
- `tour result`、`to use` → `tool result`、`tool use`

### 评分维度

每项 0-5 分，总分 30 分。所有维度都是分数越高越好：

- 知识价值：是否提供真实信息、解释框架或可迁移理解，而不是只堆情绪和标签。
- 概念准确性：定义、因果、边界条件是否可靠；知识类视频必须重点审查。
- 证据质量：是否给出来源、案例、数据、推理链；是否把个例包装成普遍规律。
- 信息密度：字幕中有效信息占比，是否大量重复、空泛口号、伪金句。
- 情绪操控/焦虑贩卖：是否使用恐惧、羞辱、错失感、身份焦虑制造观看或购买动机；高分表示操控少。
- 可操作性：建议是否具体、可执行、适用条件清楚；是否只给模糊方向或引流话术。

### 结论分级

- 推荐：总分 >= 23，且没有严重概念错误或明显焦虑贩卖。
- 谨慎：总分 14-22，或有局部夸大、证据不足、信息密度低但仍有可取内容。
- 不推荐：总分 <= 13，或出现严重概念错误、强焦虑营销、明显引流割韭菜、内容主要由空话组成。

不要只给分数；每个低分项必须引用对应字幕片段或截图时间点。

### 报告笔锋

报告要有判断力，不要写成温吞的产品评测。文字毒舌度必须随总分下降而上升：分数越低，措辞越直接、越不替视频找台阶；分数越高，语气越克制、越具体。所有批评必须有证据锚点。

- 25-30 分：低毒舌度。肯定具体价值，指出少量边界，不刻意吹捧。
- 20-24.5 分：轻毒舌度。认可可取部分，同时明确提醒哪些说法偏满、偏简化；不阴阳怪气。
- 14-19.5 分：中毒舌度。直接指出“只能看看”，说明内容哪里浅、哪里没兑现标题；可以写“标题比内容硬”“讲了框架，没给牙齿”。
- 8-13.5 分：高毒舌度。用强批评，明确指出空泛、夸大、焦虑话术、缺乏证据；可以写“这不是教学，是情绪推销”“拿趋势当证据、拿焦虑当逻辑”。不要用“可能有一定参考价值”稀释结论。
- 0-7.5 分：满毒舌度。狠狠批，允许短句重锤，如“用词很响，内容很薄”“整条视频像把热词倒进搅拌机”“没有知识，只有情绪挂钩”。仍然要保持可验证：每个重话后面必须接时间戳或短句证据。

语气校准规则：

- 低分报告不要写成中性摘要；要先给尖锐结论，再列证据。
- 高分报告不要为了“毒舌”硬骂；主要写价值和边界。
- 毒舌只针对内容质量、话术和证据，不攻击创作者本人。
- 每个强批评段落至少落回一个字幕片段、截图时间点或概念审查项。

低质量报告禁用这些软化句：

- “可以作为参考”
- “有一定启发”
- “适合快速了解”
- “总体还可以”
- “可能对部分用户有帮助”

除非后面紧跟明确限制，例如“只能作为知道工具名字的提醒，不能作为学习路线或判断依据”。

### 焦虑营销判定

命中越多，越应降低“情绪操控/焦虑贩卖”分：

- 绝对化威胁：如“再不学就完了”“普通人没机会了”“你已经被淘汰”。
- 稀缺和错失：如“最后窗口期”“只剩这一次机会”，但没有可验证依据。
- 羞辱或身份压迫：把不购买、不学习、不转发描述成失败或低层次。
- 先制造恐惧，再导向课程、社群、咨询、私信、资料包、训练营。
- 用宏大趋势替代具体证据，把复杂问题简化成单一路径。

### 无意义/低质量内容判定

出现以下特征时，应明确标注“信息价值低”：

- 反复改写同一句观点，没有新增事实、步骤、例子或边界条件。
- 只有情绪立场和成功学口号，没有解释“为什么”和“怎么做”。
- 标题承诺很大，字幕中没有兑现核心问题。
- 把常识包装成独家认知，或把无法验证的经验当作普遍规律。
- 大量使用 AI 生成式套话：趋势、红利、认知、底层逻辑、闭环、赋能等词密集出现，但缺少实质内容。

### 知识教学类视频审查

如果视频在教学、科普、解释概念、给专业建议：

1. 先抽取 3-8 条关键断言，优先选择定义、因果关系、操作建议、数据判断。
2. 对每条标注：正确 / 可疑 / 错误 / 无法核验。
3. 对“可疑/错误”断言说明问题：概念混淆、因果倒置、样本不足、过度泛化、遗漏前提、风险提示不足。
4. 医疗、法律、金融、心理健康、升学就业等高风险领域，必须提示用户不要仅凭视频内容决策，必要时咨询专业人士。
5. 如果需要联网核验且用户未禁止搜索，应查官方文档、论文、监管机构、权威教材等一手或高可信来源。

## 证据选择规则

从 `sentences` 中选 3-6 个时间点用于截图和引用，优先覆盖：

- 开头承诺或核心论点
- 最强的恐惧/焦虑/稀缺话术
- 知识类视频中的关键定义或关键步骤
- 有争议、夸大、疑似错误的断言
- 具体案例、数据、证据来源或缺失证据的位置
- 结尾转化动作，如引导购买、私信、加群、领取资料

抽帧时间建议用该字幕句子的中点：`(begin_time + end_time) / 2000` 秒。截图只作为画面证据，判断理由必须同时引用字幕文字。

## HTML 评估报告要求

输出一个单页 HTML 报告。报告应清晰、克制、可扫描，适合普通观众快速判断。

必须优先使用内置模板：

```bash
cp "$SKILL_DIR/assets/video_eval_report_template.html" "<输出目录>/report.html"
```

然后替换模板中的 `{{...}}` 占位符。不要每次重新设计页面样式；只有用户明确要求更换视觉风格时，才允许偏离该模板。

模板风格是犀利评审杂志感：浅色纸面背景、深色大标题、右侧票据式结论卡、浮层评分章、平台 logo、六项语义评分卡、双栏判断、断言表、截图证据画廊、字幕证据与口播摘要折叠区。生成报告时保持这个信息结构和视觉密度，不要改成营销落地页或纯仪表盘。

模板设计规则：

- 首屏结论优先：标题、总分、评分章、平台信息和一句结论必须在首屏清楚出现。
- 右侧结论卡应像评审票据：总分和结论之间留出稳定间距，元信息紧凑但不挤。
- 低质量视频要有容器级审判感：低分评分卡、焦虑营销卡、空洞判断卡应通过边线、进度条和轻背景体现严重程度，不只靠红色文字。
- 保持浅色报告风格，不引入外链字体、CDN、JS 动效或暗黑主题。

评分标识必须使用内置一体化 PNG，不能在 HTML 中叠加文字：

| 总分区间 | 标识文字 | 文件 |
|---|---|---|
| 25-30 | 夯爆了 | `assets/rating-badges/badge-hangbaole.png` |
| 20-24.5 | 还挺顶 | `assets/rating-badges/badge-haitingding.png` |
| 14-19.5 | 能看看 | `assets/rating-badges/badge-nengkankan.png` |
| 10-13.5 | 有点虚 | `assets/rating-badges/badge-youdianxu.png` |
| 0-9.5 | 拉完了 | `assets/rating-badges/badge-lawangle.png` |

如果结论分级和标识区间冲突，以总分区间选择标识，再在文字说明中解释原因。生成报告时把选中的 PNG 复制到输出目录的 `assets/` 下，用相对路径填入模板；不要用 CSS、SVG 或 HTML 文本临时重画这些标识。

评分标识 PNG 使用透明背景，模板会把它作为约 12 度倾斜的印章式浮层压在顶部结论卡左上角空白区域。标识中心点应向卡片内侧和下方移动，用来占住左上角留白，并避免移动端贴到屏幕边缘；标识不参与卡片排版，不允许为了标识额外撑高结论卡、移动分数或移动元信息。不要给标识图片额外加白底、卡片底、文字叠层或二次描边。如果替换标识资源，新图也必须是透明 PNG。

平台标识必须使用内置四个平台 PNG，并显示在顶部结论卡的“平台 / ID”行里：

| `platform` 字段 | 平台显示名 | 文件 |
|---|---|---|
| `douyin` | 抖音 | `assets/platform-logos/logo-douyin.png` |
| `kuaishou` | 快手 | `assets/platform-logos/logo-kuaishou.png` |
| `xhs` | 小红书 | `assets/platform-logos/logo-xiaohongshu.png` |
| `bilibili` | B站 | `assets/platform-logos/logo-bilibili.png` |

生成报告时把对应平台 PNG 复制到输出目录的 `assets/` 下，用相对路径填入 `{{PLATFORM_LOGO_SRC}}`，并用中文平台名填入 `{{PLATFORM_LABEL}}`。不要热链接外部 logo，不要用 emoji、文字方块或临时 SVG 代替平台 logo。

报告文字允许使用少量语义强调，但必须克制：

- 批判性关键短语使用 `<span class="tone-critical">...</span>`，如“焦虑话术”“内容空心化”“证据链断裂”。
- 正向关键短语使用 `<span class="tone-positive">...</span>`，如“概念正确”“教学价值明确”“边界说明清楚”。
- 警示但未到负面定性的短语可用 `<span class="tone-warning">...</span>`。
- 不要整段、整列表、整页染色。原则上每个段落最多强调 1-2 个短语，整页强调文字占比应低于 10%；一般描述保持黑色或模板默认灰色。

六项评分卡必须加入语义 class：

- `score-low`：单项分数 `< 2.5`，使用红色进度条和轻红背景。
- `score-mid`：单项分数 `>= 2.5` 且 `< 3.5`，使用橙色进度条和轻橙背景。
- `score-high`：单项分数 `>= 3.5`，使用绿色进度条和轻绿背景。

示例：

```html
<article class="score-card score-low">
  <div class="score-head"><span>证据质量</span><strong>1/5</strong></div>
  <div class="bar"><span style="width:20%"></span></div>
  <p>没有来源、没有推理链。</p>
</article>
```

必须包含：

- 视频基本信息：标题、平台、视频 ID、话题、评估时间。
- 顶部结论：推荐 / 谨慎 / 不推荐，一句话说明主要原因。
- 总分和六项评分：知识价值、概念准确性、证据质量、信息密度、情绪操控/焦虑贩卖、可操作性。
- 焦虑营销判断：是否存在、严重程度、对应字幕证据。
- 无意义内容判断：是否空洞、重复或标题党，引用字幕说明。
- 知识类概念审查：关键断言表格和正确性标签；非知识类视频可写“不适用”。
- 证据画廊：每张截图显示时间点、对应字幕、评估理由。
- 字幕证据与口播摘要：使用折叠区或可滚动区域展示；保留关键证据时间戳和必要短句，不要长篇逐字搬运完整口播。

截图展示规则：

- 必须完整显示截图，不要裁切画面；横屏和竖屏都保留原始比例。
- 模板里的 `.evidence-card img` 使用 `height: auto`、`object-fit: contain` 和 `max-height`，不要改回固定 `16:9` 或 `object-fit: cover`。
- 如果平台返回的视频帧自带黑边或横竖屏包装，报告中保持原样展示，不要二次裁切。

模板占位符约定：

- `{{RATING_BADGE_SRC}}` 使用相对 HTML 的评分标识图片路径，例如 `assets/badge-lawangle.png`
- `{{RATING_BADGE_ALT}}` 使用对应标识文字，例如 `拉完了`
- `{{PLATFORM_LOGO_SRC}}` 使用相对 HTML 的平台 logo 路径，例如 `assets/logo-douyin.png`
- `{{PLATFORM_LABEL}}` 使用中文平台名，例如 `抖音`
- `{{SCORE_CARDS_HTML}}` 生成 6 张 `.score-card`，每张必须同时带 `score-low` / `score-mid` / `score-high` 之一，并包含分数、进度条和一句依据
- `{{CLAIM_ROWS_HTML}}` 生成断言审查表格行，标签类名使用 `ok` / `mid` / `warn` / `bad`
- `{{EVIDENCE_CARDS_HTML}}` 生成 3-6 张 `.evidence-card`，图片路径使用相对 HTML 的路径
- `{{TRANSCRIPT_TEXT}}` 必须先 HTML escape；优先放结构化摘要、时间轴证据和必要短句，避免长篇逐字转写破坏可读性。每行时间范围可在 escape 后包成 `<span class="timeline-time">00:00-00:03</span>`，让时间轴在黑底字幕区用绿色醒目显示；不要给整行字幕染色。

HTML 中不要堆砌免责声明。只在高风险内容或无法核验处给出简短、具体的风险提示。

生成或修改模板后必须做截图审核：至少检查桌面宽屏、普通桌面和移动端三种宽度，确认首屏结论卡更聚焦、评分章不遮挡内容、六项评分颜色与分数语义一致、无横向溢出、横竖屏截图完整显示。

## 注意事项

- 视频直链具有时效性，解析后应尽快使用
- 转录时 DashScope 需要能访问视频URL，如果URL过期会导致转录失败
- B站解析支持分P，加 `--p 2` 获取第二P
- 四个平台均不需要登录态
- 评估报告必须基于标题、话题、字幕和截图证据；不要凭风格或主观好恶下结论
- 负面判断必须有证据锚点：时间戳、截图、必要的短句摘录；不要用长篇字幕替代分析
