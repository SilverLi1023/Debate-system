# 辩论系统完整执行手册

> 本文件是防呆执行手册。每一步都有明确的「做什么」「怎么做」「检查什么」。
> **不允许跳步、不允许合并步骤、不允许自行发挥。**
> **Context 管理原则：每步完成后立即创建飞书文档，主 session 只保存文档链接，不在 context 中保留完整稿件文本。**

---

## 前置：状态文件

每次开始前，创建或更新 `sessions/current-task.json`：

```json
{
  "title": "辩论：{辩题}",
  "status": "in_progress",
  "stage": "research",
  "topic": "{辩题}",
  "pro_side": "{持方}",
  "round": 0,
  "max_rounds": 3,
  "research_retry": 0,
  "argument_research_retry": 0,
  "files": {
    "research": "",
    "argument": "",
    "opposition": [],
    "defense": [],
    "judge": "",
    "revised_argument": "",
    "battle_guide": "",
    "index": ""
  },
  "feishu_links": {
    "research": "",
    "argument": "",
    "rounds": [],
    "judge": "",
    "revised_argument": "",
    "battle_guide": "",
    "index": ""
  }
}
```

输出目录：`debate-outputs/YYYY-MM-DD/`（按当天日期创建）

---

## STEP 1：资料检索

### 1.1 构建 subagent task

用 `read` 工具读取以下文件，拼接成 task 字符串：

```
文件1: references/01-Research-Agent.md  （agent prompt）
文件2: references/04-资料检索与使用规范.md

拼接格式：
---
{文件1内容}
---
{文件2内容}
---

现在开始执行：
辩题：{topic}
持方：{pro_side}（己方资料数量必须大于对方）

第一步：先将辩题拆解为若干关键概念，列出每个概念要检索的方向。（这一步是你的检索思路，不需要写入最终文档）
第二步：按概念逐个检索，每个概念用多组关键词搜索，中英文都要搜。
第三步：整理为资料卡，严格按照 01-Research-Agent.md 中的输出格式，每个字段独占一行。
⚠️ 每条资料卡的「链接」字段必须是完整的、可直接在浏览器打开的 URL（以 http:// 或 https:// 开头）。输出前用工具验证链接可访问，禁止输出死链。

⚠️ **最终文档只输出资料卡，不要输出概念拆解、资料分类汇总、索引等其他内容。**
文档结构必须是：
1. 第一行：`**己方持方：{pro_side}** | **资料卡总数：X 条**（己方 Y 条，对方 Z 条）`
2. 分割线
3. `## 己方资料（P 系列）` 标题 + 所有己方资料卡
4. 分割线
5. `## 对方资料（R 系列）` 标题 + 所有对方资料卡

注意：只查近10年（2015年至今）的资料。总资料卡不少于20条（己方≥12条，对方≥8条）。
```

### 1.2 调用 subagent

```
sessions_spawn(
  task=上面拼接的字符串,
  mode="run",
  label="research",
  model="claude-sonnet-4-5"  ← 首选稳定模型
)
```

### 1.3 检查结果（必须执行）

- 结果是否包含至少1个完整的【资料卡】？
- 如果结果为空、报错、或没有任何资料卡 → **停止，告知用户资料检索失败，不得继续**
- 如果 subagent 超时 → 换 `model="claude-sonnet-4-5"` 重试一次，仍失败则停止
- 如果有资料卡 → 继续

### 1.4 保存 & 发飞书文档（由 subagent 直接完成）

⚠️ **重要：subagent 直接创建飞书文档，只把飞书链接返回主 session，避免主 session 被撑爆**

1. 在 subagent 的 task 最后添加：
   ```
   最后，请调用 feishu_create_doc 创建飞书文档：
   - title: "[{辩题}] 01-资料稿"
   - folder_token: "<从TOOLS.md读取，未配置则省略>"
   - content: 只包含资料卡的内容（不要包含概念拆解、资料分类汇总等）
   
   ⚠️ 飞书文档格式要求：
   - 每张资料卡用 callout 块包裹，己方用灰底（pale-gray），对方用蓝底（light-blue）
   - callout 内部用无序列表 `- **字段**：内容` 格式，每个字段一行
   - 文档结构：持方信息 → 分割线 → 己方资料标题 + 资料卡 → 分割线 → 对方资料标题 + 资料卡
   - 如果文档内容很长（>5KB），分多次创建：先 create 前半部分，再用 feishu_update_doc append 后半部分
   
   然后只返回飞书文档链接给我，格式：
   【资料稿已创建】
   链接：{飞书文档链接}
   ```
2. 调用 subagent 时把上述内容追加到 task 最后
3. 收到 subagent 的结果（仅飞书链接）后：
   - 将资料稿内容写入 `debate-outputs/YYYY-MM-DD/01_research.md`（可选，主要留档）
   - 更新 `current-task.json`：`files.research = 文件路径`，`feishu_links.research = 文档链接`，`stage = "framework"`
   - **发飞书文档链接给用户，等待确认**

**等用户说「继续」或「好的」之类的确认后，才进入 STEP 1.5。**

---

## STEP 1.5：论点框架确认（新增）

> 目的：在生成完整立论前，先让用户确认论点拆分方向，避免立论完成后大返工。

### 1.5.1 生成 2-3 种论点框架方案

**直接在主 session 中完成（不需要 subagent）**，根据辩题和资料稿，提出 2-3 种不同的论点拆分思路。

每种方案格式：

```
方案A：[方案名称]
- 论点一：[一句话论点句]（角度：XXX）
- 论点二：[一句话论点句]（角度：XXX）
- 适合场景：[这种拆法在什么情况下更有优势]
- 潜在风险：[这种拆法的薄弱点]
```

**拆分原则（必须检查）：**
- 两个论点必须从不同维度切入（如：存在论 vs 实践层面；必要性 vs 根本性；个体 vs 社会）
- 禁止两个论点本质相同（如都在讲"选择的代价"）
- 每个论点句必须能独立成立，不依赖另一个论点

### 1.5.2 发给用户确认

发送格式：

```
我为「{辩题}」整理了 {N} 种论点框架方案，请选择或调整：

{方案A内容}

{方案B内容}

{方案C内容（如有）}

请告诉我：
1. 选哪个方案？或者有调整意见？
2. 确认后我会按这个框架生成完整立论稿。
```

### 1.5.3 等待用户确认

- 用户选择方案或提出调整 → 记录确认的论点框架，进入 STEP 2
- 用户说「你来定」→ 选择你认为最强的方案，说明理由，进入 STEP 2

**将确认的论点框架写入 `current-task.json`：`confirmed_framework = {方案内容}`**

---

## STEP 2：正方立论

### 2.1 构建 subagent task

读取以下文件：

```
文件1: references/02-Argument-Agent.md
文件2: references/01-立论框架.md
文件3: references/03-价值排序与比较方法.md
文件4: references/立论示例.md
文件5: debate-outputs/YYYY-MM-DD/01_research.md  （资料稿）

拼接格式：
---
{文件1内容}
---
【立论框架知识库】
{文件2内容}
---
【价值排序知识库】
{文件3内容}
---
【立论示例】
{文件4内容}
---

现在开始执行：
辩题：{topic}
持方：{pro_side}

【已确认的论点框架（必须严格遵守）】
{confirmed_framework 内容}

⚠️ 重要：论点框架已由用户确认，禁止自行更改论点方向。只能在此框架内完善论证。

【硬性约束，违反直接重写】
- 总字数 ≤ 1100 字（约 3 分钟宣读）
- 每个论点最多 2 个论据，严禁堆砌
- 论据演绎模式：先场景/机制 → 数据验证 → 金句收束
- 禁止连续出现 3+ 个"XX年XX在XX发现……"式引用

执行步骤（必须按顺序）：
第一步：按已确认的论点框架，构建立论稿。需要数据/案例支撑的地方，先写[待补充：需要XXX方面的资料]占位。
第二步：读以下资料稿，将匹配的资料填入对应[待补充]位置。每个论点最多选 2 个最契合的资料，不要贪多。
第三步：【论点句自检】对每个论点句执行以下检查：
  - 反转测试：把论点句的主语/谓语/宾语反转，看反转后的句子是否同样成立
  - 如果反转后同样成立（说明论点句可被轻松反转），必须重写论点句，使其具有方向性和不可逆性
  - 自检报告格式（写在稿件末尾，用---分隔）：
    【论点句自检报告】
    论点一：[论点句]
    反转测试：[反转后的句子]
    结论：[可防守 / 已重写，新论点句：XXX]
    论点二：[同上]
第四步：检查是否还有未填充的[待补充]。如果有，在回复末尾列出：
  【需要补充检索的关键词】
  - 关键词1
  - 关键词2

资料稿：
{文件5内容}
```

### 2.2 调用 subagent

```
sessions_spawn(
  task=...,
  mode="run",
  label="argument",
  model="claude-sonnet-4-5"  ← 首选稳定模型
)
```

### 2.3 检查论点句自检报告

- 结果末尾是否有【论点句自检报告】？
- 如果有「已重写」的论点句 → 确认新论点句已在正文中替换
- 如果没有自检报告 → 重新调用，要求补充自检步骤

### 2.4 检查是否需要补充资料

- 结果末尾是否有【需要补充检索的关键词】？
- 如果有，且 `argument_research_retry < 2`：
  1. 用这些关键词重新调用 Research Agent（参考 STEP 1，但只搜这些关键词）
  2. `argument_research_retry += 1`
  3. 将新资料追加到资料稿，重新执行 STEP 2.1（第二步和第三步）
- 如果 `argument_research_retry >= 2` 或没有待补充项 → 继续

### 2.5 保存 & 发飞书文档（由 subagent 直接完成）

⚠️ **重要：subagent 直接创建飞书文档，只把飞书链接返回主 session，避免主 session 被撑爆**

1. 在 STEP 2.1 构建 subagent task 时，在末尾追加：
   ```
   完成立论稿后，请执行以下操作：
   1. 将完整立论稿（含自检报告）写入本地文件 debate-outputs/YYYY-MM-DD/02_argument.md
   2. 调用 feishu_create_doc 创建飞书文档：
      - title: "[{辩题}] 02-立论稿"
      - folder_token: "<从TOOLS.md读取，未配置则省略>"
      - content: 完整立论稿（含自检报告）
   3. 只返回以下信息给我，不要返回稿件全文：
      【立论稿已创建】
      链接：{飞书文档链接}
      自检结论：{论点句自检的结论摘要}
      待补充关键词：{如有，列出需要补充检索的关键词；如无，写"无"}
   ```
2. 收到 subagent 的结果（仅链接+摘要）后：
   - 更新 `current-task.json`：`files.argument = 文件路径`，`feishu_links.argument = 文档链接`，`stage = "opposition_round_1"`
   - 根据返回的自检结论和待补充关键词判断是否需要 STEP 2.3 / 2.4 的后续处理
   - **发飞书文档链接给用户，等待确认**

---

## STEP 3：攻防循环（最多3轮）

每轮包含两个子步骤：Opposition → Defense。

**Context 管理：每轮结束后立即创建飞书文档，主 session 只记录文档链接，不在 context 中保留完整攻防文本。**

### 3.1 Opposition（反方攻击）

读取文件：

```
文件1: references/03-Opposition-Agent.md
文件2: references/02-反驳与攻防技巧.md
文件3: references/05-环节执行与评委判准.md
文件4: references/攻防稿示例.md
文件5: debate-outputs/YYYY-MM-DD/02_argument.md

拼接 task：
---
{文件1内容}
---
【反驳与攻防技巧知识库】
{文件2内容}
---
【环节执行与评委判准知识库】
{文件3内容}
---
【攻防稿示例】
{文件4内容}
---

现在开始执行：
辩题：{topic}
这是第{N}轮攻击。

正方立论稿：
{文件5内容}

{如果是第2轮及以后，附上：}
前轮攻防记录（摘要）：
{前轮 03_round_N.md 的文件路径，让 agent 自行读取，不要把全文贴进 task}

请对正方立论进行最强攻击，严格按照攻防稿示例格式输出。
```

调用：
```
sessions_spawn(
  task=...,
  mode="run",
  label="opposition_round_{N}",
  model="claude-sonnet-4-5"
)
```

### 3.2 Defense（正方回应）

读取文件：

```
文件1: references/04-Defense-Agent.md
文件2: references/02-反驳与攻防技巧.md
文件3: references/05-环节执行与评委判准.md
文件4: references/攻防稿示例.md

拼接 task：
---
{文件1内容}
---
【反驳与攻防技巧知识库】
{文件2内容}
---
【环节执行与评委判准知识库】
{文件3内容}
---
【攻防稿示例】
{文件4内容}
---

现在开始执行：
辩题：{topic}
持方：{pro_side}
这是第{N}轮回应。

正方立论稿：
{立论稿内容}

反方攻击稿（本轮）：
{本轮 opposition 内容}

请回应反方攻击，严格按照攻防稿示例格式输出。
如果需要补充资料，在回复末尾列出【需要补充检索的关键词】。
```

调用：
```
sessions_spawn(
  task=...,
  mode="run",
  label="defense_round_{N}",
  model="claude-sonnet-4-5"
)
```

### 3.3 每轮结束后（由 subagent 直接完成飞书文档创建）

⚠️ **重要：每轮的 Opposition 和 Defense subagent 的 task 末尾都要追加飞书文档创建指令**

**在 STEP 3.1 和 3.2 的 subagent task 末尾分别追加：**

Opposition subagent 追加：
```
完成攻击稿后，请将完整攻击稿写入本地文件 debate-outputs/YYYY-MM-DD/03_round_{N}_opposition.md
然后只返回以下信息：
【反方攻击稿已完成】
攻击要点摘要：{列出3-5个核心攻击点的一句话摘要}
```

Defense subagent 追加：
```
完成回应稿后，请执行以下操作：
1. 将完整回应稿写入本地文件 debate-outputs/YYYY-MM-DD/03_round_{N}_defense.md
2. 读取本轮攻击稿 debate-outputs/YYYY-MM-DD/03_round_{N}_opposition.md
3. 将攻击稿 + 回应稿合并，调用 feishu_create_doc 创建飞书文档：
   - title: "[{辩题}] 03-攻防R{N}"
   - folder_token: "<从TOOLS.md读取，未配置则省略>"
   - content: 合并后的完整攻防记录
4. 只返回以下信息：
   【第{N}轮攻防已创建】
   链接：{飞书文档链接}
   防守要点摘要：{列出核心防守口径的一句话摘要}
   待补充关键词：{如有，列出；如无，写"无"}
```

**主 session 收到结果后：**
1. 更新 `current-task.json`：`files.opposition[N]` / `files.defense[N]` = 文件路径
2. 更新 `feishu_links.rounds[N] = 链接`
3. **发链接给用户，等待确认是否继续下一轮**
4. ⚠️ **主 session 只保存文件路径和飞书链接，不在 context 中保留完整攻防文本**

**用户说「继续」→ 下一轮；用户说「够了」或「进入裁判」→ 跳出循环进入 STEP 4。**

---

## STEP 4：裁判评判

### 4.1 构建 subagent task

```
文件1: references/05-Judge-Agent.md
文件2: references/05-环节执行与评委判准.md
文件3: references/00-核心原则.md

拼接 task：
---
{文件1内容}
---
【评委判准知识库】
{文件2内容}
---
【核心原则知识库】
{文件3内容}
---

现在开始执行：
辩题：{topic}
持方：{pro_side}

正方立论稿（文件路径，请自行读取）：
{debate-outputs/YYYY-MM-DD/02_argument.md}

攻防记录（共{N}轮，文件路径，请自行读取）：
{debate-outputs/YYYY-MM-DD/03_round_1.md}
{debate-outputs/YYYY-MM-DD/03_round_2.md}（如有）
{debate-outputs/YYYY-MM-DD/03_round_3.md}（如有）

请给出完整裁判评判，必须包含：
1. 己方最有利的观点
2. 己方最薄弱的观点
3. 攻击对方最痛的点
4. 修正建议（具体到论点句和论证逻辑）
5. 明确的胜负判定（己方获胜 / 己方落败）
```

### 4.2 调用 subagent

```
sessions_spawn(
  task=...,
  mode="run",
  label="judge",
  model="claude-sonnet-4-5"
)
```

### 4.3 保存（由 subagent 直接完成飞书文档创建）

⚠️ **重要：subagent 直接创建飞书文档，只把链接和判定结果返回主 session**

在 STEP 4.1 构建 subagent task 时，在末尾追加：
```
完成裁判评判后，请执行以下操作：
1. 将完整评判写入本地文件 debate-outputs/YYYY-MM-DD/04_judge.md
2. 调用 feishu_create_doc 创建飞书文档：
   - title: "[{辩题}] 04-裁判评判"
   - folder_token: "<从TOOLS.md读取，未配置则省略>"
   - content: 完整裁判评判
3. 只返回以下信息：
   【裁判评判已创建】
   链接：{飞书文档链接}
   胜负判定：{己方获胜 / 己方落败}
   核心理由：{2-3句话概括判定理由}
   修正建议摘要：{列出最关键的2-3条修正建议}
```

主 session 收到结果后：
1. 更新 `current-task.json`：`files.judge = 文件路径`，`feishu_links.judge = 文档链接`
2. 根据返回的胜负判定，执行 STEP 4.4 的分支逻辑

### 4.4 处理裁判结果（关键分支）

**判断裁判结果中是否包含「己方获胜」：**

**情况A：己方获胜**
→ 直接进入 STEP 4.5

**情况B：己方落败**
→ 告知用户：「裁判判定己方落败。原因：[摘录裁判的核心理由]。是否需要返工修正立论和攻防？」
  - 用户说「返工」→ 回到 STEP 1.5，重新确认论点框架（可参考裁判的修正建议），重新跑立论和攻防，直到裁判判定获胜
  - 用户说「继续输出」→ 进入 STEP 4.5

---

## STEP 4.5：修缮立论 + 生成实战攻防稿（新增）

> 目的：基于裁判反馈和攻防结果，生成两份最终交付物：修缮后的立论稿 + 实战攻防稿。
> 两个任务并行 spawn subagent，互不依赖。

### 4.5.1 并行 spawn 两个 subagent

**任务A：修缮立论**

```
task 内容：
---
{references/02-Argument-Agent.md 内容}
---
【立论框架知识库】
{references/01-立论框架.md 内容}
---
【立论示例】
{references/立论示例.md 内容}
---

现在开始执行：修缮立论

辩题：{topic}
持方：{pro_side}

原始立论稿（请读取）：
{debate-outputs/YYYY-MM-DD/02_argument.md}

裁判评判（请读取）：
{debate-outputs/YYYY-MM-DD/04_judge.md}

修缮要求：
1. 保留裁判认为最有利的论点，强化其论证
2. 修复裁判指出的薄弱点（重写论点句或补充论证）
3. 论点句必须通过反转测试（不可被轻松反转）
4. 禁止写"对方说XXX，我们反驳"——防守口径融入论点内部
5. 字数仍然 ≤ 1100 字
6. 输出完整的修缮版立论稿，可以直接上场念

首选模型：claude-sonnet-4-5
```

```
sessions_spawn(
  task=任务A,
  mode="run",
  label="revised_argument",
  model="claude-sonnet-4-5"
)
```

**任务B：生成实战攻防稿**

```
task 内容：
---
{references/04-Defense-Agent.md 内容}
---
【反驳与攻防技巧知识库】
{references/02-反驳与攻防技巧.md 内容}
---
【攻防稿示例（严格按此格式输出）】
{references/攻防稿示例.md 内容}
---

现在开始执行：生成实战攻防稿

辩题：{topic}
持方：{pro_side}

攻防记录（请读取以下文件）：
{debate-outputs/YYYY-MM-DD/03_round_1.md}
{debate-outputs/YYYY-MM-DD/03_round_2.md}（如有）
{debate-outputs/YYYY-MM-DD/03_round_3.md}（如有）

裁判评判（请读取）：
{debate-outputs/YYYY-MM-DD/04_judge.md}

输出要求：
- 严格按照攻防稿示例.md 的格式
- 必须包含：框架速查 / 攻击角度速查 / 论点攻防（每个论点的对方攻击 + A/B/C分层反驳口径）/ 质询问题 / 收束口径
- 这是实战备战手册，不是攻防过程的原始记录
- 语言简洁口语化，可以直接上场用
- 禁止把攻防原文照搬进来，必须重新整理成备战格式

首选模型：claude-sonnet-4-5
```

```
sessions_spawn(
  task=任务B,
  mode="run",
  label="battle_guide",
  model="claude-sonnet-4-5"
)
```

### 4.5.2 等待两个 subagent 完成（由 subagent 直接完成飞书文档创建）

⚠️ **重要：两个 subagent 各自直接创建飞书文档，只把链接返回主 session**

**在 STEP 4.5.1 的任务A（修缮立论）task 末尾追加：**
```
完成修缮立论后，请执行以下操作：
1. 将完整修缮版立论稿写入本地文件 debate-outputs/YYYY-MM-DD/05_revised_argument.md
2. 调用 feishu_create_doc 创建飞书文档：
   - title: "[{辩题}] 05-修缮立论稿"
   - folder_token: "<从TOOLS.md读取，未配置则省略>"
   - content: 完整修缮版立论稿
3. 只返回以下信息：
   【修缮立论稿已创建】
   链接：{飞书文档链接}
   主要修改摘要：{列出2-3条核心修改点}
```

**在 STEP 4.5.1 的任务B（实战攻防稿）task 末尾追加：**
```
完成实战攻防稿后，请执行以下操作：
1. 将完整攻防稿写入本地文件 debate-outputs/YYYY-MM-DD/06_battle_guide.md
2. 调用 feishu_create_doc 创建飞书文档：
   - title: "[{辩题}] 06-实战攻防稿"
   - folder_token: "<从TOOLS.md读取，未配置则省略>"
   - content: 完整实战攻防稿
3. 只返回以下信息：
   【实战攻防稿已创建】
   链接：{飞书文档链接}
   包含章节：{列出攻防稿的主要章节名称}
```

**主 session 收到两个 subagent 结果后：**
1. 更新 `current-task.json`：
   - `files.revised_argument = 文件路径`，`feishu_links.revised_argument = 链接`
   - `files.battle_guide = 文件路径`，`feishu_links.battle_guide = 链接`
2. 进入 STEP 5

---

## STEP 5：创建目录页

> 不再合并所有内容到一个巨型文档，改为创建目录页，链接到各步骤的独立文档。
> 大幅降低 context 压力和超时风险。

### 5.1 生成目录页内容

```markdown
# [{辩题}] 辩论备赛文档目录

> 辩题：{topic}
> 持方：{pro_side}
> 生成时间：{YYYY-MM-DD}

## 文档导航

| 序号 | 文档 | 链接 |
|------|------|------|
| 01 | 资料稿 | {feishu_links.research} |
| 02 | 立论稿（初版） | {feishu_links.argument} |
| 03-R1 | 第1轮攻防 | {feishu_links.rounds[0]} |
| 03-R2 | 第2轮攻防 | {feishu_links.rounds[1]}（如有）|
| 03-R3 | 第3轮攻防 | {feishu_links.rounds[2]}（如有）|
| 04 | 裁判评判 | {feishu_links.judge} |
| 05 | 修缮立论稿 ⭐ | {feishu_links.revised_argument} |
| 06 | 实战攻防稿 ⭐ | {feishu_links.battle_guide} |

⭐ = 上场直接用的核心文档
```

### 5.2 创建飞书文档

```
feishu_create_doc(
  title="[{辩题}] 辩论备赛目录",
  folder_token=FEISHU_FOLDER_TOKEN  # 从TOOLS.md读取,
  content=目录页内容
)
```

### 5.3 收尾

1. 写入 `debate-outputs/YYYY-MM-DD/00_index.md`
2. 更新 `current-task.json`：`status = "done"`，`feishu_links.index = 目录页链接`
3. **发目录页链接给用户，并说明各文档用途**

---

## 分步调用模式

用户只要求单个环节时，直接执行对应 STEP，跳过其他步骤。

| 用户说 | 执行 |
|--------|------|
| 只要资料 | STEP 1 |
| 只要立论 | STEP 1.5 → STEP 2（需要用户提供资料稿或先跑 STEP 1）|
| 只要反方攻击 | STEP 3.1（需要用户提供立论稿）|
| 只要攻防回应 | STEP 3.2（需要用户提供立论稿 + 反方攻击稿）|
| 只要裁判评判 | STEP 4（需要用户提供立论稿 + 攻防记录）|
| 只要修缮立论 | STEP 4.5 任务A（需要用户提供立论稿 + 裁判评判）|
| 只要攻防稿 | STEP 4.5 任务B（需要用户提供攻防记录 + 裁判评判）|

---

## 常见错误 & 处理方式

| 错误 | 处理 |
|------|------|
| 资料稿为空 | 停止，告知用户，不继续 |
| subagent 超时 | 换 `model="claude-sonnet-4-5"` 重试一次；仍失败则告知用户 |
| 立论稿包含【模块一】等格式标签 | 重新调用 Argument Agent，明确要求「纯自然语言，可以直接念出来」|
| 攻防稿格式不符合示例 | 重新调用对应 Agent，附上攻防稿示例，要求严格按示例格式 |
| 立论稿出现"有研究指出"等模糊引用 | 重新调用 Argument Agent，要求引用必须说明具体来源和年份，格式为「20XX年[机构/学者]」，禁止英文期刊名和机构缩写 |
| 论点句自检报告缺失 | 重新调用 Argument Agent，要求补充自检步骤 |
| 两个论点本质相同 | 回到 STEP 1.5，重新确认论点框架 |
| 飞书文档创建失败 | 将文档链接列表发给用户，说明哪个文档创建失败，其余文档正常 |
| 4.5 任务A/B 其中一个失败 | 告知用户哪个任务失败，另一个成功的正常发链接，失败的询问是否重试 |
