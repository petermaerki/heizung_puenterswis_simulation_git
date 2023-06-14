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
        modell: "Modell",
    ):
        self.in_fluss_m3_pro_s = 0.0
        self.out_fluss_m3_pro_s = 0.0
        self.flussfaktor = 1.0

        self.speichers: typing.List[
            Speicher_dezentral
        ] = (  # Werte gemaess Revisionsplan 1. Etappe 2008-08-20
            Speicher_dezentral(
                stimuli=stimuli,
                modell=modell,
                fernwaermefluss_liter_pro_h=148.0 * self.flussfaktor,
                label="haus01_normal",
                description="Haus 1 Normal",
            ),
            Speicher_dezentral(
                stimuli=stimuli,
                modell=modell,
                fernwaermefluss_liter_pro_h=129.0 * self.flussfaktor,
                label="haus02_ferien",
                description="Haus 2 Ferien",
                verbrauchsfaktor_grossfamilie=0.01,  # Ferien
            ),
            Speicher_dezentral(
                stimuli=stimuli,
                modell=modell,
                fernwaermefluss_liter_pro_h=129.0 * self.flussfaktor,
                label="haus03_grossfamilie",
                description="Haus 3 Grossfamilie",
                verbrauchsfaktor_grossfamilie=1.3,  # Grossfamilie
            ),
            Speicher_dezentral(
                stimuli=stimuli,
                modell=modell,
                fernwaermefluss_liter_pro_h=178.0 * self.flussfaktor,
                label="haus04",
                description="Haus 4",
            ),
            Speicher_dezentral(
                stimuli=stimuli,
                modell=modell,
                fernwaermefluss_liter_pro_h=155.9 * self.flussfaktor,
                label="haus05",
                description="Haus 5",
            ),
            Speicher_dezentral(
                stimuli=stimuli,
                modell=modell,
                fernwaermefluss_liter_pro_h=155.9 * self.flussfaktor,
                label="haus06",
                description="Haus 6",
            ),
            Speicher_dezentral(
                stimuli=stimuli,
                modell=modell,
                fernwaermefluss_liter_pro_h=146.0 * self.flussfaktor,
                label="haus07",
                description="Haus 7",
            ),
            Speicher_dezentral(
                stimuli=stimuli,
                modell=modell,
                fernwaermefluss_liter_pro_h=152.0 * self.flussfaktor,
                label="haus08",
                description="Haus 8",
            ),
            Speicher_dezentral(
                stimuli=stimuli,
                modell=modell,
                fernwaermefluss_liter_pro_h=125.0 * self.flussfaktor,
                label="haus09",
                description="Haus 9",
            ),
            Speicher_dezentral(
                stimuli=stimuli,
                modell=modell,
                fernwaermefluss_liter_pro_h=144.8 * self.flussfaktor,
                label="haus10",
                description="Haus 10",
            ),
            Speicher_dezentral(
                stimuli=stimuli,
                modell=modell,
                fernwaermefluss_liter_pro_h=154.9 * self.flussfaktor,
                label="haus11",
                description="Haus 11",
            ),
            Speicher_dezentral(
                stimuli=stimuli,
                modell=modell,
                fernwaermefluss_liter_pro_h=169.7 * self.flussfaktor,
                label="haus12",
                description="Haus 12",
            ),
            Speicher_dezentral(
                stimuli=stimuli,
                modell=modell,
                fernwaermefluss_liter_pro_h=161.8 * self.flussfaktor,
                label="haus13",
                description="Haus 13",
                totalvolumen_m3=0.97,  # Spezial Maerki Solarspeicher
            ),
            Speicher_dezentral(
                stimuli=stimuli,
                modell=modell,
                fernwaermefluss_liter_pro_h=141.7 * self.flussfaktor,
                label="haus14",
                description="Haus 14",
            ),
            Speicher_dezentral(
                stimuli=stimuli,
                modell=modell,
                fernwaermefluss_liter_pro_h=191.0 * self.flussfaktor,
                label="haus15",
                description="Haus 15",
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
    def out_fernwaerme_angefordert(self) -> bool:
        for speicher in self.speichers:
            if speicher.out_fernwaerme_anforderung:
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
            mischsumme += (
                speicher.out_wasser_C * speicher.out_nominal_fernwaermefluss_m3_pro_s
            )
            if self.fernwaerme_totalfluss_m3_pro_s < 1e-9:
                return 0.0  # sieht besser aus im Diagramm
        return mischsumme / self.fernwaerme_totalfluss_m3_pro_s


class PlotSpeichersAnforderungen:
    def __init__(self, speichers: Speichers):
        self.speichers = speichers
        self.time_array_s = []
        self.anforderungen_warmwasser = []
        self.anforderungen_heizung = []

    def append_plot(
        self,
        timestep_s: float,
        time_s: float,
    ):
        self.time_array_s.append(time_s)

        heizung = []
        warmwasser = []
        for i, speicher in enumerate(self.speichers.speichers):
            heizung.append(int(speicher._heizung_anforderung) - i * 2.0 - 0.15)
            warmwasser.append(int(speicher._warmwasser_anforderung) - i * 2.0)
        self.anforderungen_heizung.append(heizung)
        self.anforderungen_warmwasser.append(warmwasser)

    def plot(self, directory: pathlib.Path):
        fig, ax = plt.subplots()
        # ax.plot(t, s)
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.anforderungen_heizung,
            linestyle="solid",
            linewidth=1,
            color="green",
            alpha=0.95,
            # label="Anforderung Heizung",
        )
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.anforderungen_warmwasser,
            linestyle="solid",
            linewidth=1,
            color="red",
            alpha=0.95,
            # label="Anforderung Warmwasser",
        )
        ax.set_yticks([])
        ax.set(
            xlabel="time (h)",
            ylabel="Anforderungen",
            title="Speichers, Warmwasser rot, Heizung grün",
        )
        ax.legend()
        ax.grid()
        if directory is None:
            plt.show()
            return
        plt.savefig(directory / "anforderungen.png")
        plt.close()
