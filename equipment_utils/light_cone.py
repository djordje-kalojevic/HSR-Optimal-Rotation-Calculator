from dataclasses import dataclass, field
from gui_scripts.counter import Counter


@dataclass(slots=True)
class LightCone:
    """Dataclass that represents a Light Cone (LC).

    Attributes:
        - name: Name of the LC.
        - path: LC's path, i.e., which character's can get its bonus.
        - rarity: LC's rarity.
        - is_event_reward: Check whether the LC is an event reward or not.
        - recharge_type: Represents the type of the bonus LC provides.
        - superimposition: Superimposition rank of the LC."""

    name: str = ""
    path: str = ""
    rarity: str = ""
    is_support_lc: bool = False
    is_event_reward: bool = False
    recharge_type: str = ""
    superimposition: int = 0
    bonus: float = 0
    energy_values: list[float] = field(default_factory=lambda: [])
    triggered: bool = False
    trigger: Counter = field(default_factory=Counter)

    def update_lc_bonus(self) -> None:
        self.bonus = self.energy_values[self.superimposition]
