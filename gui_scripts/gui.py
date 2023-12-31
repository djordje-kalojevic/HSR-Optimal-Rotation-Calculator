"""GUI that allows the user to input various parameters:
    - character
    - character related parameters (like Eidolons, certain talents, and traces)
    - equipment (like Light Cones, Relics, Ornaments, Ropes)
    - team buffs (e.g., Tingyun Ultimate)
    - additional parameters like the number of kills and hits taken."""

from dataclasses import dataclass
from typing import Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QLabel
from .widgets import Combobox, TooltipCheckBox, CounterInput
from .layouts.button_layout import ButtonLayout
from .layouts.character_selector import CharacterSelectorLayout
from .layouts.enemy_info_layout import EnemyInfoLayout
from .layouts.light_cone_selection import LightConeSelectionLayout
from .layouts.options_layout import OptionsLayout
from .layouts.relic_selection import RelicSelectionLayout
from .layouts.support_light_cone_selection import SupportLightConeSelectionLayout
from .gui_utils import get_int_from_selector
from .user_input import UserInput
from .counter import Counter
from character_utils.characters import CharStats, CHARACTERS
from character_utils.traces import TRACES
from character_utils.talents import TALENTS
from equipment_utils.light_cones import LIGHT_CONES
from equipment_utils.relic import Relic
from equipment_utils.relics import ALL_RELICS
from calculation_scripts.calculations import run_calculations


@dataclass
class MainWindowDemo(QDialog):
    """Main GUI window which allows the user to input all parameters."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("HSR Rotation Calculator Demo")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self._setup_layout()
        self.setMinimumWidth(650)

    def _setup_layout(self) -> None:
        """Creates and sets layout which allows user to input all the parameters."""

        layout = QVBoxLayout()
        padding = QWidget()

        layout.addWidget(QLabel(text="<u>Character info:</u>"))
        self.char_layout = CharacterSelectorLayout(self)
        layout.addLayout(self.char_layout)

        layout.addWidget(padding)
        layout.addWidget(QLabel(text="<u>Equipment info:</u>"))
        self.lc_layout = LightConeSelectionLayout(self)
        layout.addLayout(self.lc_layout)
        self.support_lc_layout = SupportLightConeSelectionLayout(self)
        layout.addLayout(self.support_lc_layout)
        self.relic_layout = RelicSelectionLayout(self)
        layout.addLayout(self.relic_layout)

        layout.addWidget(padding)
        layout.addWidget(QLabel(text="<u>Enemy info:</u>"))
        self.enemy_info_layout = EnemyInfoLayout(self)
        layout.addLayout(self.enemy_info_layout)

        layout.addWidget(padding)
        layout.addWidget(QLabel(text="<u>Combat info:</u>"))
        self.options_layout = OptionsLayout(self)
        layout.addLayout(self.options_layout)

        layout.addWidget(padding)
        self.button_layout = ButtonLayout(self)
        layout.addLayout(self.button_layout)

        self.setLayout(layout)

    def get_compatible_lc(self) -> None:
        """Filters out Light Cones that are not compatible with the character's path
        as they provide no relevant bonuses. Then adds these LCs to the relevant combobox.

        If there are no compatible LCs placeholder text will be displayed instead,
        and the combobox will be disabled."""

        selected_character = self.char_layout.char_selector.currentText()
        char = CHARACTERS.get(selected_character)
        if not char:
            return
        lcs = [lc.name for lc in LIGHT_CONES.values()
               if lc.path == char.path and not lc.is_support_lc]
        self.lc_layout.lc_selector.clear()

        if lcs:
            self.lc_layout.lc_selector.setEnabled(True)
            self.lc_layout.lc_selector.addItems(lcs)
            self.lc_layout.lc_selector.reset_selection()
        else:
            self.lc_layout.lc_selector.setPlaceholderText(
                "No supported Light Cones found for this Path")
            self.lc_layout.lc_selector.setEnabled(False)
            self.lc_layout.si_selector.setEnabled(False)

    def refresh_window(self) -> None:
        """Resets all inputs to their default values."""

        self.button_layout.confirm_button.setEnabled(False)

        for combo_box in self.findChildren(Combobox):
            combo_box.reset_selection()

        for check_box in self.findChildren(TooltipCheckBox):
            check_box.reset_selection()

        for custom_widget in self.findChildren(CounterInput):
            custom_widget.reset_selection()

        self.char_layout.char_selector.setEnabled(True)

    def enable_confirm_button(self) -> None:
        self.button_layout.confirm_button.setEnabled(True)

    def confirm_selection(self) -> None:
        """Confirms all input parameters then runs all necessary calculations."""

        self._collect_user_input()
        char = CHARACTERS.get(self.user_input.char_name)
        if not char:
            return

        stats = CharStats(char.ult_cost)
        if char.is_skill_attack:
            stats.is_skill_attack = True
        if char.is_ult_attack:
            stats.is_ult_attack = True

        run_calculations(stats, self.user_input)

    def _collect_user_input(self) -> None:
        """Collects user input and stores it to a UserInput object."""

        self.user_input = UserInput()
        self._collect_char_input()
        self._collect_gear_input()
        self._collect_combat_input()
        self._collect_other_input()

    def _collect_char_input(self) -> None:
        """Collects character input, this includes:
        their name, their Eidolon level, talent level, trace possessed,
        as well as whether their technique was used before combat."""

        self.user_input.char_name = self.char_layout.char_selector.currentText()
        self.user_input.eidolon_level = self.get_eidolon_level()
        self._collect_talent_input()
        selected_trace = self.char_layout.trace_selector.currentText()
        if selected_trace in TRACES.keys():
            self.user_input.trace = selected_trace
        self.user_input.technique = self.char_layout.technique_check.checkbox.isChecked()

    def _collect_talent_input(self):
        self.user_input.talent = TALENTS.get(self.user_input.char_name)
        if not self.user_input.talent:
            return

        self.user_input.talent.level = self._get_talent_level()
        if self.user_input.talent.level == 0:
            return

        self.user_input.talent.calculate_energy(self.user_input.talent.level)
        self.user_input.talent_triggers = self._get_talent_num_triggers()

    def _collect_gear_input(self) -> None:
        """Collects gear input, this includes:
        Light Cone's name, its Superimposition level,
        equipped relic, and the number of its triggers,
        equipped ornament, and Energy Recharge rope."""

        self.user_input.light_cone = self._get_light_cone()
        self.user_input.support_light_cone = self._get_support_light_cone()
        if self.user_input.support_light_cone:
            self.user_input.support_light_cone.trigger = self._get_support_lc_triggers()

        self.user_input.relic = self._get_relic()
        self.user_input.relic_trigger = self._get_relic_trigger()
        self.user_input.ornament = self.relic_layout.ornament_selector.currentText()
        self.user_input.rope = self.relic_layout.rope_selector.currentText()

    def _collect_combat_input(self) -> None:
        """Collects combat input, this includes the number of the following:
        hits taken, kills, ultimate kills, and follow-up attacks."""

        self.user_input.hits_taken = self._get_hits_taken()
        self.user_input.ally_hits_taken = self._get_ally_hits_taken()
        self.user_input.kills = self._get_kills()
        self.user_input.num_ult_kills = self._get_ult_kills()
        self.user_input.follow_ups = self._get_num_follow_ups()

    def _collect_other_input(self) -> None:
        options = self.options_layout.check_boxes
        user_input = self.user_input
        user_input.assume_ult = options.assume_ult.checkbox.isChecked()
        user_input.assume_tingyun_ult = options.assume_tingyun_ult.checkbox.isChecked()
        user_input.assume_tingyun_e6 = options.assume_tingyun_e6.checkbox.isChecked()
        user_input.detailed_breakdown = options.show_detailed_breakdown.checkbox.isChecked()
        user_input.show_er_breakpoints = options.show_er_breakpoints.checkbox.isChecked()
        user_input.matching_enemy_weakness = (
            self.enemy_info_layout.enemy_weakness.checkbox.isChecked())
        user_input.enemy_count = self._get_enemy_count()
        user_input.huohuo_ult_level = self._get_huohuo_ult_level()

    def _get_light_cone(self):
        light_cone_name = self.lc_layout.lc_selector.currentText()
        light_cone = LIGHT_CONES.get(light_cone_name)
        if not light_cone:
            return None

        light_cone.superimposition = self.lc_layout.si_selector.currentIndex() - 1
        light_cone.update_lc_bonus()

        return light_cone

    def _get_support_light_cone(self):
        support_light_cone_name = self.support_lc_layout.lc_selector.currentText()
        support_light_cone = LIGHT_CONES.get(support_light_cone_name)
        if not support_light_cone:
            return None

        support_light_cone.superimposition = self.support_lc_layout.si_selector.currentIndex() - 1
        support_light_cone.update_lc_bonus()

        return support_light_cone

    def get_eidolon_level(self) -> int:
        """Returns the selected Eidolons level."""
        return get_int_from_selector(self.char_layout.eidolons_selector)

    def _get_talent_level(self) -> int:
        """Returns the selected talent level."""
        return self.char_layout.talent_selector.get_num_input()

    def _get_talent_num_triggers(self) -> Counter:
        """Returns the selected number of talent triggers."""
        trigger_input = self.char_layout.talent_trigger_input

        num_triggers = trigger_input.get_num_input()
        every_turn_check = trigger_input.repeats_every_turn()
        return Counter(num_triggers, every_turn_check)

    def _get_support_lc_triggers(self) -> Counter:
        """Returns the selected number of relic triggers."""
        trigger_input = self.support_lc_layout.trigger_input

        num_triggers = trigger_input.get_num_input()
        every_turn_check = trigger_input.repeats_every_turn()
        return Counter(num_triggers, every_turn_check)

    def _get_relic(self) -> Optional[Relic]:
        """Returns the selected relic object."""
        relic_name = self.relic_layout.relic_selector.currentText()
        return ALL_RELICS.get(relic_name)

    def _get_relic_trigger(self) -> Counter:
        """Returns the selected number of relic triggers."""
        trigger_input = self.relic_layout.relic_trigger_input

        num_triggers = trigger_input.get_num_input()
        every_turn_check = trigger_input.repeats_every_turn()
        return Counter(num_triggers, every_turn_check)

    def _get_hits_taken(self) -> Counter:
        """Returns the selected number of hits taken."""
        trigger_input = self.options_layout.combo_boxes.hits_taken_cb

        num_triggers = trigger_input.get_num_input()
        every_turn_check = trigger_input.repeats_every_turn()
        return Counter(num_triggers, every_turn_check)

    def _get_ally_hits_taken(self) -> Counter:
        """Returns the selected number of hits taken."""
        trigger_input = self.options_layout.combo_boxes.ally_hits_taken_cb

        num_triggers = trigger_input.get_num_input()
        every_turn_check = trigger_input.repeats_every_turn()
        return Counter(num_triggers, every_turn_check)

    def _get_num_follow_ups(self) -> Counter:
        """Returns the selected number of follow-up attacks."""
        trigger_input = self.char_layout.follow_up_selector

        num_triggers = trigger_input.get_num_input()
        every_turn_check = trigger_input.repeats_every_turn()
        return Counter(num_triggers, every_turn_check)

    def _get_kills(self) -> Counter:
        """Returns the selected number of kills."""
        trigger_input = self.options_layout.combo_boxes.kills_input

        num_triggers = trigger_input.get_num_input()
        every_turn_check = trigger_input.repeats_every_turn()
        return Counter(num_triggers, every_turn_check)

    def _get_ult_kills(self) -> int:
        """Returns the selected number of ult kills."""
        trigger_input = self.options_layout.combo_boxes.ult_kills_input
        return trigger_input.get_num_input()

    def _get_enemy_count(self) -> int:
        """Returns the selected number of enemies.
        If no input is detected the default value is one enemy."""
        enemy_count = self.enemy_info_layout.enemy_count
        return enemy_count.get_num_input()

    def _get_huohuo_ult_level(self) -> int:
        """Returns the input level of HuoHuo's Ultimate."""
        return self.options_layout.combo_boxes.huohuo_ult_input.get_num_input()
