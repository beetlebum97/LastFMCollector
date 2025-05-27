import sys
import requests
import json
import datetime
import time
import os
import csv
import locale

API_KEY = "Introduce tu clave"

def mostrar_encabezado():
    """Muestra el encabezado con la hora actual"""
    inicio = datetime.datetime.now()
    print("[Inicio]", inicio.strftime("%Y-%m-%d %H:%M:%S"))
    return inicio

def validar_api_key():
    """Valida que se haya configurado una API key válida"""
    if API_KEY == "Introduce tu clave" or not API_KEY.strip():
        print("Error: Debes introducir tu clave API de Last.fm en la línea 10 del script.")
        print("Visita https://www.last.fm/api/account/create para obtener una clave API.")
        sys.exit(1)

def main():
    inicio = mostrar_encabezado()
    
    # Verificar argumentos primero
    if len(sys.argv) < 2:
        print("Error: Debes proporcionar un nombre de usuario como argumento.")
        print("Uso: python lastfm_scrobbles.py <nombre_usuario>")
        sys.exit(1)
    
    # Validar API key después de verificar argumentos
    validar_api_key()
        
    usuario = sys.argv[1]
    ruta = os.path.abspath(os.path.dirname(__file__))
    
    print(f"Comprobando existencia del usuario {usuario}...")

    # Primero verificamos si el usuario existe antes de crear carpetas o archivos
    if not usuario_existe(usuario):
        print(f"Error: El usuario '{usuario}' no existe en Last.fm")
        sys.exit(1)
    
    print(f"Usuario verificado. Obteniendo scrobbles de {usuario}...")

    # Crear la carpeta 'listados/usuario' solo si el usuario existe
    os.makedirs(f'listados/{usuario}', exist_ok=True)
    
    # Archivos de salida
    archivo_salida = f'listados/{usuario}/lastfm_{usuario}_scrobbles.txt'
    archivo_csv = f'listados/{usuario}/lastfm_{usuario}_scrobbles.csv'
    
    try:
        # Procesar directamente las páginas y escribir al archivo
        contador = procesar_reproducciones(usuario, archivo_salida, archivo_csv)
        
        # Resultado con formato de separación de miles
        print(f"-> Scrobbles registrados: {formato_numero(contador)}")
        print(f"-> Archivo TXT: {ruta}/{archivo_salida}")
        print(f"-> Archivo CSV: {ruta}/{archivo_csv}")
        
        # Finalización
        fin = datetime.datetime.now()
        print("[Fin]", fin.strftime("%Y-%m-%d %H:%M:%S"))
        
        # Calcular duración
        duracion = fin - inicio
        total_segundos = int(duracion.total_seconds())
        
        if total_segundos < 60:
            print(f"Tiempo de ejecución: {total_segundos} segundos")
        else:
            horas, resto = divmod(total_segundos, 3600)
            minutos, segundos = divmod(resto, 60)
            if horas > 0:
                print(f"Tiempo de ejecución: {horas} horas, {minutos} minutos y {segundos} segundos")
            else:
                print(f"Tiempo de ejecución: {minutos} minutos y {segundos} segundos")
                
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        sys.exit(1)

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
        
        # Manejar errores HTTP específicos
        if response.status_code == 404:
            return False
        elif response.status_code == 403:
            print("Error: API key inválida o sin permisos")
            sys.exit(1)
        
        response.raise_for_status()
        data = json.loads(response.text)
        
        # Si hay un error en la respuesta, el usuario no existe
        if "error" in data:
            if data["error"] == 6:  # Error específico de Last.fm para usuario no encontrado
                return False
            else:
                print(f"Error de Last.fm: {data.get('message', 'Error desconocido')}")
                return False
        
        # Verificamos que la respuesta tenga los campos esperados
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
        print(f"Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False

def procesar_reproducciones(usuario, archivo_salida, archivo_csv):
    url = "http://ws.audioscrobbler.com/2.0/"
    limite = 200  # Aumentado de 50 a 200 (máximo permitido por Last.fm)
    pagina = 1
    total_paginas = 1
    contador = 0
    delay = 0.25  # Retraso entre solicitudes para evitar límites de API
    
    # Abrir los archivos para escritura progresiva
    with open(archivo_salida, 'w', encoding='utf-8') as txt_file, \
         open(archivo_csv, 'w', encoding='utf-8', newline='') as csv_file:
        
        # Configurar el escritor CSV
        csv_writer = csv.writer(csv_file, delimiter=';')
        csv_writer.writerow(['Fecha', 'Canción', 'Disco', 'Artista', 'ID'])  # Cabecera
        
        while pagina <= total_paginas:
            params = {
                "method": "user.getRecentTracks",
                "user": usuario,
                "api_key": API_KEY,
                "format": "json",
                "limit": limite,
                "page": pagina,
                "extended": 0  # No necesitamos info extendida para mayor velocidad
            }
            
            # Realizar solicitud con manejo de errores y reintentos
            response = hacer_solicitud_con_reintentos(url, params)
            
            # Si hay canciones reproduciéndose. el total va cambiando. Estático: reales
            total_scrobbles = int(response['recenttracks']['@attr']['total']) 
            total_scrobbles_reales = total_scrobbles

            # Información sobre progreso
            if pagina == 1:
                total_paginas = int(response['recenttracks']['@attr']['totalPages'])
                total_scrobbles = int(response['recenttracks']['@attr']['total'])
                print(f"Total de scrobbles a procesar: {formato_numero(total_scrobbles)} en {formato_numero(total_paginas)} páginas")
            
            if pagina % 10 == 0 or pagina == 1:
                print(f"Procesando página {formato_numero(pagina)}/{formato_numero(total_paginas)} ({(pagina/total_paginas*100):.1f}%)")
            
            # Procesar y escribir los resultados página por página
            for reproduccion in response['recenttracks']['track']:
                # Verificar si el track está actualmente sonando (no tiene fecha)
                if '@attr' in reproduccion and reproduccion['@attr'].get('nowplaying') == 'true':
                    fecha = 'Reproduciendo ahora'
                    # Para tracks en reproducción, no asignamos ID secuencial
                    id_scrobble = 'N/A'                                                                                                                  
                else:
                    fecha = reproduccion.get('date', {}).get('#text', 'Fecha desconocida')
                    # Calcular ID secuencial (el más antiguo será 1)
                    id_scrobble = total_scrobbles_reales - contador                                                                                                     
                
                name = reproduccion['name']
                album = reproduccion['album']['#text']
                artist = reproduccion['artist']['#text']
                
                # Escribir al archivo de texto
                txt_file.write(f"Fecha: {fecha} | Canción: {name} | Disco: {album} | Artista: {artist} | ID: {id_scrobble} \n")
                
                # Escribir al archivo CSV
                csv_writer.writerow([fecha, name, album, artist, id_scrobble])
                
                # Solo incrementamos el contador para tracks que no están en reproducción
                if fecha != 'Reproduciendo ahora':                                                                                        
                    contador += 1
            
            pagina += 1
            
            # Aplicar retraso controlado entre solicitudes
            if pagina <= total_paginas:
                time.sleep(delay)
    
    return contador

def hacer_solicitud_con_reintentos(url, params, max_intentos=3, retraso_base=2):
    """Realiza una solicitud HTTP con reintentos en caso de error"""
    for intento in range(max_intentos):
        try:
            response = requests.get(url, params=params, timeout=10)
            
            # Manejar errores HTTP específicos
            if response.status_code == 404:
                raise ValueError(f"Error: El usuario no existe en Last.fm")
            elif response.status_code == 403:
                raise ValueError("Error: API key inválida o sin permisos")
            
            response.raise_for_status()  # Lanza excepción en caso de otros errores HTTP
            data = json.loads(response.text)
            
            # Verificar errores específicos de Last.fm
            if "error" in data:
                if data["error"] == 6:
                    raise ValueError(f"Error: El usuario no existe en Last.fm")
                else:
                    raise ValueError(f"Error de Last.fm: {data.get('message', 'Error desconocido')}")
            
            return data
            
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            if intento < max_intentos - 1:
                # Retraso exponencial entre reintentos
                tiempo_espera = retraso_base ** intento
                print(f"Error en solicitud (reintento {intento+1}/{max_intentos}): {str(e)}")
                print(f"Esperando {tiempo_espera} segundos antes de reintentar...")
                time.sleep(tiempo_espera)
            else:
                print(f"Error después de {max_intentos} intentos: {str(e)}")
                raise
        except ValueError:
            # Re-lanzar errores de validación sin reintentos
            raise
    
    # Esto no debería ejecutarse nunca, pero por si acaso
    raise ValueError("Error inesperado en solicitudes HTTP")

if __name__ == "__main__":
    main()