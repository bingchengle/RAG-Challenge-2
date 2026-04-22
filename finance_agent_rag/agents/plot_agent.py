"""
任务二/三：根据查询结果出图，保存为 output/result/问题编号_序号.jpg

TODO: matplotlib/seaborn；无图时 JSON 的 image 留空或 []。
"""

from pathlib import Path


def save_chart(figure, path: Path) -> str:
    raise NotImplementedError
