import logging
import pathlib
import time

from util_common import init_logging, remove_files
from util_modell import Modell
from util_stimuli import Stimuli
from util_variante import Variante

logger = logging.getLogger("simulation")

DIRECTORY_TOP = pathlib.Path(__file__).resolve().parent


class Simulation:
    def __init__(self, stimuli: Stimuli, variante=Variante):
        directory = stimuli.get_directory(variante=variante)
        if directory is not None:
            directory.mkdir(parents=True, exist_ok=True)
            remove_files(directory=directory)
        init_logging(directory=directory)

        self.plots = []
        self.modell = Modell(stimuli=stimuli, variante=variante)

    def run(self):
        begin_s = time.monotonic()

        timestep_s = self.modell.stimuli.timestep_s
        time_s = self.modell.stimuli.start_s
        while (
            time_s < self.modell.stimuli.end_s
            and self.modell.zentralheizung.heizzyklen_i < 3
        ):
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
            plot.plot(directory=self.modell.directory)

        logger.info(
            f"Simulation {self.modell.stimuli.label}: plot {time.monotonic()-begin_s:0.1f}s"
        )
