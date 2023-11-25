from dataclasses import dataclass
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout
from ..widgets import Combobox, CounterInput
from relics import ALL_RELICS


@dataclass
class RelicSelectionLayout(QGridLayout):
    """Layout which is responsible for input of all parameters related to all types of relics,
    i.e., regular relics, ornaments, and energy recharge ropes.
    Additionally, user can configure how many times relic effects are triggered."""

    def __init__(self, parent):
        super().__init__()

        relics = [r.name for r in ALL_RELICS.values()
                  if r.relic_type == "relic"]
        self.relic_selector = Combobox(parent, text="--Select Relic--",
                                       items=relics)
        self.relic_selector.currentTextChanged.connect(
            self._enable_relic_toggle)
        self.relic_trigger_input = CounterInput("Relic Triggers:",
                                                parent)
        self.relic_trigger_input.setEnabled(False)

        ornaments = [o.name for o in ALL_RELICS.values()
                     if o.relic_type == "ornament"]
        self.ornament_selector = Combobox(parent, text="--Select Ornament--",
                                          items=ornaments)

        ropes = [r.name for r in ALL_RELICS.values()
                 if r.relic_type == "rope"]
        self.rope_selector = Combobox(parent, text="--Select Energy Recharge rope--",
                                      items=ropes)

        self.addWidget(self.relic_selector, 0, 0)
        self.addWidget(self.relic_trigger_input, 0, 1,
                       alignment=Qt.AlignmentFlag.AlignLeft)
        self.addWidget(self.ornament_selector, 1, 0)
        self.addWidget(self.rope_selector, 1, 1)

    def _enable_relic_toggle(self) -> None:
        self.relic_trigger_input.setEnabled(True)
