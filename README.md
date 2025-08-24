# :guitar: LastFMCollector  :guitar:
LastFMCollector es un conjunto de herramientas en Python para extraer y analizar tus datos musicales de **Last.fm**, red social y plataforma de recomendación musical que rastrea tus hábitos de escucha a lo largo del tiempo mediante "scrobbles" (reproducciones registradas).

Este proyecto permite:

📊 Obtener resúmenes estadísticos de tu actividad en Last.fm.

📥 Exportar tus datos en formatos TXT y CSV (artistas, canciones, discos y scrobbles).

🗄️ Almacenar toda tu información en una base de datos MySQL o PostgreSQL para análisis avanzados.

🔸 **[ SCRIPTS API ]**

**lastfm.py**: Descarga listados de artistas, canciones, discos e historial de scrobbles en formato de texto y CSV.

**lastfm_db.py**: Inserta los mismos datos directamente en una base de datos SQL.

🔸 **[ REQUISITOS ]**

1º) Obten una clave API de Last.fm. Solicítala gratuitamente en https://www.last.fm/api/account/create. Manual: https://www.last.fm/es/api).

2º) Modifica la línea 12 de los scripts con tu clave API ```API_KEY = "Introduce tu clave" ```

3º) Instala Python 3 y los módulos requests (para lastfm.py) y sqlalchemy, pymysql, psycopg2-binary (para lastfm_db.py).

🔸 **[ DESPLIEGUE CLOUD ]** 

Mediante **lastfm_azure.sh** puedes realizar en la Cloud Shell de Azure un despliegue IaaS automatizado que incluye:

- Terraform para infraestructura.
- Ansible para configuración.
- Docker para contenedores.

Ver [documentación de Azure](./azure/README_AZURE.md) para detalles específicos.

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
[Inicio] 2025-08-22 16:03:30
Obteniendo información del usuario 'hayman3030' ...

RESUMEN DE ESTADÍSTICAS:
------------------------------
 + ARTISTAS  =======> 443
 + DISCOS    =======> 1.161
 + CANCIONES =======> 10.473
 + FAVORITAS =======> 170
 + SCROBBLES =======> 39.117

Consulta completada en 0.78 segundos.
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
[Inicio] 2025-08-22 16:04:42
No se especificaron opciones. Extrayendo todos los datos...

Comprobando existencia del usuario hayman3030...
Usuario verificado ✓

==================== ARTISTAS ====================
Obteniendo artistas escuchados por hayman3030...
Total de artistas a procesar: 443 en 3 páginas
Procesando página 1/3 (33.3%)

==================== CANCIONES ===================
Obteniendo canciones escuchadas por hayman3030...
Total de canciones a procesar: 10.473 en 53 páginas
Procesando página 1/53 (1.9%)
Procesando página 10/53 (18.9%)
Procesando página 20/53 (37.7%)
Procesando página 30/53 (56.6%)
Procesando página 40/53 (75.5%)
Procesando página 50/53 (94.3%)

===================== DISCOS =====================
Obteniendo discos escuchados por hayman3030...
Total de discos a procesar: 1.161 en 6 páginas
Procesando página 1/6 (16.7%)

==================== SCROBBLES ====================
Obteniendo historial de scrobbles de hayman3030...
Total de scrobbles a procesar: 39.117 en 196 páginas
Procesando página 1/196 (0.5%)
Procesando página 10/196 (5.1%)
Procesando página 20/196 (10.2%)
Procesando página 30/196 (15.3%)
Procesando página 40/196 (20.4%)
Procesando página 50/196 (25.5%)
Procesando página 60/196 (30.6%)
Procesando página 70/196 (35.7%)
Procesando página 80/196 (40.8%)
Procesando página 90/196 (45.9%)
Procesando página 100/196 (51.0%)
Procesando página 110/196 (56.1%)
Procesando página 120/196 (61.2%)
Procesando página 130/196 (66.3%)
Procesando página 140/196 (71.4%)
Procesando página 150/196 (76.5%)
Procesando página 160/196 (81.6%)
Procesando página 170/196 (86.7%)
Procesando página 180/196 (91.8%)
Procesando página 190/196 (96.9%)

============================================================
RESUMEN FINAL
============================================================
-> Artistas registrados: 443
   TXT: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_artistas.txt
   CSV: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_artistas.csv

-> Canciones registrados: 10.473
   TXT: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_canciones.txt
   CSV: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_canciones.csv

-> Discos registrados: 1.161
   TXT: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_discos.txt
   CSV: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_discos.csv

-> Scrobbles registrados: 39.117
   TXT: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_scrobbles.txt
   CSV: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_scrobbles.csv

[Fin] 2025-08-22 16:10:55
Tiempo total de ejecución: 6 minutos y 12 segundos
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
[Inicio] 2025-08-22 16:14:32

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

[Fin] 2025-08-22 16:14:35
Tiempo total de ejecución: 2 segundos
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
[Inicio] 2025-08-22 16:16:31

Comprobando existencia del usuario hayman3030...
Usuario verificado ✓

===================== DISCOS =====================
Obteniendo discos escuchados por hayman3030...
Total de discos a procesar: 1.161 en 6 páginas
Procesando página 1/6 (16.7%)

============================================================
RESUMEN FINAL
============================================================
-> Discos registrados: 1.161
   TXT: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_discos.txt
   CSV: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_discos.csv

[Fin] 2025-08-22 16:16:37
Tiempo total de ejecución: 6 segundos
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
[Inicio] 2025-08-22 16:19:28

Comprobando existencia del usuario hayman3030...
Usuario verificado ✓

==================== CANCIONES ===================
Obteniendo canciones escuchadas por hayman3030...
Total de canciones a procesar: 10.473 en 53 páginas
Procesando página 1/53 (1.9%)
Procesando página 10/53 (18.9%)
Procesando página 20/53 (37.7%)
Procesando página 30/53 (56.6%)
Procesando página 40/53 (75.5%)
Procesando página 50/53 (94.3%)

============================================================
RESUMEN FINAL
============================================================
-> Canciones registrados: 10.473
   TXT: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_canciones.txt
   CSV: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_canciones.csv

[Fin] 2025-08-22 16:20:38
Tiempo total de ejecución: 1 minutos y 9 segundos
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
[Inicio] 2025-08-22 16:23:54

Comprobando existencia del usuario hayman3030...
Usuario verificado ✓

==================== SCROBBLES ====================
Obteniendo historial de scrobbles de hayman3030...
Total de scrobbles a procesar: 39.117 en 196 páginas
Procesando página 1/196 (0.5%)
Procesando página 10/196 (5.1%)
Procesando página 20/196 (10.2%)
Procesando página 30/196 (15.3%)
Procesando página 40/196 (20.4%)
Procesando página 50/196 (25.5%)
Procesando página 60/196 (30.6%)
Procesando página 70/196 (35.7%)
Procesando página 80/196 (40.8%)
Procesando página 90/196 (45.9%)
Procesando página 100/196 (51.0%)
Procesando página 110/196 (56.1%)
Procesando página 120/196 (61.2%)
Procesando página 130/196 (66.3%)
Procesando página 140/196 (71.4%)
Procesando página 150/196 (76.5%)
Procesando página 160/196 (81.6%)
Procesando página 170/196 (86.7%)
Procesando página 180/196 (91.8%)
Procesando página 190/196 (96.9%)

============================================================
RESUMEN FINAL
============================================================
-> Scrobbles registrados: 39.117
   TXT: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_scrobbles.txt
   CSV: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_scrobbles.csv

[Fin] 2025-08-22 16:29:33
Tiempo total de ejecución: 5 minutos y 38 segundos
``` 

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/last_fm/main/capturas/scrobbles.png)

## 7. COMBINAR OPCIONES
### python lastfm.py --opción --opción usuario
```
E:\LastFMCollector>python lastfm.py --artistas --discos hayman3030
============================================================
Last.FM Collector Full Script
============================================================
[Inicio] 2025-08-22 16:32:28

Comprobando existencia del usuario hayman3030...
Usuario verificado ✓

==================== ARTISTAS ====================
Obteniendo artistas escuchados por hayman3030...
Total de artistas a procesar: 443 en 3 páginas
Procesando página 1/3 (33.3%)

===================== DISCOS =====================
Obteniendo discos escuchados por hayman3030...
Total de discos a procesar: 1.161 en 6 páginas
Procesando página 1/6 (16.7%)

============================================================
RESUMEN FINAL
============================================================
-> Artistas registrados: 443
   TXT: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_artistas.txt
   CSV: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_artistas.csv

-> Discos registrados: 1.161
   TXT: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_discos.txt
   CSV: E:\LastFMCollector/listados/hayman3030/lastfm_hayman3030_discos.csv

[Fin] 2025-08-22 16:32:35
Tiempo total de ejecución: 6 segundos
```

## 8. BASES DE DATOS

Script lastfm_db.py exportar los resultados a una Base de Datos MySQL o PostgreSQL en lugar de guardarlos en archivos externos.

### SINTAXIS: python lastfm_db.py --help
```
E:\LastFMCollector>python lastfm_db.py --help
============================================================
Last.FM Collector BBDD Script
============================================================
[Inicio] 2025-08-22 16:36:44
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
E:\LastFMCollector>python lastfm_db.py hayman3030 mysql 192.168.1.46 3306 david *****
============================================================
Last.FM Collector BBDD Script
============================================================
[Inicio] 2025-08-22 16:52:59

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
Total de discos: 1.161 en 6 páginas
Procesando: 100.0% (6/6) - Insertados: 1.161
✔ Completado: 1.161 registros insertados en la tabla 'discos'

--- Procesando CANCIONES ---
✔ Tabla 'canciones' creada/verificada
Total de canciones: 10.473 en 53 páginas
Procesando: 100.0% (53/53) - Insertados: 10.473
✔ Completado: 10.473 registros insertados en la tabla 'canciones'

--- Procesando SCROBBLES ---
✔ Tabla 'scrobbles' creada/verificada
Total de scrobbles: 39.117 en 196 páginas
Procesando: 57.7% (113/196) - Insertados: 22.600Intento 1 fallido: HTTPConnectionPool(host='ws.audioscrobbler.com', port=80): Read timed out. (read timeout=10)
Procesando: 100.0% (196/196) - Insertados: 39.117
✔ Completado: 39.117 registros insertados en la tabla 'scrobbles'

============================================================
RESUMEN FINAL
============================================================
Usuario: hayman3030
Total registros insertados: 51.194
Duración: 0:05:42
[Fin] 2025-08-22 16:58:42
============================================================
```

RESULTADOS:

```
bash-5.1# mysql -h 192.168.1.46 -u david -p
Enter password:
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 12
Server version: 8.0.43 MySQL Community Server - GPL

Copyright (c) 2000, 2025, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> use lastfm;
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
|      1 | Blur        |      2249 | hayman3030 |
|      2 | Lou Reed    |      1217 | hayman3030 |
|      3 | David Bowie |      1181 | hayman3030 |
|      4 | The Beatles |      1133 | hayman3030 |
|      5 | The Doors   |      1029 | hayman3030 |
+--------+-------------+-----------+------------+
5 rows in set (0.00 sec)

mysql> select * from canciones limit 5;
+--------+-------------------+---------------+-----------+------------+
| puesto | cancion           | artista       | scrobbles | usuario    |
+--------+-------------------+---------------+-----------+------------+
|      1 | Coney Island Baby | Lou Reed      |        77 | hayman3030 |
|      2 | Beetlebum         | Blur          |        70 | hayman3030 |
|      3 | City Lights       | Lou Reed      |        70 | hayman3030 |
|      4 | Oh Darling        | Supertramp    |        69 | hayman3030 |
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
5 rows in set (0.01 sec)

mysql> select count(*) from scrobbles;
+----------+
| count(*) |
+----------+
|    39117 |
+----------+
1 row in set (0.02 sec)
```

### POSTGRESQL

EJECUCIÓN

```
E:\LastFMCollector>python lastfm_db.py hayman3030 postgresql 192.168.1.46 5432 david *****
============================================================
Last.FM Collector BBDD Script
============================================================
[Inicio] 2025-08-22 17:07:32

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
Total de discos: 1.161 en 6 páginas
Procesando: 100.0% (6/6) - Insertados: 1.161
✔ Completado: 1.161 registros insertados en la tabla 'discos'

--- Procesando CANCIONES ---
✔ Tabla 'canciones' creada/verificada
Total de canciones: 10.473 en 53 páginas
Procesando: 100.0% (53/53) - Insertados: 10.473
✔ Completado: 10.473 registros insertados en la tabla 'canciones'

--- Procesando SCROBBLES ---
✔ Tabla 'scrobbles' creada/verificada
Total de scrobbles: 39.117 en 196 páginas
Procesando: 100.0% (196/196) - Insertados: 39.117
✔ Completado: 39.117 registros insertados en la tabla 'scrobbles'

============================================================
RESUMEN FINAL
============================================================
Usuario: hayman3030
Total registros insertados: 51.194
Duración: 0:05:34
[Fin] 2025-08-22 17:13:06
============================================================
```

RESULTADOS

```
root@2f320bf7342f:/# psql -h 192.168.1.46 -U david -d lastfm
Password for user david:
psql (17.6 (Debian 17.6-1.pgdg13+1))
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
      1 | Blur        |      2249 | hayman3030
      2 | Lou Reed    |      1217 | hayman3030
      3 | David Bowie |      1181 | hayman3030
      4 | The Beatles |      1133 | hayman3030
      5 | The Doors   |      1029 | hayman3030
(5 rows)

lastfm=# select * from canciones limit 5;
 puesto |      cancion      |    artista    | scrobbles |  usuario
--------+-------------------+---------------+-----------+------------
      1 | Coney Island Baby | Lou Reed      |        77 | hayman3030
      2 | Beetlebum         | Blur          |        70 | hayman3030
      3 | City Lights       | Lou Reed      |        70 | hayman3030
      4 | Oh Darling        | Supertramp    |        69 | hayman3030
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
 39117
(1 row)
```

## 9. CONTROL DE ERRORES

### Sin usuario:
```
E:\LastFMCollector>python lastfm.py
============================================================
Last.FM Collector Full Script
============================================================
[Inicio] 2025-08-22 17:23:28
usage: lastfm.py [-h] [--resumen] [--artistas] [--canciones] [--discos] [--scrobbles] usuario
lastfm.py: error: the following arguments are required: usuario
```

### Sin clave API:
```
E:\LastFMCollector>python lastfm.py hayman3030
============================================================
Last.FM Collector Full Script
============================================================
[Inicio] 2025-08-22 17:24:23
Error: Debes introducir tu clave API de Last.fm en la línea 12 del script.
Visita https://www.last.fm/api/account/create para obtener una clave API.
```

### Usuario no existe:

```
E:\LastFMCollector>python lastfm.py ÑÑÑÑÑÑÑÑÑ
============================================================
Last.FM Collector Full Script
============================================================
[Inicio] 2025-08-22 17:25:31
No se especificaron opciones. Extrayendo todos los datos...

Comprobando existencia del usuario ÑÑÑÑÑÑÑÑÑ...
Error: El usuario 'ÑÑÑÑÑÑÑÑÑ' no existe en Last.fm
```

### Problema de conexión durante la descarga:

```
Procesando página 120/193 (62.2%)
Procesando página 130/193 (67.4%)
Error en solicitud (reintento 1/3): 500 Server Error: Internal Server Error for url: http://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user=hayman3030&format=json&limit=200&page=140&extended=0
Esperando 1 segundos antes de reintentar...
Procesando página 140/193 (72.5%)
Error en solicitud (reintento 1/3): 500 Server Error: Internal Server Error for url: http://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user=hayman3030&format=json&limit=200&page=145&extended=0
Esperando 1 segundos antes de reintentar...
Procesando página 150/193 (77.7%)
Procesando página 160/193 (82.9%)
```








