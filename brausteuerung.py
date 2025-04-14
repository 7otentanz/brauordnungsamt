from datetime import datetime, timedelta
import time
import RPi.GPIO as GPIO

### Zuerst muss das Rezept mit allen Notwendigen Parametern zusammengestellt und initialisiert werden. ###
class Rezept:
    def __init__(self, name, schuettung, maischplan, kochzeit, hopfengaben, anstelltemperatur, hefe):
        self.name = name
        self.schuettung = schuettung
        self.maischplan = maischplan
        self.kochzeit = kochzeit
        self.dauer = sum(self.maischplan.values()) + self.kochzeit
        self.hopfengaben = hopfengaben
        self.anstelltemperatur = anstelltemperatur
        self.hefe = hefe

### Anschließend wird die Brausteuerung (Im Sinne von Hardware) zusammengestellt und initialisiert.###
### Hier wird ausschließlich Hardware angesteuert und ausgelesen, Zeitsteurung findet erst im Brauvorgang statt! ###
class Brausteuerung:
    def __init__(self, heizpin, ruehrpin, temperaturpin):
        self.heizpin = heizpin
        self.ruehrpin = ruehrpin
        self.temperaturpin = temperaturpin
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.heizpin, GPIO.OUT)
        GPIO.output(self.heizpin, GPIO.LOW)
        GPIO.setup(self.ruehrpin, GPIO.OUT)
        GPIO.output(self.ruehrpin, GPIO.LOW)
        # Temperaturpin noch zu belegen und zu programmieren

    def heizenAN(self):
        GPIO.output(self.heizpin, GPIO.HIGH)

    def heizenAUS(self):
        GPIO.output(self.heizpin, GPIO.LOW)

    def ruehrenAN(self):
        GPIO.output(self.ruehrpin, GPIO.HIGH)

    def ruehrenAUS(self):
        GPIO.output(self.ruehrpin, GPIO.LOW)

    def temperatur(self):
        #GPIO für temperatur ansprechen
        pass

### Hier findet unter Verwendung des Rezepts und der Hardware die Initialisierung des Brauprozesses statt. ###
### An dieser Stelle wird der Brauprozess gestartet, zeitgesteuert und getrackt. ###
class Brauvorgang:
    def __init__(self, rezept, hardware):
        self.rezept = rezept
        self.hardware = hardware
        self.beginn = "beginn"
        self.ende = "ende"
        self.status = "Einmaischen"

    def einmaischenVorbereiten(self):
        self.einmaischtemperaturHalten = True
        benachrichtigt = False
        while self.einmaischtemperaturHalten:
            istTemperatur = self.hardware.temperatur()
            if istTemperatur < 59.5:
                self.hardware.heizenAN()
            else:
                self.hardware.heizenAUS()
                # Wenn das este mal die Einmaischtemperatur erreicht ist wird das Rührwerk eingeschalten und eine Benachrichtigung gesendet.
                if benachrichtigt == False:
                    ### Benachrichtung per Mail?###
                    self.hardware.ruehrenAN()
                    benachrichtigt = True
            time.sleep(25)

    def brauvorgangStarten(self):
        # einmaischenVorbereiten zuerst beenden
        self.einmaischtemperaturHalten = False
        time.sleep(25)
        # eigentlichen Brauvorgang beginnen
        self.beginn = datetime.now()
        self.ende = self.beginn + timedelta(minutes=(self.rezept.dauer))
        self.statusAendern("Erste Rast beginnt.")
        self.maischen()

    def statusAnzeigen(self):
        # Hier eine Funktion, die den aktuellen Status des Prozesses auf dem Display anzeigt
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

    def statusAendern(self, status):
        self.status = status
        # Benachrichtigung, wenn sich der Status ändert - auch die einzelnen Rasten
        # Status auf Maischplan ändern mit Klick auf Startbutton oder so?
        # während des Fahrens der Rasten: "Temperatur und Restzeit"
        # Kochen: "Kochen und Restzeit"
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
HeuteBrauIch.einmaischenVorbereiten()

### Mit Klick auf einen Startbutton ###
HeuteBrauIch.brauvorgangStarten()

print(HeuteBrauIch.ende)

