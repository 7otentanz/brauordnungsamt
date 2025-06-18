from django.shortcuts import render, HttpResponse, redirect
import os, json, threading

static = "/var/www/brauordnungsamt/static"

def brautest(request):
	from . import brausteuerung
	brausteuerung.test()


def lcddisplay(request):
	from . import lcddisplay
	lcddisplay.lcdAnzeigen("Dieser Text wird\nangezeigt!")

	return HttpResponse("Prima, klappt auch.")

def relaisschalten(request):
	from . import relais
	relais.undlos()

	return HttpResponse("Relais schalten!")

#### INDEX ####

def index(request):
	return render(request, "app/index.html")

#### REZEPT ####

def rezept(request):
	return render(request, "app/rezept.html")

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
				"menge": int(menge),
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

		rezeptjson = os.path.join(static, "rezept.json")
		with open(rezeptjson, "w", encoding="utf-8") as datei:
			json.dump(rezept, datei, indent=4)

		# Brauvorgang im Hintergrund starten, dass sofort weitergeleitet werden kann auf die Statusseite
		def brauvorgangstarten():
			from . import brausteuerung
			bierrezept = brausteuerung.Rezept(name, schuettung, maischplan, kochzeit, hopfengaben, anstelltemperatur, hefe)
			brauhaus = brausteuerung.Brausteuerung(temperaturpin="Pin3")
			brauvorgang = brausteuerung.Brauvorgang(bierrezept, brauhaus)
			brauvorgang.einmaischenVorbereiten()
		
		thread = threading.Thread(target=brauvorgangstarten)
		thread.start()
		
		return redirect("status")

#### NUTZER ####	

def nutzer(request):
	nutzerjson = os.path.join(static, "nutzer.json")
	with open(nutzerjson, "r", encoding="utf-8") as datei:
		nutzerdaten = json.load(datei)
	
	return render(request, 'app/nutzer.html', {"nutzer": nutzerdaten})

def nutzerdatenaendern(request):
	nutzerjson = os.path.join(static, "nutzer.json")
	with open(nutzerjson, "r", encoding="utf-8") as datei:
		nutzerdaten = json.load(datei)
	
	if request.method == "POST":
		name = request.POST.get("name", "")
		hauptzollamt = request.POST.get("hauptzollamt", "")
		menge = int(request.POST.get("menge", ""))

		nutzerdaten.update({"name": name, "hauptzollamt": hauptzollamt, "menge": menge})

		with open(nutzerjson, "w", encoding="utf-8") as datei:
			json.dump(nutzerdaten, datei, indent=4)
	
	return redirect("nutzer")

#### STATUS ####

def status(request):
	with open("/var/www/brauordnungsamt/static/status.txt", "r", encoding="utf-8") as datei:
		status = datei.read()
	
	return render(request, "app/status.html", {"status": status})