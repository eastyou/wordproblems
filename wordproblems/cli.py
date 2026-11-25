"""wordproblems 命令行入口。"""

import argparse
import json
import sys
from typing import List, Optional, Sequence

from wordproblems import __version__
from wordproblems.checker import check_answer, format_number
from wordproblems.generator import (
    Problem,
    format_problems,
    generate_problems,
)
from wordproblems.worksheet import render_answers, render_worksheet


def _ensure_utf8_console() -> None:
    """尽力把标准输出与标准错误切换为 UTF-8，避免中文乱码。"""
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            continue


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="wordproblems",
        description="小学应用题自动生成器：一步题、两步题、打印练习纸与答案校验。",
    )
    subparsers = parser.add_subparsers(
        dest="command", metavar="COMMAND", required=True
    )

    gen_parser = subparsers.add_parser(
        "gen", help="生成题目并输出到终端", description="在终端输出题目、答案与解题步骤。"
    )
    gen_parser.add_argument(
        "--count", type=int, default=10, metavar="N", help="题目数量，1~200（默认 10）"
    )
    gen_parser.add_argument(
        "--seed", type=int, default=None, metavar="N", help="随机种子，用于复现同一组题目"
    )
    gen_parser.add_argument(
        "--steps",
        choices=["1", "2", "mixed"],
        default="mixed",
        help="步数：1 一步题，2 两步题，mixed 混合（默认 mixed）",
    )
    gen_parser.add_argument(
        "--json", dest="json_output", action="store_true", help="以 JSON 格式输出，便于脚本处理"
    )

    sheet_parser = subparsers.add_parser(
        "sheet", help="生成可打印的 HTML 练习纸", description="生成 A4 版式的 HTML 练习纸，答案可单独输出。"
    )
    sheet_parser.add_argument(
        "--count", type=int, default=10, metavar="N", help="题目数量，1~200（默认 10）"
    )
    sheet_parser.add_argument(
        "--seed", type=int, default=None, metavar="N", help="随机种子，用于复现同一组题目"
    )
    sheet_parser.add_argument(
        "--steps",
        choices=["1", "2", "mixed"],
        default="mixed",
        help="步数：1 一步题，2 两步题，mixed 混合（默认 mixed）",
    )
    sheet_parser.add_argument(
        "--out", default="problems.html", metavar="PATH", help="练习纸输出路径（默认 problems.html）"
    )
    sheet_parser.add_argument(
        "--answers-out",
        default=None,
        metavar="PATH",
        help="参考答案单独输出路径；不指定时答案附在练习纸末尾",
    )

    check_parser = subparsers.add_parser(
        "check", help="校验算式与答案", description="安全计算算式并校验用户答案。"
    )
    check_parser.add_argument(
        "--expr", required=True, metavar="EXPR", help="待校验的算式，例如 3*4+2"
    )
    check_parser.add_argument(
        "--answer", required=True, metavar="VALUE", help="用户给出的答案"
    )

    subparsers.add_parser(
        "demo", help="打印一段示例", description="打印一段生成与校验的示例，便于快速了解用法。"
    )
    return parser


def _format_problems_json(
    problems: Sequence[Problem], seed: Optional[int], steps: str
) -> str:
    """把题目列表序列化为 JSON 文本。"""
    payload = {
        "count": len(problems),
        "seed": seed,
        "steps": steps,
        "problems": [problem.to_dict() for problem in problems],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _write_text(path: str, content: str) -> None:
    """以 UTF-8 写文件；写入失败时转为带中文提示的 ValueError。"""
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
    except OSError as exc:
        raise ValueError(
            "写入文件失败：{0}（{1}）".format(path, exc.strerror or exc)
        ) from exc


def _run_gen(args: argparse.Namespace) -> int:
    """执行 gen 子命令。"""
    problems = generate_problems(args.count, args.seed, args.steps)
    if args.json_output:
        print(_format_problems_json(problems, args.seed, args.steps))
    else:
        print(format_problems(problems))
    return 0


def _run_sheet(args: argparse.Namespace) -> int:
    """执行 sheet 子命令。"""
    problems = generate_problems(args.count, args.seed, args.steps)
    if args.answers_out:
        page = render_worksheet(problems, include_answers=False)
        answers_page = render_answers(problems)
        _write_text(args.out, page)
        _write_text(args.answers_out, answers_page)
        print("练习题已写入：{0}".format(args.out))
        print("参考答案已写入：{0}".format(args.answers_out))
    else:
        page = render_worksheet(problems, include_answers=True)
        _write_text(args.out, page)
        print("练习题已写入：{0}（含参考答案）".format(args.out))
    return 0


def _run_check(args: argparse.Namespace) -> int:
    """执行 check 子命令。"""
    correct, expected = check_answer(args.expr, args.answer)
    if correct:
        print("正确")
    else:
        print("错误，正确答案是 {0}".format(format_number(expected)))
    return 0


def _run_demo() -> int:
    """执行 demo 子命令。"""
    problems = generate_problems(2, seed=2026, steps="mixed")
    correct, _ = check_answer("3*4+2", 14)
    lines: List[str] = [
        "wordproblems {0} 示例".format(__version__),
        "",
        format_problems(problems),
        "",
        "校验示例：wordproblems check --expr \"3*4+2\" --answer 14",
        "结果：{0}".format("正确" if correct else "错误"),
    ]
    print("\n".join(lines))
    return 0


def _run(args: argparse.Namespace) -> int:
    """按子命令分发执行。"""
    if args.command == "gen":
        return _run_gen(args)
    if args.command == "sheet":
        return _run_sheet(args)
    if args.command == "check":
        return _run_check(args)
    if args.command == "demo":
        return _run_demo()
    raise ValueError("未知子命令：{0}".format(args.command))


def main(argv: Optional[Sequence[str]] = None) -> int:
    """命令行主函数，成功返回 0，参数或运算错误返回 2。"""
    _ensure_utf8_console()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except (TypeError, ValueError) as exc:
        print("错误：{0}".format(exc), file=sys.stderr)
        return 2
