"""安全表达式求值与答案校验。

只允许数字、``+ - * / ( )`` 与空白字符，使用 :mod:`ast` 解析并限定节点类型，
避免执行任意代码。
"""

import ast
import math
import re
from typing import Tuple, Union

Number = Union[int, float]
CheckResult = Tuple[bool, float]

_MAX_EXPRESSION_LENGTH = 200
_ALLOWED_CHARS = set("0123456789.+-*/() ")
_NUMBER_PATTERN = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$")

_ALLOWED_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Constant,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.UAdd,
    ast.USub,
)


def _validate_node(node: ast.AST) -> None:
    """递归检查语法树，只允许数字与四则运算节点。"""
    if not isinstance(node, _ALLOWED_NODES):
        raise ValueError("表达式包含不支持的语法：{0}".format(type(node).__name__))
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise ValueError("表达式只能包含数字")
        return
    for child in ast.iter_child_nodes(node):
        _validate_node(child)


def _eval_node(node: ast.AST) -> float:
    """对已校验的语法树求值，除数为 0 时抛出 ValueError。"""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant):
        return float(node.value)
    if isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        if isinstance(node.op, ast.USub):
            return -operand
        return operand
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            if right == 0:
                raise ValueError("除数不能为 0")
            return left / right
    raise ValueError("表达式包含不支持的运算")


def evaluate_expression(expr: str) -> float:
    """安全计算四则运算表达式，返回浮点结果。

    参数:
        expr: 仅含数字、``+ - * / ( )`` 与空格的表达式。

    异常:
        TypeError: ``expr`` 不是字符串。
        ValueError: 表达式为空、过长、含非法字符、语法错误或除数为 0。
    """
    if not isinstance(expr, str):
        raise TypeError("表达式必须是字符串")
    text = expr.strip()
    if not text:
        raise ValueError("表达式不能为空")
    if len(text) > _MAX_EXPRESSION_LENGTH:
        raise ValueError("表达式过长，不能超过 {0} 个字符".format(_MAX_EXPRESSION_LENGTH))
    for char in text:
        if char not in _ALLOWED_CHARS and not char.isspace():
            raise ValueError("表达式只能包含数字、+ - * / ( ) 和空格")
    try:
        tree = ast.parse(text, mode="eval")
    except SyntaxError as exc:
        raise ValueError("表达式语法错误：{0}".format(exc.msg)) from exc
    _validate_node(tree)
    result = _eval_node(tree)
    if not math.isfinite(result):
        raise ValueError("计算结果超出可用范围")
    return result


def _coerce_number(value: Union[Number, str]) -> float:
    """把用户答案转换为有限浮点数。"""
    if isinstance(value, bool):
        raise ValueError("答案必须是数值")
    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError("答案不能为空")
        if not _NUMBER_PATTERN.match(text):
            raise ValueError("答案必须是数字：{0}".format(text))
        number = float(text)
    elif isinstance(value, (int, float)):
        try:
            number = float(value)
        except OverflowError as exc:
            raise ValueError("答案超出可用范围") from exc
    else:
        raise ValueError("答案必须是数值")
    if not math.isfinite(number):
        raise ValueError("答案必须是有限数值")
    return number


def check_answer(expr: str, answer: Union[Number, str]) -> CheckResult:
    """校验用户答案，返回 ``(是否正确, 正确答案)``。"""
    expected = evaluate_expression(expr)
    given = _coerce_number(answer)
    return abs(expected - given) <= 1e-9, expected


def format_number(value: Number) -> str:
    """把数值格式化为简洁字符串，例如 ``14.0`` 输出 ``14``。"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("数值必须是数字")
    try:
        number = float(value)
    except OverflowError as exc:
        raise ValueError("数值超出可用范围") from exc
    if not math.isfinite(number):
        raise ValueError("数值必须是有限数")
    rounded = round(number, 10)
    if abs(rounded - round(rounded)) <= 1e-9:
        return str(int(round(rounded)))
    return "{0:.10f}".format(rounded).rstrip("0").rstrip(".")
