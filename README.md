# :guitar: LAST FM SCROBBLES  :guitar:
Last.fm es una red social, radio virtual y sistema de recomendación de música que construye perfiles y estadísticas sobre gustos musicales basándose en los datos enviados por los usuarios. 
Mediante la técnica de scrobbling, registra las canciones reproducidas obteniendo diversos datos tales como artista, disco, título, estilo u hora. Cada escucha equivale a un scrobble.
De esta manera, realiza un seguimiento de la fonoteca del usuario explorando sus scrobbles para crear un resumen detallado de sus gustos y poder ofrecerle recomendaciones similares.
Mas información en https://www.last.fm/es/

Los scripts del repositorio listan y guardan todos los registros musicales del usuario introducido como parámetro, obteniendo artistas, discos, canciones y escuchas realizadas. 
Programados en Python, para poder ejecutarlos hay que solicitar acceso a la API de Last.fm (https://www.last.fm/api/account/create) (https://www.last.fm/es/api). 
Dicho acceso es gratuito, pero requiere registro en la plataforma. También es necesaria una conexión a un servidor SQL Server para el script de base de datos lastfm_db.py

## SCRIPTS PRINCIPALES
### lastfm.py
Cuatro grandes listados de información:
| LISTADO | DATOS |
| ------ | ------ |
| ARTISTAS | Puesto, artista y nº de scrobbles |
| DISCOS | Puesto, disco, artista y nº de scrobbles |
| CANCIONES | Puesto, canción, artista y nº de scrobbles |
| SCROBBLES (escuchas) | Canción, disco, artista y fecha-hora |

También muestra la duración del script y un resumen de los resultados.

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/lastfm_1.jpg)
![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/lastfm_2.jpg)


### lastfm_output.py
En lugar de mostrar la información en pantalla, guarda los datos en archivo lasfm_{usuario}.txt. Incluyo un ejemplo en el repositorio: lastfm_hayman3030.txt. 
hayman3030 es mi usuario en last.fm ;).

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/lastfm_output.jpg)

### lastfm_db.py
Crea una base de datos (LASTFM) en SQL SERVER y vuelca en ella los artistas, discos, canciones y scrobbles (escuchas) del usuario. 

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/lastfm_db.jpg)

## SCRIPTS PARCIALES
Los siguientes scripts muestran los registros de un listado concreto.
- lastfm_artistas.py
- lastfm_discos.py
- lastfm_canciones.py
- lastfm_scrobbles.py

## SCRIPTS TEST
La principal finalidad de estos scripts es hacer pruebas con los diccionarios de datos, por eso el nº de registros devueltos está limitado, 
para una ejecución rápida.

- lastfm_artistas_test.py
- lastfm_discos_test.py
- lastfm_canciones_test.py
- lastfm_scrobbles_test.py

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/lastfm_test.jpg)

## EJECUCIÓN

### 1) EDITAR SCRIPT 

Introducir clave API en las funciones:
```sh
def obtener_artistas(user):
	url = "http://ws.audioscrobbler.com/2.0/"
	api_key = "clave_api" # Reemplaza esto con tu clave API

def obtener_discos(user):
	url = "http://ws.audioscrobbler.com/2.0/"
	api_key = "clave_api" # Reemplaza esto con tu clave API

def obtener_canciones(user):
	url = "http://ws.audioscrobbler.com/2.0/"
	api_key = "clave_api" # Reemplaza esto con tu clave API

def obtener_escuchas(user):
	url = "http://ws.audioscrobbler.com/2.0/"
	api_key = "clave_api" # Reemplaza esto con tu clave API
```

En la conexión a SQL Server del script lastfm_db.py, introducir datos de conexión:

```sh
	SERVER = 'Servidor SQL Server'
	USERNAME = 'usuario'
	PASSWORD = 'contraseña'
```

### 2) LANZAR SCRIPT

Todos los scripts deben ejecutarse con un parámetro: nombre de usuario registrado en lastfm.

```sh
python lastfm.py <usuario>
```
![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/lastfm_1.jpg)
![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/lastfm_test2.jpg)
