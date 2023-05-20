import matplotlib.pyplot as plt
import numpy as np

WASSER_WAERMEKAP = 4190 # J / kg / K

class speicher_dezentral:
    def __init__(self, startTempC = 20.0, totalvolumen_m3 = 0.69):
        #self.teilspeicher_i = 10
        self.totalvolumen_m3 = totalvolumen_m3
        #self.teilvolumen_m3 = 0.69 / self.teilspeicher_i
        self.volumenliste = [] #self.teilspeicher_i * [(startTempC, self.teilvolumen_m3)]
        self.volumenliste.append((startTempC, self.totalvolumen_m3))
        self.volumenliste_vorher_debug = []
    def print(self):
        for [temp_C, volumen_m3] in self.volumenliste:
            print (f'Temperatur C: {temp_C:0.1f}, Volumen m^3: {volumen_m3:0.6f}')
    def _sort(self):
        self.volumenliste.sort(key=lambda a: a[0], reverse = True)
    def _gesamtvolumen_justieren(self): # wegen rundungsfehlern justieren
        gesamt_volumen_m3 = 0.0
        for (temp_C, volumen_m3) in self.volumenliste:
            gesamt_volumen_m3 += volumen_m3
        abweichung_m3 = self.totalvolumen_m3 - gesamt_volumen_m3 
        if abs(abweichung_m3) > 1e-5:
            print('vorher')
            for [temp_C, volumen_m3] in self.volumenliste_vorher_debug:
                print (f'Temperatur C: {temp_C:0.1f}, Volumen m^3: {volumen_m3:0.6f}')
            print('nachher')
            self.print()
            print(f'abweichung_m3 {abweichung_m3} zu gross')
            assert False
        self.volumenliste[0] = (self.volumenliste[0][0], self.volumenliste[0][1] + abweichung_m3)
        return(gesamt_volumen_m3)
    def _einfuellen(self, temp_rein_C = 70.0, volumen_rein_m3 = 0.010):
        #print(f'einfuellen  temp_rein_C = {temp_rein_C}, volumen_rein_m3 = {volumen_rein_m3}')
        self.volumenliste_vorher_debug = self.volumenliste.copy()
        volumenliste_neu = []
        bestehend_eingefuellt = False
        for (temp_C, volumen_m3) in self.volumenliste:
            if abs (temp_C - temp_rein_C) < 1E-5 and not bestehend_eingefuellt:
                volumenliste_neu.append((temp_C, volumen_m3 + volumen_rein_m3))
                bestehend_eingefuellt = True
            else:
                volumenliste_neu.append((temp_C, volumen_m3))
        if not bestehend_eingefuellt:
            volumenliste_neu.append((temp_rein_C, volumen_rein_m3))
            volumenliste_neu.sort(key=lambda a: a[0], reverse = True)
        self.volumenliste = volumenliste_neu
        '''
        volumen_summe_m3 = 0.0
        for (temp_C, volumen_m3) in self.volumenliste:
            volumen_summe_m3 += volumen_m3
        print(f'abweichung nach einfuellen {self.totalvolumen_m3-volumen_summe_m3} m3')
        '''

    def austauschen(self, temp_rein_C = 70.0, volumen_rein_m3 = 0.010, position_raus_anteil_von_unten = 0.5):
        assert volumen_rein_m3 >= 0.0
        assert position_raus_anteil_von_unten >= 0.0 and position_raus_anteil_von_unten <= 1.0
        #print('einfuellen')
        self._einfuellen(temp_rein_C = temp_rein_C, volumen_rein_m3 = volumen_rein_m3)
        #self._sort() # braucht es nicht mehr, ist immer sortiert
        #print('raus nehmen')
        raus_bei_volumen_m3 = self.totalvolumen_m3 * (1-position_raus_anteil_von_unten)
        volumenliste_neu = []
        volumen_summe_m3 = 0.0
        genommen_summe_m3 = 0.0
        energie = 0.0
        for (temp_C, volumen_m3) in self.volumenliste:
            volumen_summe_m3 += volumen_m3
            volumen_verbleiben_m3 = volumen_m3
            if  (volumen_rein_m3 - genommen_summe_m3) > 1e-9: # es muss noch genommen werden
                if volumen_summe_m3 > raus_bei_volumen_m3:# ab hier nehmen
                    nehme_m3 = min(volumen_rein_m3-genommen_summe_m3, volumen_m3)
                    assert nehme_m3 > 0.0
                    energie += temp_C * nehme_m3
                    genommen_summe_m3 += nehme_m3
                    volumen_verbleiben_m3 = volumen_m3 - nehme_m3
            else:
                volumen_verbleiben_m3 = volumen_m3 # bleibt gleich
            if volumen_verbleiben_m3 > 1e-8: # zu kleine Volumen skipen
                volumenliste_neu.append((temp_C, volumen_verbleiben_m3))
        temperatur_raus_C = energie / genommen_summe_m3
        self.volumenliste = volumenliste_neu
        self._gesamtvolumen_justieren()
        return(temperatur_raus_C)
    def temperaturprofil(self, temperaturen_i = 10):
        temperaturen = []
        index = 0
        volumen_summe_m3 = 0.0
        for (temp_C, volumen_m3) in self.volumenliste:
            volumen_summe_m3 += volumen_m3
            while volumen_summe_m3 > self.totalvolumen_m3 / temperaturen_i * index and index < temperaturen_i:
                temperaturen.append(temp_C)
                index += 1
        assert len(temperaturen) == temperaturen_i
        return(temperaturen)


anfang_nichts_h = 5
rampe_rauf_h = 1
voll_heizen_h = 2
rampe_runter_h = 1
zeit_s_array =       [0   , anfang_nichts_h*3660, (anfang_nichts_h+rampe_rauf_h)*3660, (anfang_nichts_h+rampe_rauf_h+voll_heizen_h)*3660, (anfang_nichts_h+rampe_rauf_h+voll_heizen_h+rampe_runter_h)*3660]
temperatur_C_array = [30.0, 30.0                , 70.0                               , 70.0                                             , 30.0]
def fernwaerme_vorgabe(zeit_s = 0):
    return(np.interp(zeit_s, zeit_s_array, temperatur_C_array))



speicher1 = speicher_dezentral(startTempC = 40.0)
#print (speicher1.volumenliste)
#speicher1.print()
#speicher1.volumenliste[4]=(31.1,0.1)
#speicher1.print()
#speicher1._equalize()
#speicher1._sort()
#speicher1.print()
#print(speicher1.volumenliste[0][1])
if False:
    for i in range(5):
        print(speicher1.austauschen())
    speicher1.print()




if True:
    temperaturen = []
    time = []
    fernwaerme_hot = []
    fernwaerme_cold = []
    leistung_in_speicher = []
    time_step_s = 60
    fluss_liter_pro_h = 148.0
    fluss_m3_pro_s = fluss_liter_pro_h / 1000 / 3600
    for time_s in range(0, 12*60*60, time_step_s):

        fernwaerme_hot_C = fernwaerme_vorgabe(zeit_s = time_s)
        fernwarme_cold_C = speicher1.austauschen(temp_rein_C = fernwaerme_hot_C, volumen_rein_m3 = fluss_m3_pro_s * time_step_s, position_raus_anteil_von_unten = 0.64)
        temperaturen.append(speicher1.temperaturprofil())
        fernwaerme_hot.append(fernwaerme_hot_C)
        fernwaerme_cold.append(fernwarme_cold_C)
        leistung_W = WASSER_WAERMEKAP * (fernwaerme_hot_C-fernwarme_cold_C) * fluss_m3_pro_s * 1000
        leistung_in_speicher.append(leistung_W)
        time.append(time_s)
    speicher1.print()


    if False:
        # Data for plotting
        #t = np.arange(0.0, 2.0, 0.01)
        #s = 1 + np.sin(2 * np.pi * t)

        fig, ax = plt.subplots()
        #ax.plot(t, s)
        ax.plot(np.array(time) / 3600, temperaturen, linewidth=1.0, alpha=0.5)
        ax.plot(np.array(time) / 3600, fernwaerme_hot, linestyle='dashed', linewidth=3, color='red', alpha=0.5, label='fernwaerme_hot')
        ax.plot(np.array(time) / 3600, fernwaerme_cold, linestyle='dotted', linewidth=3, color='blue', alpha=0.5, label = 'fernwaerme_cold')
        ax2 = ax.twinx()
        ax2.plot(np.array(time) / 3600, leistung_in_speicher, linestyle='dotted', linewidth=5, color='orange', alpha=0.5, label = 'leistung')
        ax.set(xlabel='time (h)', ylabel='Temperature C',
            title='Temperaturprofil')
        ax2.set(ylabel='Power W')
        ax.legend()
        ax2.legend()
        ax.grid()

    if True:
        

    #fig.savefig("test.png")
    plt.show()