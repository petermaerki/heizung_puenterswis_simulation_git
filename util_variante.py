import pathlib
from dataclasses import dataclass


@dataclass(frozen=True, repr=True)
class Variante:
    warmwasser_plateau_s: float
    fernleitung_hot_max_C: float

    @property
    def warmwasser_plateau_h(self) -> float:
        return self.warmwasser_plateau_s / 3600.0

    @property
    def label(self) -> str:
        return f"ww_ladung_{self.fernleitung_hot_max_C:0.0f}C_{self.warmwasser_plateau_h:0.1f}h"

    @property
    def tab_delimited(self) -> str:
        return "\t".join(
            [
                format(self.fernleitung_hot_max_C, "0.0f"),
                format(self.warmwasser_plateau_h, "0.1f"),
            ]
        )

    @staticmethod
    def tab_delimited_header() -> str:
        return "\t".join(
            [
                "fernleitung_hot_max_C",
                "warmwasser_plateau_h",
            ]
        )


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


# v = Variante(warmwasser_plateau_s=4000, fernleitung_hot_max_C=70)
# print(v.directory)
# print(v.tab_delimited)
