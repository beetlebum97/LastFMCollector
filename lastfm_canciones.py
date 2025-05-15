import sys
import requests
import json
import datetime
import time
import os
import csv
import locale

API_KEY = "Introduce tu clave"

def main():
    if len(sys.argv) < 2:
        print("Error: Debes proporcionar un nombre de usuario")
        sys.exit(1)
        
    usuario = sys.argv[1]
    ruta = os.path.abspath(os.path.dirname(__file__))
    
    inicio = datetime.datetime.now()
    print("[Inicio]", inicio.strftime("%Y-%m-%d %H:%M:%S"))
    print(f"Comprobando existencia del usuario {usuario}...")
    
    # Primero verificamos si el usuario existe antes de crear carpetas o archivos
    if not usuario_existe(usuario):
        print(f"Error: El usuario '{usuario}' no existe o no es válido en Last.fm")
        sys.exit(1)
    
    print(f"Usuario verificado. Obteniendo canciones reproducidas por {usuario}...")
    
    # Crear la carpeta 'listados/usuario' solo si el usuario existe
    os.makedirs(f'listados/{usuario}', exist_ok=True)
    
    # Archivos de salida
    archivo_salida = f'listados/{usuario}/lastfm_{usuario}_canciones.txt'
    archivo_csv = f'listados/{usuario}/lastfm_{usuario}_canciones.csv'
    
    try:
        # Procesar directamente las páginas y escribir al archivo
        contador = procesar_canciones(usuario, archivo_salida, archivo_csv)
        
        # Resultado con formato de separación de miles
        print(f"-> Canciones registradas: {formato_numero(contador)}")
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
        data = json.loads(response.text)
        
        # Si hay un error en la respuesta, el usuario no existe
        if "error" in data:
            return False
        
        # Verificamos que la respuesta tenga los campos esperados
        if "user" in data and "name" in data["user"]:
            return True
        
        return False
    except Exception:
        # En caso de error de conexión u otro problema, asumimos que no existe
        return False

def procesar_canciones(usuario, archivo_salida, archivo_csv):
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
        csv_writer.writerow(['Puesto', 'Canción', 'Artista', 'Scrobbles'])  # Cabecera
        
        while pagina <= total_paginas:
            params = {
                "method": "user.getTopTracks",
                "user": usuario,
                "api_key": API_KEY,
                "format": "json",
                "limit": limite,
                "page": pagina
            }
            
            # Realizar solicitud con manejo de errores y reintentos
            response = hacer_solicitud_con_reintentos(url, params)
            
            # Ya no necesitamos esta verificación aquí porque comprobamos que el usuario existe al inicio
            # but we'll keep a safeguard just in case
            if "error" in response:
                raise ValueError(f"Error inesperado: {response.get('message', 'Error desconocido')}")
            
            # Información sobre progreso
            if pagina == 1:
                total_paginas = int(response['toptracks']['@attr']['totalPages'])
                total_canciones = int(response['toptracks']['@attr'].get('total', 0))
                print(f"Total de canciones a procesar: {formato_numero(total_canciones)} en {formato_numero(total_paginas)} páginas")
            
            if pagina % 10 == 0 or pagina == 1:
                print(f"Procesando página {formato_numero(pagina)}/{formato_numero(total_paginas)} ({(pagina/total_paginas*100):.1f}%)")

            # Procesar y escribir los resultados página por página
            for cancion in response['toptracks']['track']:
                rank = cancion['@attr']['rank']
                name = cancion['name']
                artist = cancion['artist']['name']
                playcount = cancion['playcount']
                
                # Escribir al archivo de texto
                txt_file.write(f"Puesto: {rank} | Canción: {name} | Artista: {artist} | Scrobbles: {playcount}\n")
                
                # Escribir al archivo CSV
                csv_writer.writerow([rank, name, artist, playcount])
                
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
            response.raise_for_status()  # Lanza excepción en caso de error HTTP
            return json.loads(response.text)
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
    
    # Esto no debería ejecutarse nunca, pero por si acaso
    raise ValueError("Error inesperado en solicitudes HTTP")

if __name__ == "__main__":
    main()
