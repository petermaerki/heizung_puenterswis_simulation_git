import os
import pathlib

import papermill

import util_modell_speicher_dezentral
import util_modell_zentralheizung
import util_stimuli
from util_modell_fernleitung import PlotFernleitung
from util_modell_speichers import PlotSpeichersAnforderungen
from util_simulation import Simulation

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).resolve().parent
DIRECTORY_REPORTS = DIRECTORY_OF_THIS_FILE / "reports"


def plot_images(stimuli: util_stimuli.Stimuli, directory: pathlib.Path):
    simulation = Simulation(stimuli=stimuli)
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
        modell.speichers.get_speicher("Haus 1 Normal"),
        modell.speichers.get_speicher("Haus 2 Ferien"),
        modell.speichers.get_speicher("Haus 3 Grossfamilie"),
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

    simulation.run()

    simulation.plot(directory=directory)


def plot_notebooks(stimuli: util_stimuli.Stimuli, directory: pathlib.Path):
    # https://papermill.readthedocs.io/en/latest/

    for notebook in DIRECTORY_OF_THIS_FILE.glob("report_.*.ipynb"):
        papermill.execute_notebook(
            input_path=notebook,
            output_path=directory / notebook.name,
            cwd=DIRECTORY_OF_THIS_FILE,
            parameters=dict(
                stimuli_label=stimuli.label,
            ),
            report_mode=True,
        )


def build_report(stimuli: util_stimuli.Stimuli):
    directory = DIRECTORY_REPORTS / stimuli.label
    directory.mkdir(parents=True, exist_ok=True)
    os.chdir(directory)

    plot_images(stimuli=stimuli, directory=directory)
    plot_notebooks(stimuli=stimuli, directory=directory)


def remove_files():
    """
    Remove all files in DIRECTORY_REPORTS if possible
    """
    for filename in DIRECTORY_REPORTS.rglob("*.*"):
        try:
            filename.unlink()
        except Exception as e:
            print(
                f"DEBUG: Failed to remove {filename.relative_to(DIRECTORY_OF_THIS_FILE) }"
            )


def main():
    remove_files()
    for stimuli in util_stimuli.ALL:
        build_report(stimuli)


if __name__ == "__main__":
    main()
