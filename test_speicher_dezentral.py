import cProfile
import pathlib

from util_modell import Modell
from util_modell_speicher_dezentral import Speicher_dezentral
from util_stimuli import stimuli_wintertag

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).resolve().parent
DIRECTORY_RESULTS = DIRECTORY_OF_THIS_FILE / "test_speicher_dezentral-results"
DIRECTORY_RESULTS.mkdir(exist_ok=True)


def test_a():
    stimuli = stimuli_wintertag
    speicher = Speicher_dezentral(stimuli=stimuli, startTempC=60.0)

    label = "test_a"
    speicher.dump(filename=DIRECTORY_RESULTS / f"{label}-vorher.txt")
    out_wasser_C = speicher.austausch_zentralheizung(
        temp_rein_C=70.0,
        volumen_rein_m3=0.1,
    )
    speicher.dump(
        filename=DIRECTORY_RESULTS / f"{label}-nachher1.txt",
        aux=dict(out_wasser_C=f"{out_wasser_C:0.3f}"),
    )
    out_wasser_C = speicher.austausch_zentralheizung(
        temp_rein_C=50.0, volumen_rein_m3=0.1
    )
    speicher.dump(
        filename=DIRECTORY_RESULTS / f"{label}-nachher2.txt",
        aux=dict(out_wasser_C=f"{out_wasser_C:0.3f}"),
    )
    out_wasser_C = speicher.austausch_zentralheizung(
        temp_rein_C=70.0, volumen_rein_m3=0.1
    )
    speicher.dump(
        filename=DIRECTORY_RESULTS / f"{label}-nachher3.txt",
        aux=dict(out_wasser_C=f"{out_wasser_C:0.3f}"),
    )

    # with cProfile.Profile() as pr:

    #     pr.print_stats("tottime")


def test_b():
    stimuli = stimuli_wintertag
    speicher = Speicher_dezentral(stimuli=stimuli, startTempC=60.0)
    speicher.reset(packets=((90.0, 0.1),))
    label = "test_b"
    speicher.dump(filename=DIRECTORY_RESULTS / f"{label}-vorher.txt")
    speicher.austausch_warmwasser(energie_J=10000.0)
    speicher.dump(filename=DIRECTORY_RESULTS / f"{label}-nachher1.txt")


def test_c():
    stimuli = stimuli_wintertag
    speicher = Speicher_dezentral(stimuli=stimuli, startTempC=60.0)
    speicher.reset(packets=((90.0, 0.001),))
    label = "test_c"
    speicher.dump(filename=DIRECTORY_RESULTS / f"{label}-vorher.txt")
    speicher.austausch_warmwasser(energie_J=1e6)
    speicher.dump(filename=DIRECTORY_RESULTS / f"{label}-nachher1.txt")


def test_c1():
    stimuli = stimuli_wintertag
    speicher = Speicher_dezentral(stimuli=stimuli, startTempC=30.0)
    speicher.reset(packets=((90.0, 0.001),))
    label = "test_c1"
    speicher.dump(filename=DIRECTORY_RESULTS / f"{label}-vorher.txt")
    speicher.austausch_warmwasser(energie_J=1e6)
    speicher.dump(filename=DIRECTORY_RESULTS / f"{label}-nachher1.txt")


def test_d():
    stimuli = stimuli_wintertag
    speicher = Speicher_dezentral(stimuli=stimuli, startTempC=60.0)
    speicher.reset(packets=((90.0, 0.001),))
    label = "test_d"
    speicher.dump(filename=DIRECTORY_RESULTS / f"{label}-vorher.txt")
    out_wasser_C = speicher.austausch_heizung(energie_J=1e5)
    speicher.dump(
        filename=DIRECTORY_RESULTS / f"{label}-nachher1.txt",
        aux=dict(out_wasser_C=f"{out_wasser_C:0.3f}"),
    )


def test_e():
    stimuli = stimuli_wintertag
    speicher = Speicher_dezentral(stimuli=stimuli, startTempC=60.0)
    speicher.reset(packets=((40.0, speicher.volumen_auslass_von_unten_m3 - 0.001),))
    label = "test_e"
    speicher.dump(filename=DIRECTORY_RESULTS / f"{label}-vorher.txt")
    out_wasser_C = speicher.austausch_heizung(energie_J=1e6)
    speicher.dump(
        filename=DIRECTORY_RESULTS / f"{label}-nachher1.txt",
        aux=dict(out_wasser_C=f"{out_wasser_C:0.3f}"),
    )
    out_wasser_C = speicher.austausch_heizung(energie_J=1e6)
    speicher.dump(
        filename=DIRECTORY_RESULTS / f"{label}-nachher2.txt",
        aux=dict(out_wasser_C=f"{out_wasser_C:0.3f}"),
    )


def test_f():
    stimuli = stimuli_wintertag
    # ruecklauf_bodenheizung_C = 24.0
    temp_knapp_ueber_ruecklauf_C = 24.0001
    speicher = Speicher_dezentral(
        stimuli=stimuli, startTempC=temp_knapp_ueber_ruecklauf_C
    )
    speicher.reset(packets=((temp_knapp_ueber_ruecklauf_C - 1e-12, 0.1),))
    label = "test_f"
    speicher.dump(filename=DIRECTORY_RESULTS / f"{label}-vorher.txt")
    out_wasser_C = speicher.austausch_heizung(energie_J=1e6)
    speicher.dump(
        filename=DIRECTORY_RESULTS / f"{label}-nachher1.txt",
        aux=dict(out_wasser_C=f"{out_wasser_C:0.3f}"),
    )


def main():
    test_a()
    test_b()
    test_c()
    test_c1()
    test_d()
    test_e()
    test_f()


if __name__ == "__main__":
    main()
