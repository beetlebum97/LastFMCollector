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
    print("|||| LAST.FM SCROBBLES STAGING PROCESSOR ||||".center(ANCHO))
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
        if archivo.startswith("scrobbles_raw_")
        and archivo.endswith(".json")
    ]

    if not archivos:

        raise FileNotFoundError(
            "No se encontraron archivos RAW de scrobbles"
        )

    archivos.sort(reverse=True)

    return os.path.join(ruta_usuario, archivos[0])


def procesar_scrobbles(raw_data):

    scrobbles_staging = []

    tracks = raw_data["tracks"]

    for track in tracks:

        fecha = track.get("date", {})

        uts = fecha.get("uts")

        timestamp = (
            datetime.datetime.utcfromtimestamp(
                int(uts)
            ).isoformat()
            if uts
            else None
        )

        scrobble_staging = {

            "artist_name": (
                track.get("artist", {}).get("name")
            ),

            "artist_mbid": (
                track.get("artist", {}).get("mbid")
                or None
            ),

            "track_name": track.get("name"),

            "track_mbid": (
                track.get("mbid")
                or None
            ),

            "album_name": (
                track.get("album", {}).get("#text")
            ),

            "album_mbid": (
                track.get("album", {}).get("mbid")
                or None
            ),

            "track_url": track.get("url"),

            "loved": int(
                track.get("loved", 0)
            ),

            "streamable": int(
                track.get("streamable", 0)
            ),

            "nowplaying": (
                track.get("@attr", {}).get("nowplaying")
                == "true"
            ),

            "timestamp_uts": (
                int(uts)
                if uts
                else None
            ),

            "timestamp_iso": timestamp
        }

        scrobbles_staging.append(
            scrobble_staging
        )

    return scrobbles_staging


def guardar_json(scrobbles, archivo_json):

    with open(archivo_json, "w", encoding="utf-8") as json_file:

        json.dump(
            scrobbles,
            json_file,
            ensure_ascii=False,
            indent=2
        )


def guardar_csv(scrobbles, archivo_csv):

    columnas = [
        "artist_name",
        "artist_mbid",
        "track_name",
        "track_mbid",
        "album_name",
        "album_mbid",
        "track_url",
        "loved",
        "streamable",
        "nowplaying",
        "timestamp_uts",
        "timestamp_iso"
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

        writer.writerows(scrobbles)


def main():

    parser = argparse.ArgumentParser(
        description="Procesa scrobbles RAW a STAGING"
    )

    parser.add_argument("usuario")

    args = parser.parse_args()

    mostrar_encabezado()

    print()

    print(
        Fore.LIGHTMAGENTA_EX
        + f"Procesando scrobbles RAW de {args.usuario}..."
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

    scrobbles_staging = procesar_scrobbles(raw_data)

    ruta_usuario_staging = (
        f"{ruta_staging}/{args.usuario}"
    )

    os.makedirs(ruta_usuario_staging, exist_ok=True)

    archivo_json = (
        f"{ruta_usuario_staging}/scrobbles_staging.json"
    )

    archivo_csv = (
        f"{ruta_usuario_staging}/scrobbles_staging.csv"
    )

    guardar_json(
        scrobbles_staging,
        archivo_json
    )

    guardar_csv(
        scrobbles_staging,
        archivo_csv
    )

    print()

    print(
        Fore.LIGHTGREEN_EX
        + f"✓ Scrobbles procesados: "
        + formato_numero(len(scrobbles_staging))
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