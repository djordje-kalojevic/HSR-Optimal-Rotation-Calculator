"""Module for handling character Traces.

This module provides functionality for reading character traces from a CSV file,
storing them, as well as applying their bonuses."""

from dataclasses import dataclass
from csv import DictReader
from .characters import CharStats


TRACES_CSV = "data/traces.csv"


@dataclass(slots=True)
class Trace:
    """Dataclass that represents a character's trace.

    Attributes:
        - char_name: Name of the character.
        - name: Name of the trace.
        - type: Type of the bonus trace provides.
        - value_bonus: Value of the bonus the trace provides."""

    char_name: str
    name: str
    type: str
    value_bonus: int


def apply_traces(stats: CharStats, trace_name: str = "") -> None:
    """Applies trace bonuses to the character's stats.

    Args:
        - stats: Character's stats to be modified.
        - trace_name: Name of the trace."""

    trace = TRACES.get(trace_name)

    if not trace:
        return

    value_bonus = trace.value_bonus

    match trace.type:
        case "basic":
            stats.basic += value_bonus
        case "battle_start":
            stats.init_energy += value_bonus
        case "ult_act":
            stats.ult_act += value_bonus
        case "yukong":
            stats.skill += 2 * value_bonus
        case "turn":
            stats.basic += value_bonus
            stats.skill += value_bonus


def _read_traces() -> dict[str, Trace]:
    """Reads the traces from the CSV file and returns them as a dictionary.

    Returns:
        - Dictionary of traces, where the keys are trace names,
        and the values are trace objects."""

    with open(TRACES_CSV, "r", encoding="utf-8") as file:
        traces: dict[str, Trace] = {}

        reader = DictReader(file)
        for row in reader:
            char_name = row["char_name"]
            name = row["trace_name"]
            type = row["trace_type"]
            value_bonus = int(row["value"])

            trace = Trace(char_name, name, type, value_bonus)
            traces[name] = trace

    return traces


TRACES = _read_traces()
