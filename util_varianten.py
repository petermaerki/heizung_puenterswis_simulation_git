from dataclasses import dataclass
from typing import List

from util_variante import Variante


@dataclass(frozen=True, repr=True)
class Varianten:
    varianten: List[Variante]

    @property
    def labels(self) -> List[str]:
        return [v.label for v in self.varianten]

    @property
    def labels_text(self) -> str:
        return ",".join(self.labels)

    def get_by_label(self, label: str) -> Variante:
        assert isinstance(label, str)
        for variante in self.varianten:
            if variante.label == label:
                return variante

        raise Exception(
            f"Variante '{label}' nicht gefunden. Gültige Varianten sind {self.labels_text}"
        )


VARIANTEN = Varianten(
    [
        Variante(warmwasser_plateau_s=4000, fernleitung_hot_max_C=65),
        Variante(warmwasser_plateau_s=4000, fernleitung_hot_max_C=70),
        Variante(warmwasser_plateau_s=4000, fernleitung_hot_max_C=75),
    ]
)
