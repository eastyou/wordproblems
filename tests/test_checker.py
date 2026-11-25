"""checker 模块单元测试。"""

import unittest

from wordproblems.checker import check_answer, evaluate_expression, format_number


class EvaluateExpressionTest(unittest.TestCase):
    """安全表达式求值。"""

    def test_addition(self) -> None:
        self.assertEqual(evaluate_expression("3 + 4"), 7)

    def test_precedence(self) -> None:
        self.assertEqual(evaluate_expression("3*4+2"), 14)

    def test_parentheses(self) -> None:
        self.assertEqual(evaluate_expression("(3+4)*2"), 14)

    def test_left_associativity(self) -> None:
        self.assertEqual(evaluate_expression("10 - 2 - 3"), 5)

    def test_decimal(self) -> None:
        self.assertEqual(evaluate_expression("1.5 + 2.5"), 4)

    def test_decimal_division(self) -> None:
        self.assertEqual(evaluate_expression("  7 / 2 "), 3.5)

    def test_division(self) -> None:
        self.assertEqual(evaluate_expression("8 / 4"), 2)

    def test_negative_operand(self) -> None:
        self.assertEqual(evaluate_expression("-3 + 5"), 2)

    def test_unary_plus(self) -> None:
        self.assertEqual(evaluate_expression("+4"), 4)

    def test_leading_dot_decimal(self) -> None:
        self.assertEqual(evaluate_expression(".5 + .5"), 1)

    def test_nested_parentheses(self) -> None:
        self.assertEqual(evaluate_expression("((2 + 3) * (4 - 1)) / 5"), 3)

    def test_returns_float(self) -> None:
        self.assertIsInstance(evaluate_expression("1 + 1"), float)

    def test_function_call_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_expression("abs(1)")

    def test_variable_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_expression("x + 1")

    def test_power_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_expression("2 ** 3")

    def test_modulo_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_expression("5 % 2")

    def test_floor_division_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_expression("5 // 2")

    def test_division_by_zero_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_expression("1 / 0")

    def test_division_by_zero_expression_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_expression("1 / (2 - 2)")

    def test_semicolon_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_expression("1; 2")

    def test_empty_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_expression("")

    def test_blank_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_expression("   ")

    def test_thousands_separator_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_expression("1,000")

    def test_dangling_operator_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_expression("5 -")

    def test_letters_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_expression("10 apples")

    def test_too_long_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_expression("1" * 201)

    def test_non_string_type_rejected(self) -> None:
        with self.assertRaises(TypeError):
            evaluate_expression(123)  # type: ignore[arg-type]

    def test_none_rejected(self) -> None:
        with self.assertRaises(TypeError):
            evaluate_expression(None)  # type: ignore[arg-type]


class CheckAnswerTest(unittest.TestCase):
    """答案比对。"""

    def test_correct_integer(self) -> None:
        correct, expected = check_answer("3*4+2", 14)
        self.assertTrue(correct)
        self.assertEqual(expected, 14)

    def test_incorrect_integer(self) -> None:
        correct, expected = check_answer("3*4+2", 15)
        self.assertFalse(correct)
        self.assertEqual(expected, 14)

    def test_correct_string_answer(self) -> None:
        correct, expected = check_answer("3*4+2", "14")
        self.assertTrue(correct)
        self.assertEqual(expected, 14)

    def test_correct_decimal_string(self) -> None:
        correct, _ = check_answer("7/2", "3.5")
        self.assertTrue(correct)

    def test_incorrect_decimal(self) -> None:
        correct, expected = check_answer("7/2", 3)
        self.assertFalse(correct)
        self.assertEqual(expected, 3.5)

    def test_float_answer(self) -> None:
        correct, _ = check_answer("1 + 1", 2.0)
        self.assertTrue(correct)

    def test_tolerance_for_float_error(self) -> None:
        correct, _ = check_answer("0.1 + 0.2", 0.3)
        self.assertTrue(correct)

    def test_bool_answer_rejected(self) -> None:
        with self.assertRaises(ValueError):
            check_answer("1 + 1", True)

    def test_nan_answer_rejected(self) -> None:
        with self.assertRaises(ValueError):
            check_answer("1 + 1", float("nan"))

    def test_inf_answer_rejected(self) -> None:
        with self.assertRaises(ValueError):
            check_answer("1 + 1", float("inf"))

    def test_invalid_string_answer_rejected(self) -> None:
        with self.assertRaises(ValueError):
            check_answer("1 + 1", "abc")

    def test_blank_string_answer_rejected(self) -> None:
        with self.assertRaises(ValueError):
            check_answer("1 + 1", "   ")

    def test_none_answer_rejected(self) -> None:
        with self.assertRaises(ValueError):
            check_answer("1 + 1", None)  # type: ignore[arg-type]

    def test_huge_answer_rejected(self) -> None:
        with self.assertRaises(ValueError):
            check_answer("1 + 1", 10 ** 400)

    def test_invalid_expression_raises(self) -> None:
        with self.assertRaises(ValueError):
            check_answer("__import__('os')", 1)

    def test_zero_division_expression_raises(self) -> None:
        with self.assertRaises(ValueError):
            check_answer("1/0", 0)


class FormatNumberTest(unittest.TestCase):
    """数字格式化。"""

    def test_integer_value(self) -> None:
        self.assertEqual(format_number(14.0), "14")

    def test_decimal_value(self) -> None:
        self.assertEqual(format_number(14.5), "14.5")

    def test_float_rounding(self) -> None:
        self.assertEqual(format_number(0.1 + 0.2), "0.3")

    def test_int_input(self) -> None:
        self.assertEqual(format_number(7), "7")

    def test_infinite_rejected(self) -> None:
        with self.assertRaises(ValueError):
            format_number(float("inf"))

    def test_bool_rejected(self) -> None:
        with self.assertRaises(ValueError):
            format_number(True)

    def test_huge_int_rejected(self) -> None:
        with self.assertRaises(ValueError):
            format_number(10 ** 400)


if __name__ == "__main__":
    unittest.main()
