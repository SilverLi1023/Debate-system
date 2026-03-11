# 🎙️ 辩论备赛系统 (Debate System)

一个为 [OpenClaw](https://github.com/openclaw/openclaw) 构建的辩论备赛 Skill。给出辩题和持方，自动完成 **资料检索 → 立论构建 → 攻防对战 → 裁判评判 → 修缮立论 → 实战攻防稿**，全程输出到飞书文档。

## ✨ 特性

- **五大 Agent 协作**：资料检索官、立论构建官、反方博弈官、攻防整合官、裁判官
- **完整流程 & 分步调用**：支持一键跑完全流程，也可以单独跑某个阶段
- **每步确认**：关键阶段生成后先征求用户意见，再进入下一步
- **飞书文档输出**：所有稿件自动写入飞书云文档，对话中只发链接
- **知识库驱动**：内置辩论理论参考（立论框架、反驳技巧、价值排序、评委判准等）

## 📦 安装

### 方式一：Git Clone（推荐）

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/SilverLi1023/Debate-system-1023.git debate-system
```

### 方式二：手动复制

将整个 `debate-system/` 目录放到以下任意位置：

- `<workspace>/skills/debate-system/` — 仅当前 agent 可用
- `~/.openclaw/skills/debate-system/` — 所有 agent 共享

安装后 **开一个新 session** 即可生效。

## 🔧 前置依赖

- **OpenClaw** — 本 skill 作为 OpenClaw agent skill 运行
- **飞书插件**（可选）— 需要配置飞书 OpenClaw 插件（用于输出文档）
  - 安装：参考 [飞书插件文档](https://github.com/openclaw/feishu-openclaw-plugin)
  - 配置后可直接输出到飞书云文档，无需手动复制粘贴
- **联网搜索** — 资料检索阶段需要 agent 有 web search 能力

> 如果不用飞书，agent 会将稿件以 Markdown 文件保存到本地 `debate-outputs/` 目录。

## 🚀 使用方法

在 OpenClaw 对话中直接说：

```
帮我准备辩论，辩题是「社交媒体利大于弊」，我是正方
```

触发词：`辩题`、`立论`、`攻防`、`辩论资料`、`帮我准备辩论`

### 分步调用

- **仅检索资料**：`帮我查辩论资料，辩题是 XXX`
- **仅写立论**：`帮我写立论，辩题是 XXX，我方持方是 XXX`
- **仅跑攻防**：`帮我做攻防演练`
- **仅裁判评判**：`帮我评判一下这份立论`

### 示例输出

完整流程会生成以下飞书文档（或本地 Markdown 文件）：

1. **资料库** — 20+ 条高质量资料卡片，含来源、时间、核心观点
2. **立论稿** — 完整的正方立论，包含价值、标准、论点、论证
3. **攻防稿** — 预判反方攻击 + 防守策略
4. **裁判评判** — 模拟裁判视角的评分和改进建议
5. **修缮立论** — 根据裁判意见优化后的最终版本

## 📁 文件结构

```
debate-system/
├── SKILL.md                     ← Skill 入口（OpenClaw 自动读取）
├── README.md                    ← 本文件
├── LICENSE                      ← MIT 协议
└── references/
    ├── workflow.md              ← 完整执行手册（核心）
    ├── 01-Research-Agent.md     ← 资料检索 agent prompt
    ├── 02-Argument-Agent.md     ← 立论构建 agent prompt
    ├── 03-Opposition-Agent.md   ← 反方攻击 agent prompt
    ├── 04-Defense-Agent.md      ← 攻防整合 agent prompt
    ├── 05-Judge-Agent.md        ← 裁判评判 agent prompt
    ├── 00-核心原则.md
    ├── 01-立论框架.md
    ├── 02-反驳与攻防技巧.md
    ├── 03-价值排序与比较方法.md
    ├── 04-资料检索与使用规范.md
    ├── 05-环节执行与评委判准.md
    ├── 立论示例.md
    ├── 攻防稿示例.md
    └── 资料库示例.md
```

## ⚙️ 配置

### 飞书文档输出目录

默认写入飞书根目录。如需指定文件夹，在你的 `TOOLS.md` 中添加：

```markdown
### 飞书文档配置
- **默认文件夹**: 你的文件夹token
```

## 🔒 核心原则

1. **事实红线** — 所有资料必须有权威来源，禁止编造数据
2. **格式规范** — 严格按照内置示例格式输出
3. **阶段确认** — 每个关键阶段完成后等用户确认才继续
4. **文档分发** — 稿件写飞书文档，对话中不直接输出正文

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

- 发现 bug？[提交 Issue](https://github.com/SilverLi1023/Debate-system-1023/issues)
- 有改进建议？欢迎 PR
- 想分享使用经验？在 Discussions 里聊聊

## 📄 License

MIT
