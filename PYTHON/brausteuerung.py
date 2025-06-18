from datetime import datetime, timedelta
import time
import RPi.GPIO as GPIO
import lcddisplay

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
    def __init__(self, temperaturpin):
        self.heizpin = 5
        self.ruehrpin = 6
        self.temperaturpin = temperaturpin
        self.status = ""

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.heizpin, GPIO.OUT)
        GPIO.output(self.heizpin, GPIO.HIGH)
        GPIO.setup(self.ruehrpin, GPIO.OUT)
        GPIO.output(self.ruehrpin, GPIO.HIGH)
        # Temperaturpin noch zu belegen und zu programmieren

    def heizenAN(self):
        GPIO.output(self.heizpin, GPIO.LOW)

    def heizenAUS(self):
        GPIO.output(self.heizpin, GPIO.HIGH)

    def ruehrenAN(self):
        GPIO.output(self.ruehrpin, GPIO.LOW)

    def ruehrenAUS(self):
        GPIO.output(self.ruehrpin, GPIO.HIGH)

    def temperatur(self):
        #GPIO für temperatur ansprechen
        return 60
	#pass

    def statusAnzeigen(self):
        displaytext = self.status
        lcddisplay.lcdAnzeigen(displaytext)

    def statusAendern(self, status):
        self.status = status
        with open("/var/www/brauordnungsamt/static/status.txt", "w", encoding="utf-8") as datei:
            datei.write(status)
        self.statusAnzeigen()

### Hier findet unter Verwendung des Rezepts und der Hardware die Initialisierung des Brauprozesses statt. ###
### An dieser Stelle wird der Brauprozess gestartet, zeitgesteuert und getrackt. ###

class Brauvorgang:
    def __init__(self, rezept, hardware):
        self.rezept = rezept
        self.hardware = hardware
        self.beginn = "beginn"
        self.ende = "ende"

    def einmaischenVorbereiten(self):
        self.einmaischtemperaturHalten = True
        benachrichtigt = False
        while self.einmaischtemperaturHalten:
            istTemperatur = self.hardware.temperatur()
            self.hardware.statusAendern(f"Aufheizen:\n{istTemperatur}°C")
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
        self.hardware.statusAendern("Erste Rast\nbeginnt.")
        self.maischen()

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
                
                self.hardware.statusAendern(f"{sollTemperatur}°C\nnoch {restzeit} Minuten")
                time.sleep(25)

        self.hardware.heizenAUS()
        ### Kochen dann auf Knopfdruck wieder starten?? Hier Pause fürs Läutern!###
        ### Benachrichtigung für Jodprobe & Würzemessung! ###
    
    def kochen(self):
        self.hardware.heizenAN()
        kochzeit = self.rezept.kochzeit
        self.hardware.statusAendern(f"Kochen:\nnoch {kochzeit} Minuten")

        start = datetime.now()
        ende= start + timedelta(minutes=kochzeit)

        while datetime.now() < ende:
            verbleibend = (ende - datetime.now()).seconds // 60

            for eineHopfengabe in self.rezept.hopfengaben["hopfengaben"]:
                if eineHopfengabe["zeit"] == verbleibend:
                    ### Benachrichtigung per Mail ###
                    pass

            self.hardware.statusAendern(f"Kochen:\nnoch{verbleibend} Minuten")            
            time.sleep(25)
        
        self.hardware.heizenAUS()
        ### Benachrichtigung: Kann gekühlt werden, Vorgang beendet ###
        self.hardware.statusAendern("Brauvorgang\nabgeschlossen!")














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

def test():
    ### Beim Anlegen des Brauprozesses - Startet auch die Aufheizphase ###
    BrauereiSteuerei = Brausteuerung(temperaturpin="Pin3")
    BrauereiSteuerei.statusAendern("Test")
    Hochzeitkveik = Rezept(name, schuettung, maischplan, kochzeit, hopfengaben, anstelltemperatur, hefe)
    HeuteBrauIch = Brauvorgang(Hochzeitkveik, BrauereiSteuerei)
    HeuteBrauIch.einmaischenVorbereiten()

    ### Mit Klick auf einen Startbutton ###
    HeuteBrauIch.brauvorgangStarten()

    ### Nach dem Läutern das Kochen starten ###
    HeuteBrauIch.kochen()

    print(HeuteBrauIch.ende)

