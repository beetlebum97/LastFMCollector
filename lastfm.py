#!/usr/bin/env python3
import sys
import requests
import datetime
import time
import concurrent.futures

# Constantes
API_KEY = "Introduce tu clave"
API_URL = "http://ws.audioscrobbler.com/2.0/"

def mostrar_encabezado():
    """Muestra el encabezado con la hora actual"""
    inicio = datetime.datetime.now()
    print()
    print("[Fecha/Hora]", inicio.strftime("%Y-%m-%d %H:%M:%S"))
    print("LastFMCollector")

def obtener_estadistica(usuario, metodo, root):
    """Obtiene una estadística específica de Last.fm para un usuario"""
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
        resp.raise_for_status()  # Lanza una excepción para errores HTTP
        data = resp.json()

        if "error" in data:
            raise ValueError(f"Error {data['error']}: {data.get('message', 'Usuario no válido o no encontrado')}")

        # Solo un nivel de clave antes de @attr.total
        return int(data[root]["@attr"]["total"])
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error de conexión: {e}")
    except (KeyError, ValueError) as e:
        if "error" in data:
            raise ValueError(f"Error {data['error']}: {data.get('message', 'Usuario no válido o no encontrado')}")
        raise ValueError(f"Error procesando datos: {e}")

def obtener_estadisticas_usuario(usuario):
    """Obtiene todas las estadísticas para un usuario utilizando concurrencia"""
    # Orden específico: Artistas, Discos, Canciones, Scrobbles, Favoritos
    estadisticas = [
        ("user.getTopArtists", "topartists", "ARTISTAS"),
        ("user.getTopAlbums", "topalbums", "DISCOS"),
        ("user.getTopTracks", "toptracks", "CANCIONES"),
        ("user.getLovedTracks", "lovedtracks", "FAVORITOS"),
        ("user.getRecentTracks", "recenttracks", "SCROBBLES") 
    ]
    
    resultados = {}
    
    # Usar ThreadPoolExecutor para hacer las llamadas en paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Crear un diccionario de futuros
        future_to_stat = {
            executor.submit(obtener_estadistica, usuario, metodo, root): (metodo, nombre)
            for metodo, root, nombre in estadisticas
        }
        
        # Procesar los resultados a medida que estén disponibles
        for future in concurrent.futures.as_completed(future_to_stat):
            _, nombre = future_to_stat[future]
            try:
                resultado = future.result()
                resultados[nombre] = resultado
            except ValueError as e:
                # Si falla una consulta, mostrar el error y abortar
                print(f"Error: {e}")
                return None
    
    # Devolver resultados en el orden específico
    return {nombre: resultados[nombre] for nombre, _, _ in [est[2::-1] for est in estadisticas] if nombre in resultados}

def main():
    """Función principal del programa"""
    mostrar_encabezado()
    
    # Verificar argumentos
    if len(sys.argv) != 2:
        print("Error: Debes proporcionar un nombre de usuario como argumento.")
        print("Uso: python lastfm.py <nombre_usuario>")
        sys.exit(1)
        
    usuario = sys.argv[1]
    print(f"Obteniendo información del usuario '{usuario}' ...\n")
    
    try:
        # Medir el tiempo de ejecución
        tiempo_inicio = time.time()
        
        # Obtener estadísticas
        resultados = obtener_estadisticas_usuario(usuario)
        
        if resultados:
            # Imprimir resultados
            for nombre, valor in resultados.items():
                print(f" + {nombre:<9} =======> {valor:,}".replace(",", "."))
            
            tiempo_total = time.time() - tiempo_inicio
            print(f"\nConsulta completada en {tiempo_total:.2f} segundos.")
        
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.")
        sys.exit(1)

if __name__ == "__main__":
    main()
