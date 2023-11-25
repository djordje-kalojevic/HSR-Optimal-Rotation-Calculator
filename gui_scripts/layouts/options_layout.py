from dataclasses import dataclass
from PyQt6.QtWidgets import QWidget, QGridLayout
from ..layouts.checkbox_options_layout import CheckboxOptionsLayout
from ..layouts.combobox_options_layout import ComboboxOptionsLayout


@dataclass
class OptionsLayout(QGridLayout):
    """Layout which is responsible for input of all additional parameters, like party buffs,
    or the assumed number of kills or hits taken."""

    def __init__(self, parent):
        super().__init__()

        self.combo_boxes = ComboboxOptionsLayout(parent)
        self.addLayout(self.combo_boxes, 0, 0)
        self.addWidget(QWidget())
        self.check_boxes = CheckboxOptionsLayout(parent)
        self.addLayout(self.check_boxes, 3, 0)
