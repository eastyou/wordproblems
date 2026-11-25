"""题目生成：可复现随机、约束校验与去重。"""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Set, Tuple, Union

from wordproblems.checker import evaluate_expression
from wordproblems.templates import (
    OPERATIONS,
    TWO_STEP_PLANS,
    templates_for_operation,
    templates_for_plan,
)

COUNT_MIN = 1
COUNT_MAX = 200
STEPS_CHOICES: Tuple[str, ...] = ("1", "2", "mixed")
_MAX_ATTEMPTS = 2000

ONE_STEP_KIND = "一步题"
TWO_STEP_KIND = "两步题"


@dataclass
class Problem:
    """一道应用题及其答案、解题步骤与元数据。"""

    text: str
    expression: str
    answer: int
    steps: List[str]
    kind: str
    steps_count: int
    difficulty: int
    scenario: str

    def to_dict(self) -> Dict[str, object]:
        """转换为可 JSON 序列化的字典。"""
        return {
            "text": self.text,
            "expression": self.expression,
            "answer": self.answer,
            "steps": list(self.steps),
            "kind": self.kind,
            "steps_count": self.steps_count,
            "difficulty": self.difficulty,
            "scenario": self.scenario,
        }


def _is_int(value: object) -> bool:
    """判断是否为整数（bool 不算）。"""
    return isinstance(value, int) and not isinstance(value, bool)


def validate_count(count: int) -> int:
    """校验题目数量，必须为 1~200 的整数。"""
    if not _is_int(count):
        raise ValueError("题目数量必须是整数")
    if count < COUNT_MIN or count > COUNT_MAX:
        raise ValueError(
            "题目数量必须在 {0} 到 {1} 之间".format(COUNT_MIN, COUNT_MAX)
        )
    return count


def validate_seed(seed: Optional[int]) -> Optional[int]:
    """校验随机种子：可为 None 或整数（bool 不算）。"""
    if seed is None:
        return None
    if not _is_int(seed):
        raise ValueError("随机种子必须是整数")
    return seed


def normalize_steps(steps: Union[str, int]) -> str:
    """把步数参数归一化为 ``"1"``、``"2"`` 或 ``"mixed"``。"""
    if isinstance(steps, bool):
        raise ValueError("步数类型必须是 1、2 或 mixed")
    if isinstance(steps, int):
        if steps in (1, 2):
            return str(steps)
        raise ValueError("步数类型必须是 1、2 或 mixed")
    if isinstance(steps, str):
        text = steps.strip().lower()
        if text in STEPS_CHOICES:
            return text
    raise ValueError("步数类型必须是 1、2 或 mixed")


def _one_step_values(rng: random.Random, operation: str) -> Dict[str, int]:
    """按运算类型生成小学范围内的一步题数值。"""
    if operation == "add":
        a = rng.randint(12, 80)
        b = rng.randint(12, 100 - a)
        return {"a": a, "b": b, "answer": a + b}
    if operation == "sub":
        total = rng.randint(30, 100)
        part = rng.randint(5, total - 5)
        return {"a": total, "b": part, "answer": total - part}
    if operation == "mul":
        a = rng.randint(2, 12)
        b = rng.randint(2, 12)
        return {"a": a, "b": b, "answer": a * b}
    if operation == "div":
        divisor = rng.randint(2, 12)
        quotient = rng.randint(2, 12)
        return {"a": divisor * quotient, "b": divisor, "answer": quotient}
    raise ValueError("未知运算类型：{0}".format(operation))


def _one_step_expression(operation: str, a: int, b: int) -> str:
    """拼接一步题的算式字符串。"""
    if operation == "add":
        return "{0} + {1}".format(a, b)
    if operation == "sub":
        return "{0} - {1}".format(a, b)
    if operation == "mul":
        return "{0} * {1}".format(a, b)
    if operation == "div":
        return "{0} / {1}".format(a, b)
    raise ValueError("未知运算类型：{0}".format(operation))


def _one_step_difficulty(operation: str, answer: int) -> int:
    """一步题难度：乘除为 2，加减按结果大小区分。"""
    if operation in ("mul", "div"):
        return 2
    return 1 if answer <= 20 else 2


def _verify(problem: Problem) -> None:
    """自检题目：整数非负、算式与答案一致、步骤与题干完整。"""
    if isinstance(problem.answer, bool) or not isinstance(problem.answer, int):
        raise ValueError("题目答案必须是整数：{0}".format(problem.expression))
    if problem.answer < 0:
        raise ValueError("题目答案不能为负数：{0}".format(problem.expression))
    value = evaluate_expression(problem.expression)
    if not float(value).is_integer():
        raise ValueError("算式结果必须是整数：{0}".format(problem.expression))
    if int(value) != problem.answer:
        raise ValueError("算式与答案不一致：{0}".format(problem.expression))
    if not problem.steps:
        raise ValueError("题目缺少解题步骤：{0}".format(problem.expression))
    if problem.steps_count == 2 and len(problem.steps) < 2:
        raise ValueError("两步题必须给出分步解题过程：{0}".format(problem.expression))
    if not any(char.isdigit() for char in problem.text):
        raise ValueError("题干必须包含数字：{0}".format(problem.text))


def _build_one_step(rng: random.Random) -> Problem:
    """生成一道一步题。"""
    operation = rng.choice(OPERATIONS)
    template = rng.choice(templates_for_operation(operation))
    values = _one_step_values(rng, operation)
    a = values["a"]
    b = values["b"]
    answer = values["answer"]
    expression = _one_step_expression(operation, a, b)
    problem = Problem(
        text=template.text.format(a=a, b=b),
        expression=expression,
        answer=answer,
        steps=["列式计算：{0} = {1}".format(expression, answer)],
        kind=ONE_STEP_KIND,
        steps_count=1,
        difficulty=_one_step_difficulty(operation, answer),
        scenario=template.scenario,
    )
    _verify(problem)
    return problem


def _two_step_values(rng: random.Random, plan: str) -> Dict[str, int]:
    """按两步方案生成数值，保证中间结果与答案都是非负整数。"""
    if plan == "mul_add":
        a = rng.randint(2, 9)
        b = rng.randint(2, 12)
        c = rng.randint(3, 20)
        mid = a * b
        return {
            "a": a,
            "b": b,
            "c": c,
            "mid": mid,
            "total": mid,
            "answer": mid + c,
        }
    if plan == "add_sub":
        a = rng.randint(15, 60)
        b = rng.randint(5, 30)
        mid = a + b
        c = rng.randint(4, mid - 1)
        return {
            "a": a,
            "b": b,
            "c": c,
            "mid": mid,
            "total": mid,
            "answer": mid - c,
        }
    if plan == "div_mul":
        groups = rng.randint(2, 12)
        per_group = rng.randint(2, 12)
        chosen = rng.randint(2, groups)
        return {
            "a": groups,
            "b": per_group,
            "c": chosen,
            "mid": groups * per_group,
            "total": groups * per_group,
            "answer": per_group * chosen,
        }
    if plan == "sub_div":
        divisor = rng.randint(2, 12)
        quotient = rng.randint(2, 12)
        removed = rng.randint(1, 20)
        mid = divisor * quotient
        return {
            "a": divisor,
            "b": divisor,
            "c": removed,
            "mid": mid,
            "total": mid + removed,
            "answer": quotient,
        }
    raise ValueError("未知两步方案：{0}".format(plan))


def _two_step_expression(plan: str, values: Dict[str, int]) -> str:
    """拼接两步题的算式字符串。"""
    a = values["a"]
    b = values["b"]
    c = values["c"]
    total = values["total"]
    if plan == "mul_add":
        return "{0} * {1} + {2}".format(a, b, c)
    if plan == "add_sub":
        return "{0} + {1} - {2}".format(a, b, c)
    if plan == "div_mul":
        return "{0} / {1} * {2}".format(total, a, c)
    if plan == "sub_div":
        return "({0} - {1}) / {2}".format(total, c, b)
    raise ValueError("未知两步方案：{0}".format(plan))


def _build_two_step(rng: random.Random) -> Problem:
    """生成一道两步题，并给出分步解题过程。"""
    plan = rng.choice(TWO_STEP_PLANS)
    template = rng.choice(templates_for_plan(plan))
    values = _two_step_values(rng, plan)
    expression = _two_step_expression(plan, values)
    problem = Problem(
        text=template.text.format(**values),
        expression=expression,
        answer=values["answer"],
        steps=[
            template.step1.format(**values),
            template.step2.format(**values),
        ],
        kind=TWO_STEP_KIND,
        steps_count=2,
        difficulty=3,
        scenario=template.scenario,
    )
    _verify(problem)
    return problem


def _build_problem(rng: random.Random, steps: str) -> Problem:
    """按步数模式生成一道题。"""
    if steps == "1":
        return _build_one_step(rng)
    if steps == "2":
        return _build_two_step(rng)
    if steps == "mixed":
        return _build_one_step(rng) if rng.random() < 0.5 else _build_two_step(rng)
    raise ValueError("步数类型必须是 1、2 或 mixed")


def generate_problems(
    count: int = 10,
    seed: Optional[int] = None,
    steps: Union[str, int] = "mixed",
) -> List[Problem]:
    """生成一组不重复的应用题。

    参数:
        count: 题目数量，1~200 的整数。
        seed: 随机种子；相同种子可复现相同题目，None 表示不固定。
        steps: ``"1"`` 只生成一步题，``"2"`` 只生成两步题，``"mixed"`` 混合。

    异常:
        ValueError: 参数非法或无法生成足够多的不重复题目。
    """
    total = validate_count(count)
    random_seed = validate_seed(seed)
    mode = normalize_steps(steps)
    rng = random.Random(random_seed)
    problems: List[Problem] = []
    seen: Set[str] = set()
    for _ in range(total):
        problem = _next_unique(rng, mode, seen)
        seen.add(problem.text)
        problems.append(problem)
    return problems


def _next_unique(rng: random.Random, mode: str, seen: Set[str]) -> Problem:
    """反复生成直到得到未出现过的题干。"""
    for _ in range(_MAX_ATTEMPTS):
        problem = _build_problem(rng, mode)
        if problem.text not in seen:
            return problem
    raise ValueError("无法生成足够多的不重复题目，请更换 seed 或减少数量")


def format_problems(problems: Sequence[Problem]) -> str:
    """把题目列表格式化为终端可读的多行文本。"""
    lines: List[str] = []
    for index, problem in enumerate(problems, start=1):
        lines.append(
            "第 {0} 题（{1} · {2}）".format(index, problem.kind, problem.scenario)
        )
        lines.append(problem.text)
        lines.append("算式：{0} = {1}".format(problem.expression, problem.answer))
        lines.append("答案：{0}".format(problem.answer))
        lines.append("步骤：")
        for step_index, step in enumerate(problem.steps, start=1):
            lines.append("  {0}. {1}".format(step_index, step))
        lines.append("")
    return "\n".join(lines).rstrip()
