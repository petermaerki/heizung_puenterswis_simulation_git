import pathlib
from typing import TYPE_CHECKING, Any, Callable, List

import matplotlib.pyplot as plt
import numpy as np

from util_modell_fernleitung import Fernleitung
from util_modell_speicher_dezentral import Speicher_dezentral
from util_modell_speichers import Speichers
from util_modell_zentralheizung import Zentralheizung
from util_stimuli import Stimuli

if TYPE_CHECKING:
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


class Integrals:
    def __init__(
        self,
        objs: List[str],
        f_value: Callable[[Any, float], float],
        f_description: Callable[[Any], str],
    ):
        self.objs = objs
        self.f_value = f_value
        self.descriptions = [f_description(o) for o in self.objs]
        self.list_integrals = [0.0 for o in self.objs]
        self.list_values = []

    @property
    def data(self):
        return self.list_values

    def append_plot(self, timestep_s: float):
        for i, o in enumerate(self.objs):
            self.list_integrals[i] += self.f_value(o, timestep_s)
        self.list_values.append(self.list_integrals.copy())

    @property
    def summe(self) -> List[float]:
        sum_integral = []
        for i, list in enumerate(self.data):
            sum_integral.append(sum(list))
        return sum_integral


class PlotVerluste:
    def __init__(self, modell: "Modell"):
        self.modell = modell
        self.time_array_s = []

        def fernleitung_value(fernleitung: Fernleitung, timestep_s: float) -> float:
            return fernleitung.verlustleistung_W * timestep_s / 3600.0 / 1000.0

        def fernleitung_label(fernleitung: Fernleitung) -> float:
            return fernleitung.label

        self.fernleitung_kWh = Integrals(
            objs=[self.modell.fernleitung_cold, self.modell.fernleitung_hot],
            f_value=fernleitung_value,
            f_description=fernleitung_label,
        )

        def speicher_value(speicher: Speicher_dezentral, timestep_s: float) -> float:
            return speicher.verlustleistung_W * timestep_s / 3600.0 / 1000.0

        def speicher_description(speicher: Speicher_dezentral) -> float:
            return speicher.description

        self.speichers_kWh = Integrals(
            objs=self.modell.speichers.speichers,
            f_value=speicher_value,
            f_description=speicher_description,
        )

    def append_plot(self, timestep_s: float, time_s: float):
        self.time_array_s.append(time_s)
        self.fernleitung_kWh.append_plot(timestep_s=timestep_s)
        self.speichers_kWh.append_plot(timestep_s=timestep_s)

    def plot(self, directory: pathlib.Path):
        fig, ax = plt.subplots()
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.speichers_kWh.data,
            linestyle="solid",
            linewidth=1,
            color="green",
            alpha=0.5
            # label=self.speichers_kWh.labels,
        )
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.speichers_kWh.summe,
            linestyle="solid",
            linewidth=2,
            color="green",
            alpha=0.95,
            label="Häuser",
        )
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.fernleitung_kWh.data,
            linestyle="solid",
            linewidth=2,
            # color="blue",
            alpha=0.95,
            label=self.fernleitung_kWh.descriptions,
        )
        ax.set(
            xlabel="time (h)",
            ylabel="Energie kWh",
            title="Verluste",
        )
        ax.legend()
        ax.grid()
        if directory is None:
            plt.show()
            return
        plt.savefig(directory / f"verluste.png")
        plt.close()
