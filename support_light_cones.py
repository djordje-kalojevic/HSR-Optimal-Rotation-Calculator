"""Module for handling support Light Cones, that is,
Light Cones that can be equipped on another character and still provide their bonuses."""


from characters import CharStats
from gui_scripts.user_input import UserInput
from light_cones import LightCone


def apply_support_lcs(stats: CharStats,
                      user_input: UserInput, curr_energy: float) -> float:
    """Applies various support LC bonuses,
    raging from temporary energy recharge boosts to bonus energy generation.
    After which it returns the new current energy value."""

    if (not user_input.support_light_cone
            or user_input.support_light_cone.trigger.num_triggers == 0):
        return curr_energy

    num_triggers = user_input.support_light_cone.trigger.num_triggers

    if user_input.support_light_cone.trigger.repeat_every_turn:
        for _ in range(num_triggers):
            curr_energy = apply_support_lc(stats, user_input.support_light_cone,
                                           curr_energy, num_triggers)
    elif num_triggers > 0:
        curr_energy = apply_support_lc(stats, user_input.support_light_cone,
                                       curr_energy, num_triggers)
        user_input.support_light_cone.trigger.num_triggers -= 1

    return curr_energy


def apply_support_lc(stats: CharStats, support_light_cone: LightCone,
                     curr_energy: float, num_triggers: int) -> float:
    """Applies Support Light Cone's bonus."""

    match support_light_cone.recharge_type:
        case "bonus_energy":
            curr_energy += support_light_cone.bonus * num_triggers
        case "temp_energy_recharge":
            apply_temp_er_support_lc(stats, support_light_cone, num_triggers)
        case "quid_pro_quo":
            curr_energy += apply_quid_pro_quo_lc(stats.ult_cost, curr_energy,
                                                 support_light_cone)

    return curr_energy


def apply_temp_er_support_lc(stats: CharStats,
                             support_light_cone: LightCone, num_triggers: int) -> None:
    """Allows for the application of Light Cones that give temporary boosts to energy recharge.
    This is achieved by cache the stat values before the application,
    then retrieving those after the buff wears off.
    This is done in such a way because of how computers interpret float values."""

    lc_bonus = support_light_cone.bonus / 100

    if not support_light_cone.triggered and num_triggers > 0:
        stats.cache("before_carve_the_moon")
        stats.apply_energy_recharge(stats.energy_recharge + lc_bonus)
        support_light_cone.triggered = True

    elif support_light_cone.triggered and num_triggers == 0:
        stats.retrieve_cache("before_carve_the_moon")
        support_light_cone.triggered = False


def apply_quid_pro_quo_lc(ult_cost: float, curr_energy: float,
                          support_light_cone: LightCone) -> float:
    """Quid Pro Quo Light Cone grants additional energy when the current energy is at or below 50%."""

    if curr_energy <= ult_cost / 2:
        return support_light_cone.bonus

    return 0
