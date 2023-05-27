import pathlib
from typing import TYPE_CHECKING, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

from util_konstanten import DICHTE_WASSER, WASSER_WAERMEKAP
from util_stimuli import Stimuli

if TYPE_CHECKING:
    from util_modell import Modell
    from util_modell_fernleitung import Fernleitung
    from util_modell_zentralheizung import Zentralheizung

TEMPERATURGRENZE_BRAUCHWASSER_C = 50.0
"""Diese Temperatur wird fuer Brauchwasser mindestens gebraucht"""


class DumpSchichtung:
    def __init__(self, speicher: "Speicher_dezentral"):
        self.speicher = speicher

    def append_plot(self, timestep_s: float, time_s: float):
        pass

    def plot(self, directory: pathlib.Path):
        self.speicher.dump(directory / f"schichtung_{self.speicher.label}.txt")
        vorher, nachher = self.speicher.purge_schichten()
        # print(f"{self.speicher.label} {vorher}->{nachher}")


class PlotSpeicher:
    def __init__(self, modell: "Modell", speicher: "Speicher_dezentral"):
        self.modell = modell
        self.speicher = speicher
        self.time_array_s = []
        self.fernwaerme_hot_C = []
        self.fernwaerme_cold_C = []
        self.temperaturen_C = []
        self.energie_verfuegbar_brauchwasser_kWh = []
        self.energie_verfuegbar_heizung_kWh = []

    def append_plot(
        self,
        timestep_s: float,
        time_s: float,
    ):
        self.time_array_s.append(time_s)
        self.temperaturen_C.append(self.speicher.temperaturprofil())
        self.fernwaerme_hot_C.append(self.speicher.in_wasser_C)
        self.fernwaerme_cold_C.append(self.speicher.out_wasser_C)
        self.energie_verfuegbar_brauchwasser_kWh.append(
            self.speicher._waermeintegral_J(
                temperaturgrenze_C=TEMPERATURGRENZE_BRAUCHWASSER_C,
                entnahmehoehe_anteil_von_unten=1.0,
            )
            / (3600 * 1000)
        )
        self.energie_verfuegbar_heizung_kWh.append(
            self.speicher._waermeintegral_J(
                temperaturgrenze_C=self.modell.zentralheizung.heizkurve_heizungswasser_C,
                entnahmehoehe_anteil_von_unten=0.68,
            )
            / (3600 * 1000)
        )

    def plot(self, directory: pathlib.Path):
        # plt.rcParams["figure.figsize"] = (20, 10)
        fig, ax = plt.subplots()
        # ax.plot(t, s)
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.temperaturen_C,
            linewidth=1.0,
            alpha=0.5,
        )
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.fernwaerme_hot_C,
            linestyle="dashed",
            linewidth=3,
            color="orange",
            alpha=0.5,
            label="fernwaerme_hot",
        )
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.fernwaerme_cold_C,
            linestyle="dotted",
            linewidth=3,
            color="green",
            alpha=0.5,
            label="fernwaerme_cold",
        )
        ax2 = ax.twinx()
        ax2.plot(
            np.array(self.time_array_s) / 3600,
            self.energie_verfuegbar_brauchwasser_kWh,
            linestyle="dashdot",
            linewidth=2,
            color="blue",
            alpha=0.5,
            label="Brauchwasser verfuegbar",
        )
        ax2.plot(
            np.array(self.time_array_s) / 3600,
            self.energie_verfuegbar_heizung_kWh,
            linestyle="dashdot",
            linewidth=2,
            color="red",
            alpha=0.5,
            label="Heizung verfuegbar",
        )
        ax.set(
            xlabel="time (h)",
            ylabel="Temperature (C)",
            title="Speicher Temperaturverlauf " + self.speicher.description,
        )
        ax2.set(ylabel="Energie kWh")
        ax.legend()
        ax2.legend()
        ax.grid()
        if directory is None:
            plt.show()
            return
        plt.savefig(directory / f"speicher_temperaturverlauf_{self.speicher.label}.png")
        plt.close()


class PlotEnergiereserve:
    def __init__(self, modell: "Modell", speicher: "Speicher_dezentral"):
        self.modell = modell
        self.speicher = speicher
        self.time_array_s = []
        self.energie_verfuegbar_brauchwasser_kWh = []
        self.energie_verfuegbar_heizung_kWh = []

    def append_plot(
        self,
        timestep_s: float,
        time_s: float,
    ):
        self.time_array_s.append(time_s)
        self.energie_verfuegbar_brauchwasser_kWh.append(
            self.speicher._waermeintegral_J(
                temperaturgrenze_C=TEMPERATURGRENZE_BRAUCHWASSER_C,
                entnahmehoehe_anteil_von_unten=1.0,
            )
            / (3600 * 1000)
        )
        self.energie_verfuegbar_heizung_kWh.append(
            self.speicher._waermeintegral_J(
                temperaturgrenze_C=self.modell.zentralheizung.heizkurve_heizungswasser_C,
                entnahmehoehe_anteil_von_unten=0.68,
            )
            / (3600 * 1000)
        )

    def plot(self, directory: pathlib.Path):
        fig, ax = plt.subplots()
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.energie_verfuegbar_brauchwasser_kWh,
            linestyle="solid",
            linewidth=2,
            color="red",
            alpha=0.95,
            label="Brauchwasser verfuegbar max",
        )
        ax.plot(
            np.array(self.time_array_s) / 3600,
            self.energie_verfuegbar_heizung_kWh,
            linestyle="solid",
            linewidth=2,
            color="black",
            alpha=0.95,
            label="Heizung verfuegbar max",
        )
        ax.set(
            xlabel="time (h)",
            ylabel="Energie kWh",
            title="Speicher verfügbare Energie " + self.speicher.description,
        )
        ax.legend()
        ax.grid()
        if directory is None:
            plt.show()
            return
        plt.savefig(directory / f"energiereserve_{self.speicher.label}.png")
        plt.close()


class PlotSpeicherSchichtung:
    def __init__(self, modell: "Modell", speicher: "Speicher_dezentral"):
        self.modell = modell
        self.speicher = speicher
        self.time_array_s = []
        self.time_steps_s = []
        self.temperaturen_C = []
        self.temperaturen_i = 20  # 100

    def append_plot(
        self,
        timestep_s: float,
        time_s: float,
    ):
        self.time_array_s.append(time_s)
        self.temperaturen_C.append(
            self.speicher.temperaturprofil(temperaturen_i=self.temperaturen_i)[::-1]
        )

    def plot(self, directory: pathlib.Path):
        if False:
            self.speicher.dump(
                pathlib.Path(f"tmp_dump_speicher_{self.speicher.label}.txt")
            )

        # TODO: Gesamtvolument berechen und überprüfen, ob der Speicher noch gleich voll ist.

        min_C = 10
        max_C = 80
        levels = np.linspace(min_C, max_C, max_C - min_C + 1)
        y = np.linspace(0, 1, self.temperaturen_i)
        X, Y = np.meshgrid(np.array(self.time_array_s) / 3600, y)

        plt.contourf(
            X,
            Y,
            np.transpose(self.temperaturen_C),
            levels,
            cmap="turbo",
            antialiased=True,
        )  # "Reds", 'coolwarm',"plasma"
        plt.colorbar(ticks=range(10, 90, 10), label="Temperature (C)")
        # plt.contour( X, Y, np.transpose(self.temperaturen_C), 8, colors="black", linewidth=0.5)
        # plt.ylabel("Speicherhöhe")
        plt.yticks([0, 1], ("unten", "oben"))
        plt.xlabel("time (h)")
        plt.title("Speicher Temperaturschichtung " + self.speicher.description)
        # ax.set(xlabel="time (h)", ylabel="Temperature C", title=self.speicher.label)
        if directory is None:
            plt.show()
            return
        plt.savefig(directory / f"schichtung__{self.speicher.label}.png")
        plt.close()


PURGE_COUNTER = 10
"""
Jedes zehnte Mal:Schichtung purge.
"""


class Speicher_dezentral:
    def __init__(
        self,
        stimuli: "Stimuli",
        label: str = "dummy_speicher",
        description: str = "Dummy Speicher",
        fernwaermefluss_liter_pro_h=150.0,
        startTempC=30.0,
        totalvolumen_m3=0.69,
        verbrauchsfaktor_grossfamilie=1.0,
    ):
        self.stimuli = stimuli
        self.label = label
        self.description = description
        self.startTempC = startTempC
        self.out_fernwaermefluss_m3_pro_s = fernwaermefluss_liter_pro_h / 1000 / 3600
        self.totalvolumen_m3 = totalvolumen_m3
        self.ruecklauf_bodenheizung_C = 24.0
        self.anteil_auslass_von_unten = 0.68
        self.volumen_auslass_von_unten_m3 = (
            self.anteil_auslass_von_unten * self.totalvolumen_m3
        )
        self.volumen_auslass_von_oben_m3 = (
            1 - self.anteil_auslass_von_unten
        ) * self.totalvolumen_m3
        # self.teilvolumen_m3 = 0.69 / self.teilspeicher_i
        self.verbrauchsfaktor_grossfamilie = verbrauchsfaktor_grossfamilie
        assert self.verbrauchsfaktor_grossfamilie > 1e-3
        self.packet_liste = [[startTempC, self.totalvolumen_m3]]
        """ self.teilspeicher_i * [(startTempC, self.teilvolumen_m3)] """
        self.volumenliste_vorher_debug = []
        self.in_wasser_C = 0.0
        self.out_wasser_C = 0.0
        self.warmwassernutzung = True
        self.heizungnutzung = True
        self.verlustleistung_W = False
        self.purge_counter = PURGE_COUNTER

    def reset(self, packets: Tuple[Tuple[float, float]]) -> None:
        self.packet_liste = []
        volumen_m3 = 0.0
        for temp_C, vol_m3 in packets:
            assert isinstance(temp_C, float)
            assert isinstance(vol_m3, float)
            self.packet_liste.append([temp_C, vol_m3])
            volumen_m3 += vol_m3
        self.packet_liste.append([self.startTempC, self.totalvolumen_m3 - volumen_m3])
        self.packet_liste.sort(reverse=True)

    def _waermeintegral_J(
        self, temperaturgrenze_C=39, entnahmehoehe_anteil_von_unten=0.68
    ):
        # Ruckzuckloesung: Tank in Schritten zerlegen und jeden Schritt summieren
        schrittweite = 0.01  # je feiner je genauer, dafuer aufwaendiger
        volumenschritt_m3 = self.totalvolumen_m3 * schrittweite
        temperaturen_x, volumen_y = self.temperaturprofil_xy()
        startvolumen_m3 = entnahmehoehe_anteil_von_unten * self.totalvolumen_m3
        volumenposition_m3 = startvolumen_m3
        energie_J = 0.0
        while volumenposition_m3 > 0.0:
            temperatur_C = np.interp(volumenposition_m3, volumen_y, temperaturen_x)
            energie_J += max(
                (temperatur_C - temperaturgrenze_C)
                * volumenschritt_m3
                * WASSER_WAERMEKAP
                * DICHTE_WASSER,
                0.0,
            )
            volumenposition_m3 -= volumenschritt_m3
            # print(f'volumenposition_m3 {volumenposition_m3:0.3f}, volumenschritt_m3 {volumenschritt_m3}, temperatur_C {temperatur_C:0.1f}, energie_J {energie_J:0.0f}')
        # print(f'Waemeintegral temperaturgrenze_C {temperaturgrenze_C} entnahmehoehe_anteil {entnahmehoehe_anteil_von_unten} energie_J {energie_J:0.3f}')
        return energie_J

    def print(self):
        for temp_C, volumen_m3 in self.packet_liste:
            print(
                f"Schichtung vom Speicher: Temperatur C: {temp_C:0.1f}, Volumen m^3: {volumen_m3:0.6f}"
            )

    @property
    def energie_total_J(self) -> None:
        energie_J = 0.0
        for temp_C, volumen_m3 in self.packet_liste:
            energie_J += temp_C * volumen_m3
        return energie_J * WASSER_WAERMEKAP * DICHTE_WASSER

    @property
    def berechnetes_volumen_total_m3(self) -> None:
        total_m3 = 0.0
        for temp_C, volumen_m3 in self.packet_liste:
            total_m3 += volumen_m3
        return total_m3

    @property
    def out_warmwasser_anforderung(self) -> bool:
        tempC, volumen_m3 = self.packet_liste[0]
        return tempC < TEMPERATURGRENZE_BRAUCHWASSER_C  # TODO(peter): +2.0

    def warnung_falls_volumenveraenderung(self) -> None:
        volumenabnahme_m3 = self.totalvolumen_m3 - self.berechnetes_volumen_total_m3
        if abs(volumenabnahme_m3) > 1e-9:
            print(f"WARNUNG: volumenabnahme_m3={volumenabnahme_m3:0.6f} m3\n")

    def purge_schichten(self) -> Tuple[int, int]:
        liste_vorher = self.packet_liste
        self.packet_liste = []
        last_entry = [1e12, 0.0]
        for packet_temp_C, packet_volumen_m3 in liste_vorher:
            if abs(last_entry[0] - packet_temp_C) < 0.01:
                last_entry[1] += packet_volumen_m3
                continue
            last_entry = [packet_temp_C, packet_volumen_m3]
            self.packet_liste.append(last_entry)
        return len(liste_vorher), len(self.packet_liste)

    def _purge(self) -> None:
        """
        Jedes PURGE_COUNTER mal sollen die Schichten gepurged werden.
        """
        self.purge_counter -= 1
        if self.purge_counter < 0:
            self.purge_counter = PURGE_COUNTER
            self.purge_schichten()

    def dump(self, filename=pathlib.Path, aux: dict = None):
        with filename.open("w") as f:
            f.write(f"Gesamtenergie {self.energie_total_J:0.1f} J\n")
            f.write(f"Gesamtvolumen {self.berechnetes_volumen_total_m3:0.6f} m^3\n")
            f.write("\n")

            f.write("Schichtung\n")
            f.write("Temperatur C Volumen m^3\n")
            for temp_C, volumen_m3 in self.packet_liste:
                f.write(f"{temp_C:0.1f} {volumen_m3:0.6f}\n")
            f.write("\n")

            if aux is not None:
                f.write("Aux\n")
                for key in sorted(aux):
                    f.write(f"{key}={aux[key]}\n")

            volumenabnahme_m3 = self.totalvolumen_m3 - self.berechnetes_volumen_total_m3
            if abs(volumenabnahme_m3) > 1e-9:
                f.write("\n")
                f.write(f"volumenabnahme_m3={volumenabnahme_m3:0.6f} m3\n")

    def austausch_zentralheizung(
        self, temp_rein_C: float, volumen_rein_m3: float
    ) -> float:
        if volumen_rein_m3 < 1e-9:
            return temp_rein_C
        self.packet_liste.append([temp_rein_C, volumen_rein_m3])
        self.packet_liste.sort(reverse=True)
        verbleibendes_volumen_m3 = volumen_rein_m3
        bezogene_energie = 0.0
        while True:
            packet_idx = len(self.packet_liste)
            tempC, volumen_m3 = self.packet_liste[packet_idx - 1]
            if volumen_m3 < verbleibendes_volumen_m3:
                self.packet_liste.pop()
                verbleibendes_volumen_m3 -= volumen_m3
                bezogene_energie += tempC * volumen_m3
                continue
            # Das ist das letzte packet
            bezogene_energie += tempC * verbleibendes_volumen_m3
            nicht_bezogenes_volumen_m3 = volumen_m3 - verbleibendes_volumen_m3
            self.packet_liste[packet_idx - 1] = [tempC, nicht_bezogenes_volumen_m3]
            # self.warnung_falls_volumenveraenderung()
            return bezogene_energie / volumen_rein_m3

    def austausch_warmwasser(self, energie_J=1.0) -> None:
        """
        Das Wasser wird zuoberst abgenommen.
        """
        kaltwasser_C = 15.0
        if energie_J < 1e-9:
            return kaltwasser_C
        verbleibende_energie_J = energie_J
        summe_bezogenes_volumen_m3 = 0.0
        while True:
            tempC, volumen_m3 = self.packet_liste[0]
            temperaturhub_C = tempC - kaltwasser_C
            packet_energie_J = (
                volumen_m3 * temperaturhub_C * WASSER_WAERMEKAP * DICHTE_WASSER
            )
            packet_genug_warm = tempC >= TEMPERATURGRENZE_BRAUCHWASSER_C
            if packet_genug_warm:
                if 0.0 <= packet_energie_J < verbleibende_energie_J:
                    self.packet_liste.pop(0)
                    verbleibende_energie_J -= packet_energie_J
                    summe_bezogenes_volumen_m3 += volumen_m3
                    continue

            # Das ist das letzte packet
            if packet_genug_warm:
                bezogenes_volumen_m3 = verbleibende_energie_J / (
                    temperaturhub_C * WASSER_WAERMEKAP * DICHTE_WASSER
                )
                summe_bezogenes_volumen_m3 += bezogenes_volumen_m3
                nicht_bezogenes_volumen_m3 = volumen_m3 - bezogenes_volumen_m3
                self.packet_liste[0] = [tempC, nicht_bezogenes_volumen_m3]
            else:
                print(
                    f"WARNUNG: Speicher {self.label}: tempC({tempC:0.2f}C) < TEMPERATURGRENZE_BRAUCHWASSER_C({TEMPERATURGRENZE_BRAUCHWASSER_C:0.2f}C)"
                )

            if summe_bezogenes_volumen_m3 > 0.0:
                self.packet_liste.insert(0, [kaltwasser_C, summe_bezogenes_volumen_m3])
                self.packet_liste.sort(reverse=True)

            # self.warnung_falls_volumenveraenderung()
            return

    def austausch_heizung(self, energie_J=1.0):
        """
        Das Wasser wird zuoberst abgenommen.

        Fehlerfälle:
          Energie nicht verfügbar.
        Manipulationen am Kessel
          1-n Pakete entziehen
          0-1 Paket einfügen
        """
        if energie_J < 1e-9:
            return self.ruecklauf_bodenheizung_C
        summe_bezogene_energie_J = 0.0
        summe_bezogenes_volumen_m3 = 0.0

        def get_idx() -> int:
            """
            Gibt den index von dem Packet zurück, das vor dem Heizausgang liegt.
            """
            sum_volumen_m3 = 0.0
            for idx, (tempC, packet_volumen_m3) in enumerate(self.packet_liste):
                sum_volumen_m3 += packet_volumen_m3
                if sum_volumen_m3 > self.volumen_auslass_von_oben_m3:
                    return idx
            raise Exception("get_idx(). Speicher nicht voll")

        packet_idx = get_idx()
        while True:
            if packet_idx >= len(self.packet_liste):
                print(f"WARNUNG: Speicher {self.label}: Zu wenig Wärme.")
                break
            packet_tempC, packet_volumen_m3 = self.packet_liste[packet_idx]
            temperaturhub_C = packet_tempC - self.ruecklauf_bodenheizung_C
            if temperaturhub_C <= 0.0:
                f"WARNUNG: Speicher {self.label}: temperaturhub_C={temperaturhub_C:0.6f}"
                break

            packet_energie_J = (
                packet_volumen_m3 * temperaturhub_C * WASSER_WAERMEKAP * DICHTE_WASSER
            )
            if packet_energie_J + summe_bezogene_energie_J > energie_J:
                # Diese Packet enthält mehr als genug als die benötigte Energie
                benoetiges_teilvolumen_m3 = (energie_J - summe_bezogene_energie_J) / (
                    temperaturhub_C * WASSER_WAERMEKAP * DICHTE_WASSER
                )
                summe_bezogenes_volumen_m3 += benoetiges_teilvolumen_m3
                nicht_bezogenes_volumen_m3 = (
                    packet_volumen_m3 - benoetiges_teilvolumen_m3
                )
                self.packet_liste[packet_idx] = [
                    packet_tempC,
                    nicht_bezogenes_volumen_m3,
                ]
                summe_bezogene_energie_J = energie_J
                break

            # Wir benötigen das gesamte Packet
            self.packet_liste.pop(packet_idx)
            summe_bezogene_energie_J += packet_energie_J
            summe_bezogenes_volumen_m3 += packet_volumen_m3

        temperaturhub_C = 0.0
        if summe_bezogenes_volumen_m3 > 0.0:
            self.packet_liste.append(
                [self.ruecklauf_bodenheizung_C, summe_bezogenes_volumen_m3]
            )
            self.packet_liste.sort(reverse=True)

            temperaturhub_C = summe_bezogene_energie_J / (
                summe_bezogenes_volumen_m3 * WASSER_WAERMEKAP * DICHTE_WASSER
            )

        # self.warnung_falls_volumenveraenderung()
        return temperaturhub_C + self.ruecklauf_bodenheizung_C

    def temperaturprofil(self, temperaturen_i=10):
        temperaturen = []
        index = 0
        volumen_summe_m3 = 0.0
        for temp_C, volumen_m3 in self.packet_liste:
            volumen_summe_m3 += volumen_m3
            while (
                volumen_summe_m3 > self.totalvolumen_m3 / temperaturen_i * index
                and index < temperaturen_i
            ):
                temperaturen.append(temp_C)
                index += 1
        assert len(temperaturen) == temperaturen_i
        return temperaturen

    def temperaturprofil_xy(self):
        temperatur_C_array = []
        volumen_m3_array = []
        volumen_m3_summe = 0.0
        for temp_C, volumen_m3 in self.packet_liste[::-1]:
            temperatur_C_array.append(temp_C)
            volumen_m3_array.append(volumen_m3_summe)
            volumen_m3_summe += volumen_m3
            temperatur_C_array.append(temp_C)
            volumen_m3_array.append(volumen_m3_summe)
        return [temperatur_C_array, volumen_m3_array]

    def _mittlere_temperatur_C(self):
        temperaturen_C = self.temperaturprofil()
        return np.average(np.array(temperaturen_C))

    def _verlustleistung_W(self):
        temperaturunterschied_C = (
            self._mittlere_temperatur_C() - 20.0
        )  # vereinfacht: Keller fix auf 20.0C
        leitwert_speicherverlust_W_pro_K = 1.332  # 20230525a_kennzahlen.ods
        verlustleistung_W = temperaturunterschied_C * leitwert_speicherverlust_W_pro_K
        return verlustleistung_W

    def run(self, timestep_s: float, time_s: float, modell: "Modell"):
        self._purge()

        if modell.zentralheizung.fernwaermepumpe_on:
            self.out_wasser_C = self.austausch_zentralheizung(
                temp_rein_C=self.in_wasser_C,
                volumen_rein_m3=self.out_fernwaermefluss_m3_pro_s * timestep_s,
            )

        if self.warmwassernutzung:
            leistung_warmwasser_W = (
                255  # gemaess 20230521b_kennzahlen.ods, fuer 3 Personen
            )
            leistung_warmwasser_W = (
                leistung_warmwasser_W * self.verbrauchsfaktor_grossfamilie
            )
            self.austausch_warmwasser(energie_J=leistung_warmwasser_W * timestep_s)

        self.verlustleistung_W = (
            self._verlustleistung_W()
        )  # den Verlust rechne ich später in den Heizungsbezug mit ein

        if self.heizungnutzung and self.stimuli.umgebungstemperatur_C < 20.0:
            kalt_C = -14.0
            warm_C = 20.0
            leistung_warm_W = 10.0  # empirisch und aufgrund von "ca 5000W pro Haus"
            leistung_kalt_W = 4700.0  # empirisch und aufgrund von "ca 5000W pro Haus"
            leistung_W = (warm_C - self.stimuli.umgebungstemperatur_C) / (
                warm_C - kalt_C
            ) * (leistung_kalt_W - leistung_warm_W) + leistung_warm_W
            leistung_W = (
                leistung_W * self.verbrauchsfaktor_grossfamilie + self.verlustleistung_W
            )
            self.austausch_heizung(energie_J=leistung_W * timestep_s)

    def update_input(self, fernleitung_hot: "Fernleitung"):
        self.in_wasser_C = fernleitung_hot.out_wasser_C
