import os
import pathlib

import papermill

import util_modell_speicher_dezentral
import util_modell_zentralheizung
import util_stimuli
from util_simulation import Simulation

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).resolve().parent
DIRECTORY_REPORTS = DIRECTORY_OF_THIS_FILE / "reports"


def plot_images(stimuli: util_stimuli.Stimuli, directory: pathlib.Path):
    simulation = Simulation(stimuli=stimuli)

    simulation.plots = (
        util_modell_speicher_dezentral.PlotSpeicher(
            modell=simulation.modell, speicher=simulation.modell.speichers[0]
        ),
        util_modell_speicher_dezentral.PlotEnergiereserve(
            modell=simulation.modell, speicher=simulation.modell.speichers[1 - 1]
        ),
        util_modell_speicher_dezentral.PlotSpeicherSchichtung(
            modell=simulation.modell, speicher=simulation.modell.speichers[1 - 1]
        ),
        util_modell_speicher_dezentral.PlotEnergiereserve(
            modell=simulation.modell, speicher=simulation.modell.speichers[2 - 1]
        ),
        util_modell_speicher_dezentral.PlotSpeicherSchichtung(
            modell=simulation.modell, speicher=simulation.modell.speichers[2 - 1]
        ),
        util_modell_speicher_dezentral.PlotEnergiereserve(
            modell=simulation.modell, speicher=simulation.modell.speichers[3 - 1]
        ),
        util_modell_speicher_dezentral.PlotSpeicherSchichtung(
            modell=simulation.modell, speicher=simulation.modell.speichers[3 - 1]
        ),
        util_modell_zentralheizung.PlotZentralheizung(
            zentralheizung=simulation.modell.zentralheizung
        ),
        util_modell_zentralheizung.PlotZentralheizungAnforderungen(
            zentralheizung=simulation.modell.zentralheizung
        ),
    )
    simulation.run()

    simulation.plot()


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
