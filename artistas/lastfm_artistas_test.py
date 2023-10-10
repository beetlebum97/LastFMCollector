import sys
import requests
import json

user = sys.argv[1]  # Argumento pasado al script. Usuario sobre el que se realiza la búsqueda.

def obtener_artistas(user):
    url = "http://ws.audioscrobbler.com/2.0/"
    api_key = "clave_api" # Reemplaza esto con tu clave API
    limit = 5 # Número de resultados por página. Cantidad baja para hacer pruebas. 50 es el valor máximo por página que permite la API
    page = 1 # Número de página inicial
    total_pages = 1 # Inicializa el número total de páginas
    artists = [] # Lista para almacenar los nombres de los artistas y el número de scrobbles

    while page <= total_pages and len(artists) < limit:   # Limitado al número indicado en limit
        params = {
            "method": "user.getTopArtists",
            "user": user,
            "api_key": api_key,
            "format": "json",
            "limit": limit,
            "page": page
        }

        response = requests.get(url, params=params)
        data = json.loads(response.text)

        # Añade los rankings, los nombres de los artistas y el número de scrobbles a la lista
        artists.extend([(artist['@attr']['rank'], artist['name'], artist['playcount']) for artist in data['topartists']['artist']])

        # Actualiza el número total de páginas
        total_pages = int(data['topartists']['@attr']['totalPages'])

        # Incrementa el número de página para la próxima solicitud
        page += 1

    return {"artists": artists,"limit": limit, } # Devuelve diccionario con los datos necesarios


artists_scrobbles = obtener_artistas(user)

# Mostrar resultados

print(f"Limitado a {artists_scrobbles['limit']} registros para hacer pruebas.")

for values in artists_scrobbles['artists']:
    rank, artist, scrobbles = values
    print(f"Puesto; {rank}, Artista: {artist}, Scrobbles: {scrobbles}")

