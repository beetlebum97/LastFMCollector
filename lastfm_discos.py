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
print(f"Obteniendo discos reproducidos por el usuario {usuario} ...")

# FUNCIÓN DISCOS
def listado_discos(usuario):
    url = "http://ws.audioscrobbler.com/2.0/"
    limite = 50 # Número máximo de resultados por página
    pagina = 1 # Número de página inicial
    total_paginas = 1 # Inicializa el número total de páginas
    discos = [] # Lista para almacenar información de los discos

    while pagina <= total_paginas:
        params = {
            "method": "user.getTopAlbums",
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

        # Añade a la lista posición (ranking), nombre, artista y número de scrobbles de cada disco
        discos.extend([(disco['@attr']['rank'], disco['name'], disco['artist']['name'], disco['playcount']) for disco in data['topalbums']['album']])

        # Actualiza el número total de páginas
        total_paginas = int(data['topalbums']['@attr']['totalPages'])

        # Incrementa el número de página para la próxima solicitud
        pagina += 1

    return discos

# Guardar los registros de la función en una variable
try:
    discos = listado_discos(usuario)
except ValueError as e:
    print(f"{e}")
    sys.exit(1)  # Salir del script si ocurre error

# Crear la carpeta 'listados/usuario' si no existe
os.makedirs(f'listados/{usuario}', exist_ok=True)

# Guardar listado en un archivo
with open(f'listados/{usuario}/lastfm_{usuario}_discos.txt', 'w', encoding='utf-8') as output:
    for rank, name, artist, playcount in discos:
        output.write(f"Puesto: {rank} | Disco: {name} | Artista: {artist} | Scrobbles: {playcount}\n")

# Resultado
print(f"-> Discos: {len(discos)}")
print(f"-> Archivo: {ruta}/listados/lastfm_{usuario}_discos.txt")

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
