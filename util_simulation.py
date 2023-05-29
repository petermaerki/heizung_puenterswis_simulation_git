import logging
import pathlib
import time

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
        begin_s = time.monotonic()

        timestep_s = self.modell.stimuli.timestep_s
        time_s = self.modell.stimuli.start_s
        while time_s < self.modell.stimuli.end_s:
            self.modell.run(timestep_s=timestep_s, time_s=time_s)
            if self.modell.stimuli.do_plot(time_s=time_s):
                for _plot in self.plots:
                    _plot.append_plot(
                        timestep_s=timestep_s,
                        time_s=time_s,
                    )
            time_s += timestep_s

        logger.info(
            f"Simulation {self.modell.stimuli.label}: run {time.monotonic()-begin_s:0.1f}s"
        )

    def plot(self):
        begin_s = time.monotonic()

        for plot in self.plots:
            logger.debug(
                f"Simulation {self.modell.stimuli.label}: {plot.__class__.__name__}"
            )
            plot.plot(directory=self.directory)

        logger.info(
            f"Simulation {self.modell.stimuli.label}: plot {time.monotonic()-begin_s:0.1f}s"
        )
