import pathlib
from dataclasses import dataclass

from util_common import DIRECTORY_REPORTS
from util_konstanten import DAY_S
from util_variante import Variante

"""
        warmwasserbedarf_haus_W = 255
        heizbedarf_haus_W = 5000
"""


@dataclass(frozen=True, repr=True)
class Stimuli:
    label: str
    umgebungstemperatur_C: float
    start_s: float = -0.5 * DAY_S
    duration_s: float = 15 * DAY_S
    timestep_s: float = 5 * 60.0
    season_duration_a: float = 1.0 / 4.0

    def do_plot(self, time_s) -> bool:
        return time_s >= 0.0  # erst nach Zeitpunkt null, also nach Einpendeln
        # return True

    @property
    def end_s(self) -> float:
        return self.start_s + self.duration_s

    def get_directory(self, variante: Variante) -> pathlib.Path:
        return DIRECTORY_REPORTS / variante.label / self.label


stimuli_wintertag = Stimuli(
    label="wintertag",
    umgebungstemperatur_C=-10.0,
)


stimuli_fruelingstag = Stimuli(
    label="fruelingstag",
    umgebungstemperatur_C=15.0,
    season_duration_a=1 / 2.0,
)


stimuli_sommertag = Stimuli(
    label="sommertag",
    umgebungstemperatur_C=25.0,
)

ALL: tuple[Stimuli] = (stimuli_wintertag, stimuli_fruelingstag, stimuli_sommertag)

season_durations_a = sum([stimuli.season_duration_a for stimuli in ALL])
if not (1.0 - 1e-6 < season_durations_a < 1.0 + 1e-6):
    print(
        f"WARNING: Alle Stimmuli zusammen sollten {1.0:0.9f}a dauern und nicht {season_durations_a:0.9f}a!"
    )


def get_stimuli(label: str) -> Stimuli:
    for stimuli in ALL:
        if stimuli.label == label:
            return stimuli

    raise Exception(f"Stimuli '{label}' nicht gefunden.")
