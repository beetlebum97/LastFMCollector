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
    print("|||| LAST.FM TOP ALBUMS STAGING PROCESSOR ||||".center(ANCHO))
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
        if archivo.startswith("top_albums_raw_")
        and archivo.endswith(".json")
    ]

    if not archivos:

        raise FileNotFoundError(
            "No se encontraron archivos RAW de albums"
        )

    archivos.sort(reverse=True)

    return os.path.join(ruta_usuario, archivos[0])


def procesar_albums(raw_data):

    albums_staging = []

    for pagina in raw_data["paginas"]:

        albums = pagina["topalbums"]["album"]

        for album in albums:

            album_staging = {

                "rank": int(
                    album.get("@attr", {}).get("rank", 0)
                ),

                "album_name": album.get("name"),

                "artist_name": (
                    album.get("artist", {}).get("name")
                ),

                "playcount": int(
                    album.get("playcount", 0)
                ),

                "album_url": album.get("url"),

                "album_mbid": album.get("mbid") or None,

                "artist_mbid": (
                    album.get("artist", {}).get("mbid")
                    or None
                )
            }

            albums_staging.append(album_staging)

    return albums_staging


def guardar_json(albums, archivo_json):

    with open(archivo_json, "w", encoding="utf-8") as json_file:

        json.dump(
            albums,
            json_file,
            ensure_ascii=False,
            indent=2
        )


def guardar_csv(albums, archivo_csv):

    columnas = [
        "rank",
        "album_name",
        "artist_name",
        "playcount",
        "album_url",
        "album_mbid",
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

        writer.writerows(albums)


def main():

    parser = argparse.ArgumentParser(
        description="Procesa top albums RAW a STAGING"
    )

    parser.add_argument("usuario")

    args = parser.parse_args()

    mostrar_encabezado()

    print()

    print(
        Fore.LIGHTMAGENTA_EX
        + f"Procesando top albums RAW de {args.usuario}..."
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

    albums_staging = procesar_albums(raw_data)

    ruta_usuario_staging = (
        f"{ruta_staging}/{args.usuario}"
    )

    os.makedirs(ruta_usuario_staging, exist_ok=True)

    archivo_json = (
        f"{ruta_usuario_staging}/top_albums_staging.json"
    )

    archivo_csv = (
        f"{ruta_usuario_staging}/top_albums_staging.csv"
    )

    guardar_json(
        albums_staging,
        archivo_json
    )

    guardar_csv(
        albums_staging,
        archivo_csv
    )

    print()

    print(
        Fore.LIGHTGREEN_EX
        + f"✓ Albums procesados: "
        + formato_numero(len(albums_staging))
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