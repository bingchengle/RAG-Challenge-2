"""泰迪杯工程入口。"""
from finance_agent_rag import config


def main() -> None:
    print("finance_agent_rag — 数据目录:", config.DATA_ROOT)
    print("输出目录:", config.OUTPUT_ROOT)
    print("实现 pipeline.task1 / task2 / task3 后在此挂接 CLI。")


if __name__ == "__main__":
    main()
