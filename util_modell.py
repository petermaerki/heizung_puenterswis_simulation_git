import typing

import matplotlib.pyplot as plt
import numpy as np

from util_modell_speicher_dezentral import Speicher_dezentral
from util_modell_zentralheizung import Zentralheizung

if typing.TYPE_CHECKING:
    from util_simulation import Stimulus


class Modell:
    def __init__(self):
        self.speichers: typing.List[
            Speicher_dezentral
        ] = (  # Werte gemaess Revisionsplan 1. Etappe 2008-08-20
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=148.0,
                label="Haus 1",
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=129.0,
                label="Haus 2",
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=129.0,
                label="Haus 3",
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=178.0,
                label="Haus 4",
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=155.9,
                label="Haus 5",
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=155.9,
                label="Haus 6",
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=146.0,
                label="Haus 7",
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=152.0,
                label="Haus 8",
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=125.0,
                label="Haus 9",
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=144.8,
                label="Haus 10",
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=154.9,
                label="Haus 11",
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=169.7,
                label="Haus 12",
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=161.8,
                label="Haus 13",
                totalvolumen_m3=0.97,  # Spezial Maerki Solarspeicher
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=141.7,
                label="Haus 14",
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=191.0,
                label="Haus 15",
            ),
        )
        self.zentralheizung = Zentralheizung()
        self.heizen = False
        self.umgebungstemperatur_C = 15.0
        self.heizkurve_heizungswasser_C = 20.0

    def run(self, timestep_s: float, time_s: float, stimulus: "Stimulus"):
        self.heizen = (
            self.umgebungstemperatur_C <= 20.0
        )  # gemaess Heizkurve VC Engineering
        self.heizkurve_heizungswasser_C = (
            20.0 - self.umgebungstemperatur_C
        ) * 10.0 / 28.0 + 25.0  # gemaess Heizkurve VC Engineering
        self.heizkurve_heizungswasser_C = min(
            self.heizkurve_heizungswasser_C, 35.0
        )  # gemaess Heizkurve VC Engineering
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
