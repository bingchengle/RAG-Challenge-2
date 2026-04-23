"""
任务一：纯规则从 Docling 导出的 `report` JSON 中抽四表数据（不调用大模型）。

策略：从各表格 Markdown 中解析行，用中文关键词 ↔ schema 字段映射；报告期用文件名 hint + 正文正则推断。
对版式与附件不完全一致的报表会有漏抽，以人工/后续规则迭代为主。
"""
from __future__ import annotations

import re
from typing import Any, Dict, Optional

from finance_agent_rag.core.extraction.report_identity import FileIdentity

# (目标表, 字段名, 多个别名关键词，匹配行首列/项目列)
# 同字段只登记一次，匹配时取最长关键词命中
_RULES: list[tuple[str, str, tuple[str, ...]]] = [
    # 核心业绩指标
    (
        "core_performance_indicators_sheet",
        "eps",
        ("基本每股收益", "稀释每股收益", "每股收益"),
    ),
    (
        "core_performance_indicators_sheet",
        "total_operating_revenue",
        ("营业收入", "营业总收入", "主营业务收入"),
    ),
    (
        "core_performance_indicators_sheet",
        "operating_revenue_yoy_growth",
        ("营业收入.*同比", "营业收入.*增长", "收入.*同比"),
    ),
    (
        "core_performance_indicators_sheet",
        "operating_revenue_qoq_growth",
        ("营业收入.*环比", "收入.*环比"),
    ),
    (
        "core_performance_indicators_sheet",
        "net_profit_10k_yuan",
        ("归属于上市公司股东的净利润", "归属于母公司.*净利润", "净利润"),
    ),
    (
        "core_performance_indicators_sheet",
        "net_profit_yoy_growth",
        ("净利润.*同比", "归属于上市公司.*同比"),
    ),
    (
        "core_performance_indicators_sheet",
        "net_profit_qoq_growth",
        ("净利润.*环比",),
    ),
    (
        "core_performance_indicators_sheet",
        "net_asset_per_share",
        ("每股净资产", "归属于母公司.*每股"),
    ),
    (
        "core_performance_indicators_sheet",
        "roe",
        ("净资产收益率", "全面摊薄净资产收益率", "加权平均净资产收益率"),
    ),
    (
        "core_performance_indicators_sheet",
        "operating_cf_per_share",
        ("每股经营活动产生.*现金流量", "每股经营.*现金流"),
    ),
    (
        "core_performance_indicators_sheet",
        "net_profit_excl_non_recurring",
        ("扣非.*净利润", "非经常性损益后净利润"),
    ),
    (
        "core_performance_indicators_sheet",
        "gross_profit_margin",
        ("毛利率", "销售毛利率"),
    ),
    (
        "core_performance_indicators_sheet",
        "net_profit_margin",
        ("净利率", "销售净利率"),
    ),
    # 资产负债
    (
        "balance_sheet",
        "asset_cash_and_cash_equivalents",
        ("货币资金", "现金及现金等价物"),
    ),
    (
        "balance_sheet",
        "asset_accounts_receivable",
        ("应收账款", "应收票据及应收账款", "应收票据及账款"),
    ),
    (
        "balance_sheet",
        "asset_inventory",
        ("存货",),
    ),
    (
        "balance_sheet",
        "asset_trading_financial_assets",
        ("交易性金融资产",),
    ),
    (
        "balance_sheet",
        "asset_construction_in_progress",
        ("在建工程",),
    ),
    (
        "balance_sheet",
        "asset_total_assets",
        ("资产总计", "资产合计", "资产总额"),
    ),
    (
        "balance_sheet",
        "liability_accounts_payable",
        ("应付账款", "应付票据及应付账款"),
    ),
    (
        "balance_sheet",
        "liability_advance_from_customers",
        ("预收款项", "合同负债", "预收账款"),
    ),
    (
        "balance_sheet",
        "liability_total_liabilities",
        ("负债合计", "负债总计", "负债总额"),
    ),
    (
        "balance_sheet",
        "liability_contract_liabilities",
        ("合同负债",),
    ),
    (
        "balance_sheet",
        "liability_short_term_loans",
        ("短期借款",),
    ),
    (
        "balance_sheet",
        "asset_liability_ratio",
        ("资产负债率",),
    ),
    (
        "balance_sheet",
        "equity_unappropriated_profit",
        ("未分配利润", "归属于母公司未分配"),
    ),
    (
        "balance_sheet",
        "equity_total_equity",
        ("所有者权益合计", "股东权益合计", "归属于母公司.*权益", "股东权益", "权益合计"),
    ),
    # 现金流量
    (
        "cash_flow_sheet",
        "net_cash_flow",
        ("现金及现金等价物净增加", "现金.*净增加", "期.*现金及现金等价物净增加额"),
    ),
    (
        "cash_flow_sheet",
        "operating_cf_net_amount",
        ("经营活动产生.*现金流量净额", "经营活动.*现金流量净额"),
    ),
    (
        "cash_flow_sheet",
        "operating_cf_cash_from_sales",
        ("销售商品.*收到.*现金", "销售商品、提供劳务收到的现金"),
    ),
    (
        "cash_flow_sheet",
        "investing_cf_net_amount",
        ("投资活动.*现金流量净额",),
    ),
    (
        "cash_flow_sheet",
        "investing_cf_cash_for_investments",
        ("购建.*支付.*现金", "购建固定资产.*支付的现金"),
    ),
    (
        "cash_flow_sheet",
        "investing_cf_cash_from_investment_recovery",
        ("收回投资.*收到.*现金", "收回投资所收到的现金"),
    ),
    (
        "cash_flow_sheet",
        "financing_cf_cash_from_borrowing",
        ("取得借款.*收到.*现金", "取得借款收到的现金"),
    ),
    (
        "cash_flow_sheet",
        "financing_cf_cash_for_debt_repayment",
        ("偿还债务.*支付.*现金", "偿还债务支付的现金"),
    ),
    (
        "cash_flow_sheet",
        "financing_cf_net_amount",
        ("筹资活动.*现金流量净额",),
    ),
    # 利润
    (
        "income_sheet",
        "total_operating_revenue",
        ("一、营业总收入", "一、营业收入", "营业总收入", "营业收入", "主营业务收入"),
    ),
    (
        "income_sheet",
        "net_profit",
        ("四、净利润", "五、净利润", "净利润", "归属.*净利润"),
    ),
    (
        "income_sheet",
        "other_income",
        ("其他收益", "其他业务收入"),
    ),
    (
        "income_sheet",
        "operating_revenue_yoy_growth",
        ("营业收入.*同比",),
    ),
    (
        "income_sheet",
        "operating_expense_cost_of_sales",
        ("减：营业成本", "营业成本", "一、营业成本", "二、营业成本", "三、营业成本", "主营业务成本", "其中：营业成本"),
    ),
    (
        "income_sheet",
        "operating_expense_selling_expenses",
        ("销售费用",),
    ),
    (
        "income_sheet",
        "operating_expense_administrative_expenses",
        ("管理费用",),
    ),
    (
        "income_sheet",
        "operating_expense_financial_expenses",
        ("财务费用",),
    ),
    (
        "income_sheet",
        "operating_expense_rnd_expenses",
        ("研发费用", "研究与开发", "研究费用"),
    ),
    (
        "income_sheet",
        "operating_expense_taxes_and_surcharges",
        ("税金及附加", "营业税金及附加"),
    ),
    (
        "income_sheet",
        "total_operating_expenses",
        ("营业总成本", "营业总支出"),
    ),
    (
        "income_sheet",
        "operating_profit",
        ("三、营业利润", "营业利润", "二、营业利润"),
    ),
    (
        "income_sheet",
        "total_profit",
        ("四、利润总额", "三、利润总额", "利润总额"),
    ),
    (
        "income_sheet",
        "asset_impairment_loss",
        ("资产减值损失",),
    ),
    (
        "income_sheet",
        "credit_impairment_loss",
        ("信用减值损失",),
    ),
]


# 同义规则按行顺序匹配，先命中的 (表, 字段) 先写入
FIXED_RULES: list[tuple[str, str, tuple[str, ...]]] = list(_RULES)


def _norm_label(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", "", s)
    s = s.replace("（", "(").replace("）", ")")
    for ch in " \t\n\r，,、；;:：":
        s = s.replace(ch, "")
    return s


def _parse_number(cell: str) -> Optional[float]:
    if not cell or not str(cell).strip():
        return None
    s = str(cell).strip()
    s = s.replace(",", "").replace("，", "").replace(" ", "")
    if s in ("-", "—", "－", "nan", "NA"):
        return None
    neg = 1.0
    if s.startswith("(") and s.endswith(")"):
        neg = -1.0
        s = s[1:-1]
    m_pct = re.search(r"([\-+]?[\d.]+)\s*[%％]", s)
    if m_pct:
        try:
            return neg * (float(m_pct.group(1)) / 100.0)
        except ValueError:
            return None
    mult = 1.0
    if "亿" in s:
        mult = 10_000.0
        s = s.replace("亿元", "").replace("亿", "")
    elif "万" in s and "百万" not in s:
        s = s.replace("万元", "").replace("万", "")
    else:
        s = re.sub(r"[^\d.\-+eE]", "", s) or s
    # 只保留最后一段数字
    nums = re.findall(r"[\-+]?[\d.]+", s.replace("，", ""))
    if not nums:
        return None
    try:
        v = float(nums[-1]) * mult * neg
        return v
    except ValueError:
        return None


def _parse_gfm_table(md: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in md.splitlines():
        line = line.strip()
        if not line or line.startswith("<!--"):
            continue
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2:
            continue
        cells = parts[1:-1] if parts[-1] == "" else parts[1:]
        if cells and all(re.match(r"^[\s\-:|]+$", c) for c in cells):
            continue
        if cells:
            rows.append(cells)
    return rows


def _table_kind_score(md: str) -> dict[str, int]:
    s = md[:4000]
    return {
        "core_performance_indicators_sheet": 5 * (
            s.count("主要会计数据")
            + s.count("主要财务数据")
            + s.count("主要会计数据和财务指标")
        )
        + 2 * s.count("每股收益")
        + 2 * s.count("营业收入"),
        "balance_sheet": 6 * (s.count("资产负债表") + s.count("合并资产负债表"))
        + s.count("流动资产")
        + s.count("非流动资产"),
        "cash_flow_sheet": 8 * s.count("现金流量表")
        + 4 * s.count("经营活动")
        + 2 * s.count("筹资活动"),
        "income_sheet": 8 * s.count("利润表")
        + 4 * s.count("营业利润")
        + 2 * s.count("营业总收入")
        + 2 * s.count("一、营业总收入"),
    }


def _pick_numeric_from_row(cells: list[str], start_idx: int) -> Optional[float]:
    for c in cells[start_idx:]:
        n = _parse_number(c)
        if n is not None:
            return n
    return None


def _row_label(cells: list[str]) -> str:
    if not cells:
        return ""
    return " ".join(cells[: min(2, len(cells))])


def _match_field(norm_label: str, pattern: str) -> bool:
    pat = pattern.strip()
    if not pat:
        return False
    if ".*" in pat or "|" in pat or (pat.startswith("^") and pat.endswith("$")):
        try:
            return bool(re.search(pat.replace("（", "(").replace("）", ")"), norm_label))
        except re.error:
            pass
    p = _norm_label(pat)
    if not p:
        return False
    return p in norm_label or norm_label in p


def _apply_rules_to_rows(
    rows: list[list[str]], allowed_tables: set[str] | None
) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {
        "core_performance_indicators_sheet": {},
        "balance_sheet": {},
        "cash_flow_sheet": {},
        "income_sheet": {},
    }
    filled: set[tuple[str, str]] = set()
    for cells in rows:
        if not cells:
            continue
        label_raw = _row_label(cells)
        nlab = _norm_label(label_raw)
        if len(nlab) < 2:
            continue
        for table_key, field, kws in FIXED_RULES:
            if allowed_tables is not None and table_key not in allowed_tables:
                continue
            if (table_key, field) in filled:
                continue
            for kw in kws:
                if _match_field(nlab, kw):
                    val = _pick_numeric_from_row(cells, 1)
                    if val is not None:
                        out[table_key][field] = val
                        filled.add((table_key, field))
                    break
    return out


def _merge_dicts(a: dict[str, dict[str, Any]], b: dict[str, dict[str, Any]]) -> None:
    for k, v in b.items():
        a[k].update({kk: vv for kk, vv in v.items() if vv is not None})


def infer_report_period(
    text: str, identity: FileIdentity
) -> tuple[Optional[str], Optional[int]]:
    if identity.report_period_hint:
        rp = identity.report_period_hint
        y = int(rp[:4]) if len(rp) >= 4 and rp[:4].isdigit() else None
        return rp, y
    t = text[:100_000]
    # 截至 YYYY 年 M 月 D 日
    m = re.search(
        r"截至\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日",
        t,
    )
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if mo == 3 and d == 31:
            return f"{y}Q1", y
        if mo == 6 and d == 30:
            return f"{y}HY", y
        if mo == 9 and d == 30:
            return f"{y}Q3", y
        if mo == 12 and d == 31:
            return f"{y}FY", y
    pairs = [
        (r"(\d{4})年\s*第[一1]季度", lambda g: f"{g}Q1", lambda g: int(g)),
        (r"(\d{4})年\s*一季报", lambda g: f"{g}Q1", lambda g: int(g)),
        (r"(\d{4})年\s*第[二2]季度", lambda g: f"{g}Q2", lambda g: int(g)),
        (r"(\d{4})年\s*第[三3]季度", lambda g: f"{g}Q3", lambda g: int(g)),
        (r"(\d{4})年\s*第[四4]季度", lambda g: f"{g}Q4", lambda g: int(g)),
        (r"(\d{4})年\s*半年度", lambda g: f"{g}HY", lambda g: int(g)),
        (r"(\d{4})年\s*半年报", lambda g: f"{g}HY", lambda g: int(g)),
        (r"(\d{4})年\s*年度", lambda g: f"{g}FY", lambda g: int(g)),
        (r"(\d{4})年\s*年报", lambda g: f"{g}FY", lambda g: int(g)),
    ]
    for pat, rp_f, y_f in pairs:
        mm = re.search(pat, t)
        if mm:
            g = mm.group(1)
            return rp_f(g), y_f(g)
    if identity.filing_date_yyyymmdd and len(identity.filing_date_yyyymmdd) == 8:
        ymd = identity.filing_date_yyyymmdd
        y = int(ymd[:4])
        mo = int(ymd[4:6])
        if 1 <= mo <= 4:
            return f"{y}Q1", y
        if 5 <= mo <= 6:
            return f"{y}HY", y
        if 7 <= mo <= 8:
            return f"{y}Q3", y
        if mo >= 9:
            return f"{y}FY", y
    return None, None


def extract_financial_payload_from_report(
    report_data: dict[str, Any],
    identity: FileIdentity,
) -> Dict[str, Any]:
    """
    从 Docling `assemble_report` 产出的单份 JSON 抽取与旧 LLM 结构兼容的 dict。
    """
    tables = report_data.get("tables") or []
    combined: dict[str, dict[str, Any]] = {
        "core_performance_indicators_sheet": {},
        "balance_sheet": {},
        "cash_flow_sheet": {},
        "income_sheet": {},
    }
    for tab in tables:
        if not isinstance(tab, dict):
            continue
        md = (tab.get("markdown") or "").strip()
        if not md:
            continue
        rows = _parse_gfm_table(md)
        if not rows:
            continue
        scores = _table_kind_score(md)
        best = max(scores, key=scores.get)  # type: ignore
        if scores[best] < 3:
            allowed = None
        else:
            best_score = scores[best]
            near = [k for k, v in scores.items() if v >= best_score * 0.4]
            allowed = set(near) if len(near) <= 2 else {best}
        part = _apply_rules_to_rows(rows, allowed)
        _merge_dicts(combined, part)
    if not any(combined[k] for k in combined):
        for tab in tables:
            if not isinstance(tab, dict):
                continue
            md = (tab.get("markdown") or "").strip()
            if not md:
                continue
            rows = _parse_gfm_table(md)
            part = _apply_rules_to_rows(rows, None)
            _merge_dicts(combined, part)
    text = ""
    for p in report_data.get("content") or []:
        for blk in p.get("content") or []:
            if isinstance(blk, dict) and blk.get("text"):
                text += str(blk.get("text", "")) + "\n"
    text += "\n".join(
        (t.get("markdown") or "") for t in tables if isinstance(t, dict)
    )
    rp, ry = infer_report_period(text, identity)
    top: dict[str, Any] = {
        "report_period": rp,
        "report_year": ry,
        "core_performance_indicators_sheet": combined["core_performance_indicators_sheet"],
        "balance_sheet": combined["balance_sheet"],
        "cash_flow_sheet": combined["cash_flow_sheet"],
        "income_sheet": combined["income_sheet"],
    }
    return top
