import typing

import matplotlib.pyplot as plt
import numpy as np

from util_konstanten import DICHTE_WASSER, WASSER_WAERMEKAP

if typing.TYPE_CHECKING:
    from util_modell import Modell
    from util_modell_zentralheizung import Zentralheizung

TEMPERATURGRENZE_BRAUCHWASSER_C = (
    50.0  # diese Temperatur wird fuer Brauchwasser mindestens gebraucht
)


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
        self.fernwaerme_hot_C.append(self.speicher.fernwaerme_hot_C)
        self.fernwaerme_cold_C.append(self.speicher.fernwaerme_cold_C)
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

    def plot(self):
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
            title="Speicher Temperaturverlauf " + self.speicher.label,
        )
        ax2.set(ylabel="Energie kWh")
        ax.legend()
        ax2.legend()
        ax.grid()
        plt.show()


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

    def plot(self):
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
            title="Speicher verfügbare Energie " + self.speicher.label,
        )
        ax.legend()
        ax.grid()
        plt.savefig(
            "C:/data/peters_daten\haus_13_zelglistrasse_49/heizung/heizung_peter_schaer_siedlung/heizung_puenterswis_simulation_git/pictures/energiereserve_"
            + self.speicher.label
            + ".png"
        )
        plt.show()


class PlotSpeicherSchichtung:
    def __init__(self, modell: "Modell", speicher: "Speicher_dezentral"):
        self.modell = modell
        self.speicher = speicher
        self.time_array_s = []
        self.time_steps_s = []
        self.temperaturen_C = []
        self.temperaturen_i = 100

    def append_plot(
        self,
        timestep_s: float,
        time_s: float,
    ):
        self.time_array_s.append(time_s)
        self.temperaturen_C.append(
            self.speicher.temperaturprofil(temperaturen_i=self.temperaturen_i)[::-1]
        )

    def plot(self):
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
        plt.title("Speicher Temperaturschichtung " + self.speicher.label)
        # ax.set(xlabel="time (h)", ylabel="Temperature C", title=self.speicher.label)
        plt.savefig(
            "C:/data/peters_daten\haus_13_zelglistrasse_49/heizung/heizung_peter_schaer_siedlung/heizung_puenterswis_simulation_git/pictures/schichtung__"
            + self.speicher.label
            + ".png"
        )
        plt.show()


class Speicher_dezentral:
    def __init__(
        self,
        stimuli: "StimuliWintertag",
        label="Speicher XY",
        fernwaermefluss_liter_pro_h=150.0,
        startTempC=30.0,
        totalvolumen_m3=0.69,
        verbrauchsfaktor_party=1.0,
    ):
        self.stimuli = stimuli
        self.label = label
        self.fernwaermefluss_m3_pro_s = fernwaermefluss_liter_pro_h / 1000 / 3600
        # self.teilspeicher_i = 10
        self.totalvolumen_m3 = totalvolumen_m3
        # self.teilvolumen_m3 = 0.69 / self.teilspeicher_i
        self.verbrauchsfaktor_party = verbrauchsfaktor_party
        assert self.verbrauchsfaktor_party > 1e-3
        self.volumenliste = (
            []
        )  # self.teilspeicher_i * [(startTempC, self.teilvolumen_m3)]
        self.volumenliste.append((startTempC, self.totalvolumen_m3))
        self.volumenliste_vorher_debug = []
        self.fernwaerme_hot_C = 0.0
        self.fernwaerme_cold_C = 0.0
        self.warmwassernutzung = True
        self.heizungnutzung = True
        self.warmwasser_anforderung = False

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
        for [temp_C, volumen_m3] in self.volumenliste:
            print(
                f"Schichtung vom Speicher: Temperatur C: {temp_C:0.1f}, Volumen m^3: {volumen_m3:0.6f}"
            )

    def _sort(self):
        self.volumenliste.sort(key=lambda a: a[0], reverse=True)

    def _gesamtvolumen_justieren(self):  # wegen rundungsfehlern justieren
        gesamt_volumen_m3 = 0.0
        for temp_C, volumen_m3 in self.volumenliste:
            gesamt_volumen_m3 += volumen_m3
        abweichung_m3 = self.totalvolumen_m3 - gesamt_volumen_m3
        if abs(abweichung_m3) > 1e-5:
            print("vorher")
            for [temp_C, volumen_m3] in self.volumenliste_vorher_debug:
                print(f"Temperatur C: {temp_C:0.1f}, Volumen m^3: {volumen_m3:0.6f}")
            print("nachher")
            self.print()
            print(f"abweichung_m3 {abweichung_m3} zu gross")
            assert False
        self.volumenliste[0] = (
            self.volumenliste[0][0],
            self.volumenliste[0][1] + abweichung_m3,
        )
        return gesamt_volumen_m3

    def _einfuellen(self, temp_rein_C=70.0, volumen_rein_m3=0.010):
        # print(f'einfuellen  temp_rein_C = {temp_rein_C}, volumen_rein_m3 = {volumen_rein_m3}')
        self.volumenliste_vorher_debug = self.volumenliste.copy()
        volumenliste_neu = []
        bestehend_eingefuellt = False
        for temp_C, volumen_m3 in self.volumenliste:
            if abs(temp_C - temp_rein_C) < 1e-5 and not bestehend_eingefuellt:
                volumenliste_neu.append((temp_C, volumen_m3 + volumen_rein_m3))
                bestehend_eingefuellt = True
            else:
                volumenliste_neu.append((temp_C, volumen_m3))
        if not bestehend_eingefuellt:
            volumenliste_neu.append((temp_rein_C, volumen_rein_m3))
            volumenliste_neu.sort(key=lambda a: a[0], reverse=True)
        self.volumenliste = volumenliste_neu
        """
        volumen_summe_m3 = 0.0
        for (temp_C, volumen_m3) in self.volumenliste:
            volumen_summe_m3 += volumen_m3
        print(f'abweichung nach einfuellen {self.totalvolumen_m3-volumen_summe_m3} m3')
        """

    def austauschen(
        self,
        temp_rein_C=70.0,
        volumen_rein_m3=0.001,
        position_raus_anteil_von_unten=0.5,
    ):
        assert volumen_rein_m3 >= 0.0
        assert (
            position_raus_anteil_von_unten >= 0.0
            and position_raus_anteil_von_unten <= 1.0
        )
        self._einfuellen(temp_rein_C=temp_rein_C, volumen_rein_m3=volumen_rein_m3)
        raus_bei_volumen_m3 = self.totalvolumen_m3 * (
            1.0 - position_raus_anteil_von_unten
        )
        volumenliste_neu = []
        volumen_summe_m3 = 0.0
        genommen_summe_m3 = 0.0
        energie = 0.0
        for temp_C, volumen_m3 in self.volumenliste:
            volumen_summe_m3 += volumen_m3
            volumen_verbleiben_m3 = volumen_m3
            if (
                volumen_rein_m3 - genommen_summe_m3
            ) > 1e-9:  # es muss noch genommen werden
                if volumen_summe_m3 > raus_bei_volumen_m3:  # ab hier nehmen
                    nehme_m3 = min(volumen_rein_m3 - genommen_summe_m3, volumen_m3)
                    assert nehme_m3 > 0.0
                    energie += temp_C * nehme_m3
                    genommen_summe_m3 += nehme_m3
                    volumen_verbleiben_m3 = volumen_m3 - nehme_m3
            else:
                volumen_verbleiben_m3 = volumen_m3  # bleibt gleich
            if volumen_verbleiben_m3 > 1e-8:  # zu kleine Volumen skipen
                volumenliste_neu.append((temp_C, volumen_verbleiben_m3))
        temperatur_raus_C = energie / genommen_summe_m3
        self.volumenliste = volumenliste_neu
        self._gesamtvolumen_justieren()
        return temperatur_raus_C

    def temperatur_bei_position(self, position_raus_anteil_von_unten=0.5):
        startvolumen_m3 = position_raus_anteil_von_unten * self.totalvolumen_m3
        volumenposition_m3 = startvolumen_m3
        temperaturen_x, volumen_y = self.temperaturprofil_xy()
        return np.interp(volumenposition_m3, volumen_y, temperaturen_x)

    def energiebezug(
        self, energie_J=1.0, volumen_m3=0.001, position_raus_anteil_von_unten=0.5
    ):
        temperatur_raus_C = self.temperatur_bei_position(position_raus_anteil_von_unten)
        temperatur_rein_C = temperatur_raus_C - energie_J / (
            volumen_m3 * DICHTE_WASSER * WASSER_WAERMEKAP
        )
        self.austauschen(
            temp_rein_C=temperatur_rein_C,
            volumen_rein_m3=volumen_m3,
            position_raus_anteil_von_unten=position_raus_anteil_von_unten,
        )
        return temperatur_raus_C

    def warmwasserbezug(self, energie_J=1.0):
        warmwassertemperatur_C = self.temperatur_bei_position(
            position_raus_anteil_von_unten=1.0
        )
        kaltwasser_C = 15.0
        temperaturhub_C = warmwassertemperatur_C - kaltwasser_C
        assert temperaturhub_C >= 0.0
        volumen_m3 = energie_J / (temperaturhub_C * WASSER_WAERMEKAP * DICHTE_WASSER)
        self.austauschen(
            temp_rein_C=kaltwasser_C,
            position_raus_anteil_von_unten=1.0,
            volumen_rein_m3=volumen_m3,
        )

        self.warmwasser_anforderung = (
            self.temperatur_bei_position(position_raus_anteil_von_unten=1.0)
            < TEMPERATURGRENZE_BRAUCHWASSER_C
        )

        return warmwassertemperatur_C, volumen_m3

    def heizungbezug(self, energie_J=1.0, volumen_m3=0.001):
        return self.energiebezug(
            energie_J=energie_J,
            volumen_m3=volumen_m3,
            position_raus_anteil_von_unten=0.68,
        )

    def temperaturprofil(self, temperaturen_i=10):
        temperaturen = []
        index = 0
        volumen_summe_m3 = 0.0
        for temp_C, volumen_m3 in self.volumenliste:
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
        for temp_C, volumen_m3 in self.volumenliste[::-1]:
            temperatur_C_array.append(temp_C)
            volumen_m3_array.append(volumen_m3_summe)
            volumen_m3_summe += volumen_m3
            temperatur_C_array.append(temp_C)
            volumen_m3_array.append(volumen_m3_summe)
        return [temperatur_C_array, volumen_m3_array]

    def run(self, timestep_s: float, time_s: float, modell: "Modell"):
        if modell.zentralheizung.fernwaermepumpe_on:
            self.fernwaerme_cold_C = self.austauschen(
                temp_rein_C=self.fernwaerme_hot_C,
                volumen_rein_m3=self.fernwaermefluss_m3_pro_s * timestep_s,
                position_raus_anteil_von_unten=0.0,
            )

        if self.warmwassernutzung:
            leistung_warmwasser_W = (
                255  # gemaess 20230521b_kennzahlen.ods, fuer 3 Personen
            )
            leistung_warmwasser_W = leistung_warmwasser_W * self.verbrauchsfaktor_party
            self.warmwasserbezug(energie_J=leistung_warmwasser_W * timestep_s)
        if self.heizungnutzung and self.stimuli.umgebungstemperatur_C < 20.0:
            kalt_C = -14.0
            warm_C = 20.0
            leistung_warm_W = 10.0  # empirisch und aufgrund von "ca 5000W pro Haus"
            leistung_kalt_W = 4700.0  # empirisch und aufgrund von "ca 5000W pro Haus"
            leistung_W = (warm_C - self.stimuli.umgebungstemperatur_C) / (
                warm_C - kalt_C
            ) * (leistung_kalt_W - leistung_warm_W) + leistung_warm_W
            leistung_W = leistung_W * self.verbrauchsfaktor_party
            self.heizungbezug(energie_J=leistung_W * timestep_s)

    def update_input(self, zentralheizung: "Zentralheizung"):
        self.fernwaerme_hot_C = zentralheizung.fernwaerme_hot_C
