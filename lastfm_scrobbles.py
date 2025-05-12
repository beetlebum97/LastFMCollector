import sys
import requests
import json
import datetime
import time
import os

clave_api="Introduce tu clave"
usuario = sys.argv[1]  # Argumento 1
ruta  = os.path.abspath(os.path.dirname(__file__)) # Ruta ejecución

inicio = datetime.datetime.now()
print("[Inicio]", inicio.strftime("%Y-%m-%d %H:%M:%S"))
print(f"Obteniendo scrobbles (reproducciones) del usuario {usuario} ...")

# FUNCIÓN SCROBBLES
def listado_reproducciones(usuario):
    url = "http://ws.audioscrobbler.com/2.0/"
    limite = 50 # Número máximo de resultados por página
    pagina = 1 # Número de página inicial
    total_paginas = 1 # Inicializa el número total de páginas
    reproducciones = [] # Lista para almacenar información de las reproducciones

    while pagina <= total_paginas:
        params = {
            "method": "user.getRecentTracks",
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

        # Añade a la lista canción, disco, artista y fecha de cada reproducción
        reproducciones.extend([(reproduccion['name'], reproduccion['album']['#text'], reproduccion['artist']['#text'], reproduccion['date']['#text']) for reproduccion in data['recenttracks']['track']])

        # Actualiza el número total de páginas
        total_paginas = int(data['recenttracks']['@attr']['totalPages'])

        # Incrementa el número de página para la próxima solicitud
        pagina += 1

    return reproducciones

# Guardar los registros de la función en una variable
try:
    reproducciones = listado_reproducciones(usuario)
except ValueError as e:
    print(f"{e}")
    sys.exit(1)  # Salir del script si ocurre error

# Crear la carpeta 'listados/usuario' si no existe
os.makedirs(f'listados/{usuario}', exist_ok=True)


# Guardar resultados en archivo
with open(f'listados/{usuario}/lastfm_{usuario}_scrobbles.txt', 'w', encoding='utf-8') as output:
    for name, album, artist, date in reproducciones:
        output.write(f"Canción: {name} | Disco: {album} | Artista: {artist} | Fecha: {date}\n")

# Resultado
print(f"-> Scrobbles: {len(reproducciones)}")
print(f"-> Archivo: {ruta}/listados/lastfm_{usuario}_scrobbles.txt")

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
