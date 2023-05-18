class speicher_dezentral:
    def __init__(self, startTempC = 20.0, totalvolumen_m3 = 0.69):
        #self.teilspeicher_i = 10
        self.totalvolumen_m3 = totalvolumen_m3
        #self.teilvolumen_m3 = 0.69 / self.teilspeicher_i
        self.volumenliste = [] #self.teilspeicher_i * [(startTempC, self.teilvolumen_m3)]
        self.volumenliste.append((startTempC, self.totalvolumen_m3))
    def print(self):
        for [temp_C, volumen_m3] in self.volumenliste:
            print (f'Temperatur C: {temp_C:0.1f}, Volumen m^3: {volumen_m3:0.3f}')
    def _sort(self):
        self.volumenliste.sort(key=lambda a: a[0], reverse = True)
    def _gesamtvolumen(self):
        gesamt_volumen_m3 = 0.0
        for (temp_C, volumen_m3) in self.volumenliste:
            gesamt_volumen_m3 += volumen_m3
        return(gesamt_volumen_m3)
    def austauschen(self, temp_rein_C = 70.0, volumen_rein_m3 = 0.010, position_raus_anteil_von_unten = 0.5):
        assert volumen_rein_m3 >= 0.0
        assert position_raus_anteil_von_unten >= 0.0 and position_raus_anteil_von_unten <= 1.0
        self.volumenliste.append((temp_rein_C, volumen_rein_m3))
        self._sort()

        raus_bei_volumen_m3 = self.totalvolumen_m3 * (1-position_raus_anteil_von_unten)
        nehmenliste = []
        volumenliste_neu = []
        volumen_summe_m3 = 0.0
        genommen_summe_m3 = 0.0
        energie = 0.0
        for (temp_C, volumen_m3) in self.volumenliste:
            volumen_summe_m3 += volumen_m3
            if  (volumen_rein_m3 - genommen_summe_m3) > 1e-5: # es muss noch genommen werden
                if volumen_summe_m3 > raus_bei_volumen_m3:# ab hier nehmen
                    nehme_m3 = min(volumen_rein_m3, volumen_m3)
                    energie += temp_C * nehme_m3
                    nehmenliste.append((temp_C, nehme_m3))
                    genommen_summe_m3 += nehme_m3
                    volumen_m3 -= nehme_m3
            if volumen_m3 > 1e-5:
                volumenliste_neu.append((temp_C, volumen_m3))
        temperatur_raus_C = energie / genommen_summe_m3
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






speicher1 = speicher_dezentral()
#print (speicher1.volumenliste)
#speicher1.print()
#speicher1.volumenliste[4]=(31.1,0.1)
#speicher1.print()
#speicher1._equalize()
#speicher1._sort()
#speicher1.print()
#print(speicher1.volumenliste[0][1])
#print(speicher1.austauschen())
#speicher1.print()



if False:
    time_min = 0.0

    temperaturen = []
    time = []
    for i in range(70):
        temperaturen.append(speicher1.temperaturprofil())
        speicher1.austauschen()
        time_min +=1
        time.append(time_min)
    #print (temperaturen)

    import matplotlib.pyplot as plt
    import numpy as np

    # Data for plotting
    #t = np.arange(0.0, 2.0, 0.01)
    #s = 1 + np.sin(2 * np.pi * t)

    fig, ax = plt.subplots()
    #ax.plot(t, s)
    ax.plot(time, temperaturen)

    ax.set(xlabel='time (min)', ylabel='Temperature C',
        title='Temperaturprofil')
    ax.grid()

    #fig.savefig("test.png")
    plt.show()