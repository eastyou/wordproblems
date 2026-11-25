# wordproblems

[![CI](https://github.com/eastyou/wordproblems/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/wordproblems/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](pyproject.toml)

小学应用题自动生成器，面向老师与家长出练习纸。命令行可以生成一步题、两步题，
直接输出到终端或保存为可打印的 A4 HTML 练习纸，还能安全校验用户答案。

## 特性

- 一步题覆盖加、减、乘、除四类，内置购物、图书、行程、分配、面积五类情境。
- 减法保证结果非负；除法必须整除，被除数不超过 200；乘法两个乘数都不超过 12。
- 两步题组合「先乘后加」「先加后减」「先除后乘」「先减后除」，结果均为非负整数，
  并给出分步解题过程。
- 相同 `--seed` 完全复现同一组题目；生成时自动去重，同一页不会出现完全相同的题干。
- 练习纸按难度排序，A4 打印样式，答案可附在页末或单独成页。
- 答案校验使用 `ast` 安全解析，只允许数字、`+ - * / ( )` 和空格。
- 纯标准库实现，无第三方依赖，兼容 Python 3.9 及以上。

## 安装

```bash
python -m pip install -e .
```

也可以不安装，直接在仓库根目录运行 `python -m wordproblems`：

```bash
python -m wordproblems --help
```

## 使用

### 生成题目

```bash
wordproblems gen --count 3 --seed 42 --steps 1
```

```text
第 1 题（一步题 · 购物）
妈妈在文具店买了 47 支铅笔和 27 块橡皮，一共买了多少件文具？
算式：47 + 27 = 74
答案：74
步骤：
  1. 列式计算：47 + 27 = 74

第 2 题（一步题 · 图书）
图书馆有 43 本绘本，借出去 10 本，还剩多少本？
算式：43 - 10 = 33
答案：33
步骤：
  1. 列式计算：43 - 10 = 33

第 3 题（一步题 · 购物）
6 支铅笔平均分给 2 个同学，每人分到多少支？
算式：6 / 2 = 3
答案：3
步骤：
  1. 列式计算：6 / 2 = 3
```

两步题会给出分步过程：

```bash
wordproblems gen --count 2 --seed 42 --steps 2
```

```text
第 1 题（两步题 · 购物）
每盒彩笔有 5 支，买了 6 盒，另外还有散装的 10 支，一共有多少支彩笔？
算式：6 * 5 + 10 = 40
答案：40
步骤：
  1. 先算整盒的支数：6 × 5 = 30（支）
  2. 再加上散装的 10 支：30 + 10 = 40（支）

第 2 题（两步题 · 购物）
商店原有 21 件商品，又进货 26 件，卖出 38 件后，还剩多少件商品？
算式：21 + 26 - 38 = 9
答案：9
步骤：
  1. 先算进货后的总数：21 + 26 = 47（件）
  2. 再减去卖出的：47 - 38 = 9（件）
```

加上 `--json` 可以输出结构化数据，便于接入其他工具：

```bash
wordproblems gen --count 1 --seed 42 --steps 1 --json
```

```json
{
  "count": 1,
  "seed": 42,
  "steps": "1",
  "problems": [
    {
      "text": "妈妈在文具店买了 47 支铅笔和 27 块橡皮，一共买了多少件文具？",
      "expression": "47 + 27",
      "answer": 74,
      "steps": [
        "列式计算：47 + 27 = 74"
      ],
      "kind": "一步题",
      "steps_count": 1,
      "difficulty": 2,
      "scenario": "购物"
    }
  ]
}
```

### 生成练习纸

```bash
wordproblems sheet --count 12 --seed 7 --steps mixed --out problems.html
```

```text
练习题已写入：problems.html（含参考答案）
```

`problems.html` 是自包含的 A4 打印版式练习纸：题目区留出作答横线，页末用
`<details><summary>参考答案</summary>` 折叠答案，浏览器直接打印即可。

需要把答案单独发给家长时，再加 `--answers-out`：

```bash
wordproblems sheet --count 12 --seed 7 --steps mixed --out problems.html --answers-out answers.html
```

```text
练习题已写入：problems.html
参考答案已写入：answers.html
```

此时 `problems.html` 不再包含答案，`answers.html` 采用题号、答案、算式、解题步骤的表格呈现，
题号与练习纸一一对应。

### 校验答案

```bash
wordproblems check --expr "3*4+2" --answer 14
```

```text
正确
```

```bash
wordproblems check --expr "3*4+2" --answer 15
```

```text
错误，正确答案是 14
```

表达式只允许数字、`+ - * / ( )` 和空格；函数调用、变量、幂、取模、分号以及除数为 0
都会给出中文错误提示并返回码 2。

### 查看示例

```bash
wordproblems demo
```

## 参数表

| 子命令 | 参数 | 说明 | 默认值 |
| --- | --- | --- | --- |
| `gen` | `--count N` | 题目数量，取值 1~200 | `10` |
| `gen` | `--seed N` | 随机种子，整数，相同种子结果可复现 | 不固定 |
| `gen` | `--steps {1,2,mixed}` | 步数模式：一步题、两步题、混合 | `mixed` |
| `gen` | `--json` | 以 JSON 输出结构化结果 | 关闭 |
| `sheet` | `--count N` | 题目数量，取值 1~200 | `10` |
| `sheet` | `--seed N` | 随机种子，整数 | 不固定 |
| `sheet` | `--steps {1,2,mixed}` | 步数模式 | `mixed` |
| `sheet` | `--out PATH` | 练习纸输出路径 | `problems.html` |
| `sheet` | `--answers-out PATH` | 参考答案单独输出路径；不指定则附在练习纸页末 | 不指定 |
| `check` | `--expr EXPR` | 待校验的算式，例如 `3*4+2` | 必填 |
| `check` | `--answer VALUE` | 用户给出的答案，可写整数或小数 | 必填 |
| `demo` | 无 | 打印一段生成与校验示例 | - |

返回码约定：成功为 `0`；参数或运算错误为 `2`，错误信息以 `错误：` 开头输出到标准错误。
`--count` 超出 1~200、`--steps` 取值非法、答案不是数字、表达式非法或除数为 0 都会触发错误。

## 作为库使用

```python
from wordproblems import Problem, check_answer, generate_problems

problems = generate_problems(count=5, seed=42, steps="mixed")
for problem in problems:
    assert isinstance(problem, Problem)
    print(problem.text)
    print(problem.expression, "=", problem.answer)
    for step in problem.steps:
        print("  -", step)

correct, expected = check_answer("3*4+2", 14)
print(correct, expected)
```

`generate_problems` 的所有参数都会做合法性校验，非法时抛出带中文提示的 `ValueError`；
`Problem.to_dict()` 可直接交给 `json.dumps` 序列化。

## 开发与测试

```bash
/usr/bin/python3 -m unittest discover -s tests -v
python3 -m unittest discover -s tests -v
```

测试覆盖参数校验、随机可复现、答案与算式一致性、除法整除、题干去重、HTML 转义与
A4 样式、答案校验以及命令行返回码等场景。

## License

[MIT](LICENSE) © 2026 eastyou
