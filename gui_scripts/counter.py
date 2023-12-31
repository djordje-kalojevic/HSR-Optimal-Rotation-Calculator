from dataclasses import dataclass


@dataclass(slots=True)
class Counter:
    num_triggers: int = 0
    repeat_every_turn: bool = False
    energy: float = 0
    _original_num_triggers: int = 0

    def cache(self):
        if self._original_num_triggers == 0:
            self._original_num_triggers = self.num_triggers

    def retrieve_cache(self):
        self.num_triggers = self._original_num_triggers
