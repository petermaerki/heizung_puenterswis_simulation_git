import logging
import pathlib

from util_common import init_logging, remove_files
from util_modell import Modell, PlotVerluste
from util_modell_fernleitung import PlotFernleitung
from util_modell_speicher_dezentral import (
    DumpSchichtung,
    PlotEnergiereserve,
    PlotSpeicherSchichtung,
)
from util_modell_speichers import PlotSpeichersAnforderungen
from util_modell_zentralheizung import PlotFluss
from util_stimuli import Stimuli, stimuli_sommertag, stimuli_wintertag

logger = logging.getLogger("simulation")

DIRECTORY_TOP = pathlib.Path(__file__).resolve().parent
DIRECTORY_TMP = DIRECTORY_TOP / "tmp"


class Simulation:
    def __init__(self, stimuli: "Stimuli", directory: pathlib.Path = None):
        if directory is not None:
            directory.mkdir(parents=True, exist_ok=True)
            remove_files(directory=directory)
        init_logging(directory=directory)

        self.directory = directory
        self.plots = []
        self.modell = Modell(stimuli)

    def run(self):
        logger.info(f"Simulation {self.modell.stimuli.label}: run")

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
            logger.info(
                f"Simulation {self.modell.stimuli.label}: {plot.__class__.__name__}"
            )
            plot.plot(directory=self.directory)

        logger.info(f"Simulation {self.modell.stimuli.label}: done")


def main():
    simulation = Simulation(stimuli=stimuli_sommertag, directory=DIRECTORY_TMP)

    modell = simulation.modell

    simulation.plots = [
        PlotVerluste(modell=modell),
        PlotSpeichersAnforderungen(speichers=modell.speichers),
        PlotFernleitung(fernleitung=modell.fernleitung_hot),
        PlotFernleitung(fernleitung=modell.fernleitung_cold),
        PlotFluss(zentralheizung=modell.zentralheizung),
    ]
    for speicher in (
        modell.speichers.get_speicher("haus01_normal"),
        modell.speichers.get_speicher("haus02_ferien"),
        modell.speichers.get_speicher("haus03_grossfamilie"),
    ):
        simulation.plots.append(
            PlotSpeicherSchichtung(modell=modell, speicher=speicher)
        )
        simulation.plots.append(PlotEnergiereserve(modell=modell, speicher=speicher))
        simulation.plots.append(DumpSchichtung(speicher=speicher))

    simulation.run()

    simulation.plot()


if __name__ == "__main__":
    main()
