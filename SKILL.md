# 辩论系统集成 Skill

## 激活条件

当用户要求进行辩论相关的任务时激活，包括：
- 生成完整辩论流程
- 检索辩论资料
- 生成立论稿
- 生成攻防稿
- 裁判评判

## 核心功能

### 1. 完整流程调用
自动调用五个辩论 Agent 完成完整辩论流程：
- Research Agent（资料检索官）
- Argument Agent（正方立论构建官）
- Opposition Agent（反方博弈官）
- Defense Agent（攻防整合官）
- Judge Agent（裁判官）

### 2. 分步调用
支持单独调用某个 Agent：
- `/debate-research` - 仅检索资料
- `/debate-argument` - 仅生成立论稿
- `/debate-opposition` - 仅生成反方攻击稿
- `/debate-defense` - 仅生成攻防回应稿
- `/debate-judge` - 仅进行裁判评判

### 3. 流程确认
每个关键阶段生成后都会先询问用户确认，用户同意后再继续：
- 资料稿生成后确认
- 立论稿生成后确认
- 每轮攻防稿生成后确认

### 4. 飞书文档输出
最终将所有稿件合并，自动上传到飞书文档。

## 使用方法

### 完整流程
```bash
python ~/.openclaw/workspace/skills/debate-system/debate_system.py debate --topic "辩题内容" --pro "正方持方" --rounds 2
```

### 分步调用
```bash
# 仅检索资料
python ~/.openclaw/workspace/skills/debate-system/debate_system.py research --topic "辩题内容"

# 仅生成立论稿
python ~/.openclaw/workspace/skills/debate-system/debate_system.py argument --topic "辩题内容" --pro "正方持方" --research "资料稿内容"

# 仅生成反方攻击稿
python ~/.openclaw/workspace/skills/debate-system/debate_system.py opposition --topic "辩题内容" --argument "立论稿内容"

# 仅生成攻防回应稿
python ~/.openclaw/workspace/skills/debate-system/debate_system.py defense --topic "辩题内容" --pro "正方持方" --argument "立论稿内容" --opposition "反方攻击稿"

# 仅进行裁判评判
python ~/.openclaw/workspace/skills/debate-system/debate_system.py judge --topic "辩题内容" --pro "正方持方" --argument "立论稿" --opposition "反方攻击稿" --defense "攻防回应稿"
```

## 包含文件

- **debate-agents/**：五个辩论 Agent 的 system prompt
- **debate-knowledge/**：完整的辩论知识库
- **debate_system.py**：主脚本，实现完整流程和分步调用
- **README.md**：使用说明文档

## 核心原则

1. **事实红线**：所有资料必须有权威来源，禁止编造
2. **格式规范**：严格按照用户提供的示例格式输出
3. **阶段确认**：每个关键阶段必须用户确认后才能继续
4. **资料补充**：立论和攻防阶段可补充资料最多 2 次

## 依赖

- Tavily API key（配置在 .env 文件中）
- Agent Reach（已安装）
- 五个辩论 Agent（已配置）
