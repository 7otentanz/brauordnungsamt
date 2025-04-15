function schuettungHinzufuegen() {
  const div = document.createElement("div");
  div.className = "schuettung";
  div.innerHTML = `<input type="text" placeholder="Malzart" required>
                   <input type="number" step="0.1" placeholder="kg" required>`;
  document.getElementById("schuettung").insertBefore(div, document.getElementById("schuettung").lastElementChild);
}

function rastHinzufuegen() {
  const div = document.createElement("div");
  div.className = "maischplan";
  div.innerHTML = `<input type="number" placeholder="Temperatur (°C)" required>
                   <input type="number" placeholder="Dauer (min)" required>`;
  document.getElementById("maischplan").insertBefore(div, document.getElementById("maischplan").lastElementChild);
}

function hopfengabeHinzufuegen() {
  const div = document.createElement("div");
  div.className = "hopfengaben";
  div.innerHTML = `<input type="text" placeholder="Sorte" required>
                   <input type="number" placeholder="Menge (g)" required>
                   <input type="number" placeholder="Zeit (min)" required>`;
  document.getElementById("hopfengaben").insertBefore(div, document.getElementById("hopfengaben").lastElementChild);
}















































































// Das hier ersetzen durch eine views-Funktion, die das Rezept ordentlich zusammenbaut!

document.getElementById("brauForm").addEventListener("submit", function(e) {
  e.preventDefault();

  const form = e.target;
  const name = form.name.value;
  const kochzeit = parseInt(form.kochzeit.value);
  const anstelltemperatur = parseInt(form.anstelltemperatur.value);
  const hefe = form.hefe.value;

  const schuettung = {};
  document.querySelectorAll(".schuettung").forEach(div => {
    const [malz, menge] = div.querySelectorAll("input");
    schuettung[malz.value] = parseFloat(menge.value);
  });

  const maischplan = {};
  document.querySelectorAll(".maisch").forEach(div => {
    const [temp, dauer] = div.querySelectorAll("input");
    maischplan[parseInt(temp.value)] = parseInt(dauer.value);
  });

  const hopfengaben = [];
  document.querySelectorAll(".hopfengabe").forEach(div => {
    const [sorte, menge, zeit] = div.querySelectorAll("input");
    hopfengaben.push({
      sorte: sorte.value,
      menge: parseInt(menge.value),
      zeit: parseInt(zeit.value)
    });
  });

  const rezept = {
    name,
    schuettung,
    maischplan,
    kochzeit,
    hopfengaben: { hopfengaben },
    anstelltemperatur,
    hefe
  };

  console.log("Rezept:", rezept);
  alert("Rezept erfolgreich erstellt! Siehe Konsole für Ausgabe.");
})