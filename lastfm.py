import sys
import requests
import datetime
import time

clave_api = "Introduce tu clave"
usuario = sys.argv[1]

inicio = datetime.datetime.now()
print()
print("[Fecha/Hora]", inicio.strftime("%Y-%m-%d %H:%M:%S"))
print()
print(f"Obteniendo información del usuario {usuario} ...")
print()

def obtener_total(usuario, metodo, root):
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": metodo,
        "user": usuario,
        "api_key": clave_api,
        "format": "json",
        "limit": 1,
        "page": 1
    }

    resp = requests.get(url, params=params)
    data = resp.json()

    if "error" in data:
        raise ValueError(f"Error {data['error']}: {data.get('message', 'Usuario no válido o no encontrado')}")

    # Solo un nivel de clave antes de @attr.total
    return int(data[root]["@attr"]["total"])

try:
    artistas   = obtener_total(usuario, "user.getTopArtists",    "topartists")
    discos     = obtener_total(usuario, "user.getTopAlbums",     "topalbums")
    canciones  = obtener_total(usuario, "user.getTopTracks",     "toptracks")
    scrobbles  = obtener_total(usuario, "user.getRecentTracks",  "recenttracks")
    favoritos  = obtener_total(usuario, "user.getLovedTracks",  "lovedtracks")

    print(f" + ARTISTAS  =======> {artistas}")
    print(f" + DISCOS    =======> {discos}")
    print(f" + CANCIONES =======> {canciones}")
    print(f" + SCROBBLES =======> {scrobbles}")
    print(f" + FAVORITOS =======> {favoritos}")
except ValueError as e:
    print(e)
