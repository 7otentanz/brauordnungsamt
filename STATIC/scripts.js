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