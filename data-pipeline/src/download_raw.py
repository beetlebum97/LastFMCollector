import sys
import requests
import json
import datetime
import time
import os
import argparse
import getpass
import shutil

from pathlib import Path

from colorama import init, Fore, Style

init()

API_KEY = None
API_URL = "http://ws.audioscrobbler.com/2.0/"
ruta_raw = "../storage/raw"

# RUTAS DINÁMICAS (Sube 2 niveles: src -> data-pipeline -> raíz)
BASE_DIR = Path(__file__).resolve().parents[2]
ruta_raw = str(BASE_DIR / "storage" / "raw")


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
    print("|||| LAST.FM RAW DOWNLOADER ||||".center(ANCHO_UI))
    
    print("<" * ANCHO_UI + Style.RESET_ALL)
    print(Fore.LIGHTYELLOW_EX + "[Inicio]".ljust(10), inicio.strftime("%Y-%m-%d %H:%M:%S") + Style.RESET_ALL)
    return inicio

def solicitar_api_key():
    global API_KEY
    intentos = 3
    for intento in range(intentos):
        print(f"\nIntroduce tu API key de Last.fm (intento {intento + 1}/{intentos}):")
        api_key = getpass.getpass("API key: ").strip()
        if not api_key:
            print(Fore.LIGHTRED_EX + "✗ La API key no puede estar vacía." + Style.RESET_ALL)
            continue
        if validar_api_key(api_key):
            API_KEY = api_key
            print(Fore.LIGHTGREEN_EX + "✓ API key válida y verificada" + Style.RESET_ALL)
            return True
        print(Fore.LIGHTRED_EX + "✗ API key no válida o sin permisos" + Style.RESET_ALL)
    print(Fore.LIGHTRED_EX + "\n✗ Demasiados intentos fallidos. Saliendo..." + Style.RESET_ALL)
    return False

def validar_api_key(api_key):
    params = {"method": "chart.getTopArtists", "api_key": api_key, "format": "json", "limit": 1}
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        if response.status_code == 403: return False
        response.raise_for_status()
        return "error" not in response.json()
    except Exception:
        return False

def usuario_existe(usuario):
    params = {"method": "user.getInfo", "user": usuario, "api_key": API_KEY, "format": "json"}
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        return "user" in response.json()
    except Exception:
        return False

def hacer_solicitud(url, params, max_intentos=5):
    for intento in range(max_intentos):
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                raise ValueError(data["message"])
            return data
        except Exception as error:
            if intento < max_intentos - 1:
                time.sleep(2)
            else:
                raise error

def mostrar_progreso(pagina, total_paginas):
    if total_paginas == 0: return
    porcentaje = (pagina / total_paginas) * 100
    
    # Barra más larga (40 caracteres) para mejor visualización
    ancho_barra = 40
    llenado = int((porcentaje / 100) * ancho_barra)
    barra = "█" * llenado + "░" * (ancho_barra - llenado)
    
    porcentaje_str = "100%" if porcentaje == 100 else f"{porcentaje:5.1f}%"
    linea = f"{barra} {porcentaje_str} ({pagina}/{total_paginas})"
    
    # \033[K es un comando de consola que borra desde donde termina el texto hasta el final de la línea
    sys.stdout.write(f"\r{linea}\033[K")
    sys.stdout.flush()

def formato_numero(numero):
    return f"{numero:,}".replace(",", ".")

def formatear_tiempo(segundos_totales):
    """Convierte segundos en un formato legible (ej: 1 minuto y 15 segundos)"""
    minutos = int(segundos_totales // 60)
    segundos = int(segundos_totales % 60)
    
    if minutos == 0:
        return f"{segundos} segundos"
    elif minutos == 1:
        return f"1 minuto y {segundos} segundos"
    else:
        return f"{minutos} minutos y {segundos} segundos"

def guardar_json(ruta_archivo, datos):
    os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
    with open(ruta_archivo, "w", encoding="utf-8") as json_file:
        json.dump(datos, json_file, ensure_ascii=False, indent=2)

# ==========================================
# FUNCIONES DE DESCARGA
# ==========================================

def descargar_scrobbles_raw(usuario):
    print(Fore.LIGHTMAGENTA_EX + f"\n--- Descargando Scrobbles RAW ---" + Style.RESET_ALL)
    limite, pagina, total_paginas = 200, 1, 1
    delay = 0.25
    tracks_raw = []

    while pagina <= total_paginas:
        params = {"method": "user.getRecentTracks", "user": usuario, "api_key": API_KEY, "format": "json", "limit": limite, "page": pagina, "extended": 1}
        response = hacer_solicitud(API_URL, params)

        if pagina == 1:
            total_paginas = int(response["recenttracks"]["@attr"]["totalPages"])
            total_scrobbles = int(response["recenttracks"]["@attr"]["total"])
            print(f"Total de scrobbles: {formato_numero(total_scrobbles)} en {formato_numero(total_paginas)} páginas")
            if total_paginas == 0:
                print(Fore.LIGHTRED_EX + f"✗ El usuario no tiene historial de scrobbles." + Style.RESET_ALL)
                return

        if pagina % 10 == 0 or pagina == 1:
            mostrar_progreso(pagina, total_paginas)

        tracks_raw.extend(response["recenttracks"]["track"])
        pagina += 1
        if pagina <= total_paginas: time.sleep(delay)

    mostrar_progreso(total_paginas, total_paginas)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_json = f"{ruta_raw}/{usuario}/scrobbles_raw_{timestamp}.json"
    
    guardar_json(archivo_json, {
        "usuario": usuario, "fecha_descarga": datetime.datetime.now().isoformat(),
        "origen": "Last.fm API", "metodo": "user.getRecentTracks",
        "total_paginas": total_paginas, "total_scrobbles": len(tracks_raw), "tracks": tracks_raw
    })
    print(Fore.LIGHTGREEN_EX + f"\n✓ Guardado en: {archivo_json}" + Style.RESET_ALL)

def descargar_top_albums_raw(usuario):
    print(Fore.LIGHTMAGENTA_EX + f"\n--- Descargando Top Albums RAW ---" + Style.RESET_ALL)
    limite, pagina, total_paginas = 200, 1, 1
    delay = 0.25
    paginas_raw = []

    while pagina <= total_paginas:
        params = {"method": "user.getTopAlbums", "user": usuario, "api_key": API_KEY, "format": "json", "limit": limite, "page": pagina}
        response = hacer_solicitud(API_URL, params)

        if pagina == 1:
            total_paginas = int(response["topalbums"]["@attr"]["totalPages"])
            total_albums = int(response["topalbums"]["@attr"]["total"])
            print(f"Total de albums: {formato_numero(total_albums)} en {formato_numero(total_paginas)} páginas")
            if total_paginas == 0: return

        if pagina % 10 == 0 or pagina == 1:
            mostrar_progreso(pagina, total_paginas)

        paginas_raw.append(response)
        pagina += 1
        if pagina <= total_paginas: time.sleep(delay)

    mostrar_progreso(total_paginas, total_paginas)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_json = f"{ruta_raw}/{usuario}/top_albums_raw_{timestamp}.json"
    
    guardar_json(archivo_json, {
        "usuario": usuario, "fecha_descarga": datetime.datetime.now().isoformat(),
        "origen": "Last.fm API", "metodo": "user.getTopAlbums",
        "total_paginas": total_paginas, "paginas": paginas_raw
    })
    print(Fore.LIGHTGREEN_EX + f"\n✓ Guardado en: {archivo_json}" + Style.RESET_ALL)

def descargar_top_artists_raw(usuario):
    print(Fore.LIGHTMAGENTA_EX + f"\n--- Descargando Top Artistas RAW ---" + Style.RESET_ALL)
    limite, pagina, total_paginas = 200, 1, 1
    delay = 0.25
    paginas_raw = []

    while pagina <= total_paginas:
        params = {"method": "user.getTopArtists", "user": usuario, "api_key": API_KEY, "format": "json", "limit": limite, "page": pagina}
        response = hacer_solicitud(API_URL, params)

        if pagina == 1:
            total_paginas = int(response["topartists"]["@attr"]["totalPages"])
            total_artistas = int(response["topartists"]["@attr"]["total"])
            print(f"Total de artistas: {formato_numero(total_artistas)} en {formato_numero(total_paginas)} páginas")
            if total_paginas == 0: return

        if pagina % 10 == 0 or pagina == 1:
            mostrar_progreso(pagina, total_paginas)

        paginas_raw.append(response)
        pagina += 1
        if pagina <= total_paginas: time.sleep(delay)

    mostrar_progreso(total_paginas, total_paginas)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_json = f"{ruta_raw}/{usuario}/top_artists_raw_{timestamp}.json"
    
    guardar_json(archivo_json, {
        "usuario": usuario, "fecha_descarga": datetime.datetime.now().isoformat(),
        "origen": "Last.fm API", "metodo": "user.getTopArtists",
        "total_paginas": total_paginas, "paginas": paginas_raw
    })
    print(Fore.LIGHTGREEN_EX + f"\n✓ Guardado en: {archivo_json}" + Style.RESET_ALL)

def descargar_top_tracks_raw(usuario):
    print(Fore.LIGHTMAGENTA_EX + f"\n--- Descargando Top Canciones RAW ---" + Style.RESET_ALL)
    limite, pagina, total_paginas = 200, 1, 1
    delay = 0.25
    paginas_raw = []

    while pagina <= total_paginas:
        params = {"method": "user.getTopTracks", "user": usuario, "api_key": API_KEY, "format": "json", "limit": limite, "page": pagina}
        response = hacer_solicitud(API_URL, params)

        if pagina == 1:
            total_paginas = int(response["toptracks"]["@attr"]["totalPages"])
            total_tracks = int(response["toptracks"]["@attr"]["total"])
            print(f"Total de canciones: {formato_numero(total_tracks)} en {formato_numero(total_paginas)} páginas")
            if total_paginas == 0: return

        if pagina % 10 == 0 or pagina == 1:
            mostrar_progreso(pagina, total_paginas)

        paginas_raw.append(response)
        pagina += 1
        if pagina <= total_paginas: time.sleep(delay)

    mostrar_progreso(total_paginas, total_paginas)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_json = f"{ruta_raw}/{usuario}/top_tracks_raw_{timestamp}.json"
    
    guardar_json(archivo_json, {
        "usuario": usuario, "fecha_descarga": datetime.datetime.now().isoformat(),
        "origen": "Last.fm API", "metodo": "user.getTopTracks",
        "total_paginas": total_paginas, "paginas": paginas_raw
    })
    print(Fore.LIGHTGREEN_EX + f"\n✓ Guardado en: {archivo_json}" + Style.RESET_ALL)

# ==========================================
# MAIN Y ARGUMENTOS
# ==========================================

def main():
    parser = argparse.ArgumentParser(description="Descarga RAW de datos desde Last.fm")
    parser.add_argument("usuario", help="Usuario de Last.fm a procesar")
    
    # Quitamos 'choices' para evitar el error de argparse con listas vacías
    parser.add_argument("opciones", nargs="*", 
                        help="Qué descargar (ej. 'artistas' o 'canciones scrobbles'). Si no pones nada, descarga TODO.")

    args = parser.parse_args()
    
    # 1. Validamos las opciones manualmente
    opciones_validas = ["scrobbles", "albums", "artistas", "canciones"]
    for opcion in args.opciones:
        if opcion not in opciones_validas:
            print(Fore.LIGHTRED_EX + f"\n✗ Error: '{opcion}' no es una opción válida." + Style.RESET_ALL)
            print(Fore.LIGHTYELLOW_EX + f"Opciones permitidas: {', '.join(opciones_validas)}\n" + Style.RESET_ALL)
            sys.exit(1)
    
    # 2. Si la lista de opciones está vacía, ejecutamos todas
    tareas = args.opciones if args.opciones else opciones_validas

    mostrar_encabezado()

    if not solicitar_api_key():
        sys.exit(1)

    tiempo_inicio = time.time()

    # Comprobar existencia del usuario ANTES de descargar nada
    if not usuario_existe(args.usuario):
        print(Fore.LIGHTRED_EX + f"\n✗ El usuario '{args.usuario}' no existe en Last.fm." + Style.RESET_ALL)
        sys.exit(1)

    print(Fore.LIGHTYELLOW_EX + f"\nUsuario validado. Tareas a ejecutar: {', '.join(tareas)}" + Style.RESET_ALL)

    # Ejecutar secuencialmente las tareas indicadas
    if "scrobbles" in tareas: descargar_scrobbles_raw(args.usuario)
    if "albums" in tareas:    descargar_top_albums_raw(args.usuario)
    if "artistas" in tareas:  descargar_top_artists_raw(args.usuario)
    if "canciones" in tareas: descargar_top_tracks_raw(args.usuario)

    tiempo_total = time.time() - tiempo_inicio
    
    # Usamos la nueva función para mostrar el tiempo
    tiempo_formateado = formatear_tiempo(tiempo_total)
    
    print(Fore.LIGHTYELLOW_EX + f"\nProceso global completado en {tiempo_formateado}." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
