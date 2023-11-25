from dataclasses import dataclass


@dataclass(slots=True)
class Counter:
    num_triggers: int = 0
    repeat_every_turn: bool = False
