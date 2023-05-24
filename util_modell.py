import typing

import matplotlib.pyplot as plt
import numpy as np

from util_modell_speicher_dezentral import Speicher_dezentral
from util_modell_zentralheizung import Zentralheizung

if typing.TYPE_CHECKING:
    from util_simulation import Stimulus


class Modell:
    def __init__(self, stimuli: "StimuliWintertag"):
        self.stimuli = stimuli
        self.speichers: typing.List[
            Speicher_dezentral
        ] = (  # Werte gemaess Revisionsplan 1. Etappe 2008-08-20
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=148.0,
                label="Haus 1 Normal",
                stimuli=self.stimuli,
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=129.0,
                label="Haus 2 Ferien",
                stimuli=self.stimuli,
                verbrauchsfaktor_party=0.01,  # Ferien
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=129.0,
                label="Haus 3 Party",
                stimuli=self.stimuli,
                verbrauchsfaktor_party=1.8,  # Party
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=178.0, label="Haus 4", stimuli=self.stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=155.9, label="Haus 5", stimuli=self.stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=155.9, label="Haus 6", stimuli=self.stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=146.0, label="Haus 7", stimuli=self.stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=152.0, label="Haus 8", stimuli=self.stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=125.0, label="Haus 9", stimuli=self.stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=144.8, label="Haus 10", stimuli=self.stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=154.9, label="Haus 11", stimuli=self.stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=169.7, label="Haus 12", stimuli=self.stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=161.8,
                label="Haus 13",
                totalvolumen_m3=0.97,  # Spezial Maerki Solarspeicher
                stimuli=self.stimuli,
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=141.7, label="Haus 14", stimuli=self.stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=191.0, label="Haus 15", stimuli=self.stimuli
            ),
        )
        self.zentralheizung = Zentralheizung(stimuli=stimuli)

    def run(self, timestep_s: float, time_s: float):
        for speicher in self.speichers:
            speicher.update_input(self.zentralheizung)
        for speicher in self.speichers:
            speicher.run(
                timestep_s=timestep_s,
                time_s=time_s,
                modell=self,
            )
        self.zentralheizung.update_input(self.speichers)
        self.zentralheizung.run(
            timestep_s=timestep_s,
            time_s=time_s,
            modell=self,
        )
