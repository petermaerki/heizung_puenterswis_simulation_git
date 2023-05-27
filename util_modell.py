import pathlib
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


class IntegralBase:
    def __init__(self):
        self.value = 0.0

    @property
    def label(self) -> str:
        1 / 0

    def add(self, incr: float) -> None:
        self.value += incr

    def append_plot(
        self,
        timestep_s: float,
        time_s: float,
    ):
        raise NotImplementedError("Please override")


class IntegralFernleitung(IntegralBase):
    def __init__(self, fernleitung: Fernleitung):
        super().__init__()
        self.fernleitung = fernleitung

    @property
    def label(self) -> str:
        return self.fernleitung.label

    def append_plot(
        self,
        timestep_s: float,
    ):
        self.add(self.fernleitung.verlustleistung_W * timestep_s / 3600.0 / 1000.0)


class IntegralSpeicher(IntegralBase):
    def __init__(self, speicher: Speicher_dezentral):
        super().__init__()
        self.speicher = speicher

    @property
    def label(self) -> str:
        return self.speicher.label

    def append_plot(
        self,
        timestep_s: float,
    ):
        self.add(self.speicher.verlustleistung_W * timestep_s / 3600.0 / 1000.0)


class Integrals:
    def __init__(self, integrals: typing.List[IntegralBase]):
        self.integrals = integrals
        self.list_values = []

    @property
    def data(self):
        return self.list_values

    @property
    def labels(self) -> str:
        return [i.label for i in self.integrals]

    def append_plot(
        self,
        timestep_s: float,
    ):
        for i in self.integrals:
            i.append_plot(timestep_s=timestep_s)
        self.list_values.append([i.value for i in self.integrals])

        # TODO(hans)


# def summe_ueber_integrale(integrals: Integrals):
#     sum_integral = None
#     for i, list in enumerate(integrals.data):
#         if sum_integral is None:
#             sum_integral = integral.copy()
#         else:
#             for i, v in enumerate(sum_integral):
#                 sum_integral[i] = sum_integral[i] + v
#     return sum_integral

# sum_integral = None
# for integral in integrals.data:
#     if sum_integral is None:
#         sum_integral = integral.copy()
#     else:
#         for i, v in enumerate(sum_integral):
#             sum_integral[i] = sum_integral[i] + v
# return sum_integral


class PlotVerluste:
    def __init__(self, modell: "Modell"):
        self.modell = modell
        self.time_array_s = []
        self.fernleitung_kWh = Integrals(
            integrals=[
                IntegralFernleitung(self.modell.fernleitung_cold),
                IntegralFernleitung(self.modell.fernleitung_hot),
            ]
        )
        self.liste_speicher_kWh = Integrals(
            integrals=[IntegralSpeicher(s) for s in self.modell.speichers.speichers]
        )
        # self.liste_speicher_integral_kWh = [0.0 for _ in self.modell.speichers.speichers]
        # self.energie_verfuegbar_brauchwasser_kWh = []
        # self.energie_verfuegbar_heizung_kWh = []

    def append_plot(
        self,
        timestep_s: float,
        time_s: float,
    ):
        self.time_array_s.append(time_s)
        self.fernleitung_kWh.append_plot(timestep_s=timestep_s)
        self.liste_speicher_kWh.append_plot(timestep_s=timestep_s)

        # try:
        #     last = self.liste_speicher_kWh[-1]
        # except IndexError:
        #     last = [0.0 for s in self.modell.speichers.speichers]
        # new_values = []
        # for i, speicher in enumerate(self.modell.speichers.speichers):
        #     integral_kWh = last[i]
        #     integral_kWh += speicher.verlustleistung_W * timestep_s / 3600.0 / 1000.0
        #     new_values.append(integral_kWh)
        # self.liste_speicher_kWh.append(new_values)

        # self.liste_speicher.append(
        #     [
        #         s.verlustleistung_W * timestep_s / 3600.0 / 1000.0
        #         for s in self.modell.speichers.speichers
        #     ]
        # )
        # self.energie_verfuegbar_brauchwasser_kWh.append(
        #     self.speicher._waermeintegral_J(
        #         temperaturgrenze_C=TEMPERATURGRENZE_BRAUCHWASSER_C,
        #         entnahmehoehe_anteil_von_unten=1.0,
        #     )
        #     / (3600 * 1000)
        # )
        # self.energie_verfuegbar_heizung_kWh.append(
        #     self.speicher._waermeintegral_J(
        #         temperaturgrenze_C=self.modell.zentralheizung.heizkurve_heizungswasser_C,
        #         entnahmehoehe_anteil_von_unten=0.68,
        #     )
        #     / (3600 * 1000)
        # )

    def plot(self, directory: pathlib.Path):
        fig, ax = plt.subplots()
        # ax.plot(
        #     np.array(self.time_array_s) / 3600,
        #     self.energie_verfuegbar_brauchwasser_kWh,
        #     linestyle="solid",
        #     linewidth=2,
        #     color="red",
        #     alpha=0.95,
        #     label="Brauchwasser verfuegbar max",
        # )
        # ax.plot(
        #     np.array(self.time_array_s) / 3600,
        #     self.energie_verfuegbar_heizung_kWh,
        #     linestyle="solid",
        #     linewidth=2,
        #     color="black",
        #     alpha=0.95,
        #     label="Heizung verfuegbar max",
        # )
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.liste_speicher_kWh.data,
            linestyle="solid",
            linewidth=1,
            color="green",
            alpha=0.95,
            label=self.liste_speicher_kWh.labels,
        )
        # TODO(hans)
        # ax.plot(
        #     np.array(self.time_array_s) / 3600,
        #     summe_ueber_integrale(self.liste_speicher_kWh),
        #     linestyle="solid",
        #     linewidth=2,
        #     color="green",
        #     alpha=0.95,
        #     label="Häuser",
        # )
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.fernleitung_kWh.data,
            linestyle="solid",
            linewidth=2,
            # color="blue",
            alpha=0.95,
            label=self.fernleitung_kWh.labels,
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
        plt.clf()
