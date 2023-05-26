import os
import pathlib

from util_modell import Modell
from util_modell_speichers import PlotSpeichersAnforderungen
from util_stimuly import Stimuli, stimuli_wintertag

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

    speicher = simulation.modell.speichers.get_speicher("Haus 3 Grossfamilie")

    simulation.plots = (
        # PlotSpeicherSchichtung(modell=simulation.modell, speicher=speicher),
        # PlotEnergiereserve(modell=simulation.modell, speicher=speicher),
        PlotSpeichersAnforderungen(speichers=simulation.modell.speichers),
    )
    simulation.run()

    simulation.plot()


if __name__ == "__main__":
    main()
