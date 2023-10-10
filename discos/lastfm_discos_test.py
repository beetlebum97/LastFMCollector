import sys
import requests
import json

user = sys.argv[1]  # Argumento pasado al script. Usuario sobre el que se realiza la búsqueda.

def obtener_discos(user):
    url = "http://ws.audioscrobbler.com/2.0/"
    api_key = "clave_api" # Reemplaza esto con tu clave API
    limit = 3 # Número de resultados por página. Cantidad baja para hacer pruebas. 50 es el valor máximo por página que permite la API
    page = 1 # Número de página inicial
    total_pages = 1 # Inicializa el número total de páginas
    albums = [] # Lista para almacenar los nombres de los álbumes, artistas y el número de scrobbles

    while page <= total_pages and len(albums) < limit:   # Limitado al número indicado en limit
        params = {
            "method": "user.getTopAlbums",
            "user": user,
            "api_key": api_key,
            "format": "json",
            "limit": limit,
            "page": page
        }

        response = requests.get(url, params=params)
        data = json.loads(response.text)
                                                               
        # Añade los nombres de los álbumes, artistas y el número de scrobbles a la lista
        albums.extend([(album['@attr']['rank'], album['name'], album['artist']['name'], album['playcount']) for album in data['topalbums']['album']])

        # Actualiza el número total de páginas
        total_pages = int(data['topalbums']['@attr']['totalPages'])

        # Incrementa el número de página para la próxima solicitud
        page += 1

    return {"albums": albums,"limit": limit, } # Devuelve diccionario con los datos necesarios

albums_scrobbles = obtener_discos(user)

print(f"Limitado a {albums_scrobbles['limit']} registros para hacer pruebas.")

for values in albums_scrobbles['albums']:
    rank, album, artist, scrobbles = values
    print(f"Puesto; {rank}, Disco: {album}, Artista: {artist}, Scrobbles: {scrobbles}")
