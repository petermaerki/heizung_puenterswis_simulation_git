import typing

import matplotlib.pyplot as plt
import numpy as np

from util_modell_speicher_dezentral import Speicher_dezentral
from util_modell_speichers import Speichers
from util_modell_zentralheizung import Zentralheizung

if typing.TYPE_CHECKING:
    from util_simulation import Stimulus


class Modell:
    def __init__(self, stimuli: "StimuliWintertag"):
        self.stimuli = stimuli
        self.speichers = Speichers(stimuli=stimuli)
        self.zentralheizung = Zentralheizung(stimuli=stimuli)

    def run(self, timestep_s: float, time_s: float):
        self.speichers.update_input(self.zentralheizung)
        self.speichers.run(timestep_s=timestep_s, time_s=time_s, modell=self)
        self.zentralheizung.update_input(self.speichers)
        self.zentralheizung.run(
            timestep_s=timestep_s,
            time_s=time_s,
            modell=self,
        )
