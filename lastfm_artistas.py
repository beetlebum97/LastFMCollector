import sys
import requests
import json
import datetime
import time
import os

clave_api="Introduce tu clave"
usuario = sys.argv[1]  # Argumento 1
ruta  = os.path.abspath(os.path.dirname(__file__)) # Ruta ejecución script

# Inicio
inicio = datetime.datetime.now()
print("[Inicio]", inicio.strftime("%Y-%m-%d %H:%M:%S"))
print(f"Obteniendo artistas reproducidos por el usuario {usuario} ...")

# FUNCIÓN ARTISTAS
def listado_artistas(usuario):
    url = "http://ws.audioscrobbler.com/2.0/"
    limite = 50 # Número máximo de resultados por página
    pagina = 1 # Número de página inicial
    total_paginas = 1 # Inicializa el número total de páginas
    artistas = [] # Lista para almacenar información de los artistas

    while pagina <= total_paginas:
        params = {
            "method": "user.getTopArtists",
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

        # Añade a la lista posición (ranking), nombre y número de scrobbles de cada artista
        artistas.extend([(artista['@attr']['rank'], artista['name'], artista['playcount']) for artista in data['topartists']['artist']])

        # Actualiza el número total de páginas
        total_paginas = int(data['topartists']['@attr']['totalPages'])

        # Incrementa el número de página para la próxima solicitud
        pagina += 1

    return artistas

# Guardar los registros de la función en una variable
try:
    artistas = listado_artistas(usuario)
except ValueError as e:
    print(f"{e}")
    sys.exit(1)  # Salir del script si ocurre error

# Crear la carpeta 'listados/usuario' si no existe
os.makedirs(f'listados/{usuario}', exist_ok=True)

# Guardar listado en un archivo
with open(f'listados/{usuario}/lastfm_{usuario}_artistas.txt', 'w', encoding='utf-8') as output:
    for rank, name, playcount in artistas:
        output.write(f"Puesto: {rank} | Artista: {name} | Scrobbles: {playcount}\n")

# Resultado
print(f"-> Artistas: {len(artistas)}")
print(f"-> Archivo: {ruta}/listados/lastfm_{usuario}_artistas.txt")

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
