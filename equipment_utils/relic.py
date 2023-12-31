from dataclasses import dataclass


@dataclass(slots=True)
class Relic:
    """Dataclass that represents a relic.

    Attributes:
        - name: Relic's name.
        - relic_type: Type of the relic.
        - recharge_type: Type of the effect relic provides.
        - recharge_value: Amount of energy relic provides."""

    name: str
    relic_type: str
    recharge_type: str
    recharge_value: float
