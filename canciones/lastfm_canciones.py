import sys
import requests
import json
import datetime
import time

user = sys.argv[1]  # Argumento pasado al script. Usuario sobre el que se realiza la búsqueda

# Comando para mostrar la hora al empezar
hora_inicio = datetime.datetime.now()
print("Hora de inicio:", datetime.datetime.now())

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
    
# Número de filas (pares clave-valor)
numero = len(tracks)

print()
print(f"Canciones escuchadas por el usuario {user}: {numero}")
print()

# Comando para mostrar la hora al terminar
hora_fin = datetime.datetime.now()
print("Hora de finalización:", datetime.datetime.now())

# Mostrar la duración del script
duracion = hora_fin - hora_inicio
minutes, seconds = divmod(duracion.seconds, 60)
print(f"Duración del script: {minutes} minutos y {seconds} segundos")