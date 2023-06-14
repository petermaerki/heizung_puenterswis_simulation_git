import argparse
import dataclasses
import os
import pathlib
import sys
from typing import List

import papermill

import util_modell_speicher_dezentral
import util_modell_zentralheizung
import util_stimuli
from util_common import DIRECTORY_REPORTS, DIRECTORY_TOP, remove_files
from util_modell import PlotVerluste
from util_modell_fernleitung import PlotFernleitung
from util_modell_speichers import PlotSpeichersAnforderungen
from util_simulation import Simulation


def plot_images(stimuli: util_stimuli.Stimuli, directory: pathlib.Path):
    simulation = Simulation(stimuli=stimuli, directory=directory)
    modell = simulation.modell

    simulation.plots = [
        PlotVerluste(modell=modell),
        util_modell_zentralheizung.PlotFluss(zentralheizung=modell.zentralheizung),
        util_modell_zentralheizung.PlotZentralheizung(
            zentralheizung=modell.zentralheizung
        ),
        PlotSpeichersAnforderungen(speichers=modell.speichers),
        PlotFernleitung(fernleitung=modell.fernleitung_hot),
        PlotFernleitung(fernleitung=modell.fernleitung_cold),
        util_modell_zentralheizung.PlotZeitpunktePerioden(
            zentralheizung=modell.zentralheizung
        ),
    ]
    for speicher in (
        modell.speichers.get_speicher("haus01_normal"),
        modell.speichers.get_speicher("haus02_ferien"),
        modell.speichers.get_speicher("haus03_grossfamilie"),
    ):
        # simulation.plots.append(
        #     util_modell_speicher_dezentral.PlotSpeicher(
        #         modell=simulation.modell, speicher=speicher
        #     )
        # ),
        simulation.plots.append(
            util_modell_speicher_dezentral.PlotSpeicherSchichtung(
                modell=modell, speicher=speicher
            )
        )
        simulation.plots.append(
            util_modell_speicher_dezentral.PlotEnergiereserve(
                modell=modell, speicher=speicher
            )
        )
        simulation.plots.append(
            util_modell_speicher_dezentral.DumpSchichtung(speicher=speicher)
        )
        simulation.plots.append(
            util_modell_speicher_dezentral.PlotSpeicherSchichtung(
                modell=modell, speicher=speicher
            )
        )
        simulation.plots.append(
            util_modell_speicher_dezentral.PlotEnergiereserve(
                modell=modell, speicher=speicher
            )
        )
        simulation.plots.append(
            util_modell_speicher_dezentral.DumpSchichtung(speicher=speicher)
        )

    simulation.run()

    simulation.plot()


def plot_notebooks(stimuli: util_stimuli.Stimuli, directory: pathlib.Path):
    # https://papermill.readthedocs.io/en/latest/

    for notebook in DIRECTORY_TOP.glob("report_*.ipynb"):
        papermill.execute_notebook(
            input_path=notebook,
            output_path=directory / notebook.name,
            cwd=DIRECTORY_TOP,
            parameters=dict(
                stimuli_label=stimuli.label,
            ),
            report_mode=True,
        )


def main(args: List[str]):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "stimuli",
        default=None,
        choices=[st.label for st in util_stimuli.ALL],
        nargs="?",
    )
    parser.add_argument("--duration_h", type=float, default=None)
    parser.add_argument(
        "--notebooks",
        type=int,
        default=1,
        help="Also build jupyter notebooks. Default 1",
    )
    args = parser.parse_args(args=args)

    if args.stimuli is None:
        stimulies = util_stimuli.ALL
    else:
        stimulies = [util_stimuli.get_stimuli(args.stimuli)]

    for stimuli in stimulies:
        assert isinstance(stimuli, util_stimuli.Stimuli)
        if args.duration_h:
            stimuli = dataclasses.replace(stimuli, duration_s=3600.0 * args.duration_h)
        directory = DIRECTORY_REPORTS / stimuli.label
        remove_files(directory)
        directory.mkdir(parents=True, exist_ok=True)
        os.chdir(directory)

        plot_images(stimuli=stimuli, directory=directory)
        if args.notebooks == 1:
            plot_notebooks(stimuli=stimuli, directory=directory)


if __name__ == "__main__":
    main(sys.argv[1:])
