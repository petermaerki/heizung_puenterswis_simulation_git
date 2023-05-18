class speicher_dezentral:
    def __init__(self, startTempC = 20.0):
        self.teilspeicher_i = 10
        self.totalvolumen_m3 = 0.69
        self.teilvolumen_m3 = 0.69 / self.teilspeicher_i
        self.volumenliste = self.teilspeicher_i * [(startTempC, self.teilvolumen_m3)]
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
    def _equalize(self): # Umschichten nach Temperatur, auf Teilspeicher verteilen, ausgleichen
        self.volumenliste.append((0.0, 1E-10)) # kleines Volumen einfuegen damit Rundungsfehler nicht stoeren
        self._sort()
        volumenliste_alt_index = 0
        volumenliste_neu = []
        for index in range (self.teilspeicher_i):
            teilvolumen_neu = (0.0, 0.0)
            while teilvolumen_neu [1] < self.teilvolumen_m3: # teilvolumen noch nicht voll
                brauche_m3 = self.teilvolumen_m3 - teilvolumen_neu[1]
                dazu_m3 = min(self.volumenliste[volumenliste_alt_index][1],brauche_m3) 
                dazu_C = self.volumenliste[volumenliste_alt_index][0]
                alt_reduziertes_volumen_m3 = self.volumenliste[volumenliste_alt_index][1] - dazu_m3
                self.volumenliste[volumenliste_alt_index] = (dazu_C, alt_reduziertes_volumen_m3)
                neu_volumen_m3 = teilvolumen_neu[1]+dazu_m3
                teilvolumen_neu = ((teilvolumen_neu[0]* teilvolumen_neu[1] + dazu_C * dazu_m3)/neu_volumen_m3, neu_volumen_m3)
                if self.volumenliste[volumenliste_alt_index][1] < 0.0001:
                    volumenliste_alt_index += 1 # naechstes Volumen nehmen
            volumenliste_neu.append(teilvolumen_neu)
        assert abs(self._gesamtvolumen()) < 1e-6
        self.volumenliste = volumenliste_neu
        assert abs(self._gesamtvolumen() - self.totalvolumen_m3 ) < 1e-6
        self._sort()
    def austauschen(self, temp_rein_C = 70.0, volumen_m3 = 0.010, position_raus_anteil_von_unten = 0.6):
        assert volumen_m3 >= 0.0
        assert volumen_m3 < self.teilvolumen_m3 # kann in einem Schritt nicht mehr austauschen als ein Teilvolumen hat
        assert position_raus_anteil_von_unten >= 0.0 and position_raus_anteil_von_unten <= 1.0
        index_raus = int(self.teilspeicher_i * (1-position_raus_anteil_von_unten))
        temperatur_raus_C = self.volumenliste[index_raus][0]
        self.volumenliste[index_raus] = (temperatur_raus_C, self.volumenliste[index_raus][1] - volumen_m3)
        self.volumenliste.append((temp_rein_C, volumen_m3))
        self._equalize()
        return(temperatur_raus_C)
    def temperaturprofil(self):
        temperaturen = []
        for (temp_C, volumen_m3) in self.volumenliste:
            temperaturen.append(temp_C)
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

time_min = 0.0

temperaturen = []
time = []
for i in range(60):
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