import numpy as np

import util_modell_speicher_dezentral
from util_modell import Modell
from util_modell_speicher_dezentral import (
    PlotEnergiereserve,
    PlotSpeicher,
    PlotSpeicherSchichtung,
    Speicher_dezentral,
)
from util_modell_zentralheizung import PlotZentralheizung, Zentralheizung
from util_simulation import Simulation
from util_stimuli import StimuliWintertag


class KurzZentralheizung:
    def __init__(self):
        self.fernwaerme_hot_C = 243.0
        self.fernwaermepumpe_on = True


class KurzModell:
    def __init__(self):
        self.zentralheizung = KurzZentralheizung()


stimuli = StimuliWintertag()
modell = KurzModell()
speicher1 = util_modell_speicher_dezentral.Speicher_dezentral(
    stimuli=stimuli, startTempC=60.0
)

# speicher1.print()

# speicher1.update_input(Zentralheizung)

# for i in range(10):
#     temperatur_raus = speicher1.austauschen(
#         temp_rein_C=40.0, volumen_rein_m3=0.1, position_raus_anteil_von_unten=0.5
#     )
#     print(f"temperatur_raus {temperatur_raus}")
# speicher1.print()

# temperatur = 5
# for i in range(14000):
#     # speicher1.run(timestep_s=60, time_s=1, modell=modell
#     temperatur, volumen = speicher1.warmwasserbezug(energie_J=10000)
# speicher1.print()
# print(temperatur, volumen)

speicher1.print()
print(speicher1._verlustleistung_W())
