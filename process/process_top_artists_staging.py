import json
import csv
import os
import argparse
import datetime
import shutil

from colorama import init, Fore, Style

init()

ANCHO = shutil.get_terminal_size().columns

ruta_raw = "../storage/raw"
ruta_staging = "../storage/staging"


def mostrar_encabezado():

    inicio = datetime.datetime.now()

    print(Fore.LIGHTCYAN_EX + ">" * ANCHO)
    print("|||| LAST.FM TOP ARTISTS STAGING PROCESSOR ||||".center(ANCHO))
    print("<" * ANCHO + Style.RESET_ALL)

    print(
        Fore.LIGHTYELLOW_EX
        + "[Inicio]".ljust(10),
        inicio.strftime("%Y-%m-%d %H:%M:%S")
        + Style.RESET_ALL
    )


def formato_numero(numero):

    return f"{numero:,}".replace(",", ".")


def obtener_ultimo_raw(usuario):

    ruta_usuario = f"{ruta_raw}/{usuario}"

    if not os.path.exists(ruta_usuario):

        raise FileNotFoundError(
            f"No existe RAW para el usuario '{usuario}'"
        )

    archivos = [
        archivo
        for archivo in os.listdir(ruta_usuario)
        if archivo.startswith("top_artists_raw_")
        and archivo.endswith(".json")
    ]

    if not archivos:

        raise FileNotFoundError(
            "No se encontraron archivos RAW de artistas"
        )

    archivos.sort(reverse=True)

    return os.path.join(ruta_usuario, archivos[0])


def procesar_artistas(raw_data):

    artistas_staging = []

    for pagina in raw_data["paginas"]:

        artistas = pagina["topartists"]["artist"]

        for artista in artistas:

            artista_staging = {

                "rank": int(
                    artista.get("@attr", {}).get("rank", 0)
                ),

                "artist_name": artista.get("name"),

                "playcount": int(
                    artista.get("playcount", 0)
                ),

                "artist_url": artista.get("url"),

                "artist_mbid": artista.get("mbid") or None
            }

            artistas_staging.append(artista_staging)

    return artistas_staging


def guardar_json(artistas, archivo_json):

    with open(archivo_json, "w", encoding="utf-8") as json_file:

        json.dump(
            artistas,
            json_file,
            ensure_ascii=False,
            indent=2
        )


def guardar_csv(artistas, archivo_csv):

    columnas = [
        "rank",
        "artist_name",
        "playcount",
        "artist_url",
        "artist_mbid"
    ]

    with open(
        archivo_csv,
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=columnas
        )

        writer.writeheader()

        writer.writerows(artistas)


def main():

    parser = argparse.ArgumentParser(
        description="Procesa top artistas RAW a STAGING"
    )

    parser.add_argument("usuario")

    args = parser.parse_args()

    mostrar_encabezado()

    print()

    print(
        Fore.LIGHTMAGENTA_EX
        + f"Procesando top artistas RAW de {args.usuario}..."
        + Style.RESET_ALL
    )

    archivo_raw = obtener_ultimo_raw(args.usuario)

    print()

    print(
        Fore.LIGHTCYAN_EX
        + "Archivo RAW detectado:"
        + Style.RESET_ALL
    )

    print(archivo_raw)

    with open(archivo_raw, "r", encoding="utf-8") as raw_file:

        raw_data = json.load(raw_file)

    artistas_staging = procesar_artistas(raw_data)

    ruta_usuario_staging = (
        f"{ruta_staging}/{args.usuario}"
    )

    os.makedirs(ruta_usuario_staging, exist_ok=True)

    archivo_json = (
        f"{ruta_usuario_staging}/top_artists_staging.json"
    )

    archivo_csv = (
        f"{ruta_usuario_staging}/top_artists_staging.csv"
    )

    guardar_json(
        artistas_staging,
        archivo_json
    )

    guardar_csv(
        artistas_staging,
        archivo_csv
    )

    print()

    print(
        Fore.LIGHTGREEN_EX
        + f"✓ Artistas procesados: "
        + formato_numero(len(artistas_staging))
        + Style.RESET_ALL
    )

    print()

    print(
        Fore.LIGHTGREEN_EX
        + "✓ Archivos STAGING generados:"
        + Style.RESET_ALL
    )

    print(archivo_json)
    print(archivo_csv)

    print()


if __name__ == "__main__":
    main()