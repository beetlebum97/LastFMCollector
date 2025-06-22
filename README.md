# :guitar: LastFMCollector  :guitar:
Last.FM es una red social, radio virtual y sistema de recomendación de música que construye perfiles y estadísticas sobre gustos musicales a partir de los metadatos de canciones enviados por los usuarios. Cada reproducción registrada por Last.FM es un scrobble que contiene toda la información relativa a esa escucha (título, artista, disco, estilo, fecha, etc.). Mas detalles en https://www.last.fm/es

lastfm.py descarga varios tipos de listados y muestra resumen general de un usuario introducido como parámetro. A modo de ejemplo, incluyo listados de mi usuario (hayman3030). Para poder obtener los datos hay que tener una clave activa en la API de Last.FM. Se puede solicitar gratuitamente en el siguiente enlace: https://www.last.fm/api/account/create. Manual: https://www.last.fm/es/api).

lastfm_db.py inserta los registros en una Base de Datos MySQL o PostgreSQL. Cada listado equivale a una tabla. El script crea el esquema relacional sobre un servidor existente.

REQUISITOS: 

-> Instalar Python y el módulo externo request ``` pip install request ```. 

-> Modificar línea 11 del script con tu clave api ```API_KEY = "Introduce tu clave" ```

-> Para el script de Bases de Datos instalar módulos adicionales: ``` pip install sqlalchemy pymysql psycopg2-binary ```

## 0. SINTAXIS
### python lastfm.py --help

Opciones de ejecución y los argumentos permitidos.

```
E:\LastFMCollector>python lastfm.py --help
============================================================
Last.FM Collector Full Script
============================================================
[Inicio] 2025-06-17 00:35:45
usage: lastfm.py [-h] [--resumen] [--artistas] [--canciones] [--discos] [--scrobbles] usuario

Extrae datos de Last.fm para un usuario específico

positional arguments:
  usuario      Nombre de usuario de Last.fm

options:
  -h, --help   show this help message and exit
  --resumen    Mostrar solo un resumen de estadísticas
  --artistas   Extraer artistas más escuchados
  --canciones  Extraer canciones más escuchadas
  --discos     Extraer discos más escuchados
  --scrobbles  Extraer historial de scrobbles

Ejemplos de uso:
  python lastfm.py usuario123                         # Extrae todos los datos
  python lastfm.py usuario123 --resumen               # Solo estadísticas resumidas
  python lastfm.py usuario123 --artistas              # Solo artistas
  python lastfm.py usuario123 --canciones             # Solo canciones
  python lastfm.py usuario123 --discos                # Solo discos
  python lastfm.py usuario123 --scrobbles             # Solo scrobbles
  python lastfm.py usuario123 --artistas --discos     # Artistas y discos
```

## 1. RESUMEN
### python lastfm.py --resumen usuario

Número total de artistas, discos, canciones, canciones favoritas y scrobbles. Opción no compatible con otras (listados). Ejecutar en solitario.
```
E:\LastFMCollector>python lastfm.py --resumen hayman3030
============================================================
Last.FM Collector Full Script
============================================================
[Inicio] 2025-06-17 20:01:36
Obteniendo información del usuario 'hayman3030' ...

RESUMEN DE ESTADÍSTICAS:
------------------------------
 + ARTISTAS  =======> 443
 + DISCOS    =======> 1.149
 + CANCIONES =======> 10.343
 + FAVORITAS =======> 165
 + SCROBBLES =======> 38.412

Consulta completada en 0.88 segundos.
```
## 2. TODOS LOS LISTADOS (SIN OPCIONES)
### python lastfm.py usuario

Guarda los registros del usuario en cuatro listados según el tipo de dato. Listados ubicados en la ruta listados/{usuario} en formato de texto (.txt) y csv.

| CLASIFICACIÓN | LISTADO | DATOS |
| ------ | ------ | ------ |
| ARTISTAS | lastfm_{usuario}_artistas | Puesto, artista, scrobbles |
| DISCOS | lastfm_{usuario}_discos | Puesto, disco, artista, scrobbles |
| CANCIONES | lastfm_{usuario}_canciones | Puesto, canción, artista, scrobbles |
| SCROBBLES | lastfm_{usuario}_scrobbles | Fecha-hora, canción, disco, artista, ID |

```
E:\LastFMCollector>python lastfm.py hayman3030
============================================================
Last.FM Collector Full Script
============================================================
[Inicio] 2025-06-17 20:16:04
No se especificaron opciones. Extrayendo todos los datos...

Comprobando existencia del usuario hayman3030...
Usuario verificado ✓

==================== ARTISTAS ====================
Obteniendo artistas escuchados por hayman3030...
Total de artistas a procesar: 443 en 3 páginas
Procesando página 1/3 (33.3%)

==================== CANCIONES ===================
Obteniendo canciones escuchadas por hayman3030...
Total de canciones a procesar: 10.343 en 52 páginas
Procesando página 1/52 (1.9%)
Procesando página 10/52 (19.2%)
Procesando página 20/52 (38.5%)
Procesando página 30/52 (57.7%)
Procesando página 40/52 (76.9%)
Procesando página 50/52 (96.2%)

===================== DISCOS =====================
Obteniendo discos escuchados por hayman3030...
Total de discos a procesar: 1.149 en 6 páginas
Procesando página 1/6 (16.7%)

==================== SCROBBLES ====================
Obteniendo historial de scrobbles de hayman3030...
Total de scrobbles a procesar: 38.412 en 193 páginas
Procesando página 1/193 (0.5%)
Procesando página 10/193 (5.2%)
Procesando página 20/193 (10.4%)
Procesando página 30/193 (15.5%)
Procesando página 40/193 (20.7%)
Procesando página 50/193 (25.9%)
Procesando página 60/193 (31.1%)
Procesando página 70/193 (36.3%)
Procesando página 80/193 (41.5%)
Procesando página 90/193 (46.6%)
Procesando página 100/193 (51.8%)
Procesando página 110/193 (57.0%)
Procesando página 120/193 (62.2%)
Procesando página 130/193 (67.4%)
Procesando página 140/193 (72.5%)
Procesando página 150/193 (77.7%)
Procesando página 160/193 (82.9%)
Procesando página 170/193 (88.1%)
Procesando página 180/193 (93.3%)
Procesando página 190/193 (98.4%)

============================================================
RESUMEN FINAL
============================================================
-> Artistas registrados: 443
   TXT: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_artistas.txt
   CSV: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_artistas.csv

-> Canciones registrados: 10.343
   TXT: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_canciones.txt
   CSV: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_canciones.csv

-> Discos registrados: 1.149
   TXT: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_discos.txt
   CSV: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_discos.csv

-> Scrobbles registrados: 38.412
   TXT: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_scrobbles.txt
   CSV: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_scrobbles.csv

[Fin] 2025-06-17 20:21:09
Tiempo total de ejecución: 5 minutos y 5 segundos
```

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/todo.png)

## 3. ARTISTAS
### python lastfm.py --artistas usuario

Artistas ordenados de mayor a menor nº de scrobbles: reproducciones canciones del artista.

```
E:\LastFMCollector>python lastfm.py --artistas hayman3030
============================================================
Last.FM Collector Full Script
============================================================
[Inicio] 2025-06-17 20:26:44

Comprobando existencia del usuario hayman3030...
Usuario verificado ✓

==================== ARTISTAS ====================
Obteniendo artistas escuchados por hayman3030...
Total de artistas a procesar: 443 en 3 páginas
Procesando página 1/3 (33.3%)

============================================================
RESUMEN FINAL
============================================================
-> Artistas registrados: 443
   TXT: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_artistas.txt
   CSV: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_artistas.csv

[Fin] 2025-06-17 20:26:48
Tiempo total de ejecución: 4 segundos
```

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/artistas.png)

## 4. DISCOS
### python lastfm.py --discos usuario

Discos ordenados de mayor a menor nº de scrobbles: reproducciones canciones de cada disco. 

```
E:\LastFMCollector>python lastfm.py --discos hayman3030
============================================================
Last.FM Collector Full Script
============================================================
[Inicio] 2025-06-17 20:29:11

Comprobando existencia del usuario hayman3030...
Usuario verificado ✓

===================== DISCOS =====================
Obteniendo discos escuchados por hayman3030...
Total de discos a procesar: 1.149 en 6 páginas
Procesando página 1/6 (16.7%)

============================================================
RESUMEN FINAL
============================================================
-> Discos registrados: 1.149
   TXT: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_discos.txt
   CSV: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_discos.csv

[Fin] 2025-06-17 20:29:19
Tiempo total de ejecución: 7 segundos
```

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/discos.png)

## 5. CANCIONES
### python lastfm.py --canciones usuario

Canciones ordenadas de mayor a menor nº de scrobbles (reproducciones de cada canción).

```
E:\LastFMCollector>python lastfm.py --canciones hayman3030
============================================================
Last.FM Collector Full Script
============================================================
[Inicio] 2025-06-17 20:32:03

Comprobando existencia del usuario hayman3030...
Usuario verificado ✓

==================== CANCIONES ===================
Obteniendo canciones escuchadas por hayman3030...
Total de canciones a procesar: 10.343 en 52 páginas
Procesando página 1/52 (1.9%)
Procesando página 10/52 (19.2%)
Procesando página 20/52 (38.5%)
Procesando página 30/52 (57.7%)
Procesando página 40/52 (76.9%)
Procesando página 50/52 (96.2%)

============================================================
RESUMEN FINAL
============================================================
-> Canciones registrados: 10.343
   TXT: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_canciones.txt
   CSV: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_canciones.csv

[Fin] 2025-06-17 20:33:11
Tiempo total de ejecución: 1 minutos y 7 segundos
```

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/canciones.png)

## 6. SCROBBLES
### python lastfm.py --scrobbles usuario

Todos los scrobbles (reproducciones) por orden descendente (fecha-hora).

```
E:\LastFMCollector>python lastfm.py --scrobbles hayman3030
============================================================
Last.FM Collector Full Script
============================================================
[Inicio] 2025-06-17 20:36:43

Comprobando existencia del usuario hayman3030...
Usuario verificado ✓

==================== SCROBBLES ====================
Obteniendo historial de scrobbles de hayman3030...
Total de scrobbles a procesar: 38.412 en 193 páginas
Procesando página 1/193 (0.5%)
Procesando página 10/193 (5.2%)
Procesando página 20/193 (10.4%)
Procesando página 30/193 (15.5%)
Procesando página 40/193 (20.7%)
Procesando página 50/193 (25.9%)
Procesando página 60/193 (31.1%)
Procesando página 70/193 (36.3%)
Procesando página 80/193 (41.5%)
Procesando página 90/193 (46.6%)
Procesando página 100/193 (51.8%)
Procesando página 110/193 (57.0%)
Procesando página 120/193 (62.2%)
Procesando página 130/193 (67.4%)
Procesando página 140/193 (72.5%)
Procesando página 150/193 (77.7%)
Procesando página 160/193 (82.9%)
Procesando página 170/193 (88.1%)
Procesando página 180/193 (93.3%)
Procesando página 190/193 (98.4%)

============================================================
RESUMEN FINAL
============================================================
-> Scrobbles registrados: 38.412
   TXT: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_scrobbles.txt
   CSV: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_scrobbles.csv

[Fin] 2025-06-17 20:41:18
Tiempo total de ejecución: 4 minutos y 34 segundos
``` 

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/scrobbles.png)

## 7. COMBINAR OPCIONES
### python lastfm.py --opción --opción usuario
```
E:\LastFMCollector>python lastfm.py --artistas --discos hayman3030
============================================================
Last.FM Collector Full Script
============================================================
[Inicio] 2025-06-18 00:27:15

Comprobando existencia del usuario hayman3030...
Usuario verificado ✓

==================== ARTISTAS ====================
Obteniendo artistas escuchados por hayman3030...
Total de artistas a procesar: 443 en 3 páginas
Procesando página 1/3 (33.3%)

===================== DISCOS =====================
Obteniendo discos escuchados por hayman3030...
Total de discos a procesar: 1.149 en 6 páginas
Procesando página 1/6 (16.7%)

============================================================
RESUMEN FINAL
============================================================
-> Artistas registrados: 443
   TXT: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_artistas.txt
   CSV: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_artistas.csv

-> Discos registrados: 1.149
   TXT: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_discos.txt
   CSV: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_discos.csv

[Fin] 2025-06-18 00:27:22
Tiempo total de ejecución: 6 segundos
```

## 8. BASES DE DATOS

Script lastfm_db.py exportar los resultados a una Base de Datos MySQL o PostgreSQL en lugar de guardarlos en archivos externos.

### SINTAXIS: python lastfm_db --help
```
E:\LastFMCollector>python lastfm_db.py --help
============================================================
Last.FM Collector BBDD Script
============================================================
[Inicio] 2025-06-22 14:12:39
usage: lastfm_db.py [-h] usuario motor ip puerto usuario_bd password

Extrae todos los datos de Last.fm e inserta en una base de datos SQL

positional arguments:
  usuario     Nombre de usuario de Last.fm
  motor       Motor de BBDD: mysql o postgresql
  ip          IP o hostname del servidor BBDD
  puerto      Puerto del servidor BBDD (ej: 3306 para MySQL, 5432 para PostgreSQL)
  usuario_bd  Usuario para la BBDD
  password    Password para la BBDD

options:
  -h, --help  show this help message and exit
```

### MYSQL

EJECUCIÓN:

```
E:\LastFMCollector>python lastfm_db.py hayman3030 mysql 192.168.1.40 3306 david *****
============================================================
Last.FM Collector BBDD Script
============================================================
[Inicio] 2025-06-22 14:26:25

Verificando usuario 'hayman3030' en Last.fm...
✔ Usuario encontrado

Verificando y creando base de datos si es necesario...
✔ Base de datos 'lastfm' verificada/creada en MySQL

Conectando a la base de datos 'lastfm' (mysql)...
✔ Conexión a la base de datos exitosa

============================================================
INICIANDO EXTRACCIÓN DE DATOS
============================================================

--- Procesando ARTISTAS ---
✔ Tabla 'artistas' creada/verificada
Total de artistas: 443 en 3 páginas
Procesando: 100.0% (3/3) - Insertados: 443
✔ Completado: 443 registros insertados en la tabla 'artistas'

--- Procesando DISCOS ---
✔ Tabla 'discos' creada/verificada
Total de discos: 1.149 en 6 páginas
Procesando: 100.0% (6/6) - Insertados: 1.149
✔ Completado: 1.149 registros insertados en la tabla 'discos'

--- Procesando CANCIONES ---
✔ Tabla 'canciones' creada/verificada
Total de canciones: 10.351 en 52 páginas
Procesando: 100.0% (52/52) - Insertados: 10.351
✔ Completado: 10.351 registros insertados en la tabla 'canciones'

--- Procesando SCROBBLES ---
✔ Tabla 'scrobbles' creada/verificada
Total de scrobbles: 38.432 en 193 páginas
Procesando: 100.0% (193/193) - Insertados: 38.432
✔ Completado: 38.432 registros insertados en la tabla 'scrobbles'

============================================================
RESUMEN FINAL
============================================================
Usuario: hayman3030
Total registros insertados: 50.375
Duración: 0:04:14
[Fin] 2025-06-22 14:30:39
============================================================
```

RESULTADOS:

```
bash-5.1# mysql -h 192.168.1.40 -u david -p
Enter password:
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 11
Server version: 8.0.42 MySQL Community Server - GPL

Copyright (c) 2000, 2025, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> use lastfm
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
mysql> show tables;
+------------------+
| Tables_in_lastfm |
+------------------+
| artistas         |
| canciones        |
| discos           |
| scrobbles        |
+------------------+
4 rows in set (0.00 sec)

mysql> select * from artistas limit 5;
+--------+-------------+-----------+------------+
| puesto | artista     | scrobbles | usuario    |
+--------+-------------+-----------+------------+
|      1 | Blur        |      2242 | hayman3030 |
|      2 | Lou Reed    |      1205 | hayman3030 |
|      3 | David Bowie |      1168 | hayman3030 |
|      4 | The Beatles |      1103 | hayman3030 |
|      5 | The Doors   |      1029 | hayman3030 |
+--------+-------------+-----------+------------+
5 rows in set (0.00 sec)

mysql> select * from canciones limit 5;
+--------+-------------------+---------------+-----------+------------+
| puesto | cancion           | artista       | scrobbles | usuario    |
+--------+-------------------+---------------+-----------+------------+
|      1 | Coney Island Baby | Lou Reed      |        77 | hayman3030 |
|      2 | City Lights       | Lou Reed      |        70 | hayman3030 |
|      3 | Oh Darling        | Supertramp    |        69 | hayman3030 |
|      4 | Beetlebum         | Blur          |        67 | hayman3030 |
|      5 | That's Life       | Frank Sinatra |        65 | hayman3030 |
+--------+-------------------+---------------+-----------+------------+
5 rows in set (0.00 sec)

mysql> select * from discos limit 5;
+--------+----------------------------------+---------------+-----------+------------+
| puesto | disco                            | artista       | scrobbles | usuario    |
+--------+----------------------------------+---------------+-----------+------------+
|      1 | Parklife                         | Blur          |       422 | hayman3030 |
|      2 | My Way the Best of Frank Sinatra | Frank Sinatra |       353 | hayman3030 |
|      3 | The Doors                        | The Doors     |       341 | hayman3030 |
|      4 | The Boss                         | Diana Ross    |       319 | hayman3030 |
|      5 | Breakfast in America             | Supertramp    |       303 | hayman3030 |
+--------+----------------------------------+---------------+-----------+------------+
5 rows in set (0.00 sec)

mysql> select count(*) from scrobbles;
+----------+
| count(*) |
+----------+
|    38432 |
+----------+
```

### POSTGRESQL

EJECUCIÓN

```
E:\LastFMCollector>python lastfm_db.py hayman3030 postgresql 192.168.1.40 5432 david *****
============================================================
Last.FM Collector BBDD Script
============================================================
[Inicio] 2025-06-22 14:38:58

Verificando usuario 'hayman3030' en Last.fm...
✔ Usuario encontrado

Verificando y creando base de datos si es necesario...
✔ Base de datos 'lastfm' creada en PostgreSQL

Conectando a la base de datos 'lastfm' (postgresql)...
✔ Conexión a la base de datos exitosa

============================================================
INICIANDO EXTRACCIÓN DE DATOS
============================================================

--- Procesando ARTISTAS ---
✔ Tabla 'artistas' creada/verificada
Total de artistas: 443 en 3 páginas
Procesando: 100.0% (3/3) - Insertados: 443
✔ Completado: 443 registros insertados en la tabla 'artistas'

--- Procesando DISCOS ---
✔ Tabla 'discos' creada/verificada
Total de discos: 1.149 en 6 páginas
Procesando: 100.0% (6/6) - Insertados: 1.149
✔ Completado: 1.149 registros insertados en la tabla 'discos'

--- Procesando CANCIONES ---
✔ Tabla 'canciones' creada/verificada
Total de canciones: 10.351 en 52 páginas
Procesando: 100.0% (52/52) - Insertados: 10.351
✔ Completado: 10.351 registros insertados en la tabla 'canciones'

--- Procesando SCROBBLES ---
✔ Tabla 'scrobbles' creada/verificada
Total de scrobbles: 38.432 en 193 páginas
Procesando: 100.0% (193/193) - Insertados: 38.432
✔ Completado: 38.432 registros insertados en la tabla 'scrobbles'

============================================================
RESUMEN FINAL
============================================================
Usuario: hayman3030
Total registros insertados: 50.375
Duración: 0:04:21
[Fin] 2025-06-22 14:43:19
============================================================
```

RESULTADOS

```
root@599e54234e13:/# psql -h 192.168.1.40 -U david -d lastfm
Password for user david:
psql (17.5 (Debian 17.5-1.pgdg120+1))
Type "help" for help.

lastfm=# \dt
         List of relations
 Schema |   Name    | Type  | Owner
--------+-----------+-------+-------
 public | artistas  | table | david
 public | canciones | table | david
 public | discos    | table | david
 public | scrobbles | table | david
(4 rows)

lastfm=# select * from artistas limit 5;
 puesto |   artista   | scrobbles |  usuario
--------+-------------+-----------+------------
      1 | Blur        |      2242 | hayman3030
      2 | Lou Reed    |      1205 | hayman3030
      3 | David Bowie |      1168 | hayman3030
      4 | The Beatles |      1103 | hayman3030
      5 | The Doors   |      1029 | hayman3030
(5 rows)

lastfm=# select * from canciones limit 5;
 puesto |      cancion      |    artista    | scrobbles |  usuario
--------+-------------------+---------------+-----------+------------
      1 | Coney Island Baby | Lou Reed      |        77 | hayman3030
      2 | City Lights       | Lou Reed      |        70 | hayman3030
      3 | Oh Darling        | Supertramp    |        69 | hayman3030
      4 | Beetlebum         | Blur          |        67 | hayman3030
      5 | That's Life       | Frank Sinatra |        65 | hayman3030
(5 rows)

lastfm=# select * from discos limit 5;
 puesto |              disco               |    artista    | scrobbles |  usuario
--------+----------------------------------+---------------+-----------+------------
      1 | Parklife                         | Blur          |       422 | hayman3030
      2 | My Way the Best of Frank Sinatra | Frank Sinatra |       353 | hayman3030
      3 | The Doors                        | The Doors     |       341 | hayman3030
      4 | The Boss                         | Diana Ross    |       319 | hayman3030
      5 | Breakfast in America             | Supertramp    |       303 | hayman3030
(5 rows)

lastfm=# select count(*) from scrobbles;
 count
-------
 38432
(1 row)

```

## 9. CONTROL DE ERRORES

### Sin usuario:
```
E:\LastFMCollector>python lastfm.py
============================================================
Last.FM Collector Full Script
============================================================
[Inicio] 2025-06-18 00:28:45
usage: lastfm.py [-h] [--resumen] [--artistas] [--canciones] [--discos] [--scrobbles] usuario
lastfm.py: error: the following arguments are required: usuario
```

### Sin clave API:
```
E:\LastFMCollector>python lastfm.py hayman3030
============================================================
Last.FM Collector Full Script
============================================================
[Inicio] 2025-06-18 00:30:29
Error: Debes introducir tu clave API de Last.fm en la línea 12 del script.
Visita https://www.last.fm/api/account/create para obtener una clave API.
```

### Usuario no existe:

```
E:\LastFMCollector>python lastfm.py ÑÑÑÑÑÑÑÑÑ
============================================================
Last.FM Collector Full Script
============================================================
[Inicio] 2025-06-18 00:32:01
No se especificaron opciones. Extrayendo todos los datos...

Comprobando existencia del usuario ÑÑÑÑÑÑÑÑÑ...
Error: El usuario 'ÑÑÑÑÑÑÑÑÑ' no existe en Last.fm
```

### Problema de conexión durante la descarga:

```
Procesando página 120/193 (62.2%)
Procesando página 130/193 (67.4%)
Error en solicitud (reintento 1/3): 500 Server Error: Internal Server Error for url: http://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user=hayman3030&api_key=4a9dea0c516c3544074b4a76fcb791a4&format=json&limit=200&page=140&extended=0
Esperando 1 segundos antes de reintentar...
Procesando página 140/193 (72.5%)
Error en solicitud (reintento 1/3): 500 Server Error: Internal Server Error for url: http://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user=hayman3030&api_key=4a9dea0c516c3544074b4a76fcb791a4&format=json&limit=200&page=145&extended=0
Esperando 1 segundos antes de reintentar...
Procesando página 150/193 (77.7%)
Procesando página 160/193 (82.9%)
```



