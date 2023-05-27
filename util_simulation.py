import os
import pathlib

from util_modell import Modell
from util_modell_fernleitung import PlotFernleitung
from util_modell_speicher_dezentral import PlotEnergiereserve, PlotSpeicherSchichtung
from util_modell_speichers import PlotSpeichersAnforderungen
from util_modell_zentralheizung import PlotFluss
from util_stimuli import Stimuli, stimuli_sommertag, stimuli_wintertag

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).resolve().parent
DIRECTORY_TMP = DIRECTORY_OF_THIS_FILE / "tmp"


class Simulation:
    def __init__(self, stimuli: "Stimuli"):
        self.plots = []

        self.modell = Modell(stimuli)

    def run(self):
        duration_s = self.modell.stimuli.duration_s
        timestep_s = self.modell.stimuli.timestep_s
        time_s = self.modell.stimuli.start_s
        while time_s < duration_s:
            self.modell.run(timestep_s=timestep_s, time_s=time_s)
            if self.modell.stimuli.do_plot(time_s=time_s):
                for _plot in self.plots:
                    _plot.append_plot(
                        timestep_s=timestep_s,
                        time_s=time_s,
                    )
            time_s += timestep_s

    def plot(self):
        for plot in self.plots:
            plot.plot()


def main():
    DIRECTORY_TMP.mkdir(parents=True, exist_ok=True)
    os.chdir(DIRECTORY_TMP)
    simulation = Simulation(stimuli=stimuli_wintertag)

    modell = simulation.modell

    simulation.plots = [
        PlotSpeichersAnforderungen(speichers=modell.speichers),
        PlotFernleitung(fernleitung=modell.fernleitung_hot),
        PlotFluss(zentralheizung=modell.zentralheizung),
    ]
    for speicher in (
        modell.speichers.get_speicher("Haus 1 Normal"),
        modell.speichers.get_speicher("Haus 2 Ferien"),
        modell.speichers.get_speicher("Haus 3 Grossfamilie"),
    ):
        simulation.plots.append(
            PlotSpeicherSchichtung(modell=modell, speicher=speicher)
        )
        simulation.plots.append(PlotEnergiereserve(modell=modell, speicher=speicher))

    simulation.run()

    simulation.plot()


if __name__ == "__main__":
    main()
