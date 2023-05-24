import typing

import matplotlib.pyplot as plt
import numpy as np

from util_konstanten import DICHTE_WASSER, WASSER_WAERMEKAP
from util_stimuly import StimuliWintertag

if typing.TYPE_CHECKING:
    from util_modell import Modell
    from util_modell_speicher_dezentral import Speicher_dezentral
    from util_simulation import Stimulus


class PlotZentralheizung:
    def __init__(self, zentralheizung: "Zentralheizung"):
        self.zentralheizung = zentralheizung
        self.time_array_s = []
        self.time_steps_s = []
        self.fernwaerme_hot_C = []
        self.fernwaerme_cold_avg_C = []
        self.fernwaerme_leistung_W = []

    def append_plot(
        self,
        timestep_s: float,
        time_s: float,
    ):
        self.time_array_s.append(time_s)
        self.fernwaerme_hot_C.append(self.zentralheizung.fernwaerme_hot_C)
        self.fernwaerme_cold_avg_C.append(self.zentralheizung.fernwaerme_cold_avg_C)
        self.fernwaerme_leistung_W.append(self.zentralheizung.fernwaerme_leistung_W)

    def plot(self):
        fig, ax = plt.subplots()
        # ax.plot(t, s)
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.fernwaerme_hot_C,
            linestyle="solid",
            linewidth=2,
            color="red",
            alpha=0.95,
            label="fernwaerme_hot",
        )
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.fernwaerme_cold_avg_C,
            linestyle="solid",
            linewidth=3,
            color="blue",
            alpha=0.95,
            label="fernwaerme_cold",
        )
        ax2 = ax.twinx()
        ax2.plot(
            np.array(self.time_array_s) / 3600,
            self.fernwaerme_leistung_W,
            linestyle="solid",
            linewidth=1,
            color="black",
            alpha=0.5,
            label="fernwaerme_leistung_W",
        )
        # ax2.plot(np.array(self.time_array_s) / 3600, leistung_in_speicher, linestyle='dotted', linewidth=5, color='orange', alpha=0.5, label = 'leistung')
        ax.set(xlabel="time (h)", ylabel="Temperature C", title="Zentralheizung")
        ax2.set(ylabel="Power W")
        ax.legend()
        ax2.legend()
        ax.grid()
        plt.show()


class Zentralheizung:
    def __init__(
        self,
        stimuli: "StimuliWintertag",
    ):
        # self.fernwaerme_cold_C = []
        # self.fernwaermefluss_m3_pro_s = []
        # self.fernwaermefluss_leistung_W = 0.0
        # self.fernwaerme_cold_mischtemperatur_C = 0.0
        self.stimuli = stimuli
        self.fernwaerme_totalfluss_m3_pro_s = 0.0
        self.fernwaerme_hot_C = 40.0
        self.fernwaerme_leistung_W = 0.0
        self.fernwaerme_cold_avg_C = 0.0
        self.heizen = False
        self.heizkurve_heizungswasser_C = 20.0
        self.fernwaermepumpe_on = True

    def _update_heizkurve(self):
        self.heizen = (
            self.stimuli.umgebungstemperatur_C <= 20.0
        )  # gemaess Heizkurve VC Engineering
        self.heizkurve_heizungswasser_C = (
            20.0 - self.stimuli.umgebungstemperatur_C
        ) * 10.0 / 28.0 + 25.0  # gemaess Heizkurve VC Engineering
        self.heizkurve_heizungswasser_C = min(
            self.heizkurve_heizungswasser_C, 35.0
        )  # gemaess Heizkurve VC Engineering

    def update_input(self, speichers: typing.List["Speicher_dezentral"]):
        # self.fernwaerme_cold_C = []
        self._update_heizkurve()
        mischsumme = 0.0
        self.fernwaerme_totalfluss_m3_pro_s = 0.0
        for speicher in speichers:
            # self.fernwaerme_cold_C.append(speicher.fernwaerme_cold_C)
            # self.fernwaermefluss_m3_pro_s.append(speicher.fernwaermefluss_m3_pro_s)
            mischsumme += speicher.fernwaerme_cold_C * speicher.fernwaermefluss_m3_pro_s
            self.fernwaerme_totalfluss_m3_pro_s += speicher.fernwaermefluss_m3_pro_s
        self.fernwaerme_cold_avg_C = mischsumme / self.fernwaerme_totalfluss_m3_pro_s
        self.fernwaerme_leistung_W = (
            (self.fernwaerme_hot_C - self.fernwaerme_cold_avg_C)
            * DICHTE_WASSER
            * WASSER_WAERMEKAP
            * self.fernwaerme_totalfluss_m3_pro_s
        )

    # @property
    # def fernwaerme_cold_avg_C(self) -> float:

    # return sum(self.fernwaerme_cold_C) / len(self.fernwaerme_cold_C)

    def run(self, timestep_s: float, time_s: float, modell: "Modell"):
        # self.fernwaerme_hot_C = self.fernwaerme_cold_avg_C + 0.5
        erhoehung_waermeverluste_C = 5.0
        self.fernwaerme_hot_C = (
            modell.zentralheizung.heizkurve_heizungswasser_C
            + erhoehung_waermeverluste_C
        )
