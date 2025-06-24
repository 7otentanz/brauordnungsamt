import requests, json
from bs4 import BeautifulSoup
from selenium import webdriver
# folgende Imports sind wichtig weil a) headless und b) selbst installierter driver!
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
# bs4 , selenium und requests muss installiert werden!

def rezeptscrapen(url):
    options = Options()
    options.add_argument("--headless")
    service = Service(executable_path="/var/www/brauordnungsamt/geckodriver")

    driver = webdriver.Firefox(service=service, options=options)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    driver.quit()

    rezept = {
        "name": "",
        "schuettung": {},
        "maischplan": {},
        "kochzeit": "",
        "hopfengaben": [],
        "anstelltemperatur": "",
        "hefe": ""
    }

    divmain = soup.find("div", class_="main")
    pname = divmain.find("p", class_="name")
    name = pname.text
    rezept["name"] = name

    hauptzutaten = soup.find_all("div", class_="hauptzutat")

    for zutat in hauptzutaten:
        
        if "Schüttung" in zutat.get_text():
            alleMalze = zutat.find_all_next("div", class_="flex_container")
            for malz in alleMalze:
                sorteA = malz.find("div", class_="left").get_text()
                sorte= sorteA.replace(":", "")
                mengeA = malz.find("div", class_="right").get_text()
                try:
                    mengeB = float(mengeA.split(" g")[0])
                    menge = mengeB / 1000
                except:
                    menge = float(mengeA.split(" kg")[0])

                if sorte == "Gesamt":
                    break

                else:
                    rezept["schuettung"][sorte] = menge

        elif "Maischplan" in zutat.get_text():
            alleRasten = zutat.find_all_next("div", class_="flex_container")
            for rast in alleRasten:
                rastnummer = rast.find("div", class_="left").get_text()
                if rastnummer == "Einmaischen:":
                    continue
                elif rastnummer == "Abmaischen:":
                    break
                else:
                    temperaturUndDauer = rast.find("div", class_="right").get_text()
                    temperatur = int(temperaturUndDauer.split("°C")[0])
                    dauer = int(temperaturUndDauer.split(" ")[3])
                    rezept["maischplan"][temperatur] = dauer
        
        elif "Würzekochen" in zutat.get_text():
            #Hier gibt es keine Möglichkeit für einen break - Funktion darf als nicht in die nächte Hauptzutat weiterlaufen
            alleObjekte = []
            for objekt in zutat.find_next_siblings():
                if "hauptzutat" in objekt.get("class", []):
                    break
                elif "flex_container" in objekt.get("class", []):
                    alleObjekte.append(objekt)

            alleHopfen = []
            for objekt in alleObjekte:
                klassen = objekt.get("class", [])
                if "info" not in klassen:
                    alleHopfen.append(objekt)

            for hopfen in alleHopfen:
                sorte = hopfen.find("div", class_="left").get_text()
                if sorte == "Würzekochzeit:":
                    dauerA = hopfen.find("div", class_="right").get_text()
                    dauer = int(dauerA.split(" ")[0])
                    rezept["kochzeit"] = dauer
                else:
                    hopfenSorteA = hopfen.find("div", class_="left").get_text()
                    hopfenSorte = hopfenSorteA.split(" ")[0]
                    if hopfenSorteA.split(" ")[-1] == "(Vorderwürze):":
                        hopfenDauer = rezept["kochzeit"]
                    else:
                        hopfenDauerA = hopfen.find("div", class_="right").get_text()
                        try:
                            hopfenDauer = int(hopfenDauerA.split(" ")[-3])
                        except:
                            continue
                    hopfenMengeA = hopfen.find("div", class_="right").get_text()
                    hopfenMenge = float(hopfenMengeA.split(" ")[1])
                    hopfenObjekt = {
                        "sorte": hopfenSorte,
                        "menge": hopfenMenge,
                        "zeit": hopfenDauer,
                    }

                    rezept["hopfengaben"].append(hopfenObjekt)

        elif "Gärung" in zutat.get_text():
            alleObjekte = zutat.find_all_next("div", class_="flex_container")
            for objekt in alleObjekte:
                objektName = objekt.find("div", class_="left").get_text()
                if objektName == "Hefe:":
                    hefe = objekt.find("div", class_="right").get_text()
                    rezept["hefe"] = hefe
                elif objektName == "Gärtemperatur:":
                    temperaturA = objekt.find("div", class_="right").get_text()
                    temperaturB = temperaturA.split(" ")[0]
                    if "-" in temperaturB:
                        temperatur = temperaturB.split("-")[0]
                    else:
                        temperatur = temperaturB
                    rezept["anstelltemperatur"] = temperatur
                else:
                    break
        
    return rezept

                