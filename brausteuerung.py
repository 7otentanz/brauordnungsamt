from datetime import datetime, timedelta, time

class Rezept:
    def __init__(self, name, schuettung, maischplan, kochzeit, hopfengaben, anstelltemperatur, hefe):
        self.name = name
        self.schuettung = schuettung
        self.maischplan = maischplan
        self.kochzeit = kochzeit
        self.hopfengaben = hopfengaben
        self.anstelltemperatur = anstelltemperatur
        self.hefe = hefe

class Brauvorgang:
    def __init__(self, rezept, hardware):
        self.rezept = rezept
        self.hardware = hardware
        self.beginn = "DatetimeObjekt"
        self.ende = "DatetimeObjekt"
        self.status = "Einmaischen"

    def einmaischenVorbereiten(self):
        # hardware.aufheizen mit temperatur von Rast [0], ohne Zeit
        pass

    def brauvorgangStarten(self):
        # Starten mit Klick auf Button, nach dem Einmaischen!
        self.beginn = datetime.now()
        self.ende = self.beginn + timedelta(minutes=self.rezept.kochzeit + sum(self.rezept.maischplan.values()))
        self.maischen() # sollte dann den Maischvorgang starten

    def statusAnzeigen(self):
        # Hier eine Funktion, die den aktuellen Status des Prozesses auf dem Display anzeigt
        pass

    def statusAendern(self, status):
        self.status = status
        # Benachrichtigung, wenn sich der Status ändert - auch die einzelnen Rasten
        # Status auf Maischplan ändern mit Klick auf Startbutton oder so?
        # während des Fahrens der Rasten: "Temperatur und Restzeit"
        # Kochen: "Kochen und Restzeit"
        pass

    def maischen(self):
        for sollTemperatur, dauer in self.rezept.maischplan.items():

            # Auf Rasttemperatur aufheizen #
            while True:
                istTemperatur = self.hardware.temperatur()
                if istTemperatur < (sollTemperatur - 0.5):      # Toleranz von 0.5 Grad
                    self.hardware.heizenAN()
                else:
                    self.hardware.heizenAUS()
                    break
                time.sleep(25)
            
            # Rasttemperatur halten #
            rastende = datetime.now() + timedelta(minutes=dauer)
            while datetime.now() < rastende:
                restzeit = (rastende - datetime.now()).seconds // 60
                istTemperatur = self.hardware.temperatur()
                if istTemperatur < (sollTemperatur - 0.5):      # Toleranz von 0.5 Grad
                    self.hardware.heizenAN()
                else:
                    self.hardware.heizenAUS()
                    break
                
                self.statusAendern(f"{sollTemperatur}°C, Restzeit {restzeit} Minuten")
                time.sleep(25)

        self.hardware.heizenAUS()

class Brausteuerung:
    def __init__(self, heizpin, ruehrpin, temperaturpin):
        self.heizpin = heizpin
        self.ruehrpin = ruehrpin
        self.temperaturpin = temperaturpin
        # GPIOs irgendwie festlegen und so

    def heizenAN(self):
        #GPIO fürs heizen ansprechen
        pass

    def heizenAUS(self):
        #GPIO fürs heizen ansprechen
        pass

    def ruehrenAN(self):
        #GPIO fürs rühren ansprechen
        pass

    def ruehrenAUS(self):
        #GPIO fürs rühren ansprechen
        pass

    def temperatur(self):
        #GPIO für temperatur ansprechen
        pass







### Rezept zusammenstellen, hier als Beispiel ###
name = "Hochzeitskveik"
schuettung = {"Pilsner Malz": 4.5, "Weizenmalz": 0.25}
maischplan = {54: 15, 63: 60, 73: 15, 76: 1} # im Format: "temperatur": "minuten"
kochzeit = 65
hopfengaben = {
    "hopfengaben": [
        {
            "sorte": "Polaris",
            "menge": 8,
            "zeit": kochzeit
        },
        {
            "sorte": "Perle",
            "menge": 20,
            "zeit": 10
        },
        {
            "sorte": "Polaris",
            "menge": 20,
            "zeit": 10
        }
    ]
}
anstelltemperatur = 16
hefe = "Oslo Kveik"

### Beim Anlegen des Brauprozesses - Startet auch die Aufheizphase ###
BrauereiSteuerei = Brausteuerung("Pin1", "Pin2", "Pin3")
Hochzeitkveik = Rezept(name, schuettung, maischplan, kochzeit, hopfengaben, anstelltemperatur, hefe)
HeuteBrauIch = Brauvorgang(Hochzeitkveik, BrauereiSteuerei)

### Mit Klick auf einen Startbutton ###
HeuteBrauIch.brauvorgangStarten()

print(HeuteBrauIch.ende)

