# -*- coding: utf-8 -*-
import os
import requests
import concurrent.futures
import argparse
import getpass
import sys
import datetime
import time
import shutil

from colorama import init, Fore, Style
init()

API_KEY = None
API_URL = "http://ws.audioscrobbler.com/2.0/"

# Unificamos el diseño UI a 60 caracteres, como en el resto de scripts
ANCHO_UI = 60

def mostrar_encabezado():
    inicio = datetime.datetime.now()
    print(Fore.LIGHTCYAN_EX + ">" * ANCHO_UI)
    print("|||| LAST.FM USER STATS ||||".center(ANCHO_UI))
    print("<" * ANCHO_UI + Style.RESET_ALL)
    print(
        Fore.LIGHTYELLOW_EX
        + "[Inicio]".ljust(10)
        + inicio.strftime("%Y-%m-%d %H:%M:%S")
        + Style.RESET_ALL
    )
    return inicio
    
def validar_api_key_en_servidor(api_key):
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
        if "error" in data:
            return False
        return True
    except requests.exceptions.RequestException:
        return False

def solicitar_api_key():
    global API_KEY
    intentos = 3
    for intento in range(intentos):
        try:
            print(f"\nIntroduce tu API key de Last.fm (intento {intento + 1}/{intentos}):")
            api_key = getpass.getpass("API key: ").strip()
            
            if not api_key:
                print(Fore.LIGHTRED_EX + "✗ La API key no puede estar vacía." + Style.RESET_ALL)
                continue
                
            if not validar_api_key_en_servidor(api_key):
                print(Fore.LIGHTRED_EX + "✗ API key no válida o sin permisos" + Style.RESET_ALL)
                continue
                
            API_KEY = api_key
            print(Fore.LIGHTGREEN_EX + "✓ API key válida y verificada" + Style.RESET_ALL)
            return

        except KeyboardInterrupt:
            print("\nOperación cancelada por el usuario.")
            sys.exit(1)

    print(Fore.LIGHTRED_EX + "\n✗ Demasiados intentos fallidos. Saliendo..." + Style.RESET_ALL)
    sys.exit(1)

def formato_numero(numero):
    return f"{numero:,}".replace(",", ".")

def obtener_estadistica(usuario, metodo, root):
    params = {
        "method": metodo,
        "user": usuario,
        "api_key": API_KEY,
        "format": "json",
        "limit": 1,
        "page": 1
    }
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        if response.status_code == 403:
            raise ValueError("API key inválida o sin permisos")
        if response.status_code == 404:
            raise ValueError(f"Usuario '{usuario}' no encontrado")
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise ValueError(data["message"])
        return int(data[root]["@attr"]["total"])
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error de conexión: {e}")

def obtener_info_usuario(usuario):
    params = {
        "method": "user.getInfo",
        "user": usuario,
        "api_key": API_KEY,
        "format": "json"
    }
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        if response.status_code == 403:
            raise ValueError("API key inválida o sin permisos")
        if response.status_code == 404:
            raise ValueError(f"Usuario '{usuario}' no encontrado")
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise ValueError(data["message"])
        usuario_data = data["user"]
        fecha_registro = datetime.datetime.fromtimestamp(int(usuario_data["registered"]["unixtime"]))
        
        return {
            "pais": usuario_data.get("country", "Desconocido"),
            "registrado": fecha_registro.strftime("%Y-%m-%d")
        }
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error de conexión: {e}")

def obtener_top_artistas(usuario, limite=5):
    params = {"method": "user.getTopArtists", "user": usuario, "api_key": API_KEY, "format": "json", "limit": limite}
    response = requests.get(API_URL, params=params, timeout=10)
    data = response.json()
    return [{"nombre": a["name"], "scrobbles": a["playcount"]} for a in data["topartists"]["artist"]]

def obtener_top_albums(usuario, limite=5):
    params = {"method": "user.getTopAlbums", "user": usuario, "api_key": API_KEY, "format": "json", "limit": limite}
    response = requests.get(API_URL, params=params, timeout=10)
    data = response.json()
    return [{"album": a["name"], "artista": a["artist"]["name"], "scrobbles": a["playcount"]} for a in data["topalbums"]["album"]]

def obtener_top_tracks(usuario, limite=5):
    params = {"method": "user.getTopTracks", "user": usuario, "api_key": API_KEY, "format": "json", "limit": limite}
    response = requests.get(API_URL, params=params, timeout=10)
    data = response.json()
    return [{"track": t["name"], "artista": t["artist"]["name"], "scrobbles": t["playcount"]} for t in data["toptracks"]["track"]]

def obtener_ultimos_scrobbles(usuario, limite=5):
    params = {"method": "user.getRecentTracks", "user": usuario, "api_key": API_KEY, "format": "json", "limit": limite}
    response = requests.get(API_URL, params=params, timeout=10)
    data = response.json()
    tracks = []

    for track in data["recenttracks"]["track"]:
        fecha = "Ahora"
        if "date" in track:
            fecha_str = track["date"]["#text"]  # Ej: "17 Jun 2026, 11:18"

            try:
                # 1. Convertimos el texto plano a un objeto de tiempo real de Python
                fecha_obj = datetime.datetime.strptime(fecha_str, "%d %b %Y, %H:%M")

                # 2. Le sumamos las 2 horas de diferencia (calcula días y meses automáticamente)
                fecha_obj += datetime.timedelta(hours=2)

                # 3. Lo volvemos a convertir a texto con el mismo formato
                fecha = fecha_obj.strftime("%d %b %Y, %H:%M")
            except ValueError:
                # Si Last.fm cambia su formato algún día, fallará de forma segura devolviendo la hora original
                fecha = fecha_str

        tracks.append({"track": track["name"], "artista": track["artist"]["#text"], "fecha": fecha})

    return tracks

def resumen_usuario(usuario):
    estadisticas = [
        ("user.getTopArtists", "topartists", "ARTISTAS"),
        ("user.getTopAlbums", "topalbums", "ALBUMS"),
        ("user.getTopTracks", "toptracks", "CANCIONES"),
        ("user.getLovedTracks", "lovedtracks", "FAVORITAS"),
        ("user.getRecentTracks", "recenttracks", "SCROBBLES")
    ]
    
    resultados = {}
    info_usuario = obtener_info_usuario(usuario)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(obtener_estadistica, usuario, metodo, root): nombre for metodo, root, nombre in estadisticas}
        for future in concurrent.futures.as_completed(futures):
            nombre = futures[future]
            resultados[nombre] = future.result()

    # --- INICIO DE CONSTRUCCIÓN DEL REPORTE Y CONSOLA ---
    # Usaremos una lista para ir guardando el texto limpio (sin colores ANSI) para el archivo txt
    reporte_limpio = []

    print()
    reporte_limpio.append("")
    
    banner_borde = "=" * ANCHO_UI
    banner_texto = f"USUARIO: {usuario}".center(ANCHO_UI)
    
    print(Fore.LIGHTCYAN_EX + banner_borde)
    print(banner_texto)
    print(banner_borde + Style.RESET_ALL)
    
    reporte_limpio.extend([banner_borde, banner_texto, banner_borde, ""])
    print()
    
    orden_estadisticas = ["ARTISTAS", "ALBUMS", "CANCIONES", "FAVORITAS", "SCROBBLES"]
    
    linea_pais = f"{'PAÍS':<12}: {info_usuario['pais']}"
    linea_miembro = f"{'MIEMBRO':<12}: {info_usuario['registrado']}"
    
    print(Fore.LIGHTCYAN_EX + linea_pais + Style.RESET_ALL)
    print(Fore.LIGHTCYAN_EX + linea_miembro + Style.RESET_ALL)
    reporte_limpio.extend([linea_pais, linea_miembro])

    for nombre in orden_estadisticas:
        valor = resultados[nombre]
        linea_stat = f"{nombre:<12}: {formato_numero(valor)}"
        print(Fore.LIGHTCYAN_EX + linea_stat + Style.RESET_ALL)
        reporte_limpio.append(linea_stat)

    print()
    reporte_limpio.append("")

    print(Fore.LIGHTMAGENTA_EX + "TOP ARTISTAS" + Style.RESET_ALL)
    reporte_limpio.append("TOP ARTISTAS")
    for idx, artista in enumerate(obtener_top_artistas(usuario), start=1):
        linea = f"{idx}. {artista['nombre']} ({artista['scrobbles']})"
        print(linea)
        reporte_limpio.append(linea)

    print()
    reporte_limpio.append("")

    print(Fore.LIGHTMAGENTA_EX + "TOP ALBUMS" + Style.RESET_ALL)
    reporte_limpio.append("TOP ALBUMS")
    for idx, album in enumerate(obtener_top_albums(usuario), start=1):
        linea = f"{idx}. {album['album']} - {album['artista']} ({album['scrobbles']})"
        print(linea)
        reporte_limpio.append(linea)

    print()
    reporte_limpio.append("")

    print(Fore.LIGHTMAGENTA_EX + "TOP CANCIONES" + Style.RESET_ALL)
    reporte_limpio.append("TOP CANCIONES")
    for idx, track in enumerate(obtener_top_tracks(usuario), start=1):
        linea = f"{idx}. {track['track']} - {track['artista']} ({track['scrobbles']})"
        print(linea)
        reporte_limpio.append(linea)

    print()
    reporte_limpio.append("")

    print(Fore.LIGHTMAGENTA_EX + "ÚLTIMOS SCROBBLES" + Style.RESET_ALL)
    reporte_limpio.append("ÚLTIMOS SCROBBLES")
    for track in obtener_ultimos_scrobbles(usuario):
        linea = f"- {track['track']} | {track['artista']} | {track['fecha']}"
        print(linea)
        reporte_limpio.append(linea)
    
    print()
    
    # --- GUARDAR EL INFORME EN UN ARCHIVO .TXT ---
    ruta_reports = "reports"
    os.makedirs(ruta_reports, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_txt = f"{ruta_reports}/{usuario}_stats_{timestamp}.txt"
    
    with open(archivo_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(reporte_limpio))
        
    print(Fore.LIGHTGREEN_EX + f"✓ Reporte guardado con éxito en: {archivo_txt}" + Style.RESET_ALL)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("usuario")

    args = parser.parse_args()

    mostrar_encabezado()
    solicitar_api_key()

    tiempo_inicio = time.time()

    try:
        resumen_usuario(args.usuario)
    except ValueError as error:
        print()
        print(Fore.RED + f"✗ {error}" + Style.RESET_ALL)
        sys.exit(1)

    tiempo_total = time.time() - tiempo_inicio

    print()
    print(
        Fore.LIGHTYELLOW_EX
        + f"Consulta completada en {tiempo_total:.2f} segundos."
        + Style.RESET_ALL
    )

if __name__ == "__main__":
    main()
