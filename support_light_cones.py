"""Module for handling support Light Cones, that is,
Light Cones that can be equipped on another character and still provide their bonuses."""


from characters import CharStats
from gui_scripts.gui_utils import UserInput
from light_cones import LightCone


def apply_support_lcs(stats: CharStats,
                      user_input: UserInput, curr_energy: float) -> float:
    """Applies various support LC bonuses,
    raging from temporary energy recharge boosts to bonus energy generation.
    After which it returns the new current energy value."""

    if (not user_input.support_light_cone
            or user_input.support_light_cone.recharge_type == "battle_start"):
        return curr_energy

    if user_input.support_light_cone.recharge_type == "temp_energy_recharge":
        apply_temp_er_support_lc(stats, user_input.support_light_cone,
                                 user_input.support_light_cone.num_triggers)

    if user_input.support_light_cone.num_triggers == 0:
        return curr_energy

    elif user_input.support_light_cone.recharge_type == "bonus_energy":
        curr_energy = apply_bonus_energy_support_lc(curr_energy,
                                                    user_input.support_light_cone)

    elif user_input.support_light_cone.name == "Quid Pro Quo":
        curr_energy = apply_quid_pro_quo_lc(stats.ult_cost, curr_energy,
                                            user_input.support_light_cone)

    if (user_input.support_light_cone.num_triggers != "every turn"
            and user_input.support_light_cone.num_triggers > 0):
        user_input.support_light_cone.num_triggers -= 1

    return curr_energy


def apply_bonus_energy_support_lc(curr_energy: float,
                                  support_light_cone: LightCone) -> float:
    curr_energy += support_light_cone.energy_values[support_light_cone.superimposition]
    return curr_energy


def apply_quid_pro_quo_lc(ult_cost: float, curr_energy: float,
                          support_light_cone: LightCone) -> float:
    if curr_energy <= ult_cost / 2:
        curr_energy += support_light_cone.energy_values[support_light_cone.superimposition]

    return curr_energy


def apply_temp_er_support_lc(stats: CharStats,
                             support_light_cone: LightCone, num_triggers: int | str):
    """Allows for the application of Light Cones that give temporary boosts to energy recharge.
    This is achieved by cache the stat values before the application,
    then retrieving those after the buff wears off.
    This is done in such a way because of how computers interpret float values."""

    lc_bonus = support_light_cone.energy_values[support_light_cone.superimposition] / 100

    if not support_light_cone.triggered and num_triggers != 0:
        stats.cache("before_carve_the_moon")
        stats.apply_energy_recharge(stats.energy_recharge + lc_bonus)
        support_light_cone.triggered = True

    elif support_light_cone.triggered and num_triggers == 0:
        stats.retrieve_cache("before_carve_the_moon")
        support_light_cone.triggered = False
        stats.retrieve_cache("before_carve_the_moon")
