# -*- coding: utf-8 -*-
import json
import csv
import os
import argparse
import datetime
import shutil

from colorama import init, Fore, Style

init()

ruta_staging = "../storage/staging"
ruta_curated = "../storage/curated"

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
    print("|||| LAST.FM CURATED PROCESSOR ||||".center(ANCHO_UI))
    
    print("<" * ANCHO_UI + Style.RESET_ALL)
    print(Fore.LIGHTYELLOW_EX + "[Inicio]".ljust(10), inicio.strftime("%Y-%m-%d %H:%M:%S") + Style.RESET_ALL)
    return inicio

def formato_numero(numero):
    return f"{numero:,}".replace(",", ".")

def obtener_archivo_staging(usuario, nombre_archivo):
    archivo = f"{ruta_staging}/{usuario}/{nombre_archivo}"
    if not os.path.exists(archivo):
        raise FileNotFoundError(f"No existe el archivo STAGING '{nombre_archivo}' para '{usuario}'")
    return archivo

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

def procesar_scrobbles_curated(usuario):
    print(Fore.LIGHTMAGENTA_EX + f"\n--- Procesando Scrobbles STAGING a CURATED ---" + Style.RESET_ALL)
    try:
        archivo_staging = obtener_archivo_staging(usuario, "scrobbles_staging.json")
        print(Fore.LIGHTCYAN_EX + f"Archivo STAGING detectado: {archivo_staging}" + Style.RESET_ALL)

        with open(archivo_staging, "r", encoding="utf-8") as staging_file:
            scrobbles_staging = json.load(staging_file)

        scrobbles_curated = []
        for scrobble in scrobbles_staging:
            timestamp_iso = scrobble.get("timestamp_iso")
            fecha_local = None

            if timestamp_iso:
                try:
                    fecha_utc = datetime.datetime.fromisoformat(timestamp_iso)
                    # Sumamos las 2 horas y aplicamos el formato clásico YYYY-MM-DD HH:MM:SS
                    fecha_local = (fecha_utc + datetime.timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    fecha_local = None

            scrobbles_curated.append({
                "artist_name": scrobble.get("artist_name"),
                "track_name": scrobble.get("track_name"),
                "album_name": scrobble.get("album_name"),
                "loved": scrobble.get("loved"),
                "date_time": fecha_local  # Cambiamos la clave aquí
            })

        ruta_usuario_curated = f"{ruta_curated}/{usuario}"
        archivo_json = f"{ruta_usuario_curated}/scrobbles_curated.json"
        archivo_csv = f"{ruta_usuario_curated}/scrobbles_curated.csv"
        # Actualizamos las columnas para el CSV
        columnas = ["artist_name", "track_name", "album_name", "loved", "date_time"]

        guardar_json(scrobbles_curated, archivo_json)
        guardar_csv(scrobbles_curated, columnas, archivo_csv)
        
        print(Fore.LIGHTGREEN_EX + f"✓ Scrobbles procesados: {formato_numero(len(scrobbles_curated))}" + Style.RESET_ALL)

    except FileNotFoundError as e:
        print(Fore.LIGHTRED_EX + f"✗ Saltando scrobbles: {e}" + Style.RESET_ALL)


def procesar_albums_curated(usuario):
    print(Fore.LIGHTMAGENTA_EX + f"\n--- Procesando Top Albums STAGING a CURATED ---" + Style.RESET_ALL)
    try:
        archivo_staging = obtener_archivo_staging(usuario, "top_albums_staging.json")
        print(Fore.LIGHTCYAN_EX + f"Archivo STAGING detectado: {archivo_staging}" + Style.RESET_ALL)

        with open(archivo_staging, "r", encoding="utf-8") as staging_file:
            albums_staging = json.load(staging_file)

        total_playcount = sum(album.get("playcount", 0) for album in albums_staging)
        albums_curated = []

        for album in albums_staging:
            playcount = album.get("playcount", 0)
            pct = round((playcount / total_playcount) * 100, 2) if total_playcount > 0 else 0.0

            albums_curated.append({
                "rank": album.get("rank"),
                "album_name": album.get("album_name"),
                "artist_name": album.get("artist_name"),
                "playcount": playcount,
                "playcount_pct": pct
            })

        ruta_usuario_curated = f"{ruta_curated}/{usuario}"
        archivo_json = f"{ruta_usuario_curated}/top_albums_curated.json"
        archivo_csv = f"{ruta_usuario_curated}/top_albums_curated.csv"
        columnas = ["rank", "album_name", "artist_name", "playcount", "playcount_pct"]

        guardar_json(albums_curated, archivo_json)
        guardar_csv(albums_curated, columnas, archivo_csv)
        
        print(Fore.LIGHTGREEN_EX + f"✓ Albums procesados: {formato_numero(len(albums_curated))}" + Style.RESET_ALL)

    except FileNotFoundError as e:
        print(Fore.LIGHTRED_EX + f"✗ Saltando albums: {e}" + Style.RESET_ALL)


def procesar_artistas_curated(usuario):
    print(Fore.LIGHTMAGENTA_EX + f"\n--- Procesando Top Artistas STAGING a CURATED ---" + Style.RESET_ALL)
    try:
        archivo_staging = obtener_archivo_staging(usuario, "top_artists_staging.json")
        print(Fore.LIGHTCYAN_EX + f"Archivo STAGING detectado: {archivo_staging}" + Style.RESET_ALL)

        with open(archivo_staging, "r", encoding="utf-8") as staging_file:
            artistas_staging = json.load(staging_file)

        total_playcount = sum(artista.get("playcount", 0) for artista in artistas_staging)
        artistas_curated = []

        for artista in artistas_staging:
            playcount = artista.get("playcount", 0)
            pct = round((playcount / total_playcount) * 100, 2) if total_playcount > 0 else 0.0

            artistas_curated.append({
                "rank": artista.get("rank"),
                "artist_name": artista.get("artist_name"),
                "playcount": playcount,
                "playcount_pct": pct
            })

        ruta_usuario_curated = f"{ruta_curated}/{usuario}"
        archivo_json = f"{ruta_usuario_curated}/top_artists_curated.json"
        archivo_csv = f"{ruta_usuario_curated}/top_artists_curated.csv"
        columnas = ["rank", "artist_name", "playcount", "playcount_pct"]

        guardar_json(artistas_curated, archivo_json)
        guardar_csv(artistas_curated, columnas, archivo_csv)
        
        print(Fore.LIGHTGREEN_EX + f"✓ Artistas procesados: {formato_numero(len(artistas_curated))}" + Style.RESET_ALL)

    except FileNotFoundError as e:
        print(Fore.LIGHTRED_EX + f"✗ Saltando artistas: {e}" + Style.RESET_ALL)


def procesar_canciones_curated(usuario):
    print(Fore.LIGHTMAGENTA_EX + f"\n--- Procesando Top Canciones STAGING a CURATED ---" + Style.RESET_ALL)
    try:
        archivo_staging = obtener_archivo_staging(usuario, "top_tracks_staging.json")
        print(Fore.LIGHTCYAN_EX + f"Archivo STAGING detectado: {archivo_staging}" + Style.RESET_ALL)

        with open(archivo_staging, "r", encoding="utf-8") as staging_file:
            tracks_staging = json.load(staging_file)

        total_playcount = sum(track.get("playcount", 0) for track in tracks_staging)
        tracks_curated = []

        for track in tracks_staging:
            playcount = track.get("playcount", 0)
            pct = round((playcount / total_playcount) * 100, 2) if total_playcount > 0 else 0.0

            tracks_curated.append({
                "rank": track.get("rank"),
                "track_name": track.get("track_name"),
                "artist_name": track.get("artist_name"),
                "playcount": playcount,
                "playcount_pct": pct
            })

        ruta_usuario_curated = f"{ruta_curated}/{usuario}"
        archivo_json = f"{ruta_usuario_curated}/top_tracks_curated.json"
        archivo_csv = f"{ruta_usuario_curated}/top_tracks_curated.csv"
        columnas = ["rank", "track_name", "artist_name", "playcount", "playcount_pct"]

        guardar_json(tracks_curated, archivo_json)
        guardar_csv(tracks_curated, columnas, archivo_csv)
        
        print(Fore.LIGHTGREEN_EX + f"✓ Canciones procesadas: {formato_numero(len(tracks_curated))}" + Style.RESET_ALL)

    except FileNotFoundError as e:
        print(Fore.LIGHTRED_EX + f"✗ Saltando canciones: {e}" + Style.RESET_ALL)

# ==========================================
# MAIN Y ARGUMENTOS
# ==========================================

def main():
    parser = argparse.ArgumentParser(description="Procesa datos STAGING a CURATED")
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
    if "scrobbles" in tareas: procesar_scrobbles_curated(args.usuario)
    if "albums" in tareas:    procesar_albums_curated(args.usuario)
    if "artistas" in tareas:  procesar_artistas_curated(args.usuario)
    if "canciones" in tareas: procesar_canciones_curated(args.usuario)

    tiempo_total = (datetime.datetime.now() - tiempo_inicio).total_seconds()
    print(Fore.LIGHTYELLOW_EX + f"\nProcesamiento CURATED completado en {tiempo_total:.2f} segundos." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
