import sys
import requests
import json
import datetime
import time

# Abre el archivo en modo de escritura con codificación utf-8 y redirige la salida estándar a este archivo
sys.stdout = open(f'lastfm_{sys.argv[1]}.txt', 'w', encoding='utf-8')

user = sys.argv[1]  # Argumento pasado al script. Usuario sobre el que se realiza la búsqueda.

# Comando para mostrar la hora al empezar
hora_inicio = datetime.datetime.now()
print("Hora de inicio:", datetime.datetime.now())
print()
print("Nombre del script:", sys.argv[0])
print("Parámetro pasado al script:", sys.argv[1])
print()

# ARTISTAS
def obtener_artistas(user):
    url = "http://ws.audioscrobbler.com/2.0/"
    api_key = "clave_api" # Reemplaza esto con tu clave API
    limit = 50 # Número máximo de resultados por página
    page = 1 # Número de página inicial
    total_pages = 1 # Inicializa el número total de páginas
    artists = [] # Lista para almacenar los nombres de los artistas y el número de scrobbles

    while page <= total_pages:
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

    return artists

artists_scrobbles = obtener_artistas(user)

# Mostrar resultados
for rank, artist, scrobbles in artists_scrobbles:
    print(f"Puesto; {rank}, Artista: {artist}, Scrobbles: {scrobbles}")


# DISCOS
def obtener_discos(user):
    url = "http://ws.audioscrobbler.com/2.0/"
    api_key = "clave_api" # Reemplaza esto con tu clave API
    limit = 50 # Número máximo de resultados por página
    page = 1 # Número de página inicial
    total_pages = 1 # Inicializa el número total de páginas
    albums = [] # Lista para almacenar los nombres de los álbumes, artistas y el número de scrobbles

    while page <= total_pages:
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

    return albums

albums_scrobbles = obtener_discos(user)

# Mostrar resultados
for rank, album, artist, scrobbles in albums_scrobbles:
    print(f"Puesto: {rank}, Disco: {album}, Artista: {artist}, Scrobbles: {scrobbles}")

# CANCIONES
def obtener_canciones(user):
    url = "http://ws.audioscrobbler.com/2.0/"
    api_key = "clave_api" # Reemplaza esto con tu clave API
    limit = 50 # Número máximo de resultados por página
    page = 1 # Número de página inicial
    total_pages = 1 # Inicializa el número total de páginas
    tracks = [] # Lista para almacenar los nombres de las canciones, álbumes, artistas y el número de scrobbles

    while page <= total_pages:
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
            tracks.append((track['@attr']['rank'], track['name'], track['artist']['name'], track['playcount']))

        # Actualiza el número total de páginas
        total_pages = int(data['toptracks']['@attr']['totalPages'])

        # Incrementa el número de página para la próxima solicitud
        page += 1

    return tracks

tracks = obtener_canciones(user)

# Mostrar resultados
for rank, track, artist, scrobbles in tracks:
    print(f"Puesto: {rank}, Canción: {track}, Artista: {artist}, Scrobbles: {scrobbles}")

# SCROBBLES (ESCUCHAS)
def obtener_escuchas(user):
    url = "http://ws.audioscrobbler.com/2.0/"
    api_key = "clave_api" # Reemplaza esto con tu clave API
    limit = 200 # Número máximo de resultados por página
    page = 1 # Número de página inicial
    total_pages = 1 # Inicializa el número total de páginas
    tracks2 = [] # Lista para almacenar los nombres de las canciones, álbumes, artistas y fechas

    while page <= total_pages:
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

    return tracks2

tracks2 = obtener_escuchas(user)

# Mostrar resultados
for track, album, artist, date in tracks2:
    print(f"Canción: {track}, Disco: {album}, Artista: {artist}, Fecha: {date}")


# Número de filas (pares clave-valor)
numero1 = len(artists_scrobbles)
numero2 = len(albums_scrobbles)
numero3 = len(tracks)
numero4 = len(tracks2)

print() 
print(f"Artistas escuchados por {user}: {numero1}")
print(f"Discos escuchados por {user}: {numero2}")
print(f"Canciones escuchadas por {user}: {numero3}")
print(f"Scrobbles (escuchas) de {user}: {numero4}")
print()

# Comando para mostrar la hora al terminar
hora_fin = datetime.datetime.now()
print("Hora de finalización:", datetime.datetime.now())

# Mostrar la duración del script
duracion = hora_fin - hora_inicio
minutes, seconds = divmod(duracion.seconds, 60)
print(f"Duración del script: {minutes} minutos y {seconds} segundos")

# Cerrar el archivo que guarda los registros
sys.stdout.close()