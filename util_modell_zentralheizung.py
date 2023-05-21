import typing

import matplotlib.pyplot as plt
import numpy as np

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

    def append_plot(
        self,
        timestep_s: float,
        time_s: float,
    ):
        self.time_array_s.append(time_s)
        self.fernwaerme_hot_C.append(self.zentralheizung.fernwaerme_hot_C)
        self.fernwaerme_cold_avg_C.append(self.zentralheizung.fernwaerme_cold_avg_C)

    def plot(self):
        fig, ax = plt.subplots()
        # ax.plot(t, s)
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.fernwaerme_hot_C,
            linestyle="dashed",
            linewidth=3,
            color="red",
            alpha=0.5,
            label="fernwaerme_hot",
        )
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.fernwaerme_cold_avg_C,
            linestyle="dotted",
            linewidth=3,
            color="blue",
            alpha=0.5,
            label="fernwaerme_cold",
        )
        # ax2 = ax.twinx()
        # ax2.plot(np.array(self.time_array_s) / 3600, leistung_in_speicher, linestyle='dotted', linewidth=5, color='orange', alpha=0.5, label = 'leistung')
        ax.set(xlabel="time (h)", ylabel="Temperature C", title="Zentralheizung")
        # ax2.set(ylabel='Power W')
        ax.legend()
        # ax2.legend()
        ax.grid()
        plt.show()


class Zentralheizung:
    def __init__(self):
        self.fernwaerme_cold_C = []
        self.fernwaerme_hot_C = 0.0

    def update_input(self, speichers: typing.List["Speicher_dezentral"]):
        self.fernwaerme_cold_C = []
        for speicher in speichers:
            self.fernwaerme_cold_C.append(speicher.fernwaerme_cold_C)

    @property
    def fernwaerme_cold_avg_C(self) -> float:
        return sum(self.fernwaerme_cold_C) / len(self.fernwaerme_cold_C)

    def run(
        self, timestep_s: float, time_s: float, stimulus: "Stimulus", modell: "Modell"
    ):
        self.fernwaerme_hot_C = self.fernwaerme_cold_avg_C + 0.5
