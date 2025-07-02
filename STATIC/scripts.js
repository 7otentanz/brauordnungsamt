function schuettungHinzufuegen() {
    const container = document.getElementById("alleSchuettungen");
    const div = document.createElement("div");
    div.className = "schuettung";

    const inputMalzart = document.createElement("input");
    inputMalzart.setAttribute("type", "text");
    inputMalzart.setAttribute("name", "malzart[]");
    inputMalzart.setAttribute("placeholder", "Malzart");
    inputMalzart.required = true;

    const inputMalzmenge = document.createElement("input");
    inputMalzmenge.setAttribute("type", "number");
    inputMalzmenge.setAttribute("name", "malzmenge[]");
    inputMalzmenge.setAttribute("placeholder", "Menge (kg)");
    inputMalzmenge.setAttribute("step", "0.1");
    inputMalzmenge.required = true;

    div.appendChild(inputMalzart);
    div.appendChild(inputMalzmenge);
    container.appendChild(div);
  }

function rastHinzufuegen() {
    const container = document.getElementById("alleRasten");
    const div = document.createElement("div");
    div.className = "maischplan";

    const inputTemp = document.createElement("input");
    inputTemp.setAttribute("type", "number");
    inputTemp.setAttribute("name", "temperatur[]");
    inputTemp.setAttribute("placeholder", "Temperatur (°C)");
    inputTemp.required = true;

    const inputDauer = document.createElement("input");
    inputDauer.setAttribute("type", "number");
    inputDauer.setAttribute("name", "dauer[]");
    inputDauer.setAttribute("placeholder", "Dauer (min)");
    inputDauer.required = true;

    div.appendChild(inputTemp);
    div.appendChild(inputDauer);
    container.appendChild(div);
  }

function hopfengabeHinzufuegen() {
    const container = document.getElementById("alleHopfengaben");
    const div = document.createElement("div");
    div.className = "hopfengaben";

    const inputSorte = document.createElement("input");
    inputSorte.setAttribute("type", "text");
    inputSorte.setAttribute("name", "sorte[]");
    inputSorte.setAttribute("placeholder", "Sorte");
    inputSorte.required = true;

    const inputMenge = document.createElement("input");
    inputMenge.setAttribute("type", "number");
    inputMenge.setAttribute("name", "hopfenmenge[]");
    inputMenge.setAttribute("placeholder", "Menge (g)");
    inputMenge.required = true;

    const inputZeit = document.createElement("input");
    inputZeit.setAttribute("type", "number");
    inputZeit.setAttribute("name", "zeit[]");
    inputZeit.setAttribute("placeholder", "Zeit (min)");
    inputZeit.required = true;

    div.appendChild(inputSorte);
    div.appendChild(inputMenge);
    div.appendChild(inputZeit);
    container.appendChild(div);
  }

function zumZoll() {
  window.open("https://www.formulare-bfinv.de/ffw/action/invoke.do?id=2075", "_blank");
}