from dataclasses import dataclass
from PyQt6.QtWidgets import QGridLayout
from ..widgets import TooltipCheckBox


@dataclass
class CheckboxOptionsLayout(QGridLayout):
    """Layout which is responsible for input of all additional parameters,
    like party buffs, or the assumed number of kills or hits taken."""

    def __init__(self, parent):
        super().__init__()

        self.assume_ult = TooltipCheckBox(
            parent, label="Assume Ultimate Activation",
            tooltip_text=("Assume Rotation starts with Ultimate activation. "
                          "They refund 5 energy on their activation."),
            checked=True)
        self.assume_ult.checkbox.stateChanged.connect(lambda:
                                                      parent.char_layout._enable_options(parent))

        self.assume_tingyun_ult = TooltipCheckBox(
            parent, label="Assume Tingyun Ult",
            tooltip_text="Tingyun Ultimate grants additional 50 energy.")

        self.assume_tingyun_e6 = TooltipCheckBox(
            parent, label="Assume Tingyun E6",
            tooltip_text="Tingyun Eidolon 6 grants additional 10 energy on her Ultimate.")

        self.show_detailed_breakdown = TooltipCheckBox(
            parent, label="Show detailed energy breakdown?",
            tooltip_text=("Currently limited, albeit accurate, energy breakdown "
                          "which lists energy sources and the amount of energy they generate."))

        self.show_er_breakpoints = TooltipCheckBox(
            parent, label="[BETA] Show Energy Recharge breakpoints?",
            tooltip_text=("Shows precise ER breakpoints, i.e., "
                          "the amount of additional ER needed to shorten a rotation by one turn.\n"
                          "Tested but might cause unintended problems. If so, please report them."),
            checked=True)

        self.addWidget(self.assume_ult, 0, 0)
        self.addWidget(self.show_detailed_breakdown, 1, 0)
        self.addWidget(self.assume_tingyun_ult, 0, 1)
        self.addWidget(self.assume_tingyun_e6, 1, 1)
        self.addWidget(self.show_er_breakpoints, 2, 0)
