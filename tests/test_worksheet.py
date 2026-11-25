"""worksheet 模块单元测试。"""

import unittest
from typing import List, Optional

from wordproblems.generator import Problem, generate_problems
from wordproblems.worksheet import ordered_problems, render_answers, render_worksheet


def make_problem(
    text: str = "小明有 3 个苹果，又买了 2 个，一共有多少个苹果？",
    expression: str = "3 + 2",
    answer: int = 5,
    steps: Optional[List[str]] = None,
    kind: str = "一步题",
    steps_count: int = 1,
    difficulty: int = 1,
    scenario: str = "购物",
) -> Problem:
    """构造测试用题目。"""
    if steps is None:
        steps = ["列式计算：3 + 2 = 5"]
    return Problem(
        text=text,
        expression=expression,
        answer=answer,
        steps=steps,
        kind=kind,
        steps_count=steps_count,
        difficulty=difficulty,
        scenario=scenario,
    )


class WorksheetRenderTest(unittest.TestCase):
    """练习纸渲染。"""

    def setUp(self) -> None:
        self.problems: List[Problem] = generate_problems(6, seed=7, steps="mixed")
        self.html = render_worksheet(self.problems)

    def test_problem_count_matches(self) -> None:
        self.assertEqual(self.html.count('<div class="problem">'), len(self.problems))

    def test_document_structure(self) -> None:
        self.assertTrue(self.html.startswith("<!DOCTYPE html>"))
        self.assertIn('<html lang="zh-CN">', self.html)
        self.assertIn('<meta charset="utf-8">', self.html)
        self.assertIn("</html>", self.html)

    def test_a4_print_style(self) -> None:
        self.assertIn("@page", self.html)
        self.assertIn("A4", self.html)
        self.assertIn("@media print", self.html)

    def test_inline_answers_included_by_default(self) -> None:
        self.assertIn("<details>", self.html)
        self.assertIn("<summary>参考答案</summary>", self.html)

    def test_inline_answers_can_be_removed(self) -> None:
        page = render_worksheet(self.problems, include_answers=False)
        self.assertNotIn("<details>", page)
        self.assertNotIn("参考答案", page)

    def test_problem_text_present(self) -> None:
        for problem in self.problems:
            self.assertIn(problem.text, self.html)

    def test_workline_count(self) -> None:
        expected = sum(2 if item.steps_count == 2 else 1 for item in self.problems)
        self.assertEqual(self.html.count('class="workline"'), expected)

    def test_worklines_use_dashed_border(self) -> None:
        self.assertIn("border-bottom: 1px dashed", self.html)

    def test_meta_counts(self) -> None:
        one_step = sum(1 for item in self.problems if item.steps_count == 1)
        two_step = len(self.problems) - one_step
        self.assertIn(
            "共 {0} 题（一步 {1} 题 / 两步 {2} 题）".format(
                len(self.problems), one_step, two_step
            ),
            self.html,
        )

    def test_answers_include_expression(self) -> None:
        for problem in self.problems:
            self.assertIn(problem.expression, self.html)

    def test_order_by_difficulty(self) -> None:
        easy = make_problem(text="简单题", difficulty=1)
        hard = make_problem(
            text="难题",
            expression="2 * 3 + 4",
            answer=10,
            steps=["先算 2 × 3 = 6", "再算 6 + 4 = 10"],
            kind="两步题",
            steps_count=2,
            difficulty=3,
        )
        page = render_worksheet([hard, easy], include_answers=False)
        self.assertLess(page.index("简单题"), page.index("难题"))

    def test_duplicate_text_removed(self) -> None:
        problem = make_problem()
        page = render_worksheet([problem, problem, make_problem(text="另一题")])
        self.assertEqual(page.count('<div class="problem">'), 2)

    def test_ordered_problems_deduplicates(self) -> None:
        problem = make_problem()
        ordered = ordered_problems([problem, problem])
        self.assertEqual(len(ordered), 1)

    def test_problem_text_escaped(self) -> None:
        problem = make_problem(text="买 <script>alert(1)</script> 个苹果？")
        page = render_worksheet([problem])
        self.assertIn("&lt;script&gt;", page)
        self.assertNotIn("<script>", page)

    def test_title_escaped(self) -> None:
        page = render_worksheet([make_problem()], title="练习 <A4>")
        self.assertIn("<title>练习 &lt;A4&gt;</title>", page)

    def test_empty_problem_list(self) -> None:
        page = render_worksheet([])
        self.assertIn("共 0 题（一步 0 题 / 两步 0 题）", page)
        self.assertNotIn("<details>", page)
        self.assertEqual(page.count('<div class="problem">'), 0)


class AnswersRenderTest(unittest.TestCase):
    """独立答案页渲染。"""

    def setUp(self) -> None:
        self.problems = generate_problems(5, seed=13, steps="mixed")

    def test_answers_page_structure(self) -> None:
        page = render_answers(self.problems)
        self.assertTrue(page.startswith("<!DOCTYPE html>"))
        self.assertIn("<table", page)
        self.assertIn("题号", page)
        self.assertIn("答案", page)

    def test_answers_page_numbering(self) -> None:
        page = render_answers(self.problems)
        self.assertIn('<td class="number">1</td>', page)
        self.assertIn('<td class="number">5</td>', page)

    def test_answers_page_contains_steps(self) -> None:
        page = render_answers(self.problems)
        for problem in self.problems:
            for step in problem.steps:
                self.assertIn(step, page)

    def test_answers_page_contains_expressions(self) -> None:
        page = render_answers(self.problems)
        for problem in self.problems:
            self.assertIn(problem.expression, page)

    def test_answers_page_escapes_title(self) -> None:
        page = render_answers([make_problem()], title="参考答案 <A4>")
        self.assertIn("参考答案 &lt;A4&gt;", page)

    def test_answers_page_escapes_steps(self) -> None:
        problem = make_problem(steps=["先算 <b>3 + 2</b>"])
        page = render_answers([problem])
        self.assertIn("&lt;b&gt;", page)
        self.assertNotIn("<b>", page)

    def test_answers_page_empty(self) -> None:
        page = render_answers([])
        self.assertIn("共 0 题", page)
        self.assertNotIn('<td class="number">', page)


if __name__ == "__main__":
    unittest.main()
