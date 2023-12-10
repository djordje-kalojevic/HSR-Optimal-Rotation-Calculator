"""Module used for selecting and applying the correct character algorithm."""

from characters import CharStats
from gui_scripts.user_input import UserInput
from calculation_scripts.rotation import RotationList
from .default_algorithm import dfs_algorithm_default, print_results_default
from .argenti_algorithm import dfs_algorithm_argenti, print_results_argenti
from .arlan_algorithm import dfs_algorithm_arlan
from .blade_algorithm import dfs_algorithm_blade, print_results_blade
from .DHIL_algorithm import dfs_algorithm_dhil, print_results_dhil
from .fu_xuan_algorithm import dfs_algorithm_fx
from .jingliu_algorithm import dfs_algorithm_jingliu
from .luka_algorithm import dfs_algorithm_luka
from .topaz_algorithm import dfs_algorithm_topaz
from .fire_mc_algorithm import dfs_algorithm_fire_mc


def apply_correct_algorithm(stats: CharStats, user_input: UserInput) -> RotationList:
    """Applies the correct Depth-First Search algorithm, that is,
    certain characters have their own customized algorithms,
    others use the default one.
    And returns all rotations found by the algorithm."""

    specific_algorithms = {
        "Argenti": dfs_algorithm_argenti,
        "Arlan": dfs_algorithm_arlan,
        "Blade": dfs_algorithm_blade,
        "Dan Heng IL": dfs_algorithm_dhil,
        "Fu Xuan": dfs_algorithm_fx,
        "Jingliu": dfs_algorithm_jingliu,
        "Luka": dfs_algorithm_luka,
        "Topaz": dfs_algorithm_topaz,
        "Trailblazer (Preservation)": dfs_algorithm_fire_mc
    }

    algorithm = specific_algorithms.get(user_input.char_name,
                                        dfs_algorithm_default)

    return algorithm(stats, user_input)


def print_results(stats: CharStats, user_input: UserInput, all_rotations: RotationList) -> None:
    """Prints calculation results for the given character. 
    If the character has a custom print function, that function will be used. 
    Otherwise, a default print function will be applied instead."""

    match user_input.char_name:
        case "Argenti":
            print_results_argenti(stats, user_input, all_rotations)
        case "Blade":
            print_results_blade(stats, user_input, all_rotations)
        case "Dan Heng IL":
            print_results_dhil(stats, user_input, all_rotations)
        case _:
            print_results_default(stats, user_input, all_rotations)
