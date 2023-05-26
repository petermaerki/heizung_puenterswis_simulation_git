from util_modell import Modell
from util_modell_speicher_dezentral import (
    PlotEnergiereserve,
    PlotSpeicher,
    PlotSpeicherSchichtung,
)
from util_stimuly import Stimuli, stimuli_wintertag


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


if __name__ == "__main__":
    simulation = Simulation(stimuli=stimuli_wintertag)

    simulation.plots = (
        PlotSpeicher(modell=simulation.modell, speicher=simulation.modell.speichers[0]),
        # PlotSpeicher(simulation.speicher_verschwender),
        # PlotSpeicher(simulation.speicher_13),
        # PlotHeizung(simulation.heizung),
    )
    simulation.run()

    simulation.plot()
