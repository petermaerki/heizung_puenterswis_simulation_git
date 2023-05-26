import os
import pathlib

import papermill

import util_stimuly
from util_modell_speicher_dezentral import PlotSpeicher
from util_simulation import Simulation

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).resolve().parent
DIRECTORY_REPORTS = DIRECTORY_OF_THIS_FILE / "reports"


def plot_images(stimuli: util_stimuly.Stimuli, directory: pathlib.Path):
    simulation = Simulation(stimuli=stimuli)

    simulation.plots = (
        PlotSpeicher(modell=simulation.modell, speicher=simulation.modell.speichers[0]),
        # PlotSpeicher(simulation.speicher_verschwender),
        # PlotSpeicher(simulation.speicher_13),
        # PlotHeizung(simulation.heizung),
    )
    simulation.run()

    simulation.plot()


def plot_notebooks(stimuli: util_stimuly.Stimuli, directory: pathlib.Path):
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


def build_report(stimuli: util_stimuly.Stimuli):
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
    for stimuli in util_stimuly.ALL:
        build_report(stimuli)


if __name__ == "__main__":
    main()
