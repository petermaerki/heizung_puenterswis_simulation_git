import logging
import pathlib
from typing import Dict, List, Set

from util_stimuli import Stimuli
from util_variante import Variante

logger = logging.getLogger("simulation")


class VarianteResults:
    def __init__(self, directory: pathlib.Path):
        assert isinstance(directory, pathlib.Path)
        self._filename = directory / "variante_results.txt"

    def exists(self) -> bool:
        return self._filename.exists()

    def write(self, label: str, value: float) -> None:
        assert isinstance(label, str)
        assert isinstance(value, float)

        with self._filename.open("a") as f:
            f.write(f"{label}={value}\n")

    def read_file(self) -> Dict[str, float]:
        d: Dict[str, float] = {}
        for line in self._filename.read_text().split("\n"):
            line = line.strip()
            if len(line) == 0:
                continue
            label, _, value = line.partition("=")
            assert label not in d
            d[label] = float(value)
        return d


class VariantenResults:
    def __init__(self, directory: pathlib.Path):
        assert isinstance(directory, pathlib.Path)
        self._filename = directory / "varianten_results.txt"
        self._dict_variante_dict: Dict[str, Dict[str, float]] = {}
        self._dict_variante: Dict[str, Variante] = {}
        self._labels: Set[str] = set()

    def delete(self):
        self._filename.unlink(missing_ok=True)

    def append(self, stimuli: Stimuli, variante: Variante) -> None:
        self._dict_variante[variante.label] = variante
        variante_sum = self._dict_variante_dict.setdefault(variante.label, {})
        directory = stimuli.get_directory(variante=variante)
        variante_results = VarianteResults(directory=directory)
        d = variante_results.read_file()
        self._labels.update(d)
        for label, value in d.items():
            assert isinstance(label, str)
            assert isinstance(value, float)
            variante_sum[label] = value + variante_sum.get(label, 0.0)

    def write(self) -> None:
        labels = sorted(self._labels)
        with self._filename.open("w") as f:
            labels_text = "\t".join(labels)
            f.write(
                f"variante\tfernleitung_hot_max_C\twarmwasser_plateau_s\t{labels_text}\n"
            )

            for label_variante in sorted(self._dict_variante_dict):
                variante = self._dict_variante[label_variante]
                dict_variante = self._dict_variante_dict[label_variante]
                values = [format(dict_variante[label], "0.9f") for label in labels]
                values_text = "\t".join(values)
                f.write(
                    f"{label_variante}\t{variante.fernleitung_hot_max_C:0.0f}\t{variante.warmwasser_plateau_s:0.0f}\t{values_text}\n"
                )
