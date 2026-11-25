"""HTML 练习纸与参考答案渲染（纯字符串拼接 + html.escape）。"""

import html
from typing import List, Sequence, Set

from wordproblems.generator import Problem

_STYLE = """
@page { size: A4; margin: 14mm 12mm; }
* { box-sizing: border-box; }
body {
  margin: 0 auto;
  padding: 16mm 12mm;
  max-width: 210mm;
  background: #ffffff;
  color: #1f1f1f;
  font-family: "Songti SC", "SimSun", "Noto Serif CJK SC", serif;
  font-size: 15px;
  line-height: 1.75;
}
header { margin-bottom: 16px; }
h1 {
  margin: 0 0 8px;
  font-size: 22px;
  text-align: center;
  letter-spacing: 2px;
}
.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 24px;
  justify-content: space-between;
  font-size: 13px;
  color: #444444;
  border-bottom: 1px solid #cccccc;
  padding-bottom: 8px;
}
.problem {
  margin: 0 0 14px;
  break-inside: avoid;
  page-break-inside: avoid;
}
.index { font-weight: 600; margin-right: 6px; }
.workline {
  border-bottom: 1px dashed #888888;
  height: 26px;
  margin: 4px 0 0 24px;
}
.answers { margin-top: 22px; }
details {
  border: 1px solid #bbbbbb;
  border-radius: 6px;
  padding: 8px 12px;
}
summary { cursor: pointer; font-weight: 600; }
details ol { margin: 8px 0 0; padding-left: 1.6em; }
details li { margin-bottom: 6px; }
.answer-value { font-weight: 600; }
.answer-expr { color: #555555; }
.steps { margin: 2px 0 0; padding-left: 1.4em; color: #444444; font-size: 14px; }
.answer-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.answer-table th,
.answer-table td {
  border: 1px solid #c0c0c0;
  padding: 6px 8px;
  text-align: left;
  vertical-align: top;
}
.answer-table th { background: #f2f2f2; }
.answer-table td.number { width: 48px; text-align: center; }
.answer-table td.answer { width: 90px; }
@media print {
  body { padding: 0; }
  .answers { break-inside: avoid; }
}
"""


def ordered_problems(problems: Sequence[Problem]) -> List[Problem]:
    """按难度排序并按题干去重，保证同一页不出现完全相同的题干。"""
    seen: Set[str] = set()
    ordered: List[Problem] = []
    for problem in sorted(
        problems, key=lambda item: (item.difficulty, item.steps_count)
    ):
        if problem.text in seen:
            continue
        seen.add(problem.text)
        ordered.append(problem)
    return ordered


def _escape(value: object) -> str:
    """HTML 转义辅助函数。"""
    return html.escape(str(value), quote=True)


def _counts(problems: Sequence[Problem]) -> str:
    """生成题量统计文本。"""
    one_step = sum(1 for item in problems if item.steps_count == 1)
    two_step = len(problems) - one_step
    return "共 {0} 题（一步 {1} 题 / 两步 {2} 题）".format(
        len(problems), one_step, two_step
    )


def _worklines(problem: Problem) -> str:
    """按步数给出作答横线。"""
    count = 2 if problem.steps_count == 2 else 1
    return "".join('<div class="workline"></div>' for _ in range(count))


def _problem_html(problem: Problem, index: int) -> str:
    """渲染单道题的题目区。"""
    return (
        '<div class="problem">'
        '<span class="index">{0}.</span>'
        '<span class="text">{1}</span>'
        "{2}"
        "</div>"
    ).format(index, _escape(problem.text), _worklines(problem))


def _inline_answers(problems: Sequence[Problem]) -> str:
    """渲染练习题页末尾的 ``<details>`` 参考答案块。"""
    if not problems:
        return ""
    items: List[str] = []
    for index, problem in enumerate(problems, start=1):
        steps_html = "".join(
            "<li>{0}</li>".format(_escape(step)) for step in problem.steps
        )
        item_html = (
            "<li>"
            '<span class="answer-value">答案：{0}</span>'
            '<span class="answer-expr">（算式：{1}）</span>'
            '<ol class="steps">{2}</ol>'
            "</li>"
        ).format(_escape(problem.answer), _escape(problem.expression), steps_html)
        items.append(item_html)
    return (
        '<section class="answers">'
        "<details>"
        "<summary>参考答案</summary>"
        "<ol>{0}</ol>"
        "</details>"
        "</section>"
    ).format("".join(items))


def render_worksheet(
    problems: Sequence[Problem],
    title: str = "小学应用题练习纸",
    include_answers: bool = True,
) -> str:
    """渲染可直接打印的 A4 练习纸 HTML。"""
    ordered = ordered_problems(problems)
    body: List[str] = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>{0}</title>".format(_escape(title)),
        "<style>{0}</style>".format(_STYLE),
        "</head>",
        "<body>",
        "<header>",
        "<h1>{0}</h1>".format(_escape(title)),
        '<div class="meta">',
        "<span>姓名：____________</span>",
        "<span>日期：____________</span>",
        "<span>{0}</span>".format(_escape(_counts(ordered))),
        "</div>",
        "</header>",
        '<main class="problems">',
    ]
    for index, problem in enumerate(ordered, start=1):
        body.append(_problem_html(problem, index))
    body.append("</main>")
    if include_answers:
        body.append(_inline_answers(ordered))
    body.extend(["</body>", "</html>", ""])
    return "\n".join(body)


def render_answers(
    problems: Sequence[Problem],
    title: str = "参考答案",
) -> str:
    """渲染独立的参考答案页 HTML（题号与练习纸一致）。"""
    ordered = ordered_problems(problems)
    rows: List[str] = []
    for index, problem in enumerate(ordered, start=1):
        steps_html = "".join(
            "<li>{0}</li>".format(_escape(step)) for step in problem.steps
        )
        row_html = (
            "<tr>"
            '<td class="number">{0}</td>'
            '<td class="answer">{1}</td>'
            "<td>{2}</td>"
            "<td><ol class=\"steps\">{3}</ol></td>"
            "</tr>"
        ).format(
            index,
            _escape(problem.answer),
            _escape(problem.expression),
            steps_html,
        )
        rows.append(row_html)
    body: List[str] = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>{0}</title>".format(_escape(title)),
        "<style>{0}</style>".format(_STYLE),
        "</head>",
        "<body>",
        "<header>",
        "<h1>{0}</h1>".format(_escape(title)),
        '<div class="meta"><span>{0}</span></div>'.format(
            _escape(_counts(ordered))
        ),
        "</header>",
        '<main class="answers-page">',
        '<table class="answer-table">',
        "<thead><tr><th>题号</th><th>答案</th><th>算式</th><th>解题步骤</th></tr></thead>",
        "<tbody>{0}</tbody>".format("".join(rows)),
        "</table>",
        "</main>",
        "</body>",
        "</html>",
        "",
    ]
    return "\n".join(body)
