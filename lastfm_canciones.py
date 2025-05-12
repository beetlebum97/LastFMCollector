import sys
import requests
import json
import datetime
import time
import os

clave_api="Introduce tu clave"
usuario = sys.argv[1]  # Argumento 1
ruta  = os.path.abspath(os.path.dirname(__file__)) # Ruta ejecución

# Inicio
inicio = datetime.datetime.now()
print("[Inicio]", inicio.strftime("%Y-%m-%d %H:%M:%S"))
print(f"Obteniendo canciones reproducidas por el usuario {usuario} ...")

# FUNCIÓN CANCIONES
def listado_canciones(usuario):
    url = "http://ws.audioscrobbler.com/2.0/"
    limite = 50 # Número máximo de resultados por página
    pagina = 1 # Número de página inicial
    total_paginas = 1 # Inicializa el número total de páginas
    canciones = [] # Lista para almacenar información de las canciones

    while pagina <= total_paginas:
        params = {
            "method": "user.getTopTracks",
            "user": usuario,
            "api_key": clave_api,
            "format": "json",
            "limit": limite,
            "page": pagina
        }

        response = requests.get(url, params=params)
        data = json.loads(response.text)

        # Verifica si hay un error en la respuesta antes de acceder a las claves
        if "error" in data:
            raise ValueError(f"Error {data['error']}: {data.get('message', 'Usuario no válido o no encontrado')}")

        # Añade la posición(ranking), nombre, artista y número de scrobbles de cada canción
        canciones.extend([(cancion['@attr']['rank'], cancion['name'], cancion['artist']['name'], cancion['playcount']) for cancion in data['toptracks']['track']])

        # Actualiza el número total de páginas
        total_paginas = int(data['toptracks']['@attr']['totalPages'])

        # Incrementa el número de página para la próxima solicitud
        pagina += 1

    return canciones

# Guardar los registros de la función en una variable
try:
    canciones = listado_canciones(usuario)
except ValueError as e:
    print(f"{e}")
    sys.exit(1)  # Salir del script si ocurre error

# Crear la carpeta 'listados/usuario' si no existe
os.makedirs(f'listados/{usuario}', exist_ok=True)

# Guardar listado en un archivo
with open(f'listados/{usuario}/lastfm_{usuario}_canciones.txt', 'w', encoding='utf-8') as output:
    for rank, name, artist, playcount in canciones:
        output.write(f"Puesto: {rank} | Canción: {name} | Artista: {artist} | Scrobbles: {playcount}\n")

# Resultado
print(f"-> Canciones: {len(canciones)}")
print(f"-> Archivo: {ruta}/listados/lastfm_{usuario}_canciones.txt")

# Finalización
fin = datetime.datetime.now()
print("[Fin]", fin.strftime("%Y-%m-%d %H:%M:%S"))

# Calcular duración
duracion = fin - inicio
total_segundos = int(duracion.total_seconds())

if total_segundos < 60:
    print(f"Tiempo de ejecución: {total_segundos} segundos")  # Solo segundos
else:
    horas, resto = divmod(total_segundos, 3600)  # 1 hora = 3600 segundos
    minutos, segundos = divmod(resto, 60)
    if horas > 0:
        print(f"Tiempo de ejecución: {horas} horas, {minutos} minutos y {segundos} segundos")
    else:
        print(f"Tiempo de ejecución: {minutos} minutos y {segundos} segundos")
