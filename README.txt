###################################################################
############# LASTFM: EXTRACCIÓN REGISTROS DE USUARIO #############
###################################################################

Last.fm es una red social, una radio virtual y un sistema de recomendación de música que construye perfiles y estadísticas sobre gustos musicales, basándose en los datos enviados por los usuarios registrados. El concepto principal es Scrobbling, proceso de seguimiento de la música escuchada a través de una aplicación. Cada escucha suma un scrobble, que almacena diversos datos (artista, disco, canción, hora, etc). Last.fm hace un seguimiento de la fonoteca del usuario explorando las canciones escuchadas desde el ordenador, teléfono u otro reproductor multimedia, y crea un perfil detallado de sus gustos. Por lo tanto, para poder hacer scrobbling es preciso otorgar permisos de acceso al historial de escuchas. Mas información en https://www.last.fm/es/

Los scripts del repositorio listan y guardan todos los registros musicales de un usuario determinado (parámetro), obteniendo artistas, discos, canciones y escuchas realizadas. Programados en Python, para poder ejecutarlos hay que solicitar acceso a la API de Last.fm (https://www.last.fm/api/account/create) (https://www.last.fm/es/api). Dicho acceso es gratuito, pero requiere registro en la plataforma. También es necesaria una conexión a servidor SQL Server para el script de base de datos lastfm_db.py

###################################################################
################# DESCRIPCIÓN SCRIPTS PRINCIPALES #################
###################################################################

[lastfm.py] 

- Muestra los artistas, discos, canciones y escuchas (scrobbles) de un usuario (parámetro). Ordenados por nº de escuchas o fecha.
- Duración del script.
- Resumen final.

[lastfm_output.py]

- Muestra y guarda en un archivo.txt (lasfm_{usuario}.txt) los artistas, discos, canciones y escuchas (scrobbles) de un usuario (parámetro). Ordenados por nº de escuchas o fecha.
- Duración del script.
- Resumen final.
- Puedes ver un ejemplo abriendo el archivo lastfm_hayman3030.txt incluido en el repositorio. hayman3030 es mi usuario en last.fm ;).

[lastfm_db.py]

- Crea una base de datos (LASTFM) en SQL SERVER y guarda en ella los artistas, discos, canciones y escuchas (scrobbles) de un usuario (parámetro). 
- Duración del script.
- Resumen final.

###################################################################
################### DESCRIPCIÓN SCRIPT PARCIALES ################## 
###################################################################

Los siguientes scripts muestran los registros de un usuario (parámetro) pero solo de un apartado concreto.

lastfm_artistas.py
lastfm_discos.py
lastfm_canciones.py
lastfm_scrobbles.py

###################################################################
##################### DESCRIPCIÓN SCRIPT TEST #####################
###################################################################

La finalidad de estos scripts es hacer pruebas principalmente con los diccionarios de datos, por eso el nº de registros devueltos está limitado, para una ejecución rápida.

lastfm_artistas_test.py
lastfm_discos_test.py
lastfm_canciones_test.py
lastfm_scrobbles_test.py

###################################################################
######################### EJECUCIÓN ###############################
###################################################################

-> Todos los scripts deben ejecutarse con 1 parámetro, que es el nombre del usuario sobre el que se realiza la búsqueda.

	python script.py <usuario>

	D:\last.fm\artistas>python lastfm_artistas_test.py hayman3030
	Limitado a 5 registros para hacer pruebas.
	Puesto; 1, Artista: Blur, Scrobbles: 1967
	Puesto; 2, Artista: Lou Reed, Scrobbles: 1083
	Puesto; 3, Artista: David Bowie, Scrobbles: 1042
	Puesto; 4, Artista: The Beatles, Scrobbles: 1019
	Puesto; 5, Artista: The Doors, Scrobbles: 913


-> Introducir clave API en las funciones:

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


-> En la conexión a SQL Server del script lastfm_db.py, editar los datos de conexión:

	SERVER = 'Servidor SQL Server'
	USERNAME = 'usuario'
	PASSWORD = 'contraseña'

