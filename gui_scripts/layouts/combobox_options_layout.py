from PyQt6.QtWidgets import QGridLayout, QWidget
from ..widgets import Tooltip, CounterInput


class ComboboxOptionsLayout(QGridLayout):
    def __init__(self, parent):
        super().__init__()

        self.hits_taken_cb = CounterInput("Hits Taken:       ", parent)
        self.hits_taken_tooltip = Tooltip(text=("Your tooltip text here"))

        self.ally_hits_taken_cb = CounterInput("Ally Hits Taken:",
                                               parent)
        self.ally_hits_taken_cb.setEnabled(False)
        self.ally_hits_taken_tooltip = Tooltip(text=("Your tooltip text here"))

        self.kills_input = CounterInput(
            "Kills:                      ", parent)

        self.ult_kills_input = CounterInput("Ult Kills:                ", parent,
                                            show_checkbox=False)
        self.ult_kills_input.setEnabled(False)

        self.huohuo_ult_input = CounterInput("HuoHuo Ult Level:", parent,
                                             show_checkbox=False, max=12)
        self.huohuo_ult_input.setEnabled(False)

        self.hits_taken_input = QGridLayout()
        self.hits_taken_input.addWidget(self.hits_taken_cb, 0, 0, 1, 10)
        self.hits_taken_input.addWidget(self.hits_taken_tooltip, 0, 10, 1, 1)

        self.ally_hits_taken_input = QGridLayout()
        self.ally_hits_taken_input.addWidget(self.ally_hits_taken_cb,
                                             0, 0, 1, 10)
        self.ally_hits_taken_input.addWidget(self.ally_hits_taken_tooltip,
                                             0, 10, 1, 1)

        self.addWidget(self.kills_input, 0, 0, 1, 1)
        self.addWidget(QWidget(), 0, 1, 1, 1)
        self.addLayout(self.hits_taken_input, 0, 3, 1, 1)

        self.addWidget(self.ult_kills_input, 1, 0, 1, 1)
        self.addLayout(self.ally_hits_taken_input, 1, 3, 1, 1)
        self.addWidget(QWidget(), 0, 4, 1, 1)

        self.addWidget(self.huohuo_ult_input, 2, 0, 1, 1)

        self.setColumnStretch(1, 1)
        self.setColumnStretch(4, 1)

        self.setSpacing(10)
