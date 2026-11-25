"""cli 模块单元测试。"""

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from typing import List, Sequence, Tuple

from wordproblems.cli import main


class CliTestCase(unittest.TestCase):
    """提供统一的命令行调用辅助方法。"""

    def run_cli(self, argv: Sequence[str]) -> Tuple[int, str, str]:
        """执行命令行并捕获返回码、标准输出与标准错误。"""
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(list(argv))
        return code, stdout.getvalue(), stderr.getvalue()


class GenCommandTest(CliTestCase):
    """gen 子命令。"""

    def test_gen_returns_zero(self) -> None:
        code, out, err = self.run_cli(["gen", "--count", "3", "--seed", "42"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertIn("第 1 题", out)
        self.assertIn("答案：", out)

    def test_gen_count_lines(self) -> None:
        code, out, _ = self.run_cli(["gen", "--count", "4", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count("答案："), 4)

    def test_gen_steps_one(self) -> None:
        _, out, _ = self.run_cli(
            ["gen", "--count", "6", "--seed", "3", "--steps", "1"]
        )
        self.assertNotIn("两步题", out)

    def test_gen_steps_two(self) -> None:
        _, out, _ = self.run_cli(
            ["gen", "--count", "6", "--seed", "3", "--steps", "2"]
        )
        self.assertIn("两步题", out)
        self.assertNotIn("一步题", out)

    def test_gen_reproducible(self) -> None:
        first = self.run_cli(["gen", "--count", "5", "--seed", "99"])[1]
        second = self.run_cli(["gen", "--count", "5", "--seed", "99"])[1]
        self.assertEqual(first, second)

    def test_gen_json_structure(self) -> None:
        code, out, _ = self.run_cli(
            ["gen", "--count", "5", "--seed", "42", "--json"]
        )
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["count"], 5)
        self.assertEqual(payload["seed"], 42)
        self.assertEqual(payload["steps"], "mixed")
        self.assertEqual(len(payload["problems"]), 5)

    def test_gen_json_problem_fields(self) -> None:
        _, out, _ = self.run_cli(["gen", "--count", "2", "--seed", "7", "--json"])
        problem = json.loads(out)["problems"][0]
        for key in (
            "text",
            "expression",
            "answer",
            "steps",
            "kind",
            "steps_count",
            "difficulty",
            "scenario",
        ):
            self.assertIn(key, problem)
        self.assertIsInstance(problem["steps"], list)

    def test_gen_json_seed_null(self) -> None:
        _, out, _ = self.run_cli(["gen", "--count", "1", "--json"])
        self.assertIsNone(json.loads(out)["seed"])

    def test_gen_count_zero_returns_two(self) -> None:
        code, out, err = self.run_cli(["gen", "--count", "0", "--seed", "1"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertTrue(err.startswith("错误："))

    def test_gen_count_too_large_returns_two(self) -> None:
        code, _, err = self.run_cli(["gen", "--count", "201", "--seed", "1"])
        self.assertEqual(code, 2)
        self.assertTrue(err.startswith("错误："))

    def test_gen_invalid_steps_exits(self) -> None:
        with self.assertRaises(SystemExit) as context:
            with redirect_stderr(io.StringIO()):
                main(["gen", "--count", "2", "--steps", "3"])
        self.assertEqual(context.exception.code, 2)

    def test_gen_invalid_count_exits(self) -> None:
        with self.assertRaises(SystemExit) as context:
            with redirect_stderr(io.StringIO()):
                main(["gen", "--count", "abc"])
        self.assertEqual(context.exception.code, 2)


class SheetCommandTest(CliTestCase):
    """sheet 子命令。"""

    def test_sheet_writes_inline_answers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "problems.html")
            code, out, err = self.run_cli(
                [
                    "sheet",
                    "--count",
                    "6",
                    "--seed",
                    "7",
                    "--steps",
                    "mixed",
                    "--out",
                    path,
                ]
            )
            self.assertEqual(code, 0)
            self.assertEqual(err, "")
            self.assertIn(path, out)
            with open(path, "r", encoding="utf-8") as handle:
                page = handle.read()
            self.assertIn("<details>", page)
            self.assertIn("参考答案", page)
            self.assertEqual(page.count('<div class="problem">'), 6)

    def test_sheet_writes_separate_answers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            page_path = os.path.join(tmp, "problems.html")
            answer_path = os.path.join(tmp, "answers.html")
            code, _, _ = self.run_cli(
                [
                    "sheet",
                    "--count",
                    "4",
                    "--seed",
                    "8",
                    "--out",
                    page_path,
                    "--answers-out",
                    answer_path,
                ]
            )
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(page_path))
            self.assertTrue(os.path.exists(answer_path))
            with open(page_path, "r", encoding="utf-8") as handle:
                page = handle.read()
            with open(answer_path, "r", encoding="utf-8") as handle:
                answers = handle.read()
            self.assertNotIn("<details>", page)
            self.assertIn("<table", answers)
            self.assertIn("题号", answers)

    def test_sheet_invalid_count_returns_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "problems.html")
            code, _, err = self.run_cli(
                ["sheet", "--count", "0", "--seed", "1", "--out", path]
            )
            self.assertEqual(code, 2)
            self.assertTrue(err.startswith("错误："))
            self.assertFalse(os.path.exists(path))

    def test_sheet_write_failure_returns_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "missing", "problems.html")
            code, _, err = self.run_cli(
                ["sheet", "--count", "2", "--seed", "1", "--out", path]
            )
            self.assertEqual(code, 2)
            self.assertTrue(err.startswith("错误："))
            self.assertIn("写入文件失败", err)

    def test_sheet_default_out_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = os.getcwd()
            os.chdir(tmp)
            try:
                code, _, _ = self.run_cli(["sheet", "--count", "2", "--seed", "1"])
            finally:
                os.chdir(old_cwd)
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(os.path.join(tmp, "problems.html")))


class CheckCommandTest(CliTestCase):
    """check 子命令。"""

    def test_check_correct(self) -> None:
        code, out, err = self.run_cli(
            ["check", "--expr", "3*4+2", "--answer", "14"]
        )
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "正确")
        self.assertEqual(err, "")

    def test_check_incorrect(self) -> None:
        code, out, _ = self.run_cli(
            ["check", "--expr", "3*4+2", "--answer", "15"]
        )
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "错误，正确答案是 14")

    def test_check_decimal(self) -> None:
        code, out, _ = self.run_cli(["check", "--expr", "7/2", "--answer", "3.5"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "正确")

    def test_check_division_by_zero_returns_two(self) -> None:
        code, _, err = self.run_cli(["check", "--expr", "1/0", "--answer", "0"])
        self.assertEqual(code, 2)
        self.assertTrue(err.startswith("错误："))
        self.assertIn("除数不能为 0", err)

    def test_check_invalid_expression_returns_two(self) -> None:
        code, _, err = self.run_cli(
            ["check", "--expr", "abs(1)", "--answer", "1"]
        )
        self.assertEqual(code, 2)
        self.assertTrue(err.startswith("错误："))

    def test_check_invalid_answer_returns_two(self) -> None:
        code, _, err = self.run_cli(
            ["check", "--expr", "1+1", "--answer", "abc"]
        )
        self.assertEqual(code, 2)
        self.assertTrue(err.startswith("错误："))

    def test_check_missing_expr_exits(self) -> None:
        with self.assertRaises(SystemExit) as context:
            with redirect_stderr(io.StringIO()):
                main(["check", "--answer", "14"])
        self.assertEqual(context.exception.code, 2)


class MiscCommandTest(CliTestCase):
    """demo、帮助与整体行为。"""

    def test_demo_returns_zero(self) -> None:
        code, out, err = self.run_cli(["demo"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertIn("示例", out)
        self.assertIn("第 1 题", out)
        self.assertIn("正确", out)

    def test_help_exits_zero(self) -> None:
        buffer = io.StringIO()
        with self.assertRaises(SystemExit) as context:
            with redirect_stdout(buffer):
                main(["--help"])
        self.assertEqual(context.exception.code, 0)
        self.assertIn("wordproblems", buffer.getvalue())

    def test_no_command_exits_two(self) -> None:
        with self.assertRaises(SystemExit) as context:
            with redirect_stderr(io.StringIO()):
                main([])
        self.assertEqual(context.exception.code, 2)

    def test_unknown_command_exits_two(self) -> None:
        with self.assertRaises(SystemExit) as context:
            with redirect_stderr(io.StringIO()):
                main(["unknown"])
        self.assertEqual(context.exception.code, 2)

    def test_gen_json_output_is_pure_json(self) -> None:
        _, out, _ = self.run_cli(["gen", "--count", "3", "--seed", "5", "--json"])
        self.assertNotIn("第 1 题", out)
        payload = json.loads(out)
        self.assertEqual(len(payload["problems"]), 3)

    def test_cli_accepts_list_argv(self) -> None:
        argv: List[str] = ["check", "--expr", "2 + 2", "--answer", "4"]
        code, out, _ = self.run_cli(argv)
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "正确")


if __name__ == "__main__":
    unittest.main()
