"""
全局配置：路径与连接。数据按赛题「附件1～6」结构放在
`data/全部数据/正式数据` 或 `data/B题-示例数据/示例数据` 下（见下）。
"""
import os
from pathlib import Path

# 本包根目录（finance_agent_rag/）
PACKAGE_ROOT = Path(__file__).resolve().parent
# 仓库根目录
REPO_ROOT = PACKAGE_ROOT.parent

# 是否使用小样本（B题-示例数据）；全量为 False
USE_SAMPLE: bool = os.environ.get("TEDDY_USE_SAMPLE", "0") == "1"
_DATA_ROOT_NAME = (
    ("B题-示例数据", "示例数据")
    if USE_SAMPLE
    else ("全部数据", "正式数据")
)
# 含附件1 xlsx、附件2 财报、… 附件6 的目录
BUNDLE_ROOT: Path = (
    PACKAGE_ROOT / "data" / _DATA_ROOT_NAME[0] / _DATA_ROOT_NAME[1]
)


def _xlsx(attachment_prefix: str) -> Path:
    """附件1/3/4/6 等在 BUNDLE 根上的 xlsx（忽略 Excel 临时文件 ~$...）。"""
    for p in sorted(BUNDLE_ROOT.glob(f"{attachment_prefix}*.xlsx")):
        if not p.name.startswith("~$"):
            return p
    raise FileNotFoundError(
        f"在 {BUNDLE_ROOT} 下未找到 {attachment_prefix}*.xlsx，请检查是否解压完整"
    )


# 与旧变量名兼容：仍然叫 DATA_ROOT，但指向「附件包」根目录
DATA_ROOT = BUNDLE_ROOT

# 财务报告
REPORT_DIR = BUNDLE_ROOT / "附件2：财务报告"
REPORTS_SH = REPORT_DIR / "reports-上交所"
REPORTS_SZ = REPORT_DIR / "reports-深交所"

# 单文件
COMPANY_INFO = _xlsx("附件1")
FIELD_SPEC = _xlsx("附件3")
TASK2_QUESTIONS = _xlsx("附件4")
TASK3_QUESTIONS = _xlsx("附件6")

# 研报根目录
RESEARCH_ROOT = BUNDLE_ROOT / "附件5：研报数据"

# 任务一：解析结果缓存（JSON），避免重复跑 Docling
PARSED_REPORTS_DIR = PACKAGE_ROOT / "data" / "intermediate" / "parsed_reports"

# 输出
OUTPUT_ROOT = PACKAGE_ROOT / "output"
RESULT_IMAGES = OUTPUT_ROOT / "result"
RESULT_2_XLSX = OUTPUT_ROOT / "result_2.xlsx"
RESULT_3_XLSX = OUTPUT_ROOT / "result_3.xlsx"
TASK2_JSON = OUTPUT_ROOT / "task2.json"
TASK3_JSON = OUTPUT_ROOT / "task3.json"

# MySQL（任务一/二）
MYSQL_DSN = ""  # 例: "mysql+pymysql://user:pass@127.0.0.1:3306/teddy_b"
