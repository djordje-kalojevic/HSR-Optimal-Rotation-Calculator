from dataclasses import dataclass
from PyQt6.QtWidgets import QGridLayout
from ..widgets import TooltipCheckBox, CounterInput


@dataclass
class EnemyInfoLayout(QGridLayout):
    def __init__(self, parent):
        super().__init__()

        self.enemy_count = CounterInput(label_text="Enemy Count:  ",
                                        show_checkbox=False,
                                        min=1, max=5)
        self.enemy_count.setMinimumWidth(200)

        self.enemy_weakness = TooltipCheckBox(
            parent, label="Enemy has corresponding weakness?",
            tooltip_text="Does the enemy have a weakness matching character's element?")
        self.enemy_weakness.setContentsMargins(50, 0, 0, 0)
        self.enemy_weakness.setEnabled(False)

        self.addWidget(self.enemy_count, 0, 0)
        self.addWidget(self.enemy_weakness, 0, 2)

        self.setColumnStretch(1, 1)
        self.setColumnStretch(3, 1)
