import pathlib
from dataclasses import dataclass

from util_modell import Modell
from util_simulation import Simulation


@dataclass
class Context:
    directory: pathlib.Path
    simulation: Simulation
    modell: Modell
