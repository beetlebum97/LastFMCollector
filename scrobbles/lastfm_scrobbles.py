import sys
import requests
import json
import datetime
import time

user = sys.argv[1]  # Argumento pasado al script. Usuario sobre el que se realiza la búsqueda

# Comando para mostrar la hora al empezar
hora_inicio = datetime.datetime.now()
print("Hora de inicio:", datetime.datetime.now())

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
numero = len(tracks2)

print()
print(f"Scrobbles (escuchas) del usuario {user}: {numero}")
print()

# Comando para mostrar la hora al terminar
hora_fin = datetime.datetime.now()
print("Hora de finalización:", datetime.datetime.now())

# Mostrar la duración del script
duracion = hora_fin - hora_inicio
minutes, seconds = divmod(duracion.seconds, 60)
print(f"Duración del script: {minutes} minutos y {seconds} segundos")