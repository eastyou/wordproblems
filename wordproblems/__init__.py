"""wordproblems：小学应用题自动生成器。"""

from wordproblems.checker import check_answer, evaluate_expression
from wordproblems.generator import Problem, generate_problems
from wordproblems.worksheet import render_answers, render_worksheet

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "Problem",
    "generate_problems",
    "render_worksheet",
    "render_answers",
    "evaluate_expression",
    "check_answer",
]
