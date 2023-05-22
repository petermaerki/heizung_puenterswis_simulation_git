from util_modell import Modell
from util_modell_speicher_dezentral import PlotSpeicher
from util_stimuly import StimuliWintertag

"""
        self.warmwasserbedarf_haus_W = 255
        self.heizbedarf_haus_W = 5000
"""


class Simulation:
    def __init__(self, stimuli: "StimuliWintertag"):
        self.duration_s = 24 * 3600
        self.timestep_s = 60
        self.plots = []

        self.modell = Modell(stimuli)

    def run(self, plot=True):
        fluss_liter_pro_h = 148.0
        fluss_m3_pro_s = fluss_liter_pro_h / 1000 / 3600
        for time_s in range(0, self.duration_s, self.timestep_s):
            self.modell.run(timestep_s=self.timestep_s, time_s=time_s)
            if plot:
                for _plot in self.plots:
                    _plot.append_plot(
                        timestep_s=self.timestep_s,
                        time_s=time_s,
                    )

    def plot(self):
        for plot in self.plots:
            plot.plot()


if __name__ == "__main__":
    stimuli = StimuliWintertag()
    simulation = Simulation(stimuli=stimuli)

    simulation.plots = (
        PlotSpeicher(speicher=simulation.modell.speichers[0]),
        # PlotSpeicher(simulation.speicher_verschwender),
        # PlotSpeicher(simulation.speicher_13),
        # PlotHeizung(simulation.heizung),
    )
    simulation.run(plot=False)
    simulation.run(plot=False)
    simulation.run(plot=True)

    simulation.plot()
