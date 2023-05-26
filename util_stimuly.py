from dataclasses import dataclass

DAY_S = 24 * 3600.0


"""
        warmwasserbedarf_haus_W = 255
        heizbedarf_haus_W = 5000
"""


@dataclass(frozen=True, repr=True)
class Stimuli:
    label: str
    umgebungstemperatur_C: float
    start_s: float
    duration_s: float
    timestep_s: float

    def do_plot(self, time_s) -> bool:
        return True


stimuli_wintertag = Stimuli(
    label="wintertag",
    umgebungstemperatur_C=-10.0,
    start_s=-2 * DAY_S,
    duration_s=5 * DAY_S,
    timestep_s=5 * 60.0,
)


stimuli_fruelingstag = Stimuli(
    label="fruelingstag",
    umgebungstemperatur_C=15.0,
    start_s=-2 * DAY_S,
    duration_s=5 * DAY_S,
    timestep_s=5 * 60.0,
)


stimuli_sommertag = Stimuli(
    label="sommertag",
    umgebungstemperatur_C=25.0,
    start_s=-2 * DAY_S,
    duration_s=5 * DAY_S,
    timestep_s=5 * 60.0,
)

# ALL: tuple[Stimuli] = (stimuli_wintertag, stimuli_fruelingstag, stimuli_sommertag)
ALL: tuple[Stimuli] = (stimuli_wintertag, stimuli_sommertag)


def get_stimuli(label: str) -> Stimuli:
    for stimuli in ALL:
        if stimuli.label == label:
            return stimuli

    raise Exception(f"Stimuli '{label}' nicht gefunden.")
