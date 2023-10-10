import sys
import requests
import json
import datetime
import time

user = sys.argv[1]  # Argumento pasado al script. Usuario sobre el que se realiza la búsqueda

# Comando para mostrar la hora al empezar
hora_inicio = datetime.datetime.now()
print("Hora de inicio:", datetime.datetime.now())

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
    
# Número de filas (pares clave-valor)
numero = len(albums_scrobbles)

print()
print(f"Discos escuchados por el usuario {user}: {numero}")
print()

# Comando para mostrar la hora al terminar
hora_fin = datetime.datetime.now()
print("Hora de finalización:", datetime.datetime.now())

# Mostrar la duración del script
duracion = hora_fin - hora_inicio
minutes, seconds = divmod(duracion.seconds, 60)
print(f"Duración del script: {minutes} minutos y {seconds} segundos")