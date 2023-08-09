from dataclasses import dataclass
from characters import CharStats
from gui_utils import UserInput


@dataclass(slots=True)
class Rotation:
    sequence: str
    skill_count: int = 0
    e_basic_count: int = 0
    basic_count: int = 0
    turns: int = 0


def print_detailed_breakdown(stats: CharStats,
                             user_input: UserInput, best_rotation: Rotation) -> None:

    print(f"Detailed energy breakdown ({stats.ult_cost} ult cost):")
    if best_rotation.basic_count > 0:
        basic = round(stats.basic, 3)
        total = round(basic * best_rotation.basic_count, 3)
        print(f"Basic: {basic} (total: {total})")

    if best_rotation.skill_count > 0:
        skill = round(stats.skill, 3)
        total = round(skill * best_rotation.skill_count, 3)
        print(f"Skill: {skill} (total: {total})")

    if best_rotation.e_basic_count > 0:
        e_basic = round(stats.e_basic, 3)
        total = round(e_basic * best_rotation.e_basic_count, 3)
        print(f"Enhanced Basic: {e_basic} (total: {total})")

    if user_input.assume_ult:
        print(f"Ultimate activation: {round(stats.ult_act, 3)}")

    _print_follow_up_details(stats, user_input, best_rotation)
    _print_get_hit_details(stats, user_input, best_rotation)
    _print_kill_details(stats, user_input, best_rotation)

    if user_input.num_ult_kills > 0:
        ult_kill_energy = round(stats.ult_kill, 3)
        total = round(ult_kill_energy * user_input.num_ult_kills, 3)
        print(f"Ultimate Kill: {ult_kill_energy} (total: {total})")

    print("\n")


def _print_kill_details(stats: CharStats,
                        user_input: UserInput, best_rotation: Rotation) -> None:
    kill_energy = round(stats.kill, 3)
    if user_input.num_kills == "every turn":
        total = kill_energy * best_rotation.turns
        print(f"Kill: {kill_energy} (total: {total})")

    elif user_input.num_kills > 0:
        total = round(kill_energy * user_input.num_kills, 3)
        print(f"Kill: {kill_energy} (total: {total})")


def _print_get_hit_details(stats: CharStats,
                           user_input: UserInput, best_rotation: Rotation) -> None:
    get_hit_energy = round(stats.get_hit, 3)

    if user_input.num_hits_taken == "every turn":
        total = get_hit_energy * best_rotation.turns
        print(f"Hit taken: {get_hit_energy} (total: {total})\n"
              "(note that it's assumed you get hit for 10 energy)")

    elif user_input.num_hits_taken > 0:
        total = round(get_hit_energy * user_input.num_hits_taken, 3)
        print(f"Hit taken: {get_hit_energy} (total: {total})\n"
              "(note: assumed you get hit for 10 energy)")


def _print_follow_up_details(stats: CharStats,
                             user_input: UserInput, best_rotation: Rotation) -> None:
    if stats.follow_up > 0:
        follow_up = round(stats.follow_up, 3)

        if user_input.num_follow_ups == "every turn":
            total = follow_up * best_rotation.turns
            print(f"Follow-up: {follow_up} (total: {total})")

        elif user_input.num_follow_ups > 0:
            total = follow_up * user_input.num_follow_ups
            print(f"Follow-up: {follow_up} (total: {total})")

        else:
            print(f"Follow-up: {follow_up}")
