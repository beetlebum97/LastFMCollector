import sys
import requests
import json
import datetime
import time
import os
import argparse
import concurrent.futures
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, text
from sqlalchemy.exc import SQLAlchemyError

API_KEY = "Introduce tu clave"
API_URL = "http://ws.audioscrobbler.com/2.0/"

def mostrar_encabezado():
    inicio = datetime.datetime.now()
    print("=" * 60)
    print("Last.FM Collector BBDD Script")
    print("=" * 60)
    print("[Inicio]", inicio.strftime("%Y-%m-%d %H:%M:%S"))
    return inicio

def validar_api_key():
    if API_KEY == "Introduce tu clave" or not API_KEY.strip():
        print("Error: Debes introducir tu clave API de Last.fm en la línea 12 del script.")
        sys.exit(1)

def configurar_argumentos():
    parser = argparse.ArgumentParser(description='Extrae todos los datos de Last.fm e inserta en una base de datos SQL')

    parser.add_argument('usuario', help='Nombre de usuario de Last.fm')
    parser.add_argument('motor', help='Motor de BBDD: mysql o postgresql')
    parser.add_argument('ip', help='IP o hostname del servidor BBDD')
    parser.add_argument('puerto', help='Puerto del servidor BBDD (ej: 3306 para MySQL, 5432 para PostgreSQL)')
    parser.add_argument('usuario_bd', help='Usuario para la BBDD')
    parser.add_argument('password', help='Password para la BBDD')

    return parser.parse_args()

def formato_numero(numero):
    return f"{numero:,}".replace(",", ".")

def usuario_existe(usuario):
    params = {
        "method": "user.getInfo",
        "user": usuario,
        "api_key": API_KEY,
        "format": "json"
    }
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        data = json.loads(response.text)
        return "user" in data and "name" in data["user"]
    except Exception as e:
        print(f"Error verificando usuario: {e}")
        return False

def hacer_solicitud_con_reintentos(url, params, max_intentos=3, retraso_base=2):
    for intento in range(max_intentos):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = json.loads(response.text)
            if "error" in data:
                raise ValueError(f"Error de Last.fm: {data.get('message', 'Error desconocido')}")
            return data
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"Intento {intento + 1} fallido: {e}")
            if intento < max_intentos - 1:
                time.sleep(retraso_base ** intento)
            else:
                raise

def crear_base_datos_si_no_existe(motor, ip, puerto, usuario_bd, password):
    nombre_bd = "lastfm"
    try:
        if motor == 'mysql':
            engine = create_engine(f"mysql+pymysql://{usuario_bd}:{password}@{ip}:{puerto}")
            with engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {nombre_bd}"))
                conn.commit()  # Commit explícito
                print(f"✔ Base de datos '{nombre_bd}' verificada/creada en MySQL")
        elif motor == 'postgresql':
            raw_url = f"postgresql://{usuario_bd}:{password}@{ip}:{puerto}/postgres"
            tmp_engine = create_engine(raw_url, isolation_level="AUTOCOMMIT")
            with tmp_engine.connect() as tmp_conn:
                result = tmp_conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'lastfm'"))
                exists = result.scalar()
                if not exists:
                    tmp_conn.execute(text("CREATE DATABASE lastfm"))
                    print(f"✔ Base de datos '{nombre_bd}' creada en PostgreSQL")
                else:
                    print(f"✔ Base de datos '{nombre_bd}' ya existe en PostgreSQL")
        else:
            raise ValueError("Motor de base de datos no soportado. Usa 'mysql' o 'postgresql'.")
    except Exception as e:
        print(f"Error creando base de datos: {e}")
        sys.exit(1)

    return nombre_bd

def procesar_entidad_sql(usuario, method, entidad, columnas, parser_func, engine, metadata):
    url = API_URL
    limite = 200
    pagina = 1
    total_paginas = 1
    contador = 0
    delay = 0.25

    tabla = Table(entidad, metadata, *columnas)
    metadata.create_all(engine)
    print(f"✔ Tabla '{entidad}' creada/verificada")

    try:
        with engine.begin() as conn:  # Usar begin() para auto-commit
            while pagina <= total_paginas:
                try:
                    params = {
                        "method": method,
                        "user": usuario,
                        "api_key": API_KEY,
                        "format": "json",
                        "limit": limite,
                        "page": pagina
                    }
                    
                    response = hacer_solicitud_con_reintentos(url, params)
                    
                    if pagina == 1:
                        attr = list(response.values())[0]['@attr']
                        total_paginas = int(attr['totalPages'])
                        total_items = int(attr.get('total', 0))
                        print(f"Total de {entidad}: {formato_numero(total_items)} en {total_paginas} páginas")

                    registros = parser_func(response, usuario, contador)
                    
                    if registros:  # Solo insertar si hay registros
                        result = conn.execute(tabla.insert(), registros)
                        contador += len(registros)
                    
                    # Calcular porcentaje y mostrar progreso
                    porcentaje = (pagina / total_paginas) * 100
                    registros_insertados = len(registros) if registros else 0
                    
                    # Mostrar progreso en la misma línea
                    print(f"\rProcesando: {porcentaje:.1f}% ({pagina}/{total_paginas}) - Insertados: {formato_numero(contador)}", end="", flush=True)
                    
                    pagina += 1
                    if pagina <= total_paginas:
                        time.sleep(delay)
                        
                except Exception as e:
                    print(f"\n✗ Error en página {pagina}: {e}")
                    break
                    
    except Exception as e:
        print(f"\n✗ Error procesando {entidad}: {e}")
        return 0

    print(f"\n✔ Completado: {formato_numero(contador)} registros insertados en la tabla '{entidad}'")
    return contador

def parse_artistas(response, usuario, _):
    try:
        return [{
            'puesto': int(item['@attr']['rank']),
            'artista': item['name'][:255],  # Truncar para evitar errores
            'scrobbles': int(item['playcount']),
            'usuario': usuario[:100]
        } for item in response['topartists']['artist']]
    except KeyError as e:
        print(f"Error parseando artistas: {e}")
        return []

def parse_discos(response, usuario, _):
    try:
        return [{
            'puesto': int(item['@attr']['rank']),
            'disco': item['name'][:255],
            'artista': item['artist']['name'][:255],
            'scrobbles': int(item['playcount']),
            'usuario': usuario[:100]
        } for item in response['topalbums']['album']]
    except KeyError as e:
        print(f"Error parseando discos: {e}")
        return []

def parse_canciones(response, usuario, _):
    try:
        return [{
            'puesto': int(item['@attr']['rank']),
            'cancion': item['name'][:255],
            'artista': item['artist']['name'][:255],
            'scrobbles': int(item['playcount']),
            'usuario': usuario[:100]
        } for item in response['toptracks']['track']]
    except KeyError as e:
        print(f"Error parseando canciones: {e}")
        return []

def parse_scrobbles(response, usuario, offset):
    registros = []
    try:
        for i, item in enumerate(response['recenttracks']['track']):
            # Saltar tracks que se están reproduciendo ahora
            if '@attr' in item and item['@attr'].get('nowplaying') == 'true':
                continue
                
            fecha = item.get('date', {}).get('#text', 'Desconocido')
            cancion = item['name'][:255]
            disco = item['album']['#text'][:255] if item['album']['#text'] else 'Desconocido'
            artista = item['artist']['#text'][:255]
            
            registros.append({
                'fecha': fecha,
                'cancion': cancion,
                'disco': disco,
                'artista': artista,
                'usuario': usuario[:100],
                'id_scrobble': offset + i + 1
            })
    except KeyError as e:
        print(f"Error parseando scrobbles: {e}")
    
    return registros

def main():
    inicio = mostrar_encabezado()
    args = configurar_argumentos()
    validar_api_key()

    print(f"\nVerificando usuario '{args.usuario}' en Last.fm...")
    if not usuario_existe(args.usuario):
        print(f"Error: El usuario '{args.usuario}' no existe en Last.fm")
        sys.exit(1)
    print("✔ Usuario encontrado")

    print(f"\nVerificando y creando base de datos si es necesario...")
    nombre_bd = crear_base_datos_si_no_existe(args.motor, args.ip, args.puerto, args.usuario_bd, args.password)

    print(f"\nConectando a la base de datos '{nombre_bd}' ({args.motor})...")
    try:
        if args.motor == 'mysql':
            engine = create_engine(f"mysql+pymysql://{args.usuario_bd}:{args.password}@{args.ip}:{args.puerto}/{nombre_bd}")
        elif args.motor == 'postgresql':
            engine = create_engine(f"postgresql://{args.usuario_bd}:{args.password}@{args.ip}:{args.puerto}/{nombre_bd}")
        else:
            raise ValueError("Motor de base de datos no soportado. Usa 'mysql' o 'postgresql'.")
        
        # Probar la conexión
        with engine.connect() as test_conn:
            test_conn.execute(text("SELECT 1"))
        print("✔ Conexión a la base de datos exitosa")
        
    except SQLAlchemyError as e:
        print(f"✗ Error de conexión a la base de datos: {str(e)}")
        sys.exit(1)

    metadata = MetaData()
    total_registros = 0

    print(f"\n{'='*60}")
    print("INICIANDO EXTRACCIÓN DE DATOS")
    print(f"{'='*60}")

    # Procesar cada entidad
    entidades = [
        (args.usuario, "user.getTopArtists", "artistas", [
            Column('puesto', Integer), 
            Column('artista', String(255)), 
            Column('scrobbles', Integer), 
            Column('usuario', String(100))
        ], parse_artistas),
        
        (args.usuario, "user.getTopAlbums", "discos", [
            Column('puesto', Integer), 
            Column('disco', String(255)), 
            Column('artista', String(255)), 
            Column('scrobbles', Integer), 
            Column('usuario', String(100))
        ], parse_discos),
        
        (args.usuario, "user.getTopTracks", "canciones", [
            Column('puesto', Integer), 
            Column('cancion', String(255)), 
            Column('artista', String(255)), 
            Column('scrobbles', Integer), 
            Column('usuario', String(100))
        ], parse_canciones),
        
        (args.usuario, "user.getRecentTracks", "scrobbles", [
            Column('fecha', String(64)), 
            Column('cancion', String(255)), 
            Column('disco', String(255)), 
            Column('artista', String(255)),
            Column('usuario', String(100)), 
            Column('id_scrobble', Integer)
        ], parse_scrobbles)
    ]

    for usuario, method, tabla, columnas, parser in entidades:
        print(f"\n--- Procesando {tabla.upper()} ---")
        registros = procesar_entidad_sql(usuario, method, tabla, columnas, parser, engine, metadata)
        total_registros += registros

    fin = datetime.datetime.now()
    duracion = fin - inicio
    
    # Formatear duración sin microsegundos
    duracion_redondeada = str(duracion).split('.')[0]
    
    print(f"\n{'='*60}")
    print("RESUMEN FINAL")
    print(f"{'='*60}")
    print(f"Usuario: {args.usuario}")
    print(f"Total registros insertados: {formato_numero(total_registros)}")
    print(f"Duración: {duracion_redondeada}")
    print(f"[Fin] {fin.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
