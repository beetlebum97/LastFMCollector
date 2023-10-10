import sys
import requests
import json

user = sys.argv[1]  # Argumento pasado al script. Usuario sobre el que se realiza la búsqueda

def obtener_escuchas(user):
    url = "http://ws.audioscrobbler.com/2.0/"
    api_key = "clave_api" # Reemplaza esto con tu clave API
    limit = 12 # Número de resultados por página. Cantidad baja para hacer pruebas. 200 es el valor máximo por página que permite la API
    page = 1 # Número de página inicial
    total_pages = 1 # Inicializa el número total de páginas
    tracks2 = [] # Lista para almacenar los nombres de las canciones, álbumes, artistas y fechas

    while page <= total_pages and len(tracks2) < limit:    # Limitado al número indicado en limit
        params = {
            "method": "user.getRecentTracks",
            "user": user,
            "api_key": api_key,
            "format": "json",
            "limit": limit,
            "page": page,
            "extended": 1
        }

        response = requests.get(url, params=params)
        data = json.loads(response.text)

        tracks2.extend([(track['name'], track['album']['#text'], track['artist']['name'], track['date']['#text']) for track in data['recenttracks']['track']])

        # Actualiza el número total de páginas
        total_pages = int(data['recenttracks']['@attr']['totalPages'])

        # Incrementa el número de página para la próxima solicitud
        page += 1

    return {"tracks2": tracks2,"limit": limit, } # Devuelve diccionario con los datos necesarios 

tracks2 = obtener_escuchas(user)

print(f"Limitado a {tracks2['limit']} registros para hacer pruebas.")

for values in tracks2['tracks2']:
    track, album, artist, date = values
    print(f"Canción: {track}, Disco: {album}, Artista: {artist}, Fecha: {date}")