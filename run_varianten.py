import argparse
import dataclasses
import os
import pathlib
import shutil
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
from util_varianten import VARIANTEN


def main(args: List[str]):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "reset", default=False, type=bool, help="Ordner 'results' loeschen"
    )
    args = parser.parse_args(args=args)

    if args.reset:
        if DIRECTORY_REPORTS.exists():
            shutil.rmtree(DIRECTORY_REPORTS)

    for variant in VARIANTEN.varianten:
        for stimuli in util_stimuli.ALL:
            plot_images(stimuli=stimuli, directory=directory)
            if args.notebooks == 1:
                plot_notebooks(stimuli=stimuli, directory=directory)


if __name__ == "__main__":
    main(sys.argv[1:])
