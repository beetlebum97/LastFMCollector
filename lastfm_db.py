import sys
import requests
import json
import pyodbc
import datetime
import time

user = sys.argv[1]  # Argumento pasado al script. Usuario sobre el que se realiza la búsqueda.

# Comando para mostrar la hora al empezar
hora_inicio = datetime.datetime.now()
print("Hora de inicio:", datetime.datetime.now())
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

# CONEXIÓN SQL SERVER. CREACIÓN BBDD E INSERCIÓN DE LOS REGISTROS

SERVER = 'Servidor SQL SERVER'
USERNAME = 'usuario'
PASSWORD = 'clave'

connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};UID={USERNAME};PWD={PASSWORD}'

conn = pyodbc.connect(connectionString, autocommit=True)
cursor = conn.cursor()

cursor.execute('CREATE DATABASE LASTFM')
cursor.execute('USE LASTFM')

SQL_QUERY_ARTISTAS = """ 
CREATE TABLE Artistas(
	Puesto int,
	Artista nvarchar(255) PRIMARY KEY,
	Escuchas int   
)
"""

cursor.execute(SQL_QUERY_ARTISTAS)

for rank, artist, scrobbles in artists_scrobbles:
        cursor.execute("""
            INSERT INTO Artistas (Puesto, Artista, Escuchas)
            VALUES (?, ?, ?)
        """, rank, artist, scrobbles)

cursor.execute("""SELECT COUNT(*) FROM Artistas""")

# Obtener y mostrar el resultado
resultado = cursor.fetchone()
print("Artistas registrados:", resultado[0])

SQL_QUERY_DISCOS = """ 
CREATE TABLE Discos(
	Puesto int PRIMARY KEY,
    Disco nvarchar (255),
	Artista nvarchar(255),
	Escuchas int,  
)
"""

cursor.execute(SQL_QUERY_DISCOS)

for rank, album, artist, scrobbles in albums_scrobbles:
        cursor.execute("""
            INSERT INTO Discos (Puesto, Disco, Artista, Escuchas)
            VALUES (?, ?, ?, ?)
        """, rank, album, artist, scrobbles)

cursor.execute("""SELECT COUNT(*) FROM Discos""")

# Obtener y mostrar el resultado
resultado = cursor.fetchone()
print("Discos registrados:", resultado[0])

SQL_QUERY_CANCIONES = """ 
CREATE TABLE Canciones(
	Puesto int PRIMARY KEY,
    Canción nvarchar (255),
	Artista nvarchar(255),
	Escuchas int,  
)
"""

cursor.execute(SQL_QUERY_CANCIONES)

for rank, track, artist, scrobbles in tracks:
        cursor.execute("""
            INSERT INTO Canciones (Puesto, Canción, Artista, Escuchas)
            VALUES (?, ?, ?, ?)
        """, rank, track, artist, scrobbles)


cursor.execute("""SELECT COUNT(*) FROM Canciones""")

# Obtener y mostrar el resultado
resultado = cursor.fetchone()
print("Canciones registradas:", resultado[0])

SQL_QUERY_ESCUCHAS = """ 
CREATE TABLE Escuchas(
	ID int IDENTITY(1,1) PRIMARY KEY,
	Canción nvarchar(255),
	Disco nvarchar(255),
	Artista nvarchar(255),
	Fecha nvarchar(255)   
)
"""

cursor.execute(SQL_QUERY_ESCUCHAS)

for track, album, artist, date in tracks2:
        cursor.execute("""
            INSERT INTO Escuchas (Canción, Disco, Artista, Fecha)
            VALUES (?, ?, ?, ?)
        """, track, album, artist, date)
        

cursor.execute("""SELECT COUNT(*) FROM Escuchas""")

# Obtener y mostrar el resultado
resultado = cursor.fetchone()
print("Escuchas registradas:", resultado[0])

conn.commit()
cursor.close()
conn.close()

print()

# Comando para mostrar la hora al terminar
hora_fin = datetime.datetime.now()
print("Hora de finalización:", datetime.datetime.now())
# Mostrar la duración del script
duracion = hora_fin - hora_inicio
minutes, seconds = divmod(duracion.seconds, 60)
print(f"Duración del script: {minutes} minutos y {seconds} segundos")