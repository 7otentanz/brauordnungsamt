from django.shortcuts import render, HttpResponse, redirect
import os, json, threading, datetime
import xml.etree.ElementTree as ET

static = "/var/www/brauordnungsamt/static"


#### INDEX ####

# Landingpage mit Auswahlkacheln.
def index(request):
	return render(request, "app/index.html")


#### REZEPT ####

# Rezeptseite zum selbst eingeben oder um eine URL für den Scraper einzutragen.
def rezept(request):
	return render(request, "app/rezept.html")

# Selbst eingetragenes Rezept anlegen und Kessel auf Einmaischtemperatur aufheizen
def rezeptanlegen(request):
	if request.method == "POST":

		name = request.POST.get("name")
		kochzeit = int(request.POST.get("kochzeit"))
		anstelltemperatur = int(request.POST.get("anstelltemperatur"))
		hefe = request.POST.get("hefe")

		malzarten = request.POST.getlist("malzart[]")
		malzmengen = request.POST.getlist("malzmenge[]")
		schuettung = {malz: float(menge) for malz, menge in zip(malzarten, malzmengen)}

		temperaturen = request.POST.getlist("temperatur[]")
		dauern = request.POST.getlist("dauer[]")
		maischplan = {int(temperatur): int(dauer) for temperatur, dauer in zip(temperaturen, dauern)}

		sorten = request.POST.getlist("sorte[]")
		hopfenmengen = request.POST.getlist("hopfenmenge[]")
		zeiten = request.POST.getlist("zeit[]")
		hopfengaben = [
				{
				"sorte": sorte,
				"menge": float(menge),
				"zeit": int(zeit)
				}
				for sorte, menge, zeit in zip(sorten, hopfenmengen, zeiten)
			]

		rezept = {
			"name": name,
			"schuettung": schuettung,
			"maischplan": maischplan,
			"kochzeit": kochzeit,
			"hopfengaben": hopfengaben,
			"anstelltemperatur": anstelltemperatur,
			"hefe": hefe
		}

		# initialisiertes Rezept in eine json schreiben.
		rezeptjson = os.path.join(static, "rezept.json")
		with open(rezeptjson, "w", encoding="utf-8") as datei:
			json.dump(rezept, datei, indent=4)

		# Protokoll-datei anlegen aber noch auf "nicht abgeschlossen" setzen.
		jetzt = datetime.datetime.now()
		heute = jetzt.strftime("%Y-%m-%d")
		rezept["abgeschlossen"] = False
		protokolljson = os.path.join(static, "protokolle", f"{heute}.json")
		with open(protokolljson, "w", encoding="utf-8") as datei:
			json.dump(rezept, datei, indent=4)

		# Heizen auf Einmaischtemperatur im Hintergrund starten, dass sofort weitergeleitet werden kann auf die Statusseite.
		def brauvorgangstarten():
			from . import brausteuerung
			bierrezept = brausteuerung.Rezept(name, schuettung, maischplan, kochzeit, hopfengaben, anstelltemperatur, hefe)
			brauhaus = brausteuerung.Brausteuerung()
			brauvorgang = brausteuerung.Brauvorgang(bierrezept, brauhaus)
			brauvorgang.einmaischenVorbereiten()
		
		thread = threading.Thread(target=brauvorgangstarten)
		thread.start()
		
		return redirect("status")

# Mit angegebener URL ein Rezept scrapen und auch hier auf Einmaischtemperatur heizen.
def scrapeRezept(request):
	from . import mmumscraper
	if request.method == "POST":

		# Rezept vom Scraper initialisieren lassen...
		url = request.POST.get("url")
		rezept = mmumscraper.rezeptscrapen(url)

		# ... und an das Template zurückgeben, dass es verarbeitet werden kann.
		return render(request, 'app/rezeptscraped.html', {"rezept": rezept})


#### NUTZER ####	

# Nutzerdaten aus der angelegten json laden.
def nutzer(request):
	nutzerjson = os.path.join(static, "nutzer.json")
	with open(nutzerjson, "r", encoding="utf-8") as datei:
		nutzerdaten = json.load(datei)
	
	return render(request, 'app/nutzer.html', {"nutzer": nutzerdaten})

# Nutzerdaten in der json ändern.
def nutzerdatenaendern(request):
	nutzerjson = os.path.join(static, "nutzer.json")
	with open(nutzerjson, "r", encoding="utf-8") as datei:
		nutzerdaten = json.load(datei)
	
	if request.method == "POST":
		nachname = request.POST.get("nachname", "")
		vorname = request.POST.get("vorname", "")
		ort = request.POST.get("ort", "")
		strasse = request.POST.get("strasse", "")
		hausnummer = request.POST.get("hausnummer", "")
		plz = request.POST.get("plz", "")
		hauptzollamt = request.POST.get("hauptzollamt", "")
		email = request.POST.get("email", "")
		telefon = request.POST.get("telefon", "")
		geburtstag = request.POST.get("geburtstag", "")
		menge = int(request.POST.get("menge", ""))
		sudmenge = int(request.POST.get("sudmenge", ""))

		nutzerdaten.update({"nachname": nachname, "vorname": vorname, "ort": ort, "strasse": strasse, "hausnummer": hausnummer, "plz": plz, "hauptzollamt": hauptzollamt, "email": email, "telefon": telefon, "geburtstag": geburtstag, "menge": menge, "sudmenge": sudmenge})

		with open(nutzerjson, "w", encoding="utf-8") as datei:
			json.dump(nutzerdaten, datei, indent=4)
	
	return redirect("nutzer")


#### STATUS ####

# Status aus der json auslesen, die die brausteuerung.py bei Statusänderung schreibt.
def status(request):
	with open("/var/www/brauordnungsamt/static/status.txt", "r", encoding="utf-8") as datei:
		status = datei.read()
	
	return render(request, "app/status.html", {"status": status})

# Mit dem Maischplan und Rasten-fahren beginnen, sobald eingemaischt wurde.
def rastenStarten(request):
	if request.method == "POST":

		rezeptjson = os.path.join(static, "rezept.json")
		with open(rezeptjson, "r", encoding="utf-8") as datei:
			rezept = json.load(datei)
		
		def maischrastenStarten():
			from . import brausteuerung
			bierrezept = brausteuerung.Rezept(rezept["name"], rezept["schuettung"], rezept["maischplan"], rezept["kochzeit"], rezept["hopfengaben"], rezept["anstelltemperatur"], rezept["hefe"])
			brauhaus = brausteuerung.Brausteuerung()
			brauvorgang = brausteuerung.Brauvorgang(bierrezept, brauhaus)
			brauvorgang.brauvorgangStarten()
		
		thread = threading.Thread(target=maischrastenStarten)
		thread.start()
		
		return redirect("status")
	
# Mit dem Würzekochen beginnen, wenn der Maischplan abgeschlossen ist und alle Rasten gefahren wurden.
def kochenStarten(request):
	if request.method == "POST":

		rezeptjson = os.path.join(static, "rezept.json")
		with open(rezeptjson, "r", encoding="utf-8") as datei:
			rezept = json.load(datei)
		
		def wuerzekochen():
			from . import brausteuerung
			bierrezept = brausteuerung.Rezept(rezept["name"], rezept["schuettung"], rezept["maischplan"], rezept["kochzeit"], rezept["hopfengaben"], rezept["anstelltemperatur"], rezept["hefe"])
			brauhaus = brausteuerung.Brausteuerung()
			brauvorgang = brausteuerung.Brauvorgang(bierrezept, brauhaus)
			brauvorgang.kochen()
		
		thread = threading.Thread(target=wuerzekochen)
		thread.start()
		
		# Menge gebrauten Biers aktualisieren
		nutzerjson = os.path.join(static, "nutzer.json")
		with open(nutzerjson, "r", encoding="utf-8") as datei:
			nutzerdaten = json.load(datei)
		nutzerdaten["menge"] = nutzerdaten["menge"] + nutzerdaten["sudmenge"]
		with open(nutzerjson, "w", encoding="utf-8") as datei:
			json.dump(nutzerdaten, datei, indent=4)

		# Protokoll abschließen & Menge hinzufügen
		jetzt = datetime.datetime.now()
		heute = jetzt.strftime("%Y-%m-%d")
		rezept["menge"] = nutzerdaten["sudmenge"]
		rezept["abgeschlossen"] = True
		protokolljson = os.path.join(static, "protokolle", f"{heute}.json")
		with open(protokolljson, "w", encoding="utf-8") as datei:
			json.dump(rezept, datei, indent=4)

		return redirect("status")
	

#### BRAUTAGEBUCH ####

# Alle Protokolle suchen, auslesen und an das Template übergeben.
def brautagebuch(request):

	protokollordner = os.path.join(static, "protokolle")
	alleProtokolle = []

	for eineJson in os.listdir(protokollordner):
		protokoll = os.path.join(protokollordner, eineJson)
		with open(protokoll, "r", encoding="utf-8") as datei:
			protokolldaten = json.load(datei)
			datum = eineJson.split(".")[0]
			alleProtokolle.append({datum: protokolldaten})

	return render(request, "app/brautagebuch.html", {"alleProtokolle": alleProtokolle})

def steuerformularErstellen(request):

	if request.method == "POST":

		# Alle Daten auslesen und in Variablen speichern
		datumA = request.POST.get("datum", "")
		datumB = datetime.datetime.strptime(datumA, "%Y-%m-%d")
		datum = datumB.strftime("%d.%m.%Y 00:00:00")

		protokolljson = os.path.join(static, "protokolle", f"{datumA}.json")
		with open(protokolljson, "r", encoding="utf-8") as datei:
			protokolldaten = json.load(datei)
		mengeA = protokolldaten["menge"]
		mengeB = mengeA / 100
		menge = f"{mengeB:.2f}"
		
		nutzerjson = os.path.join(static, "nutzer.json")
		with open(nutzerjson, "r", encoding="utf-8") as datei:
			nutzerdaten = json.load(datei)
		
		steuerformular = os.path.join(static, "formular2075.xml")

		tree = ET.parse(steuerformular)
		root = tree.getroot()
		nsURL = "http://www.lucom.com/ffw/xml-data-1.0.xsd"
		ns = {"ns": nsURL}
		ET.register_namespace("", nsURL)
		
		# Mit xPath das datarow Element mit den "Datenelementen" finden
		daten = root.find("ns:instance/ns:datarow", ns)

		# Alle Elemente suchen und jeweils Inhalte ersetzen
		for element in daten.findall("ns:element", ns):
			elementID = element.get("id")

			if elementID == "Vorblatt_vorname":
				element.text = nutzerdaten["vorname"]
			elif elementID == "Vorblatt_ort":
				element.text = nutzerdaten["ort"]
			elif elementID == "Vorblatt_strasse":
				element.text = nutzerdaten["strasse"]
			elif elementID == "Vorblatt_haus_nr":
				element.text = nutzerdaten["hausnummer"]
			elif elementID == "Vorblatt_plz_de":
				element.text = nutzerdaten["plz"]
			elif elementID == "Vorblatt_name_firma":
				element.text = nutzerdaten["nachname"]
			elif elementID == "Vorblatt_hza":
				element.text = nutzerdaten["hauptzollamt"]
			elif elementID == "Vorblatt_e_mail3":
				element.text = nutzerdaten["email"]
			elif elementID == "2075_ansprechpartner":
				element.text = f"{nutzerdaten['vorname']} {nutzerdaten['nachname']}"
			elif elementID == "2075_email":
				element.text = nutzerdaten["email"]
			elif elementID == "2075_telefon":
				element.text = nutzerdaten["telefon"]
			elif elementID == "2075_ort":
				element.text = nutzerdaten["ort"]
			elif elementID == "2075_email":
				element.text = nutzerdaten["email"]
			elif elementID == "2075_datum2":
				element.text = datum
			elif elementID == "versteuerung2":
				element.text = menge.replace(".", ",")
			elif elementID == "betrag2":
				element.text = f"{9.44 * mengeB:.2f}".replace(".", ",")
			elif elementID == "endsumme":
				element.text = f"{9.44 * mengeB:.2f}".replace(".", ",")

		steuerformularXML = ET.tostring(root, encoding="utf-8", method="xml")
		response = HttpResponse(steuerformularXML, content_type="application/xml")
		response["Content-Disposition"] = "attachment; filename=2075.xml"
		return response

	return redirect("brautagebuch")
