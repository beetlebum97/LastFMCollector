let vistaActual = "";
let pagina = 0;
const porPagina = 100;
let datos = [];

function mostrarVista(vista) {
  vistaActual = vista;
  pagina = 0;
  datos = [];
  document.getElementById("contenedor").innerHTML = "";
  document.getElementById("verMas").style.display = "none";
  cargarJSON(vista);
}

function cargarJSON(vista) {
  fetch(`lastfm_hayman3030_${vista}.json`)
    .then(res => res.json())
    .then(json => {
      datos = json[vista];
      mostrarPagina();
      if (datos.length > porPagina) {
        document.getElementById("verMas").style.display = "block";
      }
    });
}

function mostrarPagina() {
  const inicio = pagina * porPagina;
  const fin = inicio + porPagina;
  const bloque = datos.slice(inicio, fin);

  const contenedor = document.getElementById("contenedor");
  const tabla = document.createElement("table");
  const thead = document.createElement("thead");
  const tbody = document.createElement("tbody");

  let columnas = [];

  if (vistaActual === "artistas") {
    columnas = ["Puesto", "Artista", "Scrobbles"];
    bloque.forEach(item => {
      const fila = `<tr><td>${item.puesto}</td><td>${item.artista}</td><td>${item.scrobbles}</td></tr>`;
      tbody.innerHTML += fila;
    });
  } else if (vistaActual === "discos") {
    columnas = ["Puesto", "Disco", "Artista", "Scrobbles"];
    bloque.forEach(item => {
      const fila = `<tr><td>${item.puesto}</td><td>${item.disco}</td><td>${item.artista}</td><td>${item.scrobbles}</td></tr>`;
      tbody.innerHTML += fila;
    });
  } else if (vistaActual === "canciones") {
    columnas = ["Puesto", "Canción", "Artista", "Scrobbles"];
    bloque.forEach(item => {
      const fila = `<tr><td>${item.puesto}</td><td>${item.cancion}</td><td>${item.artista}</td><td>${item.scrobbles}</td></tr>`;
      tbody.innerHTML += fila;
    });
  } else if (vistaActual === "scrobbles") {
    columnas = ["Fecha", "Canción", "Disco", "Artista"];
    bloque.forEach(item => {
      const fila = `<tr><td>${item.fecha}</td><td>${item.cancion}</td><td>${item.disco}</td><td>${item.artista}</td></tr>`;
      tbody.innerHTML += fila;
    });
  }

  thead.innerHTML = `<tr>${columnas.map(col => `<th>${col}</th>`).join("")}</tr>`;
  tabla.appendChild(thead);
  tabla.appendChild(tbody);
  contenedor.appendChild(tabla);
}

document.getElementById("verMas").addEventListener("click", () => {
  pagina++;
  mostrarPagina();
});
