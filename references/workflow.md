# 辩论系统完整执行手册

> 本文件是防呆执行手册。每一步都有明确的「做什么」「怎么做」「检查什么」。
> **不允许跳步、不允许合并步骤、不允许自行发挥。**

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
    "final": ""
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
文件3: references/资料库示例.md

拼接格式：
---
{文件1内容}
---
{文件2内容}
---
{文件3内容}
---

现在开始执行：
辩题：{topic}
请检索正反双方资料，严格按照资料库示例的格式输出资料卡。
注意：只查近10年（2015年至今）的资料。
```

### 1.2 调用 subagent

```
sessions_spawn(
  task=上面拼接的字符串,
  mode="run",
  label="research"
)
```

### 1.3 检查结果（必须执行）

- 结果是否包含至少1个完整的【资料卡】？
- 如果结果为空、报错、或没有任何资料卡 → **停止，告知用户资料检索失败，不得继续**
- 如果有资料卡 → 继续

### 1.4 保存 & 发飞书文档

1. 将结果写入 `debate-outputs/YYYY-MM-DD/01_research.md`
2. 用 `feishu_doc` 创建文档，`folder_token=Qey5fKwF7lZxXWd01TycvrPknJc`，标题：`[辩题] 资料稿`
3. 更新 `current-task.json`：`files.research = 文件路径`，`stage = "argument"`
4. 发飞书文档链接给用户，等待确认

**等用户说「继续」或「好的」之类的确认后，才进入 STEP 2。**

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

执行步骤（必须按顺序）：
第一步：完全不看资料稿，独立构建最强立论框架。需要数据/案例支撑的地方，先写[待补充：需要XXX方面的资料]占位。
第二步：读以下资料稿，将匹配的资料填入对应[待补充]位置。
第三步：检查是否还有未填充的[待补充]。如果有，在回复末尾列出：
  【需要补充检索的关键词】
  - 关键词1
  - 关键词2

资料稿：
{文件5内容}
```

### 2.2 调用 subagent

```
sessions_spawn(task=..., mode="run", label="argument")
```

### 2.3 检查是否需要补充资料

- 结果末尾是否有【需要补充检索的关键词】？
- 如果有，且 `argument_research_retry < 2`：
  1. 用这些关键词重新调用 Research Agent（参考 STEP 1，但只搜这些关键词）
  2. `argument_research_retry += 1`
  3. 将新资料追加到资料稿，重新执行 STEP 2.1（第二步和第三步）
- 如果 `argument_research_retry >= 2` 或没有待补充项 → 继续

### 2.4 保存 & 发飞书文档

1. 写入 `debate-outputs/YYYY-MM-DD/02_argument.md`
2. 创建飞书文档，标题：`[辩题] 正方立论稿`
3. 更新 `current-task.json`：`files.argument = 路径`，`stage = "opposition_round_1"`
4. 发链接给用户，等待确认

---

## STEP 3：攻防循环（最多3轮）

每轮包含两个子步骤：Opposition → Defense。

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
前轮攻防记录：
{前轮 opposition + defense 内容}

请对正方立论进行最强攻击，严格按照攻防稿示例格式输出。
```

调用：`sessions_spawn(task=..., mode="run", label="opposition_round_N")`

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

调用：`sessions_spawn(task=..., mode="run", label="defense_round_N")`

### 3.3 每轮结束后

1. 将本轮 opposition + defense 写入 `debate-outputs/YYYY-MM-DD/03_round_N.md`
2. 追加到 `current-task.json`：`files.opposition[N]`、`files.defense[N]`
3. 创建飞书文档，标题：`[辩题] 第N轮攻防稿`
4. 发链接给用户，等待确认是否继续下一轮

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

正方立论稿：
{立论稿内容}

攻防记录（共{N}轮）：
{所有轮次的 opposition + defense 内容}

请给出完整裁判评判，必须包含：
1. 己方最有利的观点
2. 己方最薄弱的观点
3. 攻击对方最痛的点
4. 修正建议
5. 明确的胜负判定（己方获胜 / 己方落败）
```

### 4.2 调用 subagent

```
sessions_spawn(task=..., mode="run", label="judge")
```

### 4.3 处理裁判结果（关键分支）

**判断裁判结果中是否包含「己方获胜」：**

**情况A：己方获胜**
→ 直接进入 STEP 5

**情况B：己方落败**
→ 告知用户：「裁判判定己方落败。原因：[摘录裁判的核心理由]。是否需要返工修正立论和攻防？」
  - 用户说「返工」→ 回到 STEP 2，重新生成立论（可参考裁判的修正建议），重新跑攻防，直到裁判判定获胜
  - 用户说「继续输出」→ 进入 STEP 5

### 4.4 保存

1. 写入 `debate-outputs/YYYY-MM-DD/04_judge.md`
2. 更新 `current-task.json`：`files.judge = 路径`

---

## STEP 5：输出最终文档

### 5.1 合并内容

按以下顺序合并，用标题区分：

```markdown
# [辩题] 完整辩论文档

## 一、资料稿
{01_research.md 内容}

---

## 二、正方立论稿
{02_argument.md 内容}

---

## 三、攻防稿
{所有轮次 03_round_N.md 内容，每轮用「### 第N轮」区分}

---

## 四、裁判评判
{04_judge.md 内容}
```

### 5.2 创建飞书文档

```
feishu_doc(
  action="create",
  title="[辩题] 完整辩论文档",
  folder_token="Qey5fKwF7lZxXWd01TycvrPknJc",
  content=合并后的内容
)
```

### 5.3 收尾

1. 写入 `debate-outputs/YYYY-MM-DD/00_final.md`
2. 更新 `current-task.json`：`status = "done"`，`files.final = 路径`
3. 发最终文档链接给用户

---

## 分步调用模式

用户只要求单个环节时，直接执行对应 STEP，跳过其他步骤。

| 用户说 | 执行 |
|--------|------|
| 只要资料 | STEP 1 |
| 只要立论 | STEP 2（需要用户提供资料稿或先跑 STEP 1）|
| 只要反方攻击 | STEP 3.1（需要用户提供立论稿）|
| 只要攻防回应 | STEP 3.2（需要用户提供立论稿 + 反方攻击稿）|
| 只要裁判评判 | STEP 4（需要用户提供立论稿 + 攻防记录）|

---

## 常见错误 & 处理方式

| 错误 | 处理 |
|------|------|
| 资料稿为空 | 停止，告知用户，不继续 |
| subagent 超时 | 告知用户，询问是否重试 |
| 立论稿包含【模块一】等格式标签 | 重新调用 Argument Agent，明确要求「纯自然语言，可以直接念出来」|
| 攻防稿格式不符合示例 | 重新调用对应 Agent，附上攻防稿示例，要求严格按示例格式 |
| 飞书文档创建失败 | 将内容直接发给用户，说明飞书创建失败 |
