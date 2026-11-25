"""情境与题目模板池。

模板使用 ``str.format`` 占位符，具体数值由 :mod:`wordproblems.generator` 生成。
一步题占位符为 ``{a}``、``{b}``；两步题占位符为 ``{a}``、``{b}``、``{c}``、
``{mid}``（第一步结果）、``{total}``（总量）与 ``{answer}``。
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class OneStepTemplate:
    """一步题模板：固定情境与题干措辞。"""

    key: str
    scenario: str
    operation: str
    text: str


@dataclass(frozen=True)
class TwoStepTemplate:
    """两步题模板：题干与两步解题提示。"""

    key: str
    scenario: str
    plan: str
    text: str
    step1: str
    step2: str


OPERATIONS: Tuple[str, ...] = ("add", "sub", "mul", "div")

TWO_STEP_PLANS: Tuple[str, ...] = ("mul_add", "add_sub", "div_mul", "sub_div")

ONE_STEP_TEMPLATES: Tuple[OneStepTemplate, ...] = (
    # 加法
    OneStepTemplate(
        key="add_shopping",
        scenario="购物",
        operation="add",
        text="妈妈在文具店买了 {a} 支铅笔和 {b} 块橡皮，一共买了多少件文具？",
    ),
    OneStepTemplate(
        key="add_library",
        scenario="图书",
        operation="add",
        text="书架上层有 {a} 本故事书，下层有 {b} 本科技书，两层一共有多少本书？",
    ),
    OneStepTemplate(
        key="add_travel",
        scenario="行程",
        operation="add",
        text="爸爸上午骑行了 {a} 千米，下午骑行了 {b} 千米，这一天一共骑行多少千米？",
    ),
    OneStepTemplate(
        key="add_sharing",
        scenario="分配",
        operation="add",
        text="班里有 {a} 名男生和 {b} 名女生，全班一共有多少名学生？",
    ),
    OneStepTemplate(
        key="add_area",
        scenario="面积",
        operation="add",
        text="两个花坛的面积分别是 {a} 平方米和 {b} 平方米，两个花坛一共多少平方米？",
    ),
    # 减法
    OneStepTemplate(
        key="sub_shopping",
        scenario="购物",
        operation="sub",
        text="妈妈带了 {a} 元去超市，买蔬菜花了 {b} 元，还剩多少元？",
    ),
    OneStepTemplate(
        key="sub_library",
        scenario="图书",
        operation="sub",
        text="图书馆有 {a} 本绘本，借出去 {b} 本，还剩多少本？",
    ),
    OneStepTemplate(
        key="sub_travel",
        scenario="行程",
        operation="sub",
        text="从家到公园全程 {a} 千米，小明已经骑了 {b} 千米，还剩多少千米？",
    ),
    OneStepTemplate(
        key="sub_sharing",
        scenario="分配",
        operation="sub",
        text="班级有 {a} 名学生，其中 {b} 名是女生，男生有多少名？",
    ),
    OneStepTemplate(
        key="sub_area",
        scenario="面积",
        operation="sub",
        text="一块菜地有 {a} 平方米，其中 {b} 平方米种白菜，其余种萝卜，种萝卜的面积是多少平方米？",
    ),
    # 乘法
    OneStepTemplate(
        key="mul_shopping",
        scenario="购物",
        operation="mul",
        text="每支钢笔 {b} 元，买 {a} 支一共要多少元？",
    ),
    OneStepTemplate(
        key="mul_library",
        scenario="图书",
        operation="mul",
        text="每个书架放 {b} 本书，{a} 个书架一共可以放多少本书？",
    ),
    OneStepTemplate(
        key="mul_travel",
        scenario="行程",
        operation="mul",
        text="小明每分钟走 {b} 米，走了 {a} 分钟，一共走了多少米？",
    ),
    OneStepTemplate(
        key="mul_sharing",
        scenario="分配",
        operation="mul",
        text="每组有 {b} 名同学，{a} 组一共有多少名同学？",
    ),
    OneStepTemplate(
        key="mul_area",
        scenario="面积",
        operation="mul",
        text="长方形花坛长 {a} 米，宽 {b} 米，它的面积是多少平方米？",
    ),
    # 除法
    OneStepTemplate(
        key="div_shopping",
        scenario="购物",
        operation="div",
        text="{a} 支铅笔平均分给 {b} 个同学，每人分到多少支？",
    ),
    OneStepTemplate(
        key="div_library",
        scenario="图书",
        operation="div",
        text="{a} 本书平均放在 {b} 个书架上，每个书架放多少本？",
    ),
    OneStepTemplate(
        key="div_travel",
        scenario="行程",
        operation="div",
        text="一段 {a} 千米的路平均分 {b} 天骑完，每天骑多少千米？",
    ),
    OneStepTemplate(
        key="div_sharing",
        scenario="分配",
        operation="div",
        text="{a} 个苹果平均分给 {b} 个小朋友，每人分到多少个？",
    ),
    OneStepTemplate(
        key="div_area",
        scenario="面积",
        operation="div",
        text="一块面积是 {a} 平方米的长方形菜地，宽是 {b} 米，长是多少米？",
    ),
)

TWO_STEP_TEMPLATES: Tuple[TwoStepTemplate, ...] = (
    # 先乘后加
    TwoStepTemplate(
        key="mul_add_pen",
        scenario="购物",
        plan="mul_add",
        text="每盒彩笔有 {b} 支，买了 {a} 盒，另外还有散装的 {c} 支，一共有多少支彩笔？",
        step1="先算整盒的支数：{a} × {b} = {mid}（支）",
        step2="再加上散装的 {c} 支：{mid} + {c} = {answer}（支）",
    ),
    TwoStepTemplate(
        key="mul_add_choir",
        scenario="分配",
        plan="mul_add",
        text="合唱队每组有 {b} 名同学，共有 {a} 组，另外还有 {c} 名老师，一共有多少人？",
        step1="先算学生人数：{a} × {b} = {mid}（人）",
        step2="再加上老师：{mid} + {c} = {answer}（人）",
    ),
    TwoStepTemplate(
        key="mul_add_milk",
        scenario="购物",
        plan="mul_add",
        text="一箱牛奶有 {b} 盒，买了 {a} 箱，又单买了 {c} 盒，一共有多少盒牛奶？",
        step1="先算整箱的盒数：{a} × {b} = {mid}（盒）",
        step2="再加上单买的：{mid} + {c} = {answer}（盒）",
    ),
    # 先加后减
    TwoStepTemplate(
        key="add_sub_class",
        scenario="分配",
        plan="add_sub",
        text="班里有 {a} 名男生和 {b} 名女生，转走 {c} 名同学后，班里还有多少名同学？",
        step1="先算全班人数：{a} + {b} = {mid}（名）",
        step2="再减去转走的人数：{mid} - {c} = {answer}（名）",
    ),
    TwoStepTemplate(
        key="add_sub_books",
        scenario="图书",
        plan="add_sub",
        text="书架上有 {a} 本故事书和 {b} 本科技书，借出 {c} 本后，书架上还剩多少本书？",
        step1="先算书的总数：{a} + {b} = {mid}（本）",
        step2="再减去借出的：{mid} - {c} = {answer}（本）",
    ),
    TwoStepTemplate(
        key="add_sub_stock",
        scenario="购物",
        plan="add_sub",
        text="商店原有 {a} 件商品，又进货 {b} 件，卖出 {c} 件后，还剩多少件商品？",
        step1="先算进货后的总数：{a} + {b} = {mid}（件）",
        step2="再减去卖出的：{mid} - {c} = {answer}（件）",
    ),
    # 先除后乘
    TwoStepTemplate(
        key="div_mul_basket",
        scenario="购物",
        plan="div_mul",
        text="{total} 个苹果平均装进 {a} 个篮子，每个篮子装得同样多。其中 {c} 个篮子里一共有多少个苹果？",
        step1="先算每个篮子装几个：{total} ÷ {a} = {b}（个）",
        step2="再算 {c} 个篮子的总数：{b} × {c} = {answer}（个）",
    ),
    TwoStepTemplate(
        key="div_mul_team",
        scenario="分配",
        plan="div_mul",
        text="{total} 名同学平均分成 {a} 队，每队人数相同。其中 {c} 队一共有多少名同学？",
        step1="先算每队人数：{total} ÷ {a} = {b}（名）",
        step2="再算 {c} 队的总人数：{b} × {c} = {answer}（名）",
    ),
    TwoStepTemplate(
        key="div_mul_shelf",
        scenario="图书",
        plan="div_mul",
        text="{total} 本书平均放在 {a} 个书架上，每个书架放得一样多。其中 {c} 个书架上共有多少本书？",
        step1="先算每个书架放几本：{total} ÷ {a} = {b}（本）",
        step2="再算 {c} 个书架的总数：{b} × {c} = {answer}（本）",
    ),
    # 先减后除
    TwoStepTemplate(
        key="sub_div_store",
        scenario="购物",
        plan="sub_div",
        text="仓库有 {total} 箱饮料，运走 {c} 箱后，剩下的平均分给 {b} 家商店，每家分到多少箱？",
        step1="先算剩下的箱数：{total} - {c} = {mid}（箱）",
        step2="再平均分给 {b} 家商店：{mid} ÷ {b} = {answer}（箱）",
    ),
    TwoStepTemplate(
        key="sub_div_library",
        scenario="图书",
        plan="sub_div",
        text="图书馆有 {total} 本新书，先拿出 {c} 本做展览，剩下的平均分给 {b} 个班级，每班分到多少本？",
        step1="先算剩下的本数：{total} - {c} = {mid}（本）",
        step2="再平均分给 {b} 个班级：{mid} ÷ {b} = {answer}（本）",
    ),
    TwoStepTemplate(
        key="sub_div_parts",
        scenario="分配",
        plan="sub_div",
        text="{total} 个零件中先用了 {c} 个，剩下的平均装进 {b} 个盒子，每个盒子装多少个？",
        step1="先算剩下的零件数：{total} - {c} = {mid}（个）",
        step2="再平均装进 {b} 个盒子：{mid} ÷ {b} = {answer}（个）",
    ),
)


def templates_for_operation(operation: str) -> List[OneStepTemplate]:
    """返回指定运算（add/sub/mul/div）的一步题模板列表。"""
    return [item for item in ONE_STEP_TEMPLATES if item.operation == operation]


def templates_for_plan(plan: str) -> List[TwoStepTemplate]:
    """返回指定两步方案（mul_add/add_sub/div_mul/sub_div）的模板列表。"""
    return [item for item in TWO_STEP_TEMPLATES if item.plan == plan]
