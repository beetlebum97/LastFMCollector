import sys
import requests
import json
import datetime
import time
import os
import argparse
import concurrent.futures
import getpass
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, text
from sqlalchemy.exc import SQLAlchemyError
from colorama import init, Fore, Style
init()

API_KEY = None
API_URL = "http://ws.audioscrobbler.com/2.0/"

def mostrar_encabezado():
    """Muestra el encabezado con la hora actual"""
    inicio = datetime.datetime.now()
    print(Fore.LIGHTCYAN_EX + ">" * 60)
    print("|||| LAST.FM COLLECTOR — BBDD BACKEND ||||".center(60))
    print("<" * 60 + Style.RESET_ALL)
    print(Fore.YELLOW + "[Inicio]".ljust(10), inicio.strftime("%Y-%m-%d %H:%M:%S") + Style.RESET_ALL)
    return inicio

def solicitar_api_key():
    """Solicita la API key interactivamente con 3 intentos"""
    global API_KEY
    intentos = 3
    for intento in range(intentos):
        try:
            print(f"\nIntroduce tu API key de Last.fm (intento {intento + 1}/{intentos}):")
            api_key = getpass.getpass("API key: ").strip()
            if not api_key:
                print(Fore.LIGHTRED_EX + "✗ La API key no puede estar vacía." + Style.RESET_ALL)
                continue
            if not api_key.replace('-', '').replace('_', '').isalnum():
                print(Fore.LIGHTRED_EX + "✗ Formato inválido de API key." + Style.RESET_ALL)
                continue
            if validar_api_key_en_servidor(api_key):
                API_KEY = api_key
                print(Fore.LIGHTGREEN_EX + "✓ API key válida y verificada" + Style.RESET_ALL)
                return True
            else:
                print(Fore.LIGHTRED_EX + "✗ API key no válida o sin permisos" + Style.RESET_ALL)
        except KeyboardInterrupt:
            print("\nOperación cancelada por el usuario.")
            sys.exit(1)
        except Exception as e:
            print(Fore.LIGHTRED_EX + f"✗ Error validando API key: {e}" + Style.RESET_ALL)
    print(Fore.LIGHTRED_EX + "\n✗ Demasiados intentos fallidos. Saliendo..." + Style.RESET_ALL)
    return False

def validar_api_key_en_servidor(api_key):
    """Valida que la API key funcione correctamente con el servidor de Last.fm"""
    params = {
        "method": "chart.getTopArtists",
        "api_key": api_key,
        "format": "json",
        "limit": 1
    }
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        if response.status_code == 403:
            return False
        response.raise_for_status()
        data = response.json()
        return "error" not in data
    except:
        return False

def validar_api_key_configurada():
    """Valida que se haya configurado una API key válida"""
    if API_KEY is None:
        if not solicitar_api_key():
            sys.exit(1)

def configurar_argumentos():
    """Configura y parsea los argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description='Extrae todos los datos de Last.fm e inserta en una base de datos SQL')
    parser.add_argument('usuario')
    parser.add_argument('motor')
    parser.add_argument('ip')
    parser.add_argument('puerto')
    parser.add_argument('usuario_bd')
    parser.add_argument('password')
    return parser.parse_args()
    
def formato_numero(numero):
    return f"{numero:,}".replace(",", ".")

def usuario_existe(usuario):
    """Verifica si el usuario existe en Last.fm"""
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
        print(Fore.LIGHTRED_EX + f"✗ Error verificando usuario: {e}" + Style.RESET_ALL)
        return False

def hacer_solicitud_con_reintentos(url, params, max_intentos=5, retraso_base=3):
    """Realiza una solicitud HTTP con reintentos en caso de error, ocultando URL y API key"""
    for intento in range(max_intentos):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = json.loads(response.text)
            if "error" in data:
                raise ValueError(f"Error de Last.fm: {data.get('message', 'Error desconocido')}")
            return data

        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            if isinstance(e, requests.exceptions.HTTPError) and e.response is not None:
                codigo = e.response.status_code
                mensaje = f"{codigo} Server Error"
            else:
                mensaje = str(e) or type(e).__name__

            if intento < max_intentos - 1:
                tiempo_espera = retraso_base ** intento
                # Silenciar reintentos intermedios para evitar ruido visual
                time.sleep(tiempo_espera)
            else:
                # Solo mostrar si se agotaron los intentos
                if "for url:" in mensaje:
                    mensaje = mensaje.split("for url:")[0].strip()
                if "500 Server Error" in mensaje:
                    mensaje = "500 Server Error: Conexión perdida con la API"
                elif "ReadTimeout" in mensaje:
                    mensaje = "Timeout: el servidor no respondió a tiempo"
                elif "ConnectionError" in mensaje:
                    mensaje = "Error de conexión: no se pudo contactar con el servidor"

                print(Fore.LIGHTRED_EX + f"\n✗ Error después de {max_intentos} intentos: {mensaje}" + Style.RESET_ALL)
                raise

        except ValueError:
            raise

    raise ValueError("Error inesperado en solicitudes HTTP")

def crear_base_datos_si_no_existe(motor, ip, puerto, usuario_bd, password):
    """Verifica o crea la base de datos 'lastfm' según el motor especificado"""
    nombre_bd = "lastfm"
    try:
        if motor == 'mysql':
            engine = create_engine(f"mysql+pymysql://{usuario_bd}:{password}@{ip}:{puerto}")
            with engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {nombre_bd}"))
                conn.commit()
                print(Fore.LIGHTGREEN_EX + f"✓ Base de datos '{nombre_bd}' verificada/creada en MySQL" + Style.RESET_ALL)
        elif motor == 'postgresql':
            raw_url = f"postgresql://{usuario_bd}:{password}@{ip}:{puerto}/postgres"
            tmp_engine = create_engine(raw_url, isolation_level="AUTOCOMMIT")
            with tmp_engine.connect() as tmp_conn:
                result = tmp_conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'lastfm'"))
                exists = result.scalar()
                if not exists:
                    tmp_conn.execute(text("CREATE DATABASE lastfm"))
                    print(Fore.LIGHTGREEN_EX + f"✓ Base de datos '{nombre_bd}' creada en PostgreSQL" + Style.RESET_ALL)
                else:
                    print(Fore.LIGHTGREEN_EX + f"✓ Base de datos '{nombre_bd}' ya existe en PostgreSQL" + Style.RESET_ALL)
        else:
            raise ValueError("Motor no soportado. Usa 'mysql' o 'postgresql'.")
    except Exception as e:
        print(Fore.LIGHTRED_EX + f"✗ Error creando base de datos: {e}" + Style.RESET_ALL)
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
    print(Fore.LIGHTGREEN_EX + f"✓ Tabla '{entidad}' creada/verificada" + Style.RESET_ALL)

    try:
        with engine.begin() as conn:
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

                    # SOLUCIÓN: Solo usar offset para scrobbles
                    if entidad == "scrobbles":
                        registros = parser_func(response, usuario, contador)
                    else:
                        registros = parser_func(response, usuario, 0)
                    
                    if registros:
                        result = conn.execute(tabla.insert(), registros)
                        contador += len(registros)
                    
                    # Calcular porcentaje y mostrar progreso
                    porcentaje = (pagina / total_paginas) * 100
                    
                    if porcentaje == 100:
                        porcentaje_str = "100%"
                    else:
                        porcentaje_str = f"{porcentaje:.1f}%"
                    
                    # Limpiar línea completamente
                    linea = f"Procesando: {porcentaje_str} ({pagina}/{total_paginas}) - Insertados: {formato_numero(contador)}"
                    sys.stdout.write(f"\r{linea:<70}")
                    sys.stdout.flush()
                    
                    pagina += 1
                    if pagina <= total_paginas:
                        time.sleep(delay)
                        
                except Exception as e:
                    mensaje = str(e)
                    if "for url:" in mensaje:
                        mensaje = mensaje.split("for url:")[0].strip()

                    # Traducción narrativa para errores comunes
                    if "500 Server Error" in mensaje:
                        mensaje = "500 Server Error: Conexión perdida con la API"
                    elif "ConnectionError" in mensaje:
                        mensaje = "Error de conexión: no se pudo contactar con el servidor"
                    elif "Timeout" in mensaje:
                        mensaje = "Timeout: el servidor no respondió a tiempo"

                    print(Fore.LIGHTRED_EX + f"\n✗ Error en página {pagina}: {mensaje}" + Style.RESET_ALL)
                    print(Fore.LIGHTRED_EX + f"✗ Reintento fallido. Se agotaron los intentos para esta página." + Style.RESET_ALL)
                    break
                    
    except Exception as e:
        print(Fore.LIGHTRED_EX + f"\n✗ Error procesando {entidad}: {e}" + Style.RESET_ALL)
        return 0

    print(Fore.LIGHTGREEN_EX + f"\n✓ Completado: {formato_numero(contador)} registros insertados en la tabla '{entidad}'" + Style.RESET_ALL)
    return contador

def parse_artistas(response, usuario, _):
    """Parsea artistas desde la respuesta JSON"""
    try:
        return [{
            'puesto': int(item['@attr']['rank']),
            'artista': item['name'][:255],
            'scrobbles': int(item['playcount']),
            'usuario': usuario[:100]
        } for item in response['topartists']['artist']]
    except KeyError as e:
        print(Fore.LIGHTRED_EX + f"✗ Error parseando artistas: {e}" + Style.RESET_ALL)
        return []

def parse_discos(response, usuario, _):
    """Parsea discos desde la respuesta JSON"""
    try:
        return [{
            'puesto': int(item['@attr']['rank']),
            'disco': item['name'][:255],
            'artista': item['artist']['name'][:255],
            'scrobbles': int(item['playcount']),
            'usuario': usuario[:100]
        } for item in response['topalbums']['album']]
    except KeyError as e:
        print(Fore.LIGHTRED_EX + f"✗ Error parseando discos: {e}" + Style.RESET_ALL)
        return []

def parse_canciones(response, usuario, _):
    """Parsea canciones desde la respuesta JSON"""
    try:
        return [{
            'puesto': int(item['@attr']['rank']),
            'cancion': item['name'][:255],
            'artista': item['artist']['name'][:255],
            'scrobbles': int(item['playcount']),
            'usuario': usuario[:100]
        } for item in response['toptracks']['track']]
    except KeyError as e:
        print(Fore.LIGHTRED_EX + f"✗ Error parseando canciones: {e}" + Style.RESET_ALL)
        return []

def parse_scrobbles(response, usuario, offset):
    """Parsea scrobbles desde la respuesta JSON"""
    registros = []
    try:
        for i, item in enumerate(response['recenttracks']['track']):
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
        print(Fore.LIGHTRED_EX + f"✗ Error parseando scrobbles: {e}" + Style.RESET_ALL)
    return registros

def main():
    inicio = mostrar_encabezado()
    args = configurar_argumentos()
    
    validar_api_key_configurada()

    print(f"\nVerificando usuario '{args.usuario}' en Last.fm...")
    if not usuario_existe(args.usuario):
        print(Fore.LIGHTRED_EX + f"✗ El usuario '{args.usuario}' no existe en Last.fm" + Style.RESET_ALL)
        sys.exit(1)
    print(Fore.LIGHTGREEN_EX + "✓ Usuario encontrado" + Style.RESET_ALL)

    print(f"\nVerificando y creando base de datos si es necesario...")
    nombre_bd = crear_base_datos_si_no_existe(args.motor, args.ip, args.puerto, args.usuario_bd, args.password)

    print(f"\nConectando a la base de datos '{nombre_bd}' ({args.motor})...")
    try:
        if args.motor == 'mysql':
            engine = create_engine(f"mysql+pymysql://{args.usuario_bd}:{args.password}@{args.ip}:{args.puerto}/{nombre_bd}")
        elif args.motor == 'postgresql':
            engine = create_engine(f"postgresql://{args.usuario_bd}:{args.password}@{args.ip}:{args.puerto}/{nombre_bd}")
        else:
            raise ValueError("Motor no soportado. Usa 'mysql' o 'postgresql'.")
        with engine.connect() as test_conn:
            test_conn.execute(text("SELECT 1"))
        print(Fore.LIGHTGREEN_EX + "✓ Conexión a la base de datos exitosa" + Style.RESET_ALL)
    except SQLAlchemyError as e:
        print(Fore.LIGHTRED_EX + f"✗ Error de conexión a la base de datos: {str(e)}" + Style.RESET_ALL)
        sys.exit(1)

    metadata = MetaData()
    total_registros = 0

    print(Fore.LIGHTCYAN_EX + "\n" + "=" * 60)
    print("INICIANDO EXTRACCIÓN DE DATOS")
    print("=" * 60 + Style.RESET_ALL)

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
        print(Fore.LIGHTMAGENTA_EX + f"\n--- Procesando {tabla.upper()} ---" + Style.RESET_ALL)
        registros = procesar_entidad_sql(usuario, method, tabla, columnas, parser, engine, metadata)
        total_registros += registros

    fin = datetime.datetime.now()
    duracion = fin - inicio
    duracion_redondeada = str(duracion).split('.')[0]

    print(Fore.LIGHTCYAN_EX + "\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60 + Style.RESET_ALL)
    print(f"Usuario: {args.usuario}")
    print(f"Total registros insertados: {formato_numero(total_registros)}")
    print(f"Duración: {duracion_redondeada}")
    print(Fore.YELLOW + "[Fin]", fin.strftime("%Y-%m-%d %H:%M:%S") + Style.RESET_ALL)
    print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)

if __name__ == "__main__":
    main()