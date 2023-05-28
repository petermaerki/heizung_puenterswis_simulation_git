import os
import pathlib

import papermill

import util_modell_speicher_dezentral
import util_modell_zentralheizung
import util_stimuli
from util_common import DIRECTORY_REPORTS, DIRECTORY_TOP, remove_files
from util_modell_fernleitung import PlotFernleitung
from util_modell_speichers import PlotSpeichersAnforderungen
from util_simulation import Simulation


def plot_images(stimuli: util_stimuli.Stimuli, directory: pathlib.Path):
    simulation = Simulation(stimuli=stimuli, directory=directory)
    modell = simulation.modell

    simulation.plots = (
        util_modell_zentralheizung.PlotZentralheizung(
            zentralheizung=modell.zentralheizung
        ),
        PlotSpeichersAnforderungen(speichers=modell.speichers),
    )
    simulation.plots = [
        PlotSpeichersAnforderungen(speichers=modell.speichers),
        PlotFernleitung(fernleitung=modell.fernleitung_hot),
        util_modell_zentralheizung.PlotFluss(zentralheizung=modell.zentralheizung),
    ]
    for speicher in (
        modell.speichers.get_speicher("haus01_normal"),
        modell.speichers.get_speicher("haus02_ferien"),
        modell.speichers.get_speicher("haus03_grossfamilie"),
    ):
        simulation.plots.append(
            util_modell_speicher_dezentral.PlotSpeicher(
                modell=simulation.modell, speicher=speicher
            )
        ),
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


def build_report(stimuli: util_stimuli.Stimuli, directory: pathlib.Path):
    directory = directory / stimuli.label
    directory.mkdir(parents=True, exist_ok=True)
    os.chdir(directory)

    plot_images(stimuli=stimuli, directory=directory)
    plot_notebooks(stimuli=stimuli, directory=directory)


def main():
    remove_files(DIRECTORY_REPORTS)
    for stimuli in util_stimuli.ALL:
        build_report(stimuli, DIRECTORY_REPORTS)


if __name__ == "__main__":
    main()
