import sys
import requests
import json
import datetime
import time
import os
import argparse
import getpass
import shutil

from colorama import init, Fore, Style

init()

API_KEY = None
API_URL = "http://ws.audioscrobbler.com/2.0/"

ANCHO = shutil.get_terminal_size().columns

ruta_raw = "../storage/raw"


def mostrar_encabezado():

    inicio = datetime.datetime.now()

    print(Fore.LIGHTCYAN_EX + ">" * ANCHO)
    print("|||| LAST.FM TOP ALBUMS RAW DOWNLOADER ||||".center(ANCHO))
    print("<" * ANCHO + Style.RESET_ALL)

    print(
        Fore.LIGHTYELLOW_EX
        + "[Inicio]".ljust(10),
        inicio.strftime("%Y-%m-%d %H:%M:%S")
        + Style.RESET_ALL
    )

    return inicio


def solicitar_api_key():

    global API_KEY

    intentos = 3

    for intento in range(intentos):

        print(f"\nIntroduce tu API key de Last.fm (intento {intento + 1}/{intentos}):")

        api_key = getpass.getpass("API key: ").strip()

        if not api_key:

            print(
                Fore.LIGHTRED_EX
                + "✗ La API key no puede estar vacía."
                + Style.RESET_ALL
            )

            continue

        if validar_api_key(api_key):

            API_KEY = api_key

            print(
                Fore.LIGHTGREEN_EX
                + "✓ API key válida y verificada"
                + Style.RESET_ALL
            )

            return True

        print(
            Fore.LIGHTRED_EX
            + "✗ API key no válida o sin permisos"
            + Style.RESET_ALL
        )

    print(
        Fore.LIGHTRED_EX
        + "\n✗ Demasiados intentos fallidos. Saliendo..."
        + Style.RESET_ALL
    )

    return False


def validar_api_key(api_key):

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

    except Exception:
        return False


def usuario_existe(usuario):

    params = {
        "method": "user.getInfo",
        "user": usuario,
        "api_key": API_KEY,
        "format": "json"
    }

    try:

        response = requests.get(API_URL, params=params, timeout=10)

        response.raise_for_status()

        data = response.json()

        return "user" in data

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

    porcentaje = (pagina / total_paginas) * 100

    ancho_barra = 20

    llenado = int((porcentaje / 100) * ancho_barra)

    barra = "█" * llenado + "░" * (ancho_barra - llenado)

    porcentaje_str = "100%" if porcentaje == 100 else f"{porcentaje:5.1f}%"

    linea = f"{barra} {porcentaje_str} ({pagina}/{total_paginas})"

    sys.stdout.write(f"\r{linea:<50}")

    sys.stdout.flush()


def formato_numero(numero):

    return f"{numero:,}".replace(",", ".")


def descargar_top_albums_raw(usuario):

    limite = 200
    pagina = 1
    total_paginas = 1

    delay = 0.25

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    ruta_usuario = f"{ruta_raw}/{usuario}"

    os.makedirs(ruta_usuario, exist_ok=True)

    archivo_json = (
        f"{ruta_usuario}/top_albums_raw_{timestamp}.json"
    )

    paginas_raw = []

    while pagina <= total_paginas:

        params = {
            "method": "user.getTopAlbums",
            "user": usuario,
            "api_key": API_KEY,
            "format": "json",
            "limit": limite,
            "page": pagina
        }

        response = hacer_solicitud(API_URL, params)

        if pagina == 1:

            total_paginas = int(
                response["topalbums"]["@attr"]["totalPages"]
            )

            total_albums = int(
                response["topalbums"]["@attr"]["total"]
            )

            print()

            print(
                f"Total de albums RAW: "
                f"{formato_numero(total_albums)} "
                f"en {formato_numero(total_paginas)} páginas"
            )

        if pagina % 10 == 0 or pagina == 1:

            mostrar_progreso(pagina, total_paginas)

        paginas_raw.append(response)

        pagina += 1

        if pagina <= total_paginas:

            time.sleep(delay)

    with open(archivo_json, "w", encoding="utf-8") as json_file:

        json.dump(
            {
                "usuario": usuario,
                "fecha_descarga": datetime.datetime.now().isoformat(),
                "origen": "Last.fm API",
                "metodo": "user.getTopAlbums",
                "total_paginas": total_paginas,
                "paginas": paginas_raw
            },
            json_file,
            ensure_ascii=False,
            indent=2
        )

    mostrar_progreso(total_paginas, total_paginas)

    print("\n")

    return archivo_json


def main():

    parser = argparse.ArgumentParser(
        description="Descarga RAW de top albums desde Last.fm"
    )

    parser.add_argument("usuario")

    args = parser.parse_args()

    mostrar_encabezado()

    if not solicitar_api_key():

        sys.exit(1)

    tiempo_inicio = time.time()

    if not usuario_existe(args.usuario):

        print()

        print(
            Fore.LIGHTRED_EX
            + f"✗ El usuario '{args.usuario}' no existe."
            + Style.RESET_ALL
        )

        sys.exit(1)

    print()

    print(
        Fore.LIGHTMAGENTA_EX
        + f"Descargando top albums RAW de {args.usuario}..."
        + Style.RESET_ALL
    )

    archivo = descargar_top_albums_raw(args.usuario)

    tiempo_total = time.time() - tiempo_inicio

    print(
        Fore.LIGHTGREEN_EX
        + f"\n✓ Archivo RAW generado:"
        + Style.RESET_ALL
    )

    print(archivo)

    print()

    print(
        Fore.LIGHTYELLOW_EX
        + f"Consulta completada en {tiempo_total:.2f} segundos."
        + Style.RESET_ALL
    )


if __name__ == "__main__":
    main()