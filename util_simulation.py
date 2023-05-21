from util_modell import Modell
from util_modell_speicher_dezentral import PlotSpeicher
from util_stimuly import StimuliNormaltag


class Stimulus:
    def __init__(self):
        self.warmwasserbedarf_haus_W = 255
        self.heizbedarf_haus_W = 5000

    # def fernwaerme_vorlauf_C(time_s=0):
    #     return 50.0

    def fernwaermepumpe_on(time_s=0):
        return True


class Simulation:
    def __init__(self):
        self.duration_s = 24 * 3600
        self.timestep_s = 60
        self.stimulus = Stimulus()
        self.plots = []

        self.modell = Modell()

    def run(self, stimuli=None, plot=True):
        fluss_liter_pro_h = 148.0
        fluss_m3_pro_s = fluss_liter_pro_h / 1000 / 3600
        for time_s in range(0, self.duration_s, self.timestep_s):
            self.modell.run(
                timestep_s=self.timestep_s, time_s=time_s, stimulus=self.stimulus
            )
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
    simulation = Simulation()

    simulation.plots = (
        PlotSpeicher(speicher=simulation.modell.speichers[0]),
        # PlotSpeicher(simulation.speicher_verschwender),
        # PlotSpeicher(simulation.speicher_13),
        # PlotHeizung(simulation.heizung),
    )

    simulation.run(StimuliNormaltag(), plot=False)
    simulation.run(StimuliNormaltag(), plot=False)
    simulation.run(StimuliNormaltag(), plot=True)

    simulation.plot()
