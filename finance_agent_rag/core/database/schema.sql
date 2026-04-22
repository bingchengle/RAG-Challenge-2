-- 来源：赛题「附件3：数据库-表名及字段说明.xlsx」
-- 表名与字段英文名、类型与 xlsx 一致；可按需要增加索引。

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS teddy_b
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
USE teddy_b;

-- 中文：业绩指标表
DROP TABLE IF EXISTS `core_performance_indicators_sheet`;
CREATE TABLE `core_performance_indicators_sheet` (
  `serial_number`               INT            NULL,
  `stock_code`                  VARCHAR(20)    NOT NULL,
  `stock_abbr`                  VARCHAR(50)    NULL,
  `eps`                         DECIMAL(10,4)  NULL,
  `total_operating_revenue`     DECIMAL(20,2)  NULL,
  `operating_revenue_yoy_growth`  DECIMAL(10,4)  NULL,
  `operating_revenue_qoq_growth`  DECIMAL(10,4)  NULL,
  `net_profit_10k_yuan`         DECIMAL(20,2)  NULL,
  `net_profit_yoy_growth`       DECIMAL(10,4)  NULL,
  `net_profit_qoq_growth`       DECIMAL(10,4)  NULL,
  `net_asset_per_share`       DECIMAL(10,4)  NULL,
  `roe`                         DECIMAL(10,4)  NULL,
  `operating_cf_per_share`      DECIMAL(10,4)  NULL,
  `net_profit_excl_non_recurring`  DECIMAL(20,2)  NULL,
  `net_profit_excl_non_recurring_yoy` DECIMAL(10,4)  NULL,
  `gross_profit_margin`         DECIMAL(10,4)  NULL,
  `net_profit_margin`           DECIMAL(10,4)  NULL,
  `roe_weighted_excl_non_recurring` DECIMAL(10,4)  NULL,
  `report_period`               VARCHAR(20)    NOT NULL,
  `report_year`                 INT            NULL,
  PRIMARY KEY (`stock_code`, `report_period`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='核心业绩指标表';

-- 中文：资产负债表
DROP TABLE IF EXISTS `balance_sheet`;
CREATE TABLE `balance_sheet` (
  `serial_number`                        INT            NULL,
  `stock_code`                           VARCHAR(20)    NOT NULL,
  `stock_abbr`                           VARCHAR(50)    NULL,
  `asset_cash_and_cash_equivalents`      DECIMAL(20,2)  NULL,
  `asset_accounts_receivable`            DECIMAL(20,2)  NULL,
  `asset_inventory`                      DECIMAL(20,2)  NULL,
  `asset_trading_financial_assets`        DECIMAL(20,2)  NULL,
  `asset_construction_in_progress`       DECIMAL(20,2)  NULL,
  `asset_total_assets`                    DECIMAL(20,2)  NULL,
  `asset_total_assets_yoy_growth`         DECIMAL(10,4)  NULL,
  `liability_accounts_payable`            DECIMAL(20,2)  NULL,
  `liability_advance_from_customers`      DECIMAL(20,2)  NULL,
  `liability_total_liabilities`            DECIMAL(20,2)  NULL,
  `liability_total_liabilities_yoy_growth` DECIMAL(10,4)  NULL,
  `liability_contract_liabilities`         DECIMAL(20,2)  NULL,
  `liability_short_term_loans`           DECIMAL(20,2)  NULL,
  `asset_liability_ratio`                DECIMAL(10,4)  NULL,
  `equity_unappropriated_profit`         DECIMAL(20,2)  NULL,
  `equity_total_equity`                  DECIMAL(20,2)  NULL,
  `report_period`                        VARCHAR(20)    NOT NULL,
  `report_year`                          INT            NULL,
  PRIMARY KEY (`stock_code`, `report_period`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='资产负债表';

-- 中文：现金流量表
DROP TABLE IF EXISTS `cash_flow_sheet`;
CREATE TABLE `cash_flow_sheet` (
  `serial_number`                              INT            NULL,
  `stock_code`                                 VARCHAR(20)    NOT NULL,
  `stock_abbr`                                 VARCHAR(50)    NULL,
  `net_cash_flow`                              DECIMAL(20,2)  NULL,
  `net_cash_flow_yoy_growth`                    DECIMAL(10,4)  NULL,
  `operating_cf_net_amount`                    DECIMAL(20,2)  NULL,
  `operating_cf_ratio_of_net_cf`                DECIMAL(10,4)  NULL,
  `operating_cf_cash_from_sales`                DECIMAL(20,2)  NULL,
  `investing_cf_net_amount`                    DECIMAL(20,2)  NULL,
  `investing_cf_ratio_of_net_cf`                DECIMAL(10,4)  NULL,
  `investing_cf_cash_for_investments`            DECIMAL(20,2)  NULL,
  `investing_cf_cash_from_investment_recovery`  DECIMAL(20,2)  NULL,
  `financing_cf_cash_from_borrowing`            DECIMAL(20,2)  NULL,
  `financing_cf_cash_for_debt_repayment`         DECIMAL(20,2)  NULL,
  `financing_cf_net_amount`                    DECIMAL(20,2)  NULL,
  `financing_cf_ratio_of_net_cf`                DECIMAL(10,4)  NULL,
  `report_period`                              VARCHAR(20)    NOT NULL,
  `report_year`                                INT            NULL,
  PRIMARY KEY (`stock_code`, `report_period`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='现金流量表';

-- 中文：利润表
DROP TABLE IF EXISTS `income_sheet`;
CREATE TABLE `income_sheet` (
  `serial_number`                        INT            NULL,
  `stock_code`                          VARCHAR(20)    NOT NULL,
  `stock_abbr`                          VARCHAR(50)    NULL,
  `net_profit`                          DECIMAL(20,2)  NULL,
  `net_profit_yoy_growth`                 DECIMAL(10,4)  NULL,
  `other_income`                        DECIMAL(20,2)  NULL,
  `total_operating_revenue`              DECIMAL(20,2)  NULL,
  `operating_revenue_yoy_growth`         DECIMAL(10,4)  NULL,
  `operating_expense_cost_of_sales`     DECIMAL(20,2)  NULL,
  `operating_expense_selling_expenses`  DECIMAL(20,2)  NULL,
  `operating_expense_administrative_expenses` DECIMAL(20,2)  NULL,
  `operating_expense_financial_expenses`  DECIMAL(20,2)  NULL,
  `operating_expense_rnd_expenses`      DECIMAL(20,2)  NULL,
  `operating_expense_taxes_and_surcharges` DECIMAL(20,2)  NULL,
  `total_operating_expenses`            DECIMAL(20,2)  NULL,
  `operating_profit`                    DECIMAL(20,2)  NULL,
  `total_profit`                        DECIMAL(20,2)  NULL,
  `asset_impairment_loss`              DECIMAL(20,2)  NULL,
  `credit_impairment_loss`              DECIMAL(20,2)  NULL,
  `report_period`                        VARCHAR(20)    NOT NULL,
  `report_year`                         INT            NULL,
  PRIMARY KEY (`stock_code`, `report_period`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='利润表';

SET FOREIGN_KEY_CHECKS = 1;
