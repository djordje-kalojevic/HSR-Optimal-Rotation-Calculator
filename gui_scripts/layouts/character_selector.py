from dataclasses import dataclass
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout
from ..gui_utils import get_int_from_selector
from ..widgets import Combobox, Tooltip, TooltipCheckBox, CounterInput, SearchBox
from .enemy_info_layout import EnemyInfoLayout
from .combobox_options_layout import ComboboxOptionsLayout
from .options_layout import OptionsLayout
from character_utils.characters import Character, CHARACTERS, CHARACTER_NAMES
from character_utils.eidolons import EIDOLONS
from character_utils.follow_ups import FOLLOW_UP_ATTACKS
from character_utils.talents import TALENTS
from character_utils.traces import TRACES


@dataclass
class CharacterSelectorLayout(QGridLayout):
    """Layout which is responsible for input of all parameters related to characters,
    i.e., their name, Eidolons, talents, traces, and follow-up attacks."""

    def __init__(self, parent):
        super().__init__()

        self.char_selector = SearchBox(text="--Search Characters--",
                                       items=CHARACTER_NAMES)

        self.char_selector.currentTextChanged.connect(parent.get_compatible_lc)
        self.char_selector.currentTextChanged.connect(lambda:
                                                      self._enable_options(parent))
        self.char_selector.currentTextChanged.connect(
            parent.enable_confirm_button)

        self.eidolons_selector = Combobox(parent, text="--Eidolon Level--")
        self.eidolons_selector.setMinimumWidth(175)
        self.eidolons_selector.currentTextChanged.connect(
            lambda: self._enable_options(parent, "Skip Eidolons"))
        self.eidolons_selector.setEnabled(False)

        self.trace_selector = Combobox(parent, text="--Character Trace--")
        self.trace_selector.setEnabled(False)

        self.talent_selector = CounterInput("Talent Level:",
                                            parent, False, max=15)
        self.talent_selector.setEnabled(False)

        self.talent_trigger_input = CounterInput("Talent Triggers:", parent)
        self.talent_trigger_input.label.setMinimumWidth(110)
        self.talent_trigger_input.setEnabled(False)

        self.follow_up_selector = CounterInput("Follow-ups:", parent)
        self.follow_up_selector.label.setMinimumWidth(110)
        self.follow_up_selector.setEnabled(False)
        self.follow_up_tooltip = Tooltip(
            text=(("Please note that Topaz's follow-up attacks after her Ultimate, "
                   "are already included, this is for adding any additional such attacks.")))
        self.follow_up_tooltip.setEnabled(False)

        self.follow_up_input = QGridLayout()
        self.follow_up_input.addWidget(self.follow_up_selector, 0, 0, 1, 1)
        self.follow_up_input.addWidget(self.follow_up_tooltip, 0, 1, 1, 1)
        self.follow_up_input.setSpacing(0)

        self.technique_check = TooltipCheckBox(
            parent, label="Technique?",
            tooltip_text="Has this character's technique been used before combat?")
        self.technique_check.setEnabled(False)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.eidolons_selector)
        horizontal_layout.addWidget(self.technique_check)

        self.addWidget(self.char_selector, 1, 0)
        self.addLayout(horizontal_layout, 1, 2)
        self.addWidget(self.trace_selector, 2, 0)
        self.addLayout(self.follow_up_input, 2, 2,
                       alignment=Qt.AlignmentFlag.AlignLeft)
        self.addWidget(self.talent_selector, 3, 0)
        self.addWidget(self.talent_trigger_input, 3, 2,
                       alignment=Qt.AlignmentFlag.AlignLeft)

    def _enable_options(self, parent, options="") -> None:
        """Enables options based on what character's capable of.
        This includes Eidolons, traces, talents, follow-up attacks and the like."""

        char_name = self.char_selector.currentText()
        eidolon_level = get_int_from_selector(self.eidolons_selector)
        char = CHARACTERS.get(char_name)
        if not char:
            return

        # temporary way of avoiding infinite recursion
        if options != "Skip Eidolons":
            self._enable_char_eidolons(char_name)

        self._enable_ult_kills_input(parent, char)
        self._enable_char_traces(char_name)
        self._enable_char_talents(char_name, eidolon_level)
        self._enable_follow_up_attacks(parent, char_name)
        self._enable_technique_toggle(char)
        self._enable_enemy_weakness(parent, char_name)
        self._enable_ally_hits(parent, char_name)
        self._enable_huohuo_ult(parent, char_name)

    def _enable_ult_kills_input(self, parent, char: Character) -> None:
        options: ComboboxOptionsLayout = parent.options_layout.combo_boxes
        if char.is_ult_attack:
            options.ult_kills_input.setEnabled(True)

        else:
            options.ult_kills_input.setEnabled(False)
            options.ult_kills_input.reset_selection()

    def _enable_char_traces(self, char_name: str) -> None:
        """Fetches character specific Traces, and preselects them.
        If character has no Traces, however, the selection is reset,
        and the combobox is disabled."""

        self.trace_selector.clear()
        self.trace_selector.reset_selection()

        char_traces = [a.name for a in TRACES.values()
                       if a.char_name == char_name]

        if len(char_traces) > 0:
            self.trace_selector.setEnabled(True)
            self.trace_selector.addItems(char_traces)
            self.trace_selector.setCurrentText(char_traces[0])

        else:
            self.trace_selector.setEnabled(False)

    def _enable_char_eidolons(self, char_name: str) -> None:
        self.eidolons_selector.clear()
        self.eidolons_selector.reset_selection()

        char_eidolons = [str(e.eidolon_level) for e in EIDOLONS
                         if e.char_name == char_name]

        if char_eidolons:
            self.eidolons_selector.setEnabled(True)
            self.eidolons_selector.addItems(char_eidolons)

        else:
            self.eidolons_selector.setEnabled(False)

    def _enable_char_talents(self, char_name: str, eidolon_level: int) -> None:
        """Enables the option to select the Character's talents if they have them.
        Certain characters cannot increase the level of their talents,
        for them the option to select said level will be disabled."""

        self.talent_selector.setEnabled(False)
        self.talent_selector.reset_selection()
        self.talent_trigger_input.setEnabled(False)
        self.talent_trigger_input.reset_selection()
        talent = TALENTS.get(char_name)

        if not talent or char_name == "Welt" and eidolon_level < 2:
            return

        self.talent_selector.setEnabled(True)
        self.talent_trigger_input.setEnabled(True)

    def _enable_follow_up_attacks(self, parent, char_name: str) -> None:
        """Enables the option to select the number of follow-up attacks
        if the character possesses the ability to perform them.
        Note that Blade's follow-up attacks are a part of his rotations calculation
        thus they cannot be specified in this way."""

        eidolon_level: int = parent.get_eidolon_level()

        self.follow_up_selector.reset_selection()
        self.follow_up_selector.setEnabled(False)
        self.follow_up_tooltip.setEnabled(False)

        if not FOLLOW_UP_ATTACKS.get(char_name):
            return

        # Character name, condition for follow up attacks
        follow_up_conditions: dict[str, bool] = {
            "Blade": False,
            "Bronya": eidolon_level >= 4,
            "Dr. Ratio": True,
            "Herta": True,
            "Himeko": True,
            "Kafka": True,
            "March 7th": True,
            "Topaz": eidolon_level >= 2,
            "Yanqing": True
        }

        if follow_up_conditions.get(char_name):
            self.follow_up_selector.setEnabled(True)
            self.follow_up_tooltip.setEnabled(True)

    def _enable_technique_toggle(self, char: Character) -> None:
        """Enables the option to toggle the Character's technique if they have one."""

        if char.has_technique:
            self.technique_check.setEnabled(True)
        else:
            self.technique_check.reset_selection()
            self.technique_check.setEnabled(False)

    def _enable_enemy_weakness(self, parent, char_name: str) -> None:
        """Enables the option to toggle the enemy's elemental weakness 
        so that it matches character's element.
        Currently only Luka benefits from this."""

        enemy_info_layout: EnemyInfoLayout = parent.enemy_info_layout
        enemy_info_layout.enemy_weakness.setEnabled(False)
        if char_name == "Luka":
            enemy_info_layout.enemy_weakness.setEnabled(True)

    def _enable_ally_hits(self, parent, char_name: str) -> None:
        """Enables the option to select the number of times an ally was hit
        for characters that gain a bonus when that happens."""

        eidolon_level: int = parent.get_eidolon_level()
        options: OptionsLayout = parent.options_layout
        ally_hit_cb: CounterInput = options.combo_boxes.ally_hits_taken_cb
        ally_hit_tooltip: Tooltip = options.combo_boxes.ally_hits_taken_tooltip
        ult_assumed: bool = options.check_boxes.assume_ult.checkbox.isChecked()

        ally_hit_cb.reset_selection()
        ally_hit_cb.setEnabled(False)
        ally_hit_tooltip.setEnabled(False)

        # Character name, condition for ally hit bonuses, maximum input
        default_options = 10
        ally_hit_conditions = {
            ("Clara", ult_assumed):  2,
            ("Clara", ult_assumed and eidolon_level == 6):  3,
            ("Fu Xuan", eidolon_level >= 4): default_options,
            ("Lynx", True): default_options
        }

        maximum_input = ally_hit_conditions.get((char_name, True))
        if maximum_input:
            ally_hit_cb.spin_box.setMaximum(maximum_input)
            ally_hit_cb.setEnabled(True)
            ally_hit_tooltip.setEnabled(True)

    def _enable_huohuo_ult(self, parent, char_name: str) -> None:
        """Enables the option to select the level of HuoHuo's ultimate used, 
        note that this ultimate does not generate energy for HuoHuo herself, 
        thus the option is disabled for her."""

        options: ComboboxOptionsLayout = parent.options_layout.combo_boxes
        if char_name != "HuoHuo":
            options.huohuo_ult_input.setEnabled(True)
        else:
            options.huohuo_ult_input.reset_selection()
