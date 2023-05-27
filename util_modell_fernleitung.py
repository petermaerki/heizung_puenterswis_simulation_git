import pathlib
import typing

import matplotlib.pyplot as plt
import numpy as np

from util_konstanten import DICHTE_WASSER, WASSER_WAERMEKAP
from util_modell_speichers import Speichers
from util_modell_zentralheizung import Zentralheizung
from util_stimuli import Stimuli

if typing.TYPE_CHECKING:
    from util_modell import Modell
    from util_modell_speicher_dezentral import Speicher_dezentral
    from util_simulation import Stimulus


class PlotFernleitung:
    def __init__(self, fernleitung: "Fernleitung"):
        # self.modell = modell
        # self.speicher = speicher
        self.time_array_s = []
        self.fernleitung = fernleitung
        # self.energie_verfuegbar_brauchwasser_kWh = []
        # self.energie_verfuegbar_heizung_kWh = []
        self.fernwaerme_wassertemperatur_rein_array_C = []
        self.fernwaerme_wassertemperatur_array_raus_C = []
        # self.fernwaerme_fluss_array_m3_pro_s = []
        self.verlustleistung_array_W = []

    def append_plot(
        self,
        timestep_s: float,
        time_s: float,
    ):
        self.time_array_s.append(time_s)
        self.fernwaerme_wassertemperatur_rein_array_C.append(
            self.fernleitung.in_wasser_C
        )
        self.fernwaerme_wassertemperatur_array_raus_C.append(
            self.fernleitung.out_wasser_C
        )
        # self.fernwaerme_fluss_array_m3_pro_s.append(self.fernleitung.out_fluss_m3_pro_s)
        self.verlustleistung_array_W.append(self.fernleitung.verlustleistung_W)

    def plot(self, directory: pathlib.Path):
        fig, ax = plt.subplots()
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.fernwaerme_wassertemperatur_rein_array_C,
            linestyle="solid",
            linewidth=2,
            color="red",
            alpha=0.95,
            label="Fernleitung wasser rein temperatur C",
        )
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.fernwaerme_wassertemperatur_array_raus_C,
            linestyle="solid",
            linewidth=2,
            color="blue",
            alpha=0.95,
            label="Fernleitung wasser raus temperatur C",
        )
        ax.set(
            xlabel="time (h)",
            ylabel="Temperatur",
            title="Fernleitung Tempeatur ",  # + self.speicher.label,
        )
        ax.set(xlabel="time (h)", ylabel="Temperature C", title="Zentralheizung")
        ax2 = ax.twinx()
        ax2.plot(
            np.array(self.time_array_s) / 3600,
            np.array(self.verlustleistung_array_W) / 1000.0,
            linestyle="dotted",
            linewidth=3,
            color="black",
            alpha=0.95,
            label="Fernleitung Verlustleistung kW",
        )
        ax2.set(ylabel="Power kW")
        ax2.legend()
        ax.legend()
        ax.grid()
        # plt.savefig(
        #     "C:/data/peters_daten\haus_13_zelglistrasse_49/heizung/heizung_peter_schaer_siedlung/heizung_puenterswis_simulation_git/pictures/energiereserve_"
        #     + self.speicher.label
        #     + ".png"
        # )
        if directory is None:
            plt.show()
            return
        plt.savefig(directory / f"fernleitung_{self.fernleitung.label}.png")
        plt.clf()


class Fernleitung:  # eine Leitung, also vorlauf oder ruecklauf, Siedlung Puenterswies
    def __init__(self, stimuli: "Stimuli", label: str):
        self.label = label
        self.stimuli = stimuli
        self.in_fluss_m3_pro_s = 0.0
        self.out_fluss_m3_pro_s = 0.0
        self.in_wasser_C = 0.0
        self.out_wasser_C = 0.0
        self.verlustleistung_W = 0.0
        self.fernleitung_waermekapazitaet_J_pro_K = (
            9.24e5  # aus 20230525a_kennzahlen.ods
        )

        self.fernleitung_verlustwaerme_leitwert_W_pro_K = (
            48.0  # aus 20230525a_kennzahlen.ods
        )
        self.fernleitungstemperatur_C = 20.0
        self.umgebungstemperatur_C = 20.0  # im Sommer hoeher, im Winter tiefer, in der Erde anders. Hier ganz grob ein fixer Wert unabhaengig der Jahreszeit.

    def update_input(self, rein: typing.Union[Zentralheizung, Speichers]):
        self.in_wasser_C = rein.out_wasser_C
        self.in_fluss_m3_pro_s = rein.out_fluss_m3_pro_s

    def run(self, timestep_s: float, time_s: float, modell: "Modell"):
        self.out_fluss_m3_pro_s = self.in_fluss_m3_pro_s

        self.verlustleistung_W = (
            self.fernleitungstemperatur_C - self.umgebungstemperatur_C
        ) * self.fernleitung_verlustwaerme_leitwert_W_pro_K
        verlustenergie_J = self.verlustleistung_W * timestep_s
        self.fernleitungstemperatur_C -= (
            verlustenergie_J / self.fernleitung_waermekapazitaet_J_pro_K
        )

        waermekap_wasser_austausch_J_pro_K = (
            self.in_fluss_m3_pro_s * timestep_s * DICHTE_WASSER * WASSER_WAERMEKAP
        )

        # Ausgleich der Wärme zwischen Leitung und Wasser
        self.fernleitungstemperatur_C = (
            self.in_wasser_C * waermekap_wasser_austausch_J_pro_K
            + self.fernleitungstemperatur_C * self.fernleitung_waermekapazitaet_J_pro_K
        ) / (
            waermekap_wasser_austausch_J_pro_K
            + self.fernleitung_waermekapazitaet_J_pro_K
        )
        self.out_wasser_C = self.fernleitungstemperatur_C
