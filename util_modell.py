import typing

import matplotlib.pyplot as plt
import numpy as np

from util_modell_speicher_dezentral import Speicher_dezentral
from util_modell_zentralheizung import Zentralheizung

if typing.TYPE_CHECKING:
    from util_simulation import Stimulus


class Modell:
    def __init__(self):
        self.speichers: typing.List[Speicher_dezentral] = (
            Speicher_dezentral(
                startTempC=40.0,
                fernwaermefluss_liter_pro_h=148.0,
                label="Haus 40",
            ),
            Speicher_dezentral(
                startTempC=30.0,
                fernwaermefluss_liter_pro_h=148.0,
                label="Haus 30",
            ),
        )
        self.zentralheizung = Zentralheizung()

    def run(self, timestep_s: float, time_s: float, stimulus: "Stimulus"):
        for speicher in self.speichers:
            speicher.update_input(self.zentralheizung)
        for speicher in self.speichers:
            speicher.run(
                timestep_s=timestep_s,
                time_s=time_s,
                stimulus=stimulus,
                modell=self,
            )
        self.zentralheizung.update_input(self.speichers)
        self.zentralheizung.run(
            timestep_s=timestep_s,
            time_s=time_s,
            stimulus=stimulus,
            modell=self,
        )
