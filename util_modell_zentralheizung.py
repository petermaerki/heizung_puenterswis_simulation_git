import pathlib
import typing

import matplotlib.pyplot as plt
import numpy as np

from util_konstanten import DICHTE_WASSER, WASSER_WAERMEKAP
from util_modell_speichers import Speichers
from util_stimuli import Stimuli

if typing.TYPE_CHECKING:
    from util_modell import Modell
    from util_modell_fernleitung import Fernleitung
    from util_modell_speicher_dezentral import Speicher_dezentral
    from util_simulation import Stimulus


class PlotFluss:
    def __init__(self, zentralheizung: "Zentralheizung"):
        self.time_array_s = []
        self.zentralheizung = zentralheizung
        self.values_fluss_m3_pro_s = []

    def append_plot(
        self,
        timestep_s: float,
        time_s: float,
    ):
        self.time_array_s.append(time_s)
        self.values_fluss_m3_pro_s.append(self.zentralheizung.out_fluss_m3_pro_s)

    def plot(self, directory: pathlib.Path):
        fig, ax = plt.subplots()
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.values_fluss_m3_pro_s,
            linestyle="solid",
            linewidth=2,
            color="black",
            alpha=0.95,
            label="Fluss",
        )
        ax.set(
            xlabel="time (h)",
            ylabel="Fluss (m3/s)",
            title="Fluss",
        )
        ax.legend()
        ax.grid()
        if directory is None:
            plt.show()
            return
        plt.savefig(directory / f"zentralheizung_fluss.png")
        plt.close()


class PlotZeitpunktePerioden:
    def __init__(self, zentralheizung: "Zentralheizung"):
        self.time_array_s = []
        self.zentralheizung = zentralheizung

    def append_plot(
        self,
        timestep_s: float,
        time_s: float,
    ):
        pass
        # self.time_array_s.append(time_s)

    def plot(self, directory: pathlib.Path):
        fig, ax = plt.subplots()
        ax.plot(
            np.array(self.zentralheizung.heizzyklenzeitpunte_s[1::]) / 3600,
            np.array(self.zentralheizung.heizzyklenperioden_s()[1::]) / 3600,
            "-o",
            # markevery="markers_on",
            # linestyle="solid",
            linewidth=2,
            color="purple",
            alpha=1.0,
            # label="Fluss",
        )
        ax.set(
            xlabel="time (h)",
            ylabel="Periode (h)",
            title="Heizzyklen Periodendauer",
        )
        ax.legend()
        ax.grid()
        if directory is None:
            plt.show()
            return
        plt.savefig(directory / f"zentralheizung_periode.png")
        plt.close()


class PlotZentralheizung:
    def __init__(self, zentralheizung: "Zentralheizung"):
        self.zentralheizung = zentralheizung
        self.time_array_s = []
        # self.time_steps_s = []
        self.fernwaerme_hot_C = []
        self.fernwaerme_cold_avg_C = []
        self.fernwaerme_leistung_W = []

    def append_plot(
        self,
        timestep_s: float,
        time_s: float,
    ):
        self.time_array_s.append(time_s)
        self.fernwaerme_hot_C.append(self.zentralheizung.out_wasser_C)
        self.fernwaerme_cold_avg_C.append(self.zentralheizung.in_wasser_C)
        self.fernwaerme_leistung_W.append(self.zentralheizung.fernwaerme_leistung_W)

    def plot(self, directory: pathlib.Path):
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
            linewidth=2,
            color="blue",
            alpha=0.95,
            label="fernwaerme_cold",
        )
        ax2 = ax.twinx()
        ax2.plot(
            np.array(self.time_array_s) / 3600,
            np.array(self.fernwaerme_leistung_W) / 1000.0,
            linestyle="solid",
            linewidth=1,
            color="black",
            alpha=0.5,
            label="fernwaerme_leistung kW",
        )
        # ax2.plot(np.array(self.time_array_s) / 3600, leistung_in_speicher, linestyle='dotted', linewidth=5, color='orange', alpha=0.5, label = 'leistung')
        ax.set(xlabel="time (h)", ylabel="Temperature C", title="Zentralheizung")
        ax.legend()
        ax2.set(ylabel="Power kW")

        ax2.legend()
        ax.grid()
        if directory is None:
            plt.show()
            return
        plt.savefig(directory / "zentralheizung.png")
        plt.close()


class Zentralheizung:
    def __init__(
        self,
        stimuli: "Stimuli",
    ):
        # self.fernwaerme_cold_C = []
        # self.fernwaermefluss_m3_pro_s = []
        # self.fernwaermefluss_leistung_W = 0.0
        # self.fernwaerme_cold_mischtemperatur_C = 0.0
        self.stimuli = stimuli
        self.fernwaerme_totalfluss_m3_pro_s = 0.0
        self.in_wasser_C = 0.0
        self.out_wasser_C = 40.0
        self.in_fluss_m3_pro_s = 40.0
        self.out_fluss_m3_pro_s = 40.0
        self.fernwaerme_leistung_W = 0.0
        self.heizkurve_heizungswasser_C = 20.0
        self.fernwaermepumpe_on = True
        self.warmwasserladung_start_s = None
        self.in_fernwaerme_angefordert = False
        self.heizzyklen_i = 0
        self.heizzyklenzeitpunte_s = []

    def heizzyklenperioden_s(self):
        last_time_s = 0.0
        perioden_array_s = []
        for zeitpunkt_s in self.heizzyklenzeitpunte_s:
            periode_s = zeitpunkt_s - last_time_s
            last_time_s = zeitpunkt_s
            perioden_array_s.append(periode_s)
        return perioden_array_s

    def _update_heizkurve(self):
        # self.heizen = (
        #     self.stimuli.umgebungstemperatur_C <= 20.0
        # )  # gemaess Heizkurve VC Engineering
        heizkurve_heizungswasser_C = (
            20.0 - self.stimuli.umgebungstemperatur_C
        ) * 10.0 / 28.0 + 25.0  # gemaess Heizkurve VC Engineering
        self.heizkurve_heizungswasser_C = min(
            heizkurve_heizungswasser_C, 35.0
        )  # gemaess Heizkurve VC Engineering

    def update_input(self, speichers: "Speichers", fernleitung: "Fernleitung"):
        self._update_heizkurve()
        self.in_fernwaerme_angefordert = speichers.out_fernwaerme_angefordert
        self.in_wasser_C = speichers.fernwaerme_cold_avg_C
        if not self.fernwaermepumpe_on:
            self.in_wasser_C = 20.0
        self.fernwaerme_leistung_W = (
            (self.out_wasser_C - self.in_wasser_C)
            * DICHTE_WASSER
            * WASSER_WAERMEKAP
            * speichers.fernwaerme_totalfluss_m3_pro_s
        )
        if not self.fernwaermepumpe_on:
            self.fernwaerme_leistung_W = 0.0

    # @property
    # def fernwaerme_cold_avg_C(self) -> float:

    # return sum(self.fernwaerme_cold_C) / len(self.fernwaerme_cold_C)

    def run(self, timestep_s: float, time_s: float, modell: "Modell"):
        self.out_wasser_C = None

        self._run(timestep_s=timestep_s, time_s=time_s, modell=modell)

        if self.fernwaermepumpe_on:
            self.out_fluss_m3_pro_s = modell.speichers.fernwaerme_totalfluss_m3_pro_s
        else:
            self.out_fluss_m3_pro_s = 0.0

    def _run(self, timestep_s: float, time_s: float, modell: "Modell"):
        warmwasser_rampe_rauf_s = 4.0 * 3600
        warmwasser_plateau_zeit_s = 7.0 * 3600
        self.fernwaermepumpe_on = False

        if self.warmwasserladung_start_s is None:
            if self.in_fernwaerme_angefordert:
                self.warmwasserladung_start_s = time_s
        else:
            duration_on_s = time_s - self.warmwasserladung_start_s
            assert duration_on_s >= 0.0
            if duration_on_s > warmwasser_plateau_zeit_s + warmwasser_rampe_rauf_s:
                self.warmwasserladung_start_s = None
                self.heizzyklen_i += 1
                self.heizzyklenzeitpunte_s.append(time_s)

            def calculate_C():
                rampe_start_C = 45.0
                fernwarme_max_C = 75.0
                if duration_on_s > warmwasser_rampe_rauf_s:
                    return fernwarme_max_C
                return (
                    rampe_start_C
                    + (fernwarme_max_C - rampe_start_C)
                    * duration_on_s
                    / warmwasser_rampe_rauf_s
                )

            self.out_wasser_C = calculate_C()
            self.fernwaermepumpe_on = True
            return

        if modell.stimuli.umgebungstemperatur_C < 20.0:
            self.fernwaermepumpe_on = True

            # geschätzer Verbrauch der Siedlung
            kalt_C = -14.0
            warm_C = 20.0
            leistung_warm_W = 10.0  # empirisch und aufgrund von "ca 5000W pro Haus"
            leistung_kalt_W = 4700.0  # empirisch und aufgrund von "ca 5000W pro Haus"
            leistung_W = (warm_C - self.stimuli.umgebungstemperatur_C) / (
                warm_C - kalt_C
            ) * (leistung_kalt_W - leistung_warm_W) + leistung_warm_W
            leistung_W = leistung_W * 15.0

            if modell.speichers.fernwaerme_totalfluss_m3_pro_s < 1e-9:
                self.out_wasser_C = 0.0
                return
            temperaturhub_fuer_leistung_C = leistung_W / (
                modell.speichers.fernwaerme_totalfluss_m3_pro_s
                * WASSER_WAERMEKAP
                * DICHTE_WASSER
            )
            erhoehung_reserve_C = 5.0
            self.out_wasser_C = (
                modell.zentralheizung.heizkurve_heizungswasser_C
                + temperaturhub_fuer_leistung_C
                + erhoehung_reserve_C
            )
            return
        self.out_wasser_C = 0.0
