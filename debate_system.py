#!/usr/bin/env python3
"""
辩论系统集成 Skill - 主脚本
实现完整辩论流程，每个阶段生成后先确认再继续
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# 配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
DEBATE_AGENTS_DIR = WORKSPACE / "debate-agents"
DEBATE_OUTPUTS_DIR = WORKSPACE / "debate-outputs"
DEBATE_OUTPUTS_DIR.mkdir(exist_ok=True)

# 飞书文件夹 token（从 TOOLS.md 读取，未配置则为空）
TOOLS_FILE = WORKSPACE / "TOOLS.md"
FEISHU_FOLDER_TOKEN = ""  # 默认为空，存入根目录


def load_feishu_folder_token():
    """从 TOOLS.md 读取飞书文件夹 token"""
    global FEISHU_FOLDER_TOKEN
    if TOOLS_FILE.exists():
        content = TOOLS_FILE.read_text(encoding="utf-8")
        for line in content.split("\n"):
            if "默认文件夹" in line and "**:" in line:
                # 解析格式：- **默认文件夹**: <token>
                parts = line.split(":", 1)
                if len(parts) == 2:
                    token = parts[1].strip()
                    if token:
                        FEISHU_FOLDER_TOKEN = token
                        break


def call_subagent(agent_id: str, message: str, timeout: int = 300) -> str:
    """调用子 Agent"""
    try:
        result = subprocess.run(
            ["openclaw", "agent", "--agent", agent_id, "--message", message],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return f"[Error] Agent {agent_id} timed out after {timeout} seconds"
    except Exception as e:
        return f"[Error] Failed to call agent {agent_id}: {str(e)}"


def save_output(stage: str, content: str) -> Path:
    """保存输出到文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{stage}_{timestamp}.md"
    filepath = DEBATE_OUTPUTS_DIR / filename
    filepath.write_text(content, encoding="utf-8")
    return filepath


def get_user_confirmation(prompt: str) -> bool:
    """获取用户确认（这里模拟，实际使用时需要交互式输入）"""
    # 在实际使用中，这里应该通过聊天界面获取用户确认
    # 目前先默认返回 True，后续完善
    print(f"\n[确认] {prompt}")
    print("默认继续... (在实际使用中会等待用户确认)")
    return True


def run_research_stage(topic: str) -> str:
    """运行资料检索阶段"""
    print("\n" + "="*80)
    print("阶段 1：资料检索")
    print("="*80)

    # 加载 Research Agent 的 prompt
    prompt_file = DEBATE_AGENTS_DIR / "01-Research-Agent.md"
    if not prompt_file.exists():
        return "[Error] Research Agent prompt not found"

    prompt = prompt_file.read_text(encoding="utf-8")
    task = f"{prompt}\n\n现在请检索关于以下辩题的资料：\n辩题：{topic}"

    # 调用 Research Agent
    result = call_subagent("research", task)

    # 保存输出
    filepath = save_output("01_research", result)
    print(f"资料稿已保存到：{filepath}")

    # 检查是否失败
    if "[Error]" in result or "无法确认" in result:
        print("\n⚠️  警告：资料检索可能失败！")
        print("请确认是否继续？")

    # 获取用户确认
    if not get_user_confirmation("资料稿已生成，是否继续？"):
        print("用户取消流程")
        sys.exit(0)

    return result


def run_argument_stage(topic: str, pro_side: str, research_content: str) -> str:
    """运行立论阶段"""
    print("\n" + "="*80)
    print("阶段 2：正方立论")
    print("="*80)

    # 加载 Argument Agent 的 prompt
    prompt_file = DEBATE_AGENTS_DIR / "02-Argument-Agent.md"
    if not prompt_file.exists():
        return "[Error] Argument Agent prompt not found"

    prompt = prompt_file.read_text(encoding="utf-8")
    task = f"""{prompt}

辩题：{topic}
持方：{pro_side}

以下是检索到的资料：
{research_content}

请基于以上资料生成立论稿。"""

    # 调用 Argument Agent
    result = call_subagent("argument", task)

    # 保存输出
    filepath = save_output("02_argument", result)
    print(f"立论稿已保存到：{filepath}")

    # 获取用户确认
    if not get_user_confirmation("立论稿已生成，是否继续？"):
        print("用户取消流程")
        sys.exit(0)

    return result


def run_opposition_stage(topic: str, argument_content: str, round_num: int) -> str:
    """运行反方攻击阶段"""
    print(f"\n" + "="*80)
    print(f"阶段 3：反方攻击（第 {round_num} 轮）")
    print("="*80)

    # 加载 Opposition Agent 的 prompt
    prompt_file = DEBATE_AGENTS_DIR / "03-Opposition-Agent.md"
    if not prompt_file.exists():
        return "[Error] Opposition Agent prompt not found"

    prompt = prompt_file.read_text(encoding="utf-8")
    task = f"""{prompt}

辩题：{topic}

以下是正方立论稿：
{argument_content}

请对正方立论进行最强攻击。"""

    # 调用 Opposition Agent
    result = call_subagent("opposition", task)

    # 保存输出
    filepath = save_output(f"03_opposition_round{round_num}", result)
    print(f"反方攻击稿（第 {round_num} 轮）已保存到：{filepath}")

    # 获取用户确认
    if not get_user_confirmation(f"反方攻击稿（第 {round_num} 轮）已生成，是否继续？"):
        print("用户取消流程")
        sys.exit(0)

    return result


def run_defense_stage(topic: str, pro_side: str, argument_content: str, opposition_content: str, round_num: int) -> str:
    """运行正方防守阶段"""
    print(f"\n" + "="*80)
    print(f"阶段 4：正方防守（第 {round_num} 轮）")
    print("="*80)

    # 加载 Defense Agent 的 prompt
    prompt_file = DEBATE_AGENTS_DIR / "04-Defense-Agent.md"
    if not prompt_file.exists():
        return "[Error] Defense Agent prompt not found"

    prompt = prompt_file.read_text(encoding="utf-8")
    task = f"""{prompt}

辩题：{topic}
持方：{pro_side}

以下是正方立论稿：
{argument_content}

以下是反方攻击稿：
{opposition_content}

请对反方攻击进行回应。"""

    # 调用 Defense Agent
    result = call_subagent("defense", task)

    # 保存输出
    filepath = save_output(f"04_defense_round{round_num}", result)
    print(f"正方防守稿（第 {round_num} 轮）已保存到：{filepath}")

    # 获取用户确认
    if not get_user_confirmation(f"正方防守稿（第 {round_num} 轮）已生成，是否继续？"):
        print("用户取消流程")
        sys.exit(0)

    return result


def run_judge_stage(topic: str, pro_side: str, argument_content: str, opposition_contents: list, defense_contents: list) -> str:
    """运行裁判阶段"""
    print("\n" + "="*80)
    print("阶段 5：裁判评判")
    print("="*80)

    # 加载 Judge Agent 的 prompt
    prompt_file = DEBATE_AGENTS_DIR / "05-Judge-Agent.md"
    if not prompt_file.exists():
        return "[Error] Judge Agent prompt not found"

    prompt = prompt_file.read_text(encoding="utf-8")

    # 整理攻防记录
    attack_defense_records = ""
    for i, (opp, defs) in enumerate(zip(opposition_contents, defense_contents), 1):
        attack_defense_records += f"\n--- 第 {i} 轮攻防 ---\n"
        attack_defense_records += f"反方攻击：\n{opp}\n"
        attack_defense_records += f"正方回应：\n{defs}\n"

    task = f"""{prompt}

辩题：{topic}
持方：{pro_side}

以下是正方立论稿：
{argument_content}

以下是攻防记录：
{attack_defense_records}

请进行裁判评判。"""

    # 调用 Judge Agent
    result = call_subagent("judge", task)

    # 保存输出
    filepath = save_output("05_judge", result)
    print(f"裁判评判文档已保存到：{filepath}")

    return result


def merge_final_document(topic: str, pro_side: str, research_content: str, argument_content: str, opposition_contents: list, defense_contents: list, judge_content: str) -> str:
    """合并最终文档"""
    print("\n" + "="*80)
    print("阶段 6：合并最终文档")
    print("="*80)

    # 整理攻防记录
    attack_defense_records = ""
    for i, (opp, defs) in enumerate(zip(opposition_contents, defense_contents), 1):
        attack_defense_records += f"\n## 第 {i} 轮攻防\n"
        attack_defense_records += f"### 反方攻击\n{opp}\n"
        attack_defense_records += f"### 正方回应\n{defs}\n"

    # 合并文档
    final_content = f"""# 完整辩论结果

## 辩题
{topic}

## 持方
{pro_side}

---

## 一、资料稿
{research_content}

---

## 二、正方立论稿
{argument_content}

---

## 三、攻防对战记录
{attack_defense_records}

---

## 四、裁判评判文档
{judge_content}
"""

    # 保存最终文档
    filepath = save_output("00_final_document", final_content)
    print(f"最终文档已保存到：{filepath}")

    return final_content


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="辩论系统集成 Skill")
    parser.add_argument("command", choices=["debate", "research", "argument", "opposition", "defense", "judge"], help="命令")
    parser.add_argument("--topic", required=True, help="辩题")
    parser.add_argument("--pro", help="正方持方（完整流程和立论时需要）")
    parser.add_argument("--rounds", type=int, default=2, help="攻防轮数（默认 2 轮）")
    parser.add_argument("--research", help="资料稿内容（分步调用时使用）")
    parser.add_argument("--argument", help="立论稿内容（分步调用时使用）")
    parser.add_argument("--opposition", help="反方攻击稿内容（分步调用时使用）")
    parser.add_argument("--defense", help="正方防守稿内容（分步调用时使用）")

    args = parser.parse_args()

    load_feishu_folder_token()

    if args.command == "debate":
        # 完整流程
        if not args.pro:
            print("错误：完整流程需要 --pro 参数指定正方持方")
            sys.exit(1)

        # 阶段 1：资料检索
        research_content = run_research_stage(args.topic)

        # 阶段 2：正方立论
        argument_content = run_argument_stage(args.topic, args.pro, research_content)

        # 阶段 3-4：攻防对战
        opposition_contents = []
        defense_contents = []
        for round_num in range(1, args.rounds + 1):
            opposition_content = run_opposition_stage(args.topic, argument_content, round_num)
            opposition_contents.append(opposition_content)

            defense_content = run_defense_stage(args.topic, args.pro, argument_content, opposition_content, round_num)
            defense_contents.append(defense_content)

        # 阶段 5：裁判评判
        judge_content = run_judge_stage(args.topic, args.pro, argument_content, opposition_contents, defense_contents)

        # 阶段 6：合并最终文档
        final_content = merge_final_document(args.topic, args.pro, research_content, argument_content, opposition_contents, defense_contents, judge_content)

        print("\n" + "="*80)
        print("完整辩论流程完成！")
        print("="*80)

    elif args.command == "research":
        # 仅资料检索
        research_content = run_research_stage(args.topic)
        print("\n资料检索完成！")

    elif args.command == "argument":
        # 仅立论
        if not args.pro:
            print("错误：立论需要 --pro 参数指定正方持方")
            sys.exit(1)
        if not args.research:
            print("错误：立论需要 --research 参数提供资料稿内容")
            sys.exit(1)
        argument_content = run_argument_stage(args.topic, args.pro, args.research)
        print("\n立论完成！")

    elif args.command == "opposition":
        # 仅反方攻击
        if not args.argument:
            print("错误：反方攻击需要 --argument 参数提供立论稿内容")
            sys.exit(1)
        opposition_content = run_opposition_stage(args.topic, args.argument, 1)
        print("\n反方攻击完成！")

    elif args.command == "defense":
        # 仅正方防守
        if not args.pro:
            print("错误：正方防守需要 --pro 参数指定正方持方")
            sys.exit(1)
        if not args.argument:
            print("错误：正方防守需要 --argument 参数提供立论稿内容")
            sys.exit(1)
        if not args.opposition:
            print("错误：正方防守需要 --opposition 参数提供反方攻击稿内容")
            sys.exit(1)
        defense_content = run_defense_stage(args.topic, args.pro, args.argument, args.opposition, 1)
        print("\n正方防守完成！")

    elif args.command == "judge":
        # 仅裁判评判
        if not args.pro:
            print("错误：裁判评判需要 --pro 参数指定正方持方")
            sys.exit(1)
        if not args.argument:
            print("错误：裁判评判需要 --argument 参数提供立论稿内容")
            sys.exit(1)
        # 这里简化处理，实际需要攻防记录
        judge_content = run_judge_stage(args.topic, args.pro, args.argument, [], [])
        print("\n裁判评判完成！")


if __name__ == "__main__":
    main()
