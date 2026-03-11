---
name: debate-system
description: 辩论备赛系统。用户给出辩题和持方时激活，自动完成资料检索、论点框架确认、正方立论（含论点句自检）、攻防对战、裁判评判、修缮立论、实战攻防稿，输出目录页飞书文档。支持完整流程和分步调用（仅资料/仅立论/仅攻防/仅裁判/仅修缮）。触发词：辩题、立论、攻防、辩论资料、帮我准备辩论。
---

# 辩论系统

## 激活后第一步：读 workflow

**立即执行：**
read("skills/debate-system/references/workflow.md")

workflow.md 是完整的防呆执行手册，包含每个步骤的 task 模板、检查点、分支处理。**严格按照 workflow.md 执行，不得跳步或自行发挥。**

## 文件结构
references/
├── workflow.md              ← 执行手册（必读）
├── 01-Research-Agent.md     ← 资料检索 agent prompt
├── 02-Argument-Agent.md     ← 立论构建 agent prompt（含论点句自检）
├── 03-Opposition-Agent.md   ← 反方攻击 agent prompt
├── 04-Defense-Agent.md      ← 攻防整合 agent prompt
├── 05-Judge-Agent.md        ← 裁判评判 agent prompt
├── 00-核心原则.md
├── 01-立论框架.md
├── 02-反驳与攻防技巧.md
├── 03-价值排序与比较方法.md
├── 04-资料检索与使用规范.md
├── 05-环节执行与评委判准.md
├── 攻防稿示例.md
├── 立论示例.md
└── 资料库示例.md

## 核心约束（不可违反）
1. 禁止在对话中直接输出稿件内容，所有稿件写飞书文档，只发链接
2. 每个阶段必须等用户确认后才继续
3. 资料稿失败必须停止，不得在无资料的情况下继续生成立论
4. 每个 subagent 调用必须注入对应知识库（workflow.md 中有明确列表）
5. 飞书文档放入文件夹：优先读取用户 TOOLS.md 中 `### 飞书文档配置` 下的 `**默认文件夹**` token；若未配置则不指定文件夹（存入根目录）
6. 每步完成后立即创建独立飞书文档，主 session 只保存文档链接，不保留完整稿件文本
