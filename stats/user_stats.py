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

ANCHO = shutil.get_terminal_size().columns

def mostrar_encabezado():

    inicio = datetime.datetime.now()

    print(Fore.LIGHTCYAN_EX + ">" * ANCHO)
    print("|||| LAST.FM USER STATS ||||".center(ANCHO))
    print("<" * ANCHO + Style.RESET_ALL)

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

            print(
                f"\nIntroduce tu API key de Last.fm "
                f"(intento {intento + 1}/{intentos}):"
            )

            api_key = getpass.getpass("API key: ").strip()

            if not api_key:

                print(
                    Fore.LIGHTRED_EX
                    + "✗ La API key no puede estar vacía."
                    + Style.RESET_ALL
                )

                continue

            if not validar_api_key_en_servidor(api_key):

                print(
                    Fore.LIGHTRED_EX
                    + "✗ API key no válida o sin permisos"
                    + Style.RESET_ALL
                )

                continue

            API_KEY = api_key

            print(
                Fore.LIGHTGREEN_EX
                + "✓ API key válida y verificada"
                + Style.RESET_ALL
            )

            return

        except KeyboardInterrupt:

            print("\nOperación cancelada por el usuario.")
            sys.exit(1)

    print(
        Fore.LIGHTRED_EX
        + "\n✗ Demasiados intentos fallidos. Saliendo..."
        + Style.RESET_ALL
    )

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

        fecha_registro = datetime.datetime.fromtimestamp(
            int(usuario_data["registered"]["unixtime"])
        )

        return {
            "pais": usuario_data.get("country", "Desconocido"),
            "registrado": fecha_registro.strftime("%Y-%m-%d")
        }

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error de conexión: {e}")



def obtener_top_artistas(usuario, limite=5):
    params = {
        "method": "user.getTopArtists",
        "user": usuario,
        "api_key": API_KEY,
        "format": "json",
        "limit": limite
    }

    response = requests.get(API_URL, params=params, timeout=10)
    data = response.json()

    artistas = []

    for artista in data["topartists"]["artist"]:
        artistas.append({
            "nombre": artista["name"],
            "scrobbles": artista["playcount"]
        })

    return artistas


def obtener_top_albums(usuario, limite=5):
    params = {
        "method": "user.getTopAlbums",
        "user": usuario,
        "api_key": API_KEY,
        "format": "json",
        "limit": limite
    }

    response = requests.get(API_URL, params=params, timeout=10)
    data = response.json()

    albums = []

    for album in data["topalbums"]["album"]:
        albums.append({
            "album": album["name"],
            "artista": album["artist"]["name"],
            "scrobbles": album["playcount"]
        })

    return albums


def obtener_top_tracks(usuario, limite=5):
    params = {
        "method": "user.getTopTracks",
        "user": usuario,
        "api_key": API_KEY,
        "format": "json",
        "limit": limite
    }

    response = requests.get(API_URL, params=params, timeout=10)
    data = response.json()

    tracks = []

    for track in data["toptracks"]["track"]:
        tracks.append({
            "track": track["name"],
            "artista": track["artist"]["name"],
            "scrobbles": track["playcount"]
        })

    return tracks


def obtener_ultimos_scrobbles(usuario, limite=5):
    params = {
        "method": "user.getRecentTracks",
        "user": usuario,
        "api_key": API_KEY,
        "format": "json",
        "limit": limite
    }

    response = requests.get(API_URL, params=params, timeout=10)
    data = response.json()

    tracks = []

    for track in data["recenttracks"]["track"]:

        fecha = "Ahora"

        if "date" in track:
            fecha = track["date"]["#text"]

        tracks.append({
            "track": track["name"],
            "artista": track["artist"]["#text"],
            "fecha": fecha
        })

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

        futures = {
            executor.submit(obtener_estadistica, usuario, metodo, root): nombre
            for metodo, root, nombre in estadisticas
        }

        for future in concurrent.futures.as_completed(futures):
            nombre = futures[future]
            resultados[nombre] = future.result()

    print()
    print(Fore.LIGHTCYAN_EX + "=" * ANCHO)
    print(f"USUARIO: {usuario}".center(ANCHO))
    print("=" * ANCHO + Style.RESET_ALL)
    
    orden_estadisticas = [
    "ARTISTAS",
    "ALBUMS",
    "CANCIONES",
    "FAVORITAS",
    "SCROBBLES"
    ]
    
    print()    
    
    print(
    Fore.LIGHTCYAN_EX
    + f"{'PAÍS':<12}: {info_usuario['pais']}"
    + Style.RESET_ALL
    )

    print(
    Fore.LIGHTCYAN_EX
    + f"{'MIEMBRO':<12}: {info_usuario['registrado']}"
    + Style.RESET_ALL
    ) 

    for nombre in orden_estadisticas:
    
        valor = resultados[nombre]
    
        print(
            Fore.LIGHTCYAN_EX
            + f"{nombre:<12}: {formato_numero(valor)}"
            + Style.RESET_ALL
        )

    print()

    print(Fore.LIGHTMAGENTA_EX + "TOP ARTISTAS" + Style.RESET_ALL)

    for idx, artista in enumerate(obtener_top_artistas(usuario), start=1):
        print(f"{idx}. {artista['nombre']} ({artista['scrobbles']})")

    print()

    print(Fore.LIGHTMAGENTA_EX + "TOP ALBUMS" + Style.RESET_ALL)

    for idx, album in enumerate(obtener_top_albums(usuario), start=1):
        print(
            f"{idx}. {album['album']} - "
            f"{album['artista']} ({album['scrobbles']})"
        )

    print()

    print(Fore.LIGHTMAGENTA_EX + "TOP CANCIONES" + Style.RESET_ALL)

    for idx, track in enumerate(obtener_top_tracks(usuario), start=1):
        print(
            f"{idx}. {track['track']} - "
            f"{track['artista']} ({track['scrobbles']})"
        )

    print()

    print(Fore.LIGHTMAGENTA_EX + "ÚLTIMOS SCROBBLES" + Style.RESET_ALL)

    for track in obtener_ultimos_scrobbles(usuario):
        print(
            f"- {track['track']} | "
            f"{track['artista']} | "
            f"{track['fecha']}"
        )
    

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

        print(
            Fore.RED
            + f"✗ {error}"
            + Style.RESET_ALL
        )

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
