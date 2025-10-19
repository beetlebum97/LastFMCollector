import sys
import requests
import json
import datetime
import time
import os
import csv
import argparse
import concurrent.futures
import getpass

from colorama import init, Fore, Style
init()


# API_KEY se definirá interactivamente
API_KEY = None
API_URL = "http://ws.audioscrobbler.com/2.0/"

def mostrar_encabezado():
    """Muestra el encabezado con la hora actual"""
    inicio = datetime.datetime.now()
    print(Fore.CYAN + ">" * 60)
    print("|||| LAST.FM COLLECTOR ||||".center(60))
    print("<" * 60 + Style.RESET_ALL)
    print(Fore.YELLOW + "[Inicio]".ljust(10), inicio.strftime("%Y-%m-%d %H:%M:%S") + Style.RESET_ALL)
    return inicio

def solicitar_api_key():
    """Solicita la API key interactivamente con 3 intentos"""
    global API_KEY
    
    intentos = 3
    for intento in range(intentos):
        try:
            print(f"\nIntroduce tu API key de Last.fm (intento {intento + 1}/{intentos}):")
            api_key = getpass.getpass("API key: ").strip()
            
            if not api_key:
                print(Fore.LIGHTRED_EX + "✗ La API key no puede estar vacía." + Style.RESET_ALL)
                continue
            
            # Validar formato básico (debería ser alfanumérico)
            if not api_key.replace('-', '').replace('_', '').isalnum():
                print(Fore.LIGHTRED_EX + "✗ Formato inválido de API key." + Style.RESET_ALL)
                continue
            
            # Validar que la API key funciona haciendo una prueba simple
            if validar_api_key_en_servidor(api_key):
                API_KEY = api_key
                print(Fore.GREEN + "✓ API key válida y verificada" + Style.RESET_ALL)
                return True
            else:
                print(Fore.LIGHTRED_EX + "✗ API key no válida o sin permisos" + Style.RESET_ALL)
                
        except KeyboardInterrupt:
            print("\nOperación cancelada por el usuario.")
            sys.exit(1)
        except Exception as e:
            print(Fore.LIGHTRED_EX + f"✗ Error validando API key: {e}" + Style.RESET_ALL)
    
    print(Fore.LIGHTRED_EX + "\n✗ Demasiados intentos fallidos. Saliendo..." + Style.RESET_ALL)
    return False

def validar_api_key_en_servidor(api_key):
    """Valida que la API key funcione correctamente con el servidor de Last.fm"""
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
    except (json.JSONDecodeError, KeyError):
        return False

def validar_api_key_configurada():
    """Valida que se haya configurado una API key válida"""
    if API_KEY is None:
        if not solicitar_api_key():
            sys.exit(1)

def configurar_argumentos():
    """Configura y parsea los argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Extrae datos de Last.fm para un usuario específico',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python lastfm.py <usuario>                         # Extrae todos los datos
  python lastfm.py <usuario> --resumen               # Solo estadísticas resumidas
  python lastfm.py <usuario> --artistas              # Solo artistas
  python lastfm.py <usuario> --discos                # Solo discos
  python lastfm.py <usuario> --canciones             # Solo canciones
  python lastfm.py <usuario> --scrobbles             # Solo scrobbles
  python lastfm.py <usuario> --artistas --discos     # Artistas y discos
        """
    )
    
    parser.add_argument('usuario', 
                       help='Nombre de usuario de Last.fm')
    
    parser.add_argument('--resumen', 
                       action='store_true',
                       help='Mostrar solo un resumen de estadísticas')
    
    parser.add_argument('--artistas', 
                       action='store_true',
                       help='Extraer artistas más escuchados')
    
    parser.add_argument('--canciones', 
                       action='store_true',
                       help='Extraer canciones más escuchadas')
    
    parser.add_argument('--discos', 
                       action='store_true',
                       help='Extraer discos más escuchados')
    
    parser.add_argument('--scrobbles', 
                       action='store_true',
                       help='Extraer historial de scrobbles')
    
    return parser.parse_args()

def obtener_estadistica_resumida(usuario, metodo, root):
    """Obtiene una estadística específica de Last.fm para un usuario (versión resumen)"""
    params = {
        "method": metodo,
        "user": usuario,
        "api_key": API_KEY,
        "format": "json",
        "limit": 1,
        "page": 1
    }

    try:
        resp = requests.get(API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if "error" in data:
            raise ValueError(f"Error {data['error']}: {data.get('message', 'Usuario no válido o no encontrado')}")

        return int(data[root]["@attr"]["total"])
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise ValueError(f"El usuario '{usuario}' no existe en Last.fm")
        else:
            raise ValueError(f"Error HTTP {e.response.status_code}: {e}")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error de conexión: {e}")
    except (KeyError, ValueError) as e:
        if "error" in str(e):
            raise
        try:
            if "error" in data:
                raise ValueError(f"Error {data['error']}: {data.get('message', 'Usuario no válido o no encontrado')}")
        except:
            pass
        raise ValueError(f"Error procesando datos: {e}")

def obtener_estadisticas_usuario(usuario):
    """Obtiene todas las estadísticas para un usuario utilizando concurrencia"""
    estadisticas = [
        ("user.getTopArtists", "topartists", "ARTISTAS"),
        ("user.getTopAlbums", "topalbums", "DISCOS"),
        ("user.getTopTracks", "toptracks", "CANCIONES"),
        ("user.getLovedTracks", "lovedtracks", "FAVORITAS"),
        ("user.getRecentTracks", "recenttracks", "SCROBBLES") 
    ]
    
    resultados = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_stat = {
            executor.submit(obtener_estadistica_resumida, usuario, metodo, root): (metodo, nombre)
            for metodo, root, nombre in estadisticas
        }
        
        for future in concurrent.futures.as_completed(future_to_stat):
            _, nombre = future_to_stat[future]
            try:
                resultado = future.result()
                resultados[nombre] = resultado
            except ValueError as e:
                print(f"Error: {e}")
                return None
    
    return {nombre: resultados[nombre] for nombre, _, _ in [est[2::-1] for est in estadisticas] if nombre in resultados}

def procesar_resumen(usuario):
    """Procesa y muestra el resumen de estadísticas del usuario"""
    print(f"Obteniendo información del usuario '{usuario}' ...\n")
    
    try:
        tiempo_inicio = time.time()
        
        resultados = obtener_estadisticas_usuario(usuario)
        
        if resultados:
            print(Fore.CYAN + "RESUMEN DE ESTADÍSTICAS:" + Style.RESET_ALL)
            print(Fore.CYAN + "-" * 30 + Style.RESET_ALL)
            for nombre, valor in resultados.items():
                print(Fore.CYAN + f"→ {nombre:<10}: {formato_numero(valor)}" + Style.RESET_ALL)
            
            tiempo_total = time.time() - tiempo_inicio
            print(f"\nConsulta completada en {tiempo_total:.2f} segundos.")
            return len(resultados)
        else:
            return 0
            
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"Error obteniendo resumen: {e}")
        return 0
        

def mostrar_progreso(pagina, total_paginas):
    porcentaje = (pagina / total_paginas) * 100
    ancho_barra = 20
    llenado = int((porcentaje / 100) * ancho_barra)
    barra = '█' * llenado + '░' * (ancho_barra - llenado)

    if porcentaje == 100:
        porcentaje_str = "100%"  # sin decimales
    else:
        porcentaje_str = f"{porcentaje:5.1f}%"

    #Limpiar toda la línea antes de escribir
    linea = f"{barra} {porcentaje_str} ({pagina}/{total_paginas})"
    # Asegurar que la línea ocupe al menos 50 caracteres con espacios
    sys.stdout.write(f"\r{linea:<50}")
    sys.stdout.flush()

def main():
    inicio = mostrar_encabezado()
    
    # Configurar argumentos
    args = configurar_argumentos()
    
    # Solicitar API key interactivamente
    validar_api_key_configurada()
    
    usuario = args.usuario
    
    # Si se solicita resumen, ejecutar solo esa funcionalidad
    if args.resumen:
        procesar_resumen(usuario)
        return
    
    # Si no se especifica ninguna opción (excepto resumen), extraer todo
    if not any([args.artistas, args.canciones, args.discos, args.scrobbles]):
        extraer_todo = True
        print("No se especificaron opciones. Extrayendo todos los datos...")
    else:
        extraer_todo = False
    
    ruta = os.path.abspath(os.path.dirname(__file__))
    
    print(f"\nComprobando existencia del usuario {usuario}...")
    
    # Verificar si el usuario existe antes de proceder
    if not usuario_existe(usuario):
        print(Fore.LIGHTRED_EX + f"✗ El usuario '{usuario}' no existe en Last.fm" + Style.RESET_ALL)
        sys.exit(1)
    
    print(f"Usuario verificado ✓")
    
    # Crear la carpeta de salida
    os.makedirs(f'listados/{usuario}', exist_ok=True)
    
    resultados = {}
    
    try:
        # Extraer artistas
        if extraer_todo or args.artistas:
            print(Fore.MAGENTA + f"\n{'='*20} ARTISTAS {'='*20}" + Style.RESET_ALL)
            print(f"Obteniendo artistas escuchados por {usuario}...")
            contador = procesar_artistas(usuario)
            resultados['artistas'] = contador
            
        # Extraer discos
        if extraer_todo or args.discos:
            print(Fore.MAGENTA + f"\n{'='*20} DISCOS {'='*20}" + Style.RESET_ALL)
            print(f"Obteniendo discos escuchados por {usuario}...")
            contador = procesar_discos(usuario)
            resultados['discos'] = contador
        
        # Extraer canciones
        if extraer_todo or args.canciones:
            print(Fore.MAGENTA + f"\n{'='*20} CANCIONES {'='*20}" + Style.RESET_ALL)
            print(f"Obteniendo canciones escuchadas por {usuario}...")
            contador = procesar_canciones(usuario)
            resultados['canciones'] = contador
        
        # Extraer scrobbles
        if extraer_todo or args.scrobbles:
            print(Fore.MAGENTA + f"\n{'='*20} SCROBBLES {'='*20}" + Style.RESET_ALL)
            print(f"Obteniendo historial de scrobbles de {usuario}...")
            contador = procesar_scrobbles(usuario)
            resultados['scrobbles'] = contador
        
        # Mostrar resumen final
        mostrar_resumen_final(usuario, ruta, resultados, inicio)
        
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        sys.exit(1)

def mostrar_resumen_final(usuario, ruta, resultados, inicio):
    """Muestra el resumen final de la ejecución"""
    print(Fore.CYAN + f"\n{'='*60}")
    print("RESUMEN FINAL")
    print(f"{'='*60}" + Style.RESET_ALL)

    
    for tipo, contador in resultados.items():
        print(Fore.GREEN + f"✓ {tipo.capitalize()} registrados: {formato_numero(contador)}" + Style.RESET_ALL)
        archivo_json = f'listados/{usuario}/lastfm_{usuario}_{tipo}.json'
        archivo_csv = f'listados/{usuario}/lastfm_{usuario}_{tipo}.csv'
        print(Fore.MAGENTA + f"   JSON: {ruta}/{archivo_json}" + Style.RESET_ALL)
        print(Fore.MAGENTA + f"   CSV:  {ruta}/{archivo_csv}" + Style.RESET_ALL)
        print()
    
    # Finalización
    fin = datetime.datetime.now()
    print(Fore.YELLOW + "[Fin]", fin.strftime("%Y-%m-%d %H:%M:%S") + Style.RESET_ALL)
    
    # Calcular duración
    duracion = fin - inicio
    total_segundos = int(duracion.total_seconds())
    
    if total_segundos < 60:
        print(f"Tiempo total de ejecución: {total_segundos} segundos")
    else:
        horas, resto = divmod(total_segundos, 3600)
        minutos, segundos = divmod(resto, 60)
        if horas > 0:
            print(f"Tiempo total de ejecución: {horas} horas, {minutos} minutos y {segundos} segundos")
        else:
            print(f"Tiempo total de ejecución: {minutos} minutos y {segundos} segundos")

def formato_numero(numero):
    """Formatea un número con separadores de miles usando puntos"""
    return f"{numero:,}".replace(",", ".")

def usuario_existe(usuario):
    """Verifica si un usuario existe en Last.fm antes de proceder"""
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "user.getInfo",
        "user": usuario,
        "api_key": API_KEY,
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 404:
            return False
        elif response.status_code == 403:
            print("Error: API key inválida o sin permisos")
            sys.exit(1)
        
        response.raise_for_status()
        data = json.loads(response.text)
        
        if "error" in data:
            if data["error"] == 6:
                return False
            else:
                print(f"Error de Last.fm: {data.get('message', 'Error desconocido')}")
                return False
        
        if "user" in data and "name" in data["user"]:
            return True
        
        return False
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return False
        else:
            print(f"Error HTTP {e.response.status_code}: {e}")
            return False
    except requests.exceptions.RequestException as e:
        print(Fore.LIGHTRED_EX + f"✗ Error de conexión: {e}" + Style.RESET_ALL)
        return False
    except Exception as e:
        print(Fore.LIGHTRED_EX + f"✗ Error inesperado: {e}" + Style.RESET_ALL)
        return False

def hacer_solicitud_con_reintentos(url, params, max_intentos=3, retraso_base=2):
    """Realiza una solicitud HTTP con reintentos en caso de error"""
    for intento in range(max_intentos):
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 404:
                raise ValueError(f"Error: El usuario no existe en Last.fm")
            elif response.status_code == 403:
                raise ValueError("Error: API key inválida o sin permisos")
            
            response.raise_for_status()
            data = json.loads(response.text)
            
            if "error" in data:
                if data["error"] == 6:
                    raise ValueError(f"Error: El usuario no existe en Last.fm")
                else:
                    raise ValueError(f"Error de Last.fm: {data.get('message', 'Error desconocido')}")
            
            return data
            
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            if isinstance(e, requests.exceptions.HTTPError) and e.response is not None:
                codigo = e.response.status_code
                mensaje = f"{codigo} Server Error"
            else:
                mensaje = type(e).__name__

            if intento < max_intentos - 1:
                tiempo_espera = retraso_base ** intento
                print(Fore.LIGHTRED_EX + f"✗ Error en solicitud (reintento {intento+1}/{max_intentos}): {mensaje}" + Style.RESET_ALL)
                print(Fore.LIGHTRED_EX + f"✗ Esperando {tiempo_espera} segundos antes de reintentar..." + Style.RESET_ALL)
                time.sleep(tiempo_espera)
            else:
                print(Fore.LIGHTRED_EX + f"✗ Error después de {max_intentos} intentos: {mensaje}") 
                raise

        except ValueError:
            raise
    
    raise ValueError("Error inesperado en solicitudes HTTP")

def procesar_artistas(usuario):
    """Procesa y guarda los artistas más escuchados"""
    url = "http://ws.audioscrobbler.com/2.0/"
    limite = 200
    pagina = 1
    total_paginas = 1
    contador = 0
    delay = 0.25
    
    archivo_json = f'listados/{usuario}/lastfm_{usuario}_artistas.json'
    archivo_csv = f'listados/{usuario}/lastfm_{usuario}_artistas.csv'
    
    # Lista para almacenar todos los artistas
    artistas_list = []
    
    with open(archivo_csv, 'w', encoding='utf-8', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';')
        csv_writer.writerow(['Puesto', 'Artista', 'Scrobbles'])
        
        while pagina <= total_paginas:
            params = {
                "method": "user.getTopArtists",
                "user": usuario,
                "api_key": API_KEY,
                "format": "json",
                "limit": limite,
                "page": pagina
            }
            
            response = hacer_solicitud_con_reintentos(url, params)
            
            if pagina == 1:
                total_paginas = int(response['topartists']['@attr']['totalPages'])
                total_artistas = int(response['topartists']['@attr'].get('total', 0))
                print(f"Total de artistas a procesar: {formato_numero(total_artistas)} en {formato_numero(total_paginas)} páginas")
            
            if pagina % 10 == 0 or pagina == 1:
                mostrar_progreso(pagina, total_paginas)
            
            for artista in response['topartists']['artist']:
                rank = artista['@attr']['rank']
                name = artista['name']
                playcount = artista['playcount']
                
                # Agregar al JSON
                artistas_list.append({
                    'puesto': int(rank),
                    'artista': name,
                    'scrobbles': int(playcount)
                })
                
                # Escribir en CSV
                csv_writer.writerow([rank, name, playcount])
                contador += 1
            
            pagina += 1
            if pagina <= total_paginas:
                time.sleep(delay)
    
    # Guardar JSON
    with open(archivo_json, 'w', encoding='utf-8') as json_file:
        json.dump({
            'usuario': usuario,
            'total': contador,
            'fecha_generacion': datetime.datetime.now().isoformat(),
            'artistas': artistas_list
        }, json_file, ensure_ascii=False, indent=2)
    
    mostrar_progreso(total_paginas, total_paginas)
    print() 
    
    return contador

def procesar_canciones(usuario):
    """Procesa y guarda las canciones más escuchadas"""
    url = "http://ws.audioscrobbler.com/2.0/"
    limite = 200
    pagina = 1
    total_paginas = 1
    contador = 0
    delay = 0.25
    
    archivo_json = f'listados/{usuario}/lastfm_{usuario}_canciones.json'
    archivo_csv = f'listados/{usuario}/lastfm_{usuario}_canciones.csv'
    
    # Lista para almacenar todas las canciones
    canciones_list = []
    
    with open(archivo_csv, 'w', encoding='utf-8', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';')
        csv_writer.writerow(['Puesto', 'Canción', 'Artista', 'Scrobbles'])
        
        while pagina <= total_paginas:
            params = {
                "method": "user.getTopTracks",
                "user": usuario,
                "api_key": API_KEY,
                "format": "json",
                "limit": limite,
                "page": pagina
            }
            
            response = hacer_solicitud_con_reintentos(url, params)
            
            if pagina == 1:
                total_paginas = int(response['toptracks']['@attr']['totalPages'])
                total_canciones = int(response['toptracks']['@attr'].get('total', 0))
                print(f"Total de canciones a procesar: {formato_numero(total_canciones)} en {formato_numero(total_paginas)} páginas")
            
            if pagina % 10 == 0 or pagina == 1:
                mostrar_progreso(pagina, total_paginas)

            
            for cancion in response['toptracks']['track']:
                rank = cancion['@attr']['rank']
                name = cancion['name']
                artist = cancion['artist']['name']
                playcount = cancion['playcount']
                
                # Agregar al JSON
                canciones_list.append({
                    'puesto': int(rank),
                    'cancion': name,
                    'artista': artist,
                    'scrobbles': int(playcount)
                })
                
                # Escribir en CSV
                csv_writer.writerow([rank, name, artist, playcount])
                contador += 1
            
            pagina += 1
            if pagina <= total_paginas:
                time.sleep(delay)
    
    # Guardar JSON
    with open(archivo_json, 'w', encoding='utf-8') as json_file:
        json.dump({
            'usuario': usuario,
            'total': contador,
            'fecha_generacion': datetime.datetime.now().isoformat(),
            'canciones': canciones_list
        }, json_file, ensure_ascii=False, indent=2)
    
    mostrar_progreso(total_paginas, total_paginas)
    print() 
    
    return contador

def procesar_discos(usuario):
    """Procesa y guarda los discos más escuchados"""
    url = "http://ws.audioscrobbler.com/2.0/"
    limite = 200
    pagina = 1
    total_paginas = 1
    contador = 0
    delay = 0.25
    
    archivo_json = f'listados/{usuario}/lastfm_{usuario}_discos.json'
    archivo_csv = f'listados/{usuario}/lastfm_{usuario}_discos.csv'
    
    # Lista para almacenar todos los discos
    discos_list = []
    
    with open(archivo_csv, 'w', encoding='utf-8', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';')
        csv_writer.writerow(['Puesto', 'Disco', 'Artista', 'Scrobbles'])
        
        while pagina <= total_paginas:
            params = {
                "method": "user.getTopAlbums",
                "user": usuario,
                "api_key": API_KEY,
                "format": "json",
                "limit": limite,
                "page": pagina
            }
            
            response = hacer_solicitud_con_reintentos(url, params)
            
            if pagina == 1:
                total_paginas = int(response['topalbums']['@attr']['totalPages'])
                total_discos = int(response['topalbums']['@attr'].get('total', 0))
                print(f"Total de discos a procesar: {formato_numero(total_discos)} en {formato_numero(total_paginas)} páginas")
            
            if pagina % 10 == 0 or pagina == 1:
                mostrar_progreso(pagina, total_paginas)
            
            for disco in response['topalbums']['album']:
                rank = disco['@attr']['rank']
                name = disco['name']
                artist = disco['artist']['name']
                playcount = disco['playcount']
                
                # Agregar al JSON
                discos_list.append({
                    'puesto': int(rank),
                    'disco': name,
                    'artista': artist,
                    'scrobbles': int(playcount)
                })
                
                # Escribir en CSV
                csv_writer.writerow([rank, name, artist, playcount])
                contador += 1
            
            pagina += 1
            if pagina <= total_paginas:
                time.sleep(delay)
    
    # Guardar JSON
    with open(archivo_json, 'w', encoding='utf-8') as json_file:
        json.dump({
            'usuario': usuario,
            'total': contador,
            'fecha_generacion': datetime.datetime.now().isoformat(),
            'discos': discos_list
        }, json_file, ensure_ascii=False, indent=2)
    
    mostrar_progreso(total_paginas, total_paginas)
    print() 
    
    return contador

def procesar_scrobbles(usuario):
    """Procesa y guarda el historial de scrobbles"""
    url = "http://ws.audioscrobbler.com/2.0/"
    limite = 200
    pagina = 1
    total_paginas = 1
    contador = 0
    delay = 0.25
    
    archivo_json = f'listados/{usuario}/lastfm_{usuario}_scrobbles.json'
    archivo_csv = f'listados/{usuario}/lastfm_{usuario}_scrobbles.csv'
    
    # Lista para almacenar todos los scrobbles
    scrobbles_list = []
    
    with open(archivo_csv, 'w', encoding='utf-8', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';')
        csv_writer.writerow(['Fecha', 'Canción', 'Disco', 'Artista', 'ID'])
        
        while pagina <= total_paginas:
            params = {
                "method": "user.getRecentTracks",
                "user": usuario,
                "api_key": API_KEY,
                "format": "json",
                "limit": limite,
                "page": pagina,
                "extended": 0
            }
            
            response = hacer_solicitud_con_reintentos(url, params)
            
            total_scrobbles = int(response['recenttracks']['@attr']['total'])
            total_scrobbles_reales = total_scrobbles
            
            if pagina == 1:
                total_paginas = int(response['recenttracks']['@attr']['totalPages'])
                print(f"Total de scrobbles a procesar: {formato_numero(total_scrobbles)} en {formato_numero(total_paginas)} páginas")
            
            if pagina % 10 == 0 or pagina == 1:
                mostrar_progreso(pagina, total_paginas)
            
            for reproduccion in response['recenttracks']['track']:
                if '@attr' in reproduccion and reproduccion['@attr'].get('nowplaying') == 'true':
                    fecha = 'Reproduciendo ahora'
                    id_scrobble = 'N/A'
                    now_playing = True
                else:
                    fecha = reproduccion.get('date', {}).get('#text', 'Fecha desconocida')
                    id_scrobble = total_scrobbles_reales - contador
                    now_playing = False
                
                name = reproduccion['name']
                album = reproduccion['album']['#text']
                artist = reproduccion['artist']['#text']
                
                # Agregar al JSON
                scrobbles_list.append({
                    'fecha': fecha,
                    'cancion': name,
                    'disco': album,
                    'artista': artist,
                    'id': id_scrobble if not now_playing else 'N/A',
                    'reproduciendo_ahora': now_playing
                })
                
                # Escribir en CSV
                csv_writer.writerow([fecha, name, album, artist, id_scrobble])
                
                if fecha != 'Reproduciendo ahora':
                    contador += 1
            
            pagina += 1
            if pagina <= total_paginas:
                time.sleep(delay)
    
    # Guardar JSON
    with open(archivo_json, 'w', encoding='utf-8') as json_file:
        json.dump({
            'usuario': usuario,
            'total': contador,
            'fecha_generacion': datetime.datetime.now().isoformat(),
            'scrobbles': scrobbles_list
        }, json_file, ensure_ascii=False, indent=2)
    
    mostrar_progreso(total_paginas, total_paginas)
    print() 
    
    return contador

if __name__ == "__main__":
    main()
