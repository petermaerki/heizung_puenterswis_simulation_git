import typing

import matplotlib.pyplot as plt
import numpy as np

from util_modell_fernleitung import Fernleitung
from util_modell_speicher_dezentral import Speicher_dezentral
from util_modell_speichers import Speichers
from util_modell_zentralheizung import Zentralheizung
from util_stimuli import Stimuli

if typing.TYPE_CHECKING:
    from util_simulation import Stimulus


class Modell:
    def __init__(self, stimuli: "Stimuli"):
        self.stimuli = stimuli
        self.speichers = Speichers(stimuli=stimuli)
        self.zentralheizung = Zentralheizung(stimuli=stimuli)
        self.fernleitung_cold = Fernleitung(stimuli=stimuli, label="cold")
        self.fernleitung_hot = Fernleitung(stimuli=stimuli, label="hot")

    def run(self, timestep_s: float, time_s: float):
        self.zentralheizung.update_input(
            speichers=self.speichers,
            fernleitung=self.fernleitung_cold,
        )
        self.zentralheizung.run(
            timestep_s=timestep_s,
            time_s=time_s,
            modell=self,
        )

        self.fernleitung_hot.update_input(rein=self.zentralheizung)
        self.fernleitung_hot.run(timestep_s=timestep_s, time_s=time_s, modell=self)

        self.speichers.update_input(self.fernleitung_hot)
        self.speichers.run(timestep_s=timestep_s, time_s=time_s, modell=self)

        self.fernleitung_cold.update_input(rein=self.speichers)
        self.fernleitung_cold.run(timestep_s=timestep_s, time_s=time_s, modell=self)
