import json
import csv
import os
import argparse
import datetime
import shutil

from colorama import init, Fore, Style

init()

ruta_raw = "../storage/raw"
ruta_staging = "../storage/staging"

# Mantenemos esto para limpiar la barra de progreso
ANCHO_TERMINAL = shutil.get_terminal_size().columns 
# Usamos esto para unificar el diseño de todas las cabeceras
ANCHO_UI = 60


# ==========================================
# FUNCIONES DE UTILIDAD
# ==========================================

def mostrar_encabezado():
    inicio = datetime.datetime.now()
    print(Fore.LIGHTCYAN_EX + ">" * ANCHO_UI)
    
    # Aquí puedes cambiar el texto según el script: RAW, STAGING o CURATED
    print("|||| LAST.FM STAGING PROCESSOR ||||".center(ANCHO_UI))
    
    print("<" * ANCHO_UI + Style.RESET_ALL)
    print(Fore.LIGHTYELLOW_EX + "[Inicio]".ljust(10), inicio.strftime("%Y-%m-%d %H:%M:%S") + Style.RESET_ALL)
    return inicio

def formato_numero(numero):
    return f"{numero:,}".replace(",", ".")

def obtener_ultimo_raw(usuario, prefijo):
    ruta_usuario = f"{ruta_raw}/{usuario}"
    if not os.path.exists(ruta_usuario):
        raise FileNotFoundError(f"No existe el directorio RAW para el usuario '{usuario}'")

    archivos = [
        archivo for archivo in os.listdir(ruta_usuario)
        if archivo.startswith(prefijo) and archivo.endswith(".json")
    ]

    if not archivos:
        raise FileNotFoundError(f"No se encontraron archivos RAW con el prefijo '{prefijo}'")

    archivos.sort(reverse=True)
    return os.path.join(ruta_usuario, archivos[0])

def guardar_json(datos, archivo_json):
    os.makedirs(os.path.dirname(archivo_json), exist_ok=True)
    with open(archivo_json, "w", encoding="utf-8") as json_file:
        json.dump(datos, json_file, ensure_ascii=False, indent=2)

def guardar_csv(datos, columnas, archivo_csv):
    os.makedirs(os.path.dirname(archivo_csv), exist_ok=True)
    with open(archivo_csv, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columnas)
        writer.writeheader()
        writer.writerows(datos)

# ==========================================
# FUNCIONES DE PROCESAMIENTO
# ==========================================

def procesar_scrobbles_staging(usuario):
    print(Fore.LIGHTMAGENTA_EX + f"\n--- Procesando Scrobbles RAW a STAGING ---" + Style.RESET_ALL)
    try:
        archivo_raw = obtener_ultimo_raw(usuario, "scrobbles_raw_")
        print(Fore.LIGHTCYAN_EX + f"Archivo RAW detectado: {archivo_raw}" + Style.RESET_ALL)
        
        with open(archivo_raw, "r", encoding="utf-8") as raw_file:
            raw_data = json.load(raw_file)

        scrobbles_staging = []
        for track in raw_data.get("tracks", []):
            fecha = track.get("date", {})
            uts = fecha.get("uts")
            timestamp = datetime.datetime.fromtimestamp(int(uts), datetime.timezone.utc).isoformat() if uts else None

            scrobbles_staging.append({
                "artist_name": track.get("artist", {}).get("name"),
                "artist_mbid": track.get("artist", {}).get("mbid") or None,
                "track_name": track.get("name"),
                "track_mbid": track.get("mbid") or None,
                "album_name": track.get("album", {}).get("#text"),
                "album_mbid": track.get("album", {}).get("mbid") or None,
                "track_url": track.get("url"),
                "loved": int(track.get("loved", 0)),
                "streamable": int(track.get("streamable", 0)),
                "nowplaying": track.get("@attr", {}).get("nowplaying") == "true",
                "timestamp_uts": int(uts) if uts else None,
                "timestamp_iso": timestamp
            })

        ruta_usuario_staging = f"{ruta_staging}/{usuario}"
        archivo_json = f"{ruta_usuario_staging}/scrobbles_staging.json"
        archivo_csv = f"{ruta_usuario_staging}/scrobbles_staging.csv"
        columnas = ["artist_name", "artist_mbid", "track_name", "track_mbid", "album_name", "album_mbid", "track_url", "loved", "streamable", "nowplaying", "timestamp_uts", "timestamp_iso"]

        guardar_json(scrobbles_staging, archivo_json)
        guardar_csv(scrobbles_staging, columnas, archivo_csv)
        
        print(Fore.LIGHTGREEN_EX + f"✓ Scrobbles procesados: {formato_numero(len(scrobbles_staging))}" + Style.RESET_ALL)

    except FileNotFoundError as e:
        print(Fore.LIGHTRED_EX + f"✗ Saltando scrobbles: {e}" + Style.RESET_ALL)

def procesar_albums_staging(usuario):
    print(Fore.LIGHTMAGENTA_EX + f"\n--- Procesando Top Albums RAW a STAGING ---" + Style.RESET_ALL)
    try:
        archivo_raw = obtener_ultimo_raw(usuario, "top_albums_raw_")
        print(Fore.LIGHTCYAN_EX + f"Archivo RAW detectado: {archivo_raw}" + Style.RESET_ALL)
        
        with open(archivo_raw, "r", encoding="utf-8") as raw_file:
            raw_data = json.load(raw_file)

        albums_staging = []
        for pagina in raw_data.get("paginas", []):
            for album in pagina.get("topalbums", {}).get("album", []):
                albums_staging.append({
                    "rank": int(album.get("@attr", {}).get("rank", 0)),
                    "album_name": album.get("name"),
                    "artist_name": album.get("artist", {}).get("name"),
                    "playcount": int(album.get("playcount", 0)),
                    "album_url": album.get("url"),
                    "album_mbid": album.get("mbid") or None,
                    "artist_mbid": album.get("artist", {}).get("mbid") or None
                })

        ruta_usuario_staging = f"{ruta_staging}/{usuario}"
        archivo_json = f"{ruta_usuario_staging}/top_albums_staging.json"
        archivo_csv = f"{ruta_usuario_staging}/top_albums_staging.csv"
        columnas = ["rank", "album_name", "artist_name", "playcount", "album_url", "album_mbid", "artist_mbid"]

        guardar_json(albums_staging, archivo_json)
        guardar_csv(albums_staging, columnas, archivo_csv)
        
        print(Fore.LIGHTGREEN_EX + f"✓ Albums procesados: {formato_numero(len(albums_staging))}" + Style.RESET_ALL)

    except FileNotFoundError as e:
        print(Fore.LIGHTRED_EX + f"✗ Saltando albums: {e}" + Style.RESET_ALL)

def procesar_artistas_staging(usuario):
    print(Fore.LIGHTMAGENTA_EX + f"\n--- Procesando Top Artistas RAW a STAGING ---" + Style.RESET_ALL)
    try:
        archivo_raw = obtener_ultimo_raw(usuario, "top_artists_raw_")
        print(Fore.LIGHTCYAN_EX + f"Archivo RAW detectado: {archivo_raw}" + Style.RESET_ALL)
        
        with open(archivo_raw, "r", encoding="utf-8") as raw_file:
            raw_data = json.load(raw_file)

        artistas_staging = []
        for pagina in raw_data.get("paginas", []):
            for artista in pagina.get("topartists", {}).get("artist", []):
                artistas_staging.append({
                    "rank": int(artista.get("@attr", {}).get("rank", 0)),
                    "artist_name": artista.get("name"),
                    "playcount": int(artista.get("playcount", 0)),
                    "artist_url": artista.get("url"),
                    "artist_mbid": artista.get("mbid") or None
                })

        ruta_usuario_staging = f"{ruta_staging}/{usuario}"
        archivo_json = f"{ruta_usuario_staging}/top_artists_staging.json"
        archivo_csv = f"{ruta_usuario_staging}/top_artists_staging.csv"
        columnas = ["rank", "artist_name", "playcount", "artist_url", "artist_mbid"]

        guardar_json(artistas_staging, archivo_json)
        guardar_csv(artistas_staging, columnas, archivo_csv)
        
        print(Fore.LIGHTGREEN_EX + f"✓ Artistas procesados: {formato_numero(len(artistas_staging))}" + Style.RESET_ALL)

    except FileNotFoundError as e:
        print(Fore.LIGHTRED_EX + f"✗ Saltando artistas: {e}" + Style.RESET_ALL)

def procesar_canciones_staging(usuario):
    print(Fore.LIGHTMAGENTA_EX + f"\n--- Procesando Top Canciones RAW a STAGING ---" + Style.RESET_ALL)
    try:
        archivo_raw = obtener_ultimo_raw(usuario, "top_tracks_raw_")
        print(Fore.LIGHTCYAN_EX + f"Archivo RAW detectado: {archivo_raw}" + Style.RESET_ALL)
        
        with open(archivo_raw, "r", encoding="utf-8") as raw_file:
            raw_data = json.load(raw_file)

        tracks_staging = []
        for pagina in raw_data.get("paginas", []):
            for track in pagina.get("toptracks", {}).get("track", []):
                tracks_staging.append({
                    "rank": int(track.get("@attr", {}).get("rank", 0)),
                    "track_name": track.get("name"),
                    "artist_name": track.get("artist", {}).get("name"),
                    "playcount": int(track.get("playcount", 0)),
                    "track_url": track.get("url"),
                    "track_mbid": track.get("mbid") or None,
                    "artist_mbid": track.get("artist", {}).get("mbid") or None
                })

        ruta_usuario_staging = f"{ruta_staging}/{usuario}"
        archivo_json = f"{ruta_usuario_staging}/top_tracks_staging.json"
        archivo_csv = f"{ruta_usuario_staging}/top_tracks_staging.csv"
        columnas = ["rank", "track_name", "artist_name", "playcount", "track_url", "track_mbid", "artist_mbid"]

        guardar_json(tracks_staging, archivo_json)
        guardar_csv(tracks_staging, columnas, archivo_csv)
        
        print(Fore.LIGHTGREEN_EX + f"✓ Canciones procesadas: {formato_numero(len(tracks_staging))}" + Style.RESET_ALL)

    except FileNotFoundError as e:
        print(Fore.LIGHTRED_EX + f"✗ Saltando canciones: {e}" + Style.RESET_ALL)

# ==========================================
# MAIN Y ARGUMENTOS
# ==========================================

def main():
    parser = argparse.ArgumentParser(description="Procesa datos RAW a STAGING")
    parser.add_argument("usuario", help="Usuario de Last.fm a procesar")
    
    # Quitamos 'choices' para evitar el error de argparse con listas vacías
    parser.add_argument("opciones", nargs="*", 
                        help="Qué procesar (ej. 'artistas' o 'canciones scrobbles'). Si no pones nada, procesa TODO.")

    args = parser.parse_args()
    
    # 1. Validamos las opciones manualmente
    opciones_validas = ["scrobbles", "albums", "artistas", "canciones"]
    for opcion in args.opciones:
        if opcion not in opciones_validas:
            import sys
            print(Fore.LIGHTRED_EX + f"\n✗ Error: '{opcion}' no es una opción válida." + Style.RESET_ALL)
            print(Fore.LIGHTYELLOW_EX + f"Opciones permitidas: {', '.join(opciones_validas)}\n" + Style.RESET_ALL)
            sys.exit(1)
            
    # 2. Si la lista de opciones está vacía, ejecutamos todas
    tareas = args.opciones if args.opciones else opciones_validas

    tiempo_inicio = mostrar_encabezado()
    print(Fore.LIGHTYELLOW_EX + f"\nUsuario: {args.usuario} | Tareas a ejecutar: {', '.join(tareas)}" + Style.RESET_ALL)

    # Ejecutar secuencialmente las tareas indicadas
    if "scrobbles" in tareas: procesar_scrobbles_staging(args.usuario)
    if "albums" in tareas:    procesar_albums_staging(args.usuario)
    if "artistas" in tareas:  procesar_artistas_staging(args.usuario)
    if "canciones" in tareas: procesar_canciones_staging(args.usuario)

    tiempo_total = (datetime.datetime.now() - tiempo_inicio).total_seconds()
    print(Fore.LIGHTYELLOW_EX + f"\nProcesamiento STAGING completado en {tiempo_total:.2f} segundos." + Style.RESET_ALL)

if __name__ == "__main__":
    main()