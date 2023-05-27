import pathlib
import typing

import numpy as np
from matplotlib import pyplot as plt

from util_modell_speicher_dezentral import Speicher_dezentral

if typing.TYPE_CHECKING:
    from util_modell import Modell
    from util_modell_fernleitung import Fernleitung
    from util_modell_zentralheizung import Zentralheizung
    from util_stimuli import Stimuli


class Speichers:
    def __init__(
        self,
        stimuli: "Stimuli",
    ):
        self.in_fluss_m3_pro_s = 0.0
        self.out_fluss_m3_pro_s = 0.0

        self.speichers: typing.List[
            Speicher_dezentral
        ] = (  # Werte gemaess Revisionsplan 1. Etappe 2008-08-20
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=148.0,
                label="Haus 1 Normal",
                stimuli=stimuli,
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=129.0,
                label="Haus 2 Ferien",
                stimuli=stimuli,
                verbrauchsfaktor_grossfamilie=0.01,  # Ferien
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=129.0,
                label="Haus 3 Grossfamilie",
                stimuli=stimuli,
                verbrauchsfaktor_grossfamilie=1.4,  # Grossfamilie
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=178.0, label="Haus 4", stimuli=stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=155.9, label="Haus 5", stimuli=stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=155.9, label="Haus 6", stimuli=stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=146.0, label="Haus 7", stimuli=stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=152.0, label="Haus 8", stimuli=stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=125.0, label="Haus 9", stimuli=stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=144.8, label="Haus 10", stimuli=stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=154.9, label="Haus 11", stimuli=stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=169.7, label="Haus 12", stimuli=stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=161.8,
                label="Haus 13",
                totalvolumen_m3=0.97,  # Spezial Maerki Solarspeicher
                stimuli=stimuli,
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=141.7, label="Haus 14", stimuli=stimuli
            ),
            Speicher_dezentral(
                fernwaermefluss_liter_pro_h=191.0, label="Haus 15", stimuli=stimuli
            ),
        )

    def get_speicher(self, label: str) -> Speicher_dezentral:
        for speicher in self.speichers:
            if speicher.label == label:
                return speicher
        raise Exception(f"Speicher '{label}' nicht gefunden!")

    def update_input(self, fernleitung_hot: "Fernleitung"):
        for speicher in self.speichers:
            speicher.update_input(fernleitung_hot=fernleitung_hot)
        self.in_fluss_m3_pro_s = fernleitung_hot.out_fluss_m3_pro_s

    def run(self, timestep_s: float, time_s: float, modell: "Modell"):
        for speicher in self.speichers:
            speicher.run(
                timestep_s=timestep_s,
                time_s=time_s,
                modell=modell,
            )

        self.out_wasser_C = self.fernwaerme_cold_avg_C
        self.out_fluss_m3_pro_s = self.in_fluss_m3_pro_s

    @property
    def warmwasserladung_angefordert(self) -> bool:
        for speicher in self.speichers:
            if speicher.out_warmwasser_anforderung:
                return True
        return False

    @property
    def fernwaerme_totalfluss_m3_pro_s(self) -> float:
        fernwaerme_totalfluss_m3_pro_s = 0.0
        for speicher in self.speichers:
            fernwaerme_totalfluss_m3_pro_s += speicher.out_fernwaermefluss_m3_pro_s
        return fernwaerme_totalfluss_m3_pro_s

    @property
    def fernwaerme_cold_avg_C(self) -> float:
        mischsumme = 0.0
        for speicher in self.speichers:
            # self.fernwaerme_cold_C.append(speicher.fernwaerme_cold_C)
            # self.fernwaermefluss_m3_pro_s.append(speicher.fernwaermefluss_m3_pro_s)
            mischsumme += speicher.out_wasser_C * speicher.out_fernwaermefluss_m3_pro_s
        return mischsumme / self.fernwaerme_totalfluss_m3_pro_s


class PlotSpeichersAnforderungen:
    def __init__(self, speichers: Speichers):
        self.speichers = speichers
        self.time_array_s = []
        self.anforderungen_todo = []

    def append_plot(
        self,
        timestep_s: float,
        time_s: float,
    ):
        self.time_array_s.append(time_s)

        anforderungen = []
        for i, speicher in enumerate(self.speichers.speichers):
            anforderungen.append(int(speicher.out_warmwasser_anforderung) - i * 2.0)
        self.anforderungen_todo.append(anforderungen)

    def plot(self, directory: pathlib.Path):
        fig, ax = plt.subplots()
        # ax.plot(t, s)
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.anforderungen_todo,
            linestyle="solid",
            linewidth=1,
            color="blue",
            alpha=0.95,
            # label=[s.label for s in self.speichers.speichers],
        )
        ax.set_yticks([])
        ax.set(xlabel="time (h)", ylabel="Anforderungen", title="Speichers")
        ax.legend()
        ax.grid()
        if directory is None:
            plt.show()
            return
        plt.savefig(directory / "anforderungen.png")
        plt.clf()
