from dataclasses import dataclass
from typing import Optional, Iterable
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (QDialog, QWidget, QLabel, QComboBox, QGridLayout,
                             QCheckBox, QFormLayout, QStyle, QPushButton, QHBoxLayout)
from characters import Character, CHARACTERS, CHARACTER_NAMES
from traces import TRACES
from eidolons import EIDOLONS
from talents import TALENTS
from follow_ups import FOLLOW_UP_ATTACKS
from light_cones import LIGHT_CONES
from relics import ALL_RELICS


@dataclass
class Combobox(QComboBox):
    """Custom combobox widget.

    Attributes:
        - text (str): the first item and the placeholder text.
        - items (Iterable[str]) Optional: Items to be added to the combobox."""

    def __init__(self, parent, text="", items: Optional[Iterable[str]] = None):
        super().__init__(parent)
        self.text = text
        if self.text:
            self.addItem(self.text)
            self.setPlaceholderText(self.text)
        if items:
            self.addItems(items)
        self.setMaxVisibleItems(20)
        self.clearEditText()

    def reset_selection(self):
        """Resets widget to its default value."""
        self.setCurrentText(self.text)


@dataclass
class Tooltip(QLabel):
    """Custom tooltip widget."""

    def __init__(self, parent=None, text="", icon_size=QSize(16, 16)):
        super().__init__(parent)

        self.setToolTip(text)
        pixmap_name = QStyle.StandardPixmap.SP_MessageBoxQuestion
        style = self.style()
        if style:
            pixmap = style.standardPixmap(pixmap_name)
            resized_pixmap = pixmap.scaled(icon_size,
                                           Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation)
            self.setPixmap(resized_pixmap)


@dataclass
class TooltipCheckBox(QWidget):
    """Custom widget for displaying a checkbox with tooltip."""

    def __init__(self, parent: QDialog, label: str,
                 tooltip_text: str, checked=False, icon_size=QSize(16, 16)) -> None:
        super().__init__(parent)

        self.checked = checked
        form_layout = QFormLayout()
        self.checkbox = QCheckBox(label)
        self.checkbox.setChecked(checked)
        self.tooltip = Tooltip(parent, tooltip_text, icon_size)

        form_layout.addRow(self.checkbox, self.tooltip)
        self.setLayout(form_layout)

    def reset(self):
        """Resets widget to its default value."""
        self.checkbox.setChecked(self.checked)


@dataclass
class CharSelectorLayout(QGridLayout):
    """Layout which is responsible for input of all parameters related to characters,
    i.e., their name, Eidolons, talents, traces, and follow-up attacks."""

    def __init__(self, parent):
        super().__init__()

        self.char_selector = Combobox(parent, text="--Select Character--",
                                      items=CHARACTER_NAMES)
        self.char_selector.currentTextChanged.connect(parent.get_compatible_lc)
        self.char_selector.currentTextChanged.connect(lambda:
                                                      self._enable_options(parent))
        self.char_selector.currentTextChanged.connect(
            parent.enable_confirm_button)

        self.eidolons_selector = Combobox(parent, text="--Eidolon Level--")
        self.eidolons_selector.setEnabled(False)
        self.eidolons_selector.currentTextChanged.connect(lambda:
                                                          self._enable_ally_hits(parent))

        self.trace_selector = Combobox(parent, text="--Character Trace--")
        self.trace_selector.setEnabled(False)

        self.talent_selector = Combobox(parent, text="--Talent Level--",
                                        items=[str(i) for i in range(1, 16)])
        self.talent_selector.setEnabled(False)

        self.follow_up_selector = Combobox(parent, text="--Follow-up Attacks--",
                                           items=(["every turn"] +
                                                  [str(i) for i in range(1, 11)]))
        self.follow_up_selector.setEnabled(False)

        self.technique_check = TooltipCheckBox(
            parent, label="Technique?",
            tooltip_text="Has this character's technique been used before combat?")
        self.technique_check.setEnabled(False)

        self.addWidget(self.char_selector, 1, 0)
        self.addWidget(self.eidolons_selector, 1, 1)
        self.addWidget(self.technique_check, 1, 2)
        self.addWidget(self.trace_selector, 2, 0)
        self.addWidget(self.talent_selector, 2, 1)
        self.addWidget(self.follow_up_selector, 2, 2)

    def _enable_options(self, parent) -> None:
        """Enables options based on what character's capable of.
        This includes Eidolons, traces, talents, follow-up attacks and the like."""

        char_name = self.char_selector.currentText()
        char = CHARACTERS.get(char_name)
        if not char:
            return

        self._enable_ult_kills_input(parent, char)
        self._enable_char_traces(char_name)
        self._enable_char_eidolons(char_name)
        self._enable_char_talents(char_name)
        self._enable_follow_up_attacks(char_name)
        self._enable_technique_toggle(char)
        self._enable_ally_hits(parent)

    def _enable_ult_kills_input(self, parent, char: Character) -> None:
        options: ComboboxOptionsLayout = parent.options_layout.combo_boxes
        if char.is_ult_attack:
            options.ult_kills_input.setEnabled(True)

        else:
            options.ult_kills_input.setEnabled(False)
            options.ult_kills_input.reset_selection()

    def _enable_char_traces(self, char_name: str) -> None:
        char_trace = [a.name for a in TRACES.values()
                      if a.char_name == char_name]
        if len(char_trace) > 1:
            self.trace_selector.setEnabled(True)
            self.trace_selector.clear()
            self.trace_selector.addItem("--Character Trace--")
            self.trace_selector.addItems(char_trace)

        else:
            self.trace_selector.setEnabled(False)
            self.trace_selector.reset_selection()

    def _enable_char_eidolons(self, char_name: str) -> None:
        self.eidolons_selector.setEnabled(True)
        char_eidolons = [str(e.eidolon_level) for e in EIDOLONS
                         if e.char_name == char_name]
        if char_eidolons:
            self.eidolons_selector.setEnabled(True)
            self.eidolons_selector.clear()
            self.eidolons_selector.addItem("--Eidolon Level--")
            self.eidolons_selector.addItems(char_eidolons)
        else:
            self.eidolons_selector.setEnabled(False)
            self.eidolons_selector.reset_selection()

    def _enable_char_talents(self, char_name: str) -> None:
        """Enables the option to select the Character's talents if they have them."""

        if TALENTS.get(char_name):
            self.talent_selector.setEnabled(True)
        else:
            self.talent_selector.setEnabled(False)
            self.talent_selector.reset_selection()

    def _enable_follow_up_attacks(self, char_name: str) -> None:
        """Enables the option to select the number of follow-up attacks
        if the character possesses the ability to perform them
        Note that Blade's follow-up attacks are a part of his rotations calculation
        thus they cannot be specified in this way."""

        if FOLLOW_UP_ATTACKS.get(char_name) and char_name != "Blade":
            self.follow_up_selector.setEnabled(True)
        else:
            self.follow_up_selector.setEnabled(False)
            self.follow_up_selector.reset_selection()

    def _enable_technique_toggle(self, char: Character) -> None:
        """Enables the option to toggle the Character's technique if they have one."""

        if char.has_technique:
            self.technique_check.setEnabled(True)
        else:
            self.technique_check.setEnabled(False)

    def _enable_ally_hits(self, parent) -> None:
        char_name = self.char_selector.currentText()
        eidolon: int = parent.get_eidolons()
        options: OptionsLayout = parent.options_layout
        ally_hit_cb: Combobox = options.combo_boxes.ally_hits_taken_cb
        ult_assumed: bool = options.check_boxes.assume_ult.checkbox.isChecked()

        ally_hit_cb.clear()
        ally_hit_cb.addItem("--Assume ally hits taken--")
        ally_hit_cb.reset_selection()

        if char_name == "Lynx" or (char_name == "Fu Xuan" and eidolon >= 4):
            ally_hit_cb.addItems(["every turn"] +
                                 [str(i) for i in range(1, 11)])
            ally_hit_cb.setEnabled(True)

        elif char_name == "Clara" and ult_assumed:
            items = ["1", "2"]
            if eidolon == 6:
                items.append("3")
            ally_hit_cb.addItems(items)
            ally_hit_cb.setEnabled(True)

        else:
            ally_hit_cb.setEnabled(False)


@dataclass
class LightConeSelectionLayout(QGridLayout):
    """Layout which is responsible for input of all parameters related to Light Cones,
    i.e., their name, and their superimposition rank."""

    def __init__(self, parent):
        super().__init__()

        lcs = [lc.name for lc in LIGHT_CONES.values() if not lc.is_support_lc]
        self.lc_selector = Combobox(parent, text="--Select Light Cone--",
                                    items=lcs)
        self.lc_selector.currentTextChanged.connect(self._set_default_si)
        self.lc_selector.currentTextChanged.connect(
            self._enable_superimposition)

        self.si_selector = Combobox(parent, text="--Superimposition Level--",
                                    items=[f"Superimposition {i}" for i in range(1, 6)])
        self.si_selector.setEnabled(False)

        self.addWidget(self.lc_selector, 3, 0)
        self.addWidget(self.si_selector, 3, 1)

    def _enable_superimposition(self) -> None:
        selected_lc = self.lc_selector.currentText()
        light_cone = LIGHT_CONES.get(selected_lc)

        if light_cone:
            self.si_selector.setEnabled(True)
        else:
            self.si_selector.reset_selection()
            self.si_selector.setEnabled(False)

    def _set_default_si(self) -> None:
        """Sets default (assumed) superimposition level based on the following:
            - if the Light Cone is a three star, max superimposition is assumed
            - if the Light Cone is an event reward, max superimposition is assumed
            - otherwise, minimum superimposition is assumed"""

        selected_lc = self.lc_selector.currentText()
        light_cone = LIGHT_CONES.get(selected_lc)

        if not light_cone:
            return

        if light_cone.rarity == "3*" or light_cone.is_event_reward:
            self.si_selector.setCurrentText("Superimposition 5")
        else:
            self.si_selector.setCurrentText("Superimposition 1")


@dataclass
class SupportLightConeSelectionLayout(QGridLayout):
    """Layout which is responsible for input of all parameters related to Light Cones,
    i.e., their name, and their superimposition rank."""

    def __init__(self, parent):
        super().__init__()

        self.setColumnMinimumWidth(0, 325)

        support_lcs = [lc.name for lc in LIGHT_CONES.values()
                       if lc.is_support_lc]
        self.lc_selector = Combobox(parent, text="--Select Support Light Cone--",
                                    items=support_lcs)
        self.lc_selector.currentTextChanged.connect(self._set_default_si)
        self.lc_selector.currentTextChanged.connect(
            self._enable_superimposition)

        self.si_selector = Combobox(parent, text="--Superimposition Level--",
                                    items=[f"Superimposition {i}" for i in range(1, 6)])
        self.si_selector.setEnabled(False)
        self.trigger_input = Combobox(parent, text="--Light Cone Triggers--",
                                      items=(["every turn"] + [str(i) for i in range(1, 11)]))
        self.trigger_input.setEnabled(False)

        self.addWidget(self.lc_selector, 0, 0, 1, 2)
        self.addWidget(self.si_selector, 0, 3)
        self.addWidget(self.trigger_input, 0, 4)

    def _enable_superimposition(self) -> None:
        selected_lc = self.lc_selector.currentText()
        light_cone = LIGHT_CONES.get(selected_lc)

        if light_cone:
            self.si_selector.setEnabled(True)
        else:
            self.si_selector.reset_selection()
            self.si_selector.setEnabled(False)
            self.trigger_input.reset_selection()
            self.trigger_input.setEnabled(False)

    def _set_default_si(self) -> None:
        """Sets default (assumed) superimposition rank based on the following:
            - if the Light Cone is of the three star rarity, max superimposition rank is assumed
            - if the Light Cone is an event reward, max superimposition rank is assumed
            - otherwise, minimum superimposition rank is assumed"""

        selected_lc = self.lc_selector.currentText()
        light_cone = LIGHT_CONES.get(selected_lc)

        if not light_cone:
            return

        if light_cone.rarity == "3*" or light_cone.is_event_reward:
            self.si_selector.setCurrentText("Superimposition 5")
        else:
            self.si_selector.setCurrentText("Superimposition 1")

        if self.lc_selector.currentText() == "Fine Fruit":
            self.trigger_input.reset_selection()
            self.trigger_input.setEnabled(False)
        else:
            self.trigger_input.setEnabled(True)


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
        self.relic_trigger_input = Combobox(parent, text="--Relic Triggers--",
                                            items=(["every turn"] + [str(i) for i in range(1, 11)]))
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
        self.addWidget(self.relic_trigger_input, 0, 1)
        self.addWidget(self.ornament_selector, 1, 0)
        self.addWidget(self.rope_selector, 1, 1)

    def _enable_relic_toggle(self) -> None:
        self.relic_trigger_input.setEnabled(True)


@dataclass
class OptionsLayout(QGridLayout):
    """Layout which is responsible for input of all additional parameters, like party buffs,
    or the assumed number of kills or hits taken."""

    def __init__(self, parent):
        super().__init__()

        self.combo_boxes = ComboboxOptionsLayout(parent)
        self.addLayout(self.combo_boxes, 0, 0)

        self.check_boxes = CheckboxOptionsLayout(parent)
        self.addLayout(self.check_boxes, 1, 0)


@dataclass
class ComboboxOptionsLayout(QGridLayout):
    """Layout which is responsible for input of all additional parameters, like party buffs,
    or the assumed number of kills or hits taken."""

    def __init__(self, parent):
        super().__init__()

        self.hits_taken_input = QHBoxLayout()
        self.hits_taken_cb = Combobox(parent, text="--Assume hits taken--",
                                      items=(["every turn"] + [str(i) for i in range(1, 11)]))
        self.hits_taken_tooltip = Tooltip(
            text=("It is assumed that you get hit for 10 energy. "
                  "However, generated energy can range from 2 to 25 energy\n"
                  "depending on the enemy that hits you "
                  "or the number of hits the attack consists of."))

        self.ally_hits_taken_input = QHBoxLayout()
        self.ally_hits_taken_cb = Combobox(parent, text="--Assume ally hits taken--",
                                           items=(["every turn"] + [str(i) for i in range(1, 11)]))
        self.ally_hits_taken_tooltip = Tooltip(
            text=("Energy gained when ally gets hit. "
                  "Note that for Lynx to benefit from this ally must have Lynx's "
                  '"Survival Response" (continues healing effect) applied to them.\n'
                  "For Clara this refers to the energy gained from her Enhanced Counters "
                  "gained though the use of her ultimate."))
        self.ally_hits_taken_cb.setEnabled(False)

        self.kills_input = Combobox(parent, text="--Assume kills--",
                                    items=(["every turn"] + [str(i) for i in range(1, 11)]))

        self.ult_kills_input = Combobox(parent, text="--Assume Ult kills--",
                                        items=[str(i) for i in range(1, 6)])
        self.ult_kills_input.setEnabled(False)

        self.hits_taken_input.addWidget(self.hits_taken_cb, stretch=1)
        self.hits_taken_input.addWidget(self.hits_taken_tooltip)

        self.ally_hits_taken_input.addWidget(self.ally_hits_taken_cb,
                                             stretch=1)
        self.ally_hits_taken_input.addWidget(self.ally_hits_taken_tooltip)

        self.addLayout(self.hits_taken_input, 0, 0)
        self.addLayout(self.ally_hits_taken_input, 0, 1)
        self.addWidget(self.kills_input, 1, 0)
        self.addWidget(self.ult_kills_input, 1, 1)


@dataclass
class CheckboxOptionsLayout(QGridLayout):
    """Layout which is responsible for input of all additional parameters, like party buffs,
    or the assumed number of kills or hits taken."""

    def __init__(self, parent):
        super().__init__()

        self.assume_ult = TooltipCheckBox(
            parent, label="Assume Ultimate Activation",
            tooltip_text=("Assume Rotation starts with Ultimate activation. "
                          "They refund 5 energy on their activation."),
            checked=True)

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

        self.addWidget(self.assume_ult, 0, 0)
        self.addWidget(self.assume_tingyun_ult, 0, 1)
        self.addWidget(self.assume_tingyun_e6, 0, 2)
        self.addWidget(self.show_detailed_breakdown, 1, 0)


@dataclass
class EnemyInfoLayout(QGridLayout):
    def __init__(self, parent):
        super().__init__()

        self.enemy_count = Combobox(parent, text="--Enemy Count--",
                                    items=[str(i) for i in range(1, 6)])

        self.enemy_weakness = TooltipCheckBox(
            parent, label="Enemy has correctly weakness?",
            tooltip_text="Does the enemy has a weakness matching character's element?")

        self.addWidget(self.enemy_count, 0, 0)
        self.addWidget(self.enemy_weakness, 0, 1)


@dataclass
class ButtonLayout(QGridLayout):
    """Button layout with buttons for confirmation of all inputs,
    and button for refreshing the window, that is,
    for resetting all input value to their default values."""

    def __init__(self, parent):
        super().__init__()

        self.confirm_button = QPushButton("Confirm Selection")
        self.confirm_button.clicked.connect(parent.confirm_selection)
        self.confirm_button.setEnabled(False)

        self.reset_button = QPushButton("Reset Window")
        self.reset_button.clicked.connect(parent.refresh_window)
        self.addWidget(self.reset_button, 100, 0)
        self.addWidget(self.confirm_button, 100, 1)
