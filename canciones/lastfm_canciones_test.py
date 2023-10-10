import sys
import requests
import json

user = sys.argv[1]  # Argumento pasado al script. Usuario sobre el que se realiza la búsqueda.

def obtener_canciones(user):
    url = "http://ws.audioscrobbler.com/2.0/"
    api_key = "clave_api" # Reemplaza esto con tu clave API
    limit = 10 # Número de resultados por página. Cantidad baja para hacer pruebas. 50 es el valor máximo por página que permite la API
    page = 1 # Número de página inicial
    total_pages = 1 # Inicializa el número total de páginas
    tracks = [] # Lista para almacenar los nombres de las canciones, álbumes, artistas y el número de scrobbles

    while page <= total_pages and len(tracks) < limit:          # Limitado al número indicado en limit
        params = {
            "method": "user.getTopTracks",
            "user": user,
            "api_key": api_key,
            "format": "json",
            "limit": limit,
            "page": page
        }

        response = requests.get(url, params=params)
        data = json.loads(response.text)

        for track in data['toptracks']['track']:
            # Añade el nombre de la canción, el álbum, el artista y el número de scrobbles a la lista
            tracks.append((track['@attr']['rank'] ,track['name'], track['artist']['name'], track['playcount']))

        # Actualiza el número total de páginas
        total_pages = int(data['toptracks']['@attr']['totalPages'])

        # Incrementa el número de página para la próxima solicitud
        page += 1

    return {"tracks": tracks,"limit": limit, } # Devuelve diccionario con los datos necesarios 


tracks = obtener_canciones(user)

print(f"Limitado a {tracks['limit']} registros para hacer pruebas.")

for values in tracks['tracks']:
    rank, track, artist, scrobbles = values
    print(f"Puesto; {rank}, Canción: {track}, Artista: {artist}, Scrobbles: {scrobbles}")