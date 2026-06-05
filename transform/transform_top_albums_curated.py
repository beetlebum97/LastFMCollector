import json
import csv
import os
import argparse
import datetime
import shutil

from colorama import init, Fore, Style

init()

ANCHO = shutil.get_terminal_size().columns

ruta_staging = "../storage/staging"
ruta_curated = "../storage/curated"


def mostrar_encabezado():

    inicio = datetime.datetime.now()

    print(Fore.LIGHTCYAN_EX + ">" * ANCHO)
    print("|||| LAST.FM TOP ALBUMS CURATED PROCESSOR ||||".center(ANCHO))
    print("<" * ANCHO + Style.RESET_ALL)

    print(
        Fore.LIGHTYELLOW_EX
        + "[Inicio]".ljust(10),
        inicio.strftime("%Y-%m-%d %H:%M:%S")
        + Style.RESET_ALL
    )


def formato_numero(numero):

    return f"{numero:,}".replace(",", ".")


def obtener_staging(usuario):

    archivo = (
        f"{ruta_staging}/{usuario}/top_albums_staging.json"
    )

    if not os.path.exists(archivo):

        raise FileNotFoundError(
            f"No existe STAGING para '{usuario}'"
        )

    return archivo


def procesar_curated(albums_staging):

    total_playcount = sum(
        album["playcount"]
        for album in albums_staging
    )

    albums_curated = []

    for album in albums_staging:

        album_curated = {

            "rank": album["rank"],

            "album_name": album["album_name"],

            "artist_name": album["artist_name"],

            "playcount": album["playcount"],

            "playcount_pct": round(
                (
                    album["playcount"]
                    / total_playcount
                ) * 100,
                2
            )
        }

        albums_curated.append(
            album_curated
        )

    return albums_curated


def guardar_json(datos, archivo_json):

    with open(
        archivo_json,
        "w",
        encoding="utf-8"
    ) as json_file:

        json.dump(
            datos,
            json_file,
            ensure_ascii=False,
            indent=2
        )


def guardar_csv(datos, archivo_csv):

    columnas = [
        "rank",
        "album_name",
        "artist_name",
        "playcount",
        "playcount_pct"
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

        writer.writerows(datos)


def main():

    parser = argparse.ArgumentParser(
        description="Procesa albums STAGING a CURATED"
    )

    parser.add_argument("usuario")

    args = parser.parse_args()

    mostrar_encabezado()

    print()

    print(
        Fore.LIGHTMAGENTA_EX
        + f"Procesando albums STAGING de "
        + f"{args.usuario}..."
        + Style.RESET_ALL
    )

    try:

        archivo_staging = obtener_staging(
            args.usuario
        )

    except FileNotFoundError as error:

        print()

        print(
            Fore.LIGHTRED_EX
            + f"✗ {error}"
            + Style.RESET_ALL
        )

        print()

        return

    except Exception as error:

        print()

        print(
            Fore.LIGHTRED_EX
            + f"✗ Error inesperado: {error}"
            + Style.RESET_ALL
        )

        print()

        return

    print()

    print(
        Fore.LIGHTCYAN_EX
        + "Archivo STAGING detectado:"
        + Style.RESET_ALL
    )

    print(archivo_staging)

    with open(
        archivo_staging,
        "r",
        encoding="utf-8"
    ) as staging_file:

        albums_staging = json.load(
            staging_file
        )

    albums_curated = procesar_curated(
        albums_staging
    )

    ruta_usuario_curated = (
        f"{ruta_curated}/{args.usuario}"
    )

    os.makedirs(
        ruta_usuario_curated,
        exist_ok=True
    )

    archivo_json = (
        f"{ruta_usuario_curated}"
        "/top_albums_curated.json"
    )

    archivo_csv = (
        f"{ruta_usuario_curated}"
        "/top_albums_curated.csv"
    )

    guardar_json(
        albums_curated,
        archivo_json
    )

    guardar_csv(
        albums_curated,
        archivo_csv
    )

    print()

    print(
        Fore.LIGHTGREEN_EX
        + f"✓ Albums procesados: "
        + formato_numero(
            len(albums_curated)
        )
        + Style.RESET_ALL
    )

    print()

    print(
        Fore.LIGHTGREEN_EX
        + "✓ Archivos CURATED generados:"
        + Style.RESET_ALL
    )

    print(archivo_json)
    print(archivo_csv)

    print()


if __name__ == "__main__":
    main()
