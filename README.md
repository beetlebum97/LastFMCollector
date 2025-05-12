# :guitar: LastFMCollector  :guitar:
last.fm es una red social, radio virtual y sistema de recomendación de música que construye perfiles y estadísticas sobre gustos musicales a partir de los metadatos de canciones enviados por sus usuarios. Cada reproducción registrada por last.fm se denomina scrobble, y recoge toda la información relativa a esa escucha (título, artista, disco, estilo, hora etc.). Mas detalles en https://www.last.fm/es/

Los scripts del repositorio almacenan los registros de un usuario cualquiera, introducido como parámetro. A modo de ejemplo, incluyo listados de mi usuario (hayman3030). Para poder obtener los datos hay que tener una clave activa en la API de last.fm. Se puede solicitar gratuitamente en el siguiente enlace: https://www.last.fm/api/account/create. Manual: https://www.last.fm/es/api). 

## 1. INFORME
### lastfm.py
Muestra un breve resumen. Número total de artistas, discos, canciones y scrobbles.

Antes de lanzar el script, inserta tu clave API en la línea 6:

```clave_api = "Introduce tu clave" ```

Guarda el script y ejecuta:

```python lastfm.py <usuario> ```

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/LastFMCollector/main/capturas/lastfm.jpg)

## 2. LISTADOS

Archivos que contienen los registros del usuario. Cada script genera un listado concreto con la información adaptada según la clasificación.

| CLASIFICACIÓN | SCRIPT | LISTADO | DATOS |
| ------ | ------ | ------ | ------ |
| ARTISTAS | lastfm_artistas.py | lastfm_{usuario}_artistas.txt | Puesto, artista, scrobbles |
| DISCOS | lastfm_discos.py | lastfm_{usuario}_discos.txt |Puesto, disco, artista, scrobbles |
| CANCIONES | lastfm_canciones.py | lastfm_{usuario}_canciones.txt | Puesto, canción, artista, scrobbles |
| SCROBBLES | lastfm_scrobbles.py | lastfm_{usuario}_scrobbles.txt | Canción, disco, artista, fecha-hora |

El listado se guarda en la ruta ./listados/{usuario}. Por el momento en formato de texto (.txt).

Para poder ejecutar correctamente los scripts, primero insertar clave API personal en la línea 8 y guardar antes de lanzar:

```clave_api = "Introduce tu clave" ```

### lastfm_artistas.py

Artistas ordenados de mayor a menor nº de scrobbles (todas las veces que se ha reproducido una canción del artista).

```python lastfm_artistas.py <usuario> ```

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/lastfm_artistas1.jpg)

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/lastfm_artistas2.jpg)

### lastfm_discos.py

Discos ordenados de mayor a menor nº de scrobbles (todas las veces que se ha reproducido una canción perteneciente a ese disco). 

```python lastfm_discos.py <usuario> ```

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/lastfm_discos1.jpg)

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/lastfm_discos2.jpg)

### lastfm_canciones.py

Canciones ordenadas de mayor a menor nº de scrobbles (todas las veces que se ha reproducido la canción).

```python lastfm_canciones.py <usuario> ```

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/lastfm_canciones1.jpg)

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/lastfm_canciones2.jpg)

### lastfm_scrobbles.py

Todos los scrobbles (reproducciones) ordenadas por fecha-hora (Descendente).

```python lastfm_canciones.py <usuario> ```

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/lastfm_scrobbles1.jpg)

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/lastfm_scrobbles2.jpg)

## 3. CONTROL DE ERRORES

Al introducir usuario que no existe, aparecere el mensaje:

```Error 6: User not found```

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/lastfm_error.jpg)

En el caso de terminar abruptamente, podría ser error puntual de la API. Recomendable probar con otro usuario. En futuras actualizaciones incluiré scripts de test.




