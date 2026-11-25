"""generator 模块单元测试。"""

import json
import re
import unittest
from typing import List

from wordproblems.checker import evaluate_expression
from wordproblems.generator import (
    Problem,
    generate_problems,
    normalize_steps,
    validate_count,
    validate_seed,
)

SCENARIOS = {"购物", "图书", "行程", "分配", "面积"}


class GeneratorArgumentTest(unittest.TestCase):
    """参数校验。"""

    def test_default_count(self) -> None:
        self.assertEqual(len(generate_problems()), 10)

    def test_count_matches_requested(self) -> None:
        self.assertEqual(len(generate_problems(7, seed=1)), 7)

    def test_count_one_allowed(self) -> None:
        self.assertEqual(len(generate_problems(1, seed=2)), 1)

    def test_count_max_allowed(self) -> None:
        self.assertEqual(len(generate_problems(200, seed=3)), 200)

    def test_count_zero_raises(self) -> None:
        with self.assertRaises(ValueError):
            generate_problems(0, seed=4)

    def test_count_negative_raises(self) -> None:
        with self.assertRaises(ValueError):
            generate_problems(-1, seed=4)

    def test_count_above_max_raises(self) -> None:
        with self.assertRaises(ValueError):
            generate_problems(201, seed=4)

    def test_count_float_raises(self) -> None:
        with self.assertRaises(ValueError):
            generate_problems(5.0, seed=4)  # type: ignore[arg-type]

    def test_count_string_raises(self) -> None:
        with self.assertRaises(ValueError):
            generate_problems("5", seed=4)  # type: ignore[arg-type]

    def test_count_bool_raises(self) -> None:
        with self.assertRaises(ValueError):
            generate_problems(True, seed=4)

    def test_seed_reproducible(self) -> None:
        first = generate_problems(8, seed=42, steps="mixed")
        second = generate_problems(8, seed=42, steps="mixed")
        self.assertEqual([item.text for item in first], [item.text for item in second])
        self.assertEqual([item.answer for item in first], [item.answer for item in second])

    def test_different_seed_differs(self) -> None:
        first = [item.text for item in generate_problems(6, seed=1, steps="mixed")]
        second = [item.text for item in generate_problems(6, seed=2, steps="mixed")]
        self.assertNotEqual(first, second)

    def test_seed_none_allowed(self) -> None:
        self.assertEqual(len(generate_problems(3, seed=None)), 3)

    def test_seed_float_raises(self) -> None:
        with self.assertRaises(ValueError):
            generate_problems(3, seed=1.5)  # type: ignore[arg-type]

    def test_seed_bool_raises(self) -> None:
        with self.assertRaises(ValueError):
            generate_problems(3, seed=True)

    def test_steps_invalid_string_raises(self) -> None:
        with self.assertRaises(ValueError):
            generate_problems(3, seed=5, steps="3")

    def test_steps_invalid_int_raises(self) -> None:
        with self.assertRaises(ValueError):
            generate_problems(3, seed=5, steps=3)

    def test_steps_bool_raises(self) -> None:
        with self.assertRaises(ValueError):
            generate_problems(3, seed=5, steps=True)  # type: ignore[arg-type]

    def test_normalize_steps_values(self) -> None:
        self.assertEqual(normalize_steps("1"), "1")
        self.assertEqual(normalize_steps(1), "1")
        self.assertEqual(normalize_steps(" 2 "), "2")
        self.assertEqual(normalize_steps("MIXED"), "mixed")

    def test_validate_count_returns_value(self) -> None:
        self.assertEqual(validate_count(15), 15)

    def test_validate_seed_returns_value(self) -> None:
        self.assertEqual(validate_seed(7), 7)
        self.assertIsNone(validate_seed(None))


class ProblemConstraintTest(unittest.TestCase):
    """题目内容约束。"""

    def setUp(self) -> None:
        self.problems: List[Problem] = generate_problems(60, seed=42, steps="mixed")

    def test_answers_are_non_negative_integers(self) -> None:
        for problem in self.problems:
            self.assertIsInstance(problem.answer, int)
            self.assertGreaterEqual(problem.answer, 0)

    def test_expression_matches_answer(self) -> None:
        for problem in self.problems:
            self.assertAlmostEqual(
                evaluate_expression(problem.expression), float(problem.answer), places=9
            )

    def test_one_step_only(self) -> None:
        problems = generate_problems(12, seed=6, steps="1")
        self.assertTrue(problems)
        for problem in problems:
            self.assertEqual(problem.steps_count, 1)
            self.assertEqual(problem.kind, "一步题")
            self.assertIn("列式计算", problem.steps[0])

    def test_two_step_only(self) -> None:
        problems = generate_problems(12, seed=6, steps="2")
        self.assertTrue(problems)
        for problem in problems:
            self.assertEqual(problem.steps_count, 2)
            self.assertEqual(problem.kind, "两步题")
            self.assertEqual(len(problem.steps), 2)

    def test_steps_int_equals_string(self) -> None:
        with_int = generate_problems(6, seed=8, steps=1)
        with_str = generate_problems(6, seed=8, steps="1")
        self.assertEqual([item.text for item in with_int], [item.text for item in with_str])

    def test_mixed_contains_both_kinds(self) -> None:
        kinds = {problem.steps_count for problem in self.problems}
        self.assertEqual(kinds, {1, 2})

    def test_two_step_has_two_steps(self) -> None:
        for problem in self.problems:
            if problem.steps_count == 2:
                self.assertEqual(len(problem.steps), 2)
                self.assertTrue(all(step for step in problem.steps))

    def test_one_step_has_steps(self) -> None:
        for problem in self.problems:
            if problem.steps_count == 1:
                self.assertEqual(len(problem.steps), 1)

    def test_division_is_exact(self) -> None:
        divisions = [
            item
            for item in self.problems
            if item.steps_count == 1 and " / " in item.expression
        ]
        self.assertTrue(divisions)
        for problem in divisions:
            value = evaluate_expression(problem.expression)
            self.assertTrue(float(value).is_integer())

    def test_multiplication_limits(self) -> None:
        multiplications = [
            item
            for item in self.problems
            if item.steps_count == 1 and " * " in item.expression
        ]
        self.assertTrue(multiplications)
        for problem in multiplications:
            match = re.match(r"^(\d+) \* (\d+)$", problem.expression)
            self.assertIsNotNone(match)
            assert match is not None
            left = int(match.group(1))
            right = int(match.group(2))
            self.assertLessEqual(left, 12)
            self.assertLessEqual(right, 12)
            self.assertEqual(left * right, problem.answer)

    def test_division_limits(self) -> None:
        divisions = [
            item
            for item in self.problems
            if item.steps_count == 1 and " / " in item.expression
        ]
        for problem in divisions:
            match = re.match(r"^(\d+) / (\d+)$", problem.expression)
            self.assertIsNotNone(match)
            assert match is not None
            dividend = int(match.group(1))
            divisor = int(match.group(2))
            self.assertLessEqual(dividend, 200)
            self.assertLessEqual(divisor, 12)
            self.assertEqual(dividend % divisor, 0)

    def test_text_contains_digits(self) -> None:
        for problem in self.problems:
            self.assertTrue(any(char.isdigit() for char in problem.text))

    def test_scenarios_are_known(self) -> None:
        for problem in self.problems:
            self.assertIn(problem.scenario, SCENARIOS)

    def test_kind_matches_steps_count(self) -> None:
        for problem in self.problems:
            expected = "一步题" if problem.steps_count == 1 else "两步题"
            self.assertEqual(problem.kind, expected)

    def test_difficulty_bounds(self) -> None:
        for problem in self.problems:
            if problem.steps_count == 1:
                self.assertIn(problem.difficulty, (1, 2))
            else:
                self.assertEqual(problem.difficulty, 3)

    def test_no_duplicate_texts(self) -> None:
        problems = generate_problems(120, seed=9, steps="mixed")
        texts = [problem.text for problem in problems]
        self.assertEqual(len(texts), len(set(texts)))

    def test_steps_is_list(self) -> None:
        for problem in self.problems:
            self.assertIsInstance(problem.steps, list)

    def test_to_dict_json_serializable(self) -> None:
        payload = [problem.to_dict() for problem in self.problems]
        dumped = json.dumps(payload, ensure_ascii=False)
        self.assertEqual(len(json.loads(dumped)), len(payload))

    def test_to_dict_fields(self) -> None:
        data = self.problems[0].to_dict()
        self.assertEqual(
            set(data.keys()),
            {
                "text",
                "expression",
                "answer",
                "steps",
                "kind",
                "steps_count",
                "difficulty",
                "scenario",
            },
        )
        self.assertIsInstance(data["steps"], list)

    def test_one_step_difficulty_consistent(self) -> None:
        problems = generate_problems(20, seed=11, steps=1)
        self.assertTrue(any(problem.difficulty == 1 for problem in problems))
        self.assertTrue(any(problem.difficulty == 2 for problem in problems))


if __name__ == "__main__":
    unittest.main()
