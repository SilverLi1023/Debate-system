# 辩论系统集成 Skill

## 简介

这是一个用于 OpenClaw 的辩论系统集成 Skill，可以自动调用五个辩论 Agent 完成完整辩论流程。

## 功能

- **完整流程调用**：自动调用五个辩论 Agent 完成完整辩论流程
- **分步调用**：支持单独调用某个 Agent
- **流程确认**：每个关键阶段生成后都会先询问用户确认
- **飞书文档输出**：最终将所有稿件合并，自动上传到飞书文档

## 安装

1. 将 `debate-system` 目录复制到 OpenClaw 的 skills 目录：
   ```bash
   cp -r debate-system ~/.openclaw/workspace/skills/
   ```

2. 确保脚本有执行权限：
   ```bash
   chmod +x ~/.openclaw/workspace/skills/debate-system/debate_system.py
   ```

## 使用方法

### 完整流程

```bash
python ~/.openclaw/workspace/skills/debate-system/debate_system.py debate --topic "辩题内容" --pro "正方持方" --rounds 2
```

### 分步调用

#### 仅检索资料

```bash
python ~/.openclaw/workspace/skills/debate-system/debate_system.py research --topic "辩题内容"
```

#### 仅生成立论稿

```bash
python ~/.openclaw/workspace/skills/debate-system/debate_system.py argument --topic "辩题内容" --pro "正方持方" --research "资料稿内容"
```

#### 仅生成反方攻击稿

```bash
python ~/.openclaw/workspace/skills/debate-system/debate_system.py opposition --topic "辩题内容" --argument "立论稿内容"
```

#### 仅生成正方防守稿

```bash
python ~/.openclaw/workspace/skills/debate-system/debate_system.py defense --topic "辩题内容" --pro "正方持方" --argument "立论稿内容" --opposition "反方攻击稿内容"
```

#### 仅进行裁判评判

```bash
python ~/.openclaw/workspace/skills/debate-system/debate_system.py judge --topic "辩题内容" --pro "正方持方" --argument "立论稿内容"
```

## 辩论 Agent

- **Research（资料检索官）**：检索和整理辩论资料
- **Argument（正方立论构建官）**：生成正方立论稿
- **Opposition（反方博弈官）**：生成反方攻击稿
- **Defense（攻防整合官）**：生成正方防守稿
- **Judge（裁判官）**：评判胜负并提供建议

## 配置

### 飞书文件夹

默认飞书文件夹 token 为：`Qey5fKwF7lZxXWd01TycvrPknJc`

可以在 `TOOLS.md` 中修改默认文件夹 token。

## 输出文件

所有输出文件会保存到：`/root/.openclaw/workspace/debate-outputs/`

## 核心原则

1. **事实红线**：所有资料必须有权威来源，禁止编造
2. **格式规范**：严格按照用户提供的示例格式输出
3. **阶段确认**：每个关键阶段必须用户确认后才能继续
4. **资料补充**：立论和攻防阶段可补充资料最多 2 次

## 许可证

MIT
