"""公司/报告期/指标等槽位。TODO: 与 agents.clarify 配合。"""


class SlotMemory:
    def __init__(self) -> None:
        self.slots: dict = {}


def merge_turn(user_text: str, memory: SlotMemory) -> None:
    raise NotImplementedError
