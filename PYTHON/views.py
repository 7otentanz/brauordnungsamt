from django.shortcuts import render, HttpResponse, redirect
import os, json

static = "/var/www/brauordnungsamt/static"

def brautest(request):
	import brausteuerung
	brausteuerung.test()

def ledanschalten(request):
	import RPi.GPIO as GPIO
	import time

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(17, GPIO.OUT)

	GPIO.output(17, GPIO.HIGH)
	time.sleep(5)
	GPIO.output(17, GPIO.LOW)

	GPIO.cleanup()

	return HttpResponse("Toll, klappt endlich.")

def lcddisplay(request):
	import lcddisplay

	lcddisplay.lcdAnzeigen("Dieser Text wird\nangezeigt!")

	return HttpResponse("Prima, klappt auch.")

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
		with open(rezeptjson, "w") as datei:
			json.dump(rezept, datei, indent=4)
		
		#### RETURN AUF WEITERES PROZESSTEMPLATE!!!! ####
		return redirect("rezept")

#### NUTZER ####	

def nutzer(request):
	nutzerjson = os.path.join(static, "nutzer.json")
	with open(nutzerjson, "r") as datei:
		nutzerdaten = json.load(datei)
	
	return render(request, 'app/nutzer.html', {"nutzer": nutzerdaten})

def nutzerdatenaendern(request):
	nutzerjson = os.path.join(static, "nutzer.json")
	with open(nutzerjson, "r") as datei:
		nutzerdaten = json.load(datei)
	
	if request.method == "POST":
		name = request.POST.get("name", "")
		hauptzollamt = request.POST.get("hauptzollamt", "")
		menge = int(request.POST.get("menge", ""))

		nutzerdaten.update({"name": name, "hauptzollamt": hauptzollamt, "menge": menge})

		with open(nutzerjson, "w") as datei:
			json.dump(nutzerdaten, datei, indent=4)
	
	return redirect("nutzer")

#### ####
