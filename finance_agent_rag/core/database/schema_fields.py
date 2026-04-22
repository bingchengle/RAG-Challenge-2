"""四张表字段名（与 schema.sql 一致，供 loader / LLM 提示）。"""

CORE_PERF = [
    "serial_number",
    "eps",
    "total_operating_revenue",
    "operating_revenue_yoy_growth",
    "operating_revenue_qoq_growth",
    "net_profit_10k_yuan",
    "net_profit_yoy_growth",
    "net_profit_qoq_growth",
    "net_asset_per_share",
    "roe",
    "operating_cf_per_share",
    "net_profit_excl_non_recurring",
    "net_profit_excl_non_recurring_yoy",
    "gross_profit_margin",
    "net_profit_margin",
    "roe_weighted_excl_non_recurring",
]

BALANCE = [
    "serial_number",
    "asset_cash_and_cash_equivalents",
    "asset_accounts_receivable",
    "asset_inventory",
    "asset_trading_financial_assets",
    "asset_construction_in_progress",
    "asset_total_assets",
    "asset_total_assets_yoy_growth",
    "liability_accounts_payable",
    "liability_advance_from_customers",
    "liability_total_liabilities",
    "liability_total_liabilities_yoy_growth",
    "liability_contract_liabilities",
    "liability_short_term_loans",
    "asset_liability_ratio",
    "equity_unappropriated_profit",
    "equity_total_equity",
]

CASH_FLOW = [
    "serial_number",
    "net_cash_flow",
    "net_cash_flow_yoy_growth",
    "operating_cf_net_amount",
    "operating_cf_ratio_of_net_cf",
    "operating_cf_cash_from_sales",
    "investing_cf_net_amount",
    "investing_cf_ratio_of_net_cf",
    "investing_cf_cash_for_investments",
    "investing_cf_cash_from_investment_recovery",
    "financing_cf_cash_from_borrowing",
    "financing_cf_cash_for_debt_repayment",
    "financing_cf_net_amount",
    "financing_cf_ratio_of_net_cf",
]

INCOME = [
    "serial_number",
    "net_profit",
    "net_profit_yoy_growth",
    "other_income",
    "total_operating_revenue",
    "operating_revenue_yoy_growth",
    "operating_expense_cost_of_sales",
    "operating_expense_selling_expenses",
    "operating_expense_administrative_expenses",
    "operating_expense_financial_expenses",
    "operating_expense_rnd_expenses",
    "operating_expense_taxes_and_surcharges",
    "total_operating_expenses",
    "operating_profit",
    "total_profit",
    "asset_impairment_loss",
    "credit_impairment_loss",
]

COMMON_END = ["report_period", "report_year"]
