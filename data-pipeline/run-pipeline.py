import sys
import subprocess
import argparse
import time
import datetime
from pathlib import Path
from colorama import init, Fore, Style

init()

# Calculamos la raíz dinámicamente (sube 1 nivel: data-pipeline -> raíz)
BASE_DIR = Path(__file__).resolve().parent.parent

# Definimos las rutas ABSOLUTAS a los scripts
SCRIPTS = [
    str(BASE_DIR / "data-pipeline" / "src" / "download_raw.py"),
    str(BASE_DIR / "data-pipeline" / "src" / "process_staging.py"),
    str(BASE_DIR / "data-pipeline" / "src" / "transform_curated.py")
]


def formatear_tiempo(segundos_totales):
    minutos = int(segundos_totales // 60)
    segundos = segundos_totales % 60
    if minutos == 0:
        return f"{segundos:.2f} segundos"
    elif minutos == 1:
        return f"1 minuto y {int(segundos)} segundos"
    else:
        return f"{minutos} minutos y {int(segundos)} segundos"

def main():
    parser = argparse.ArgumentParser(description="Orquestador Maestro del Pipeline ETL de Last.fm")
    parser.add_argument("usuario", help="Usuario de Last.fm a procesar")
    parser.add_argument("opciones", nargs="*", 
                        help="Qué procesar (ej. 'artistas' o 'canciones'). Si no pones nada, ejecuta TODO el pipeline.")

    args = parser.parse_args()
    
    tiempo_inicio = time.time()
    
    print(Fore.LIGHTCYAN_EX + "=" * 60)
    print("🚀 INICIANDO PIPELINE ETL COMPLETO (Medallion Architecture)".center(60))
    print("=" * 60 + Style.RESET_ALL)
    print(Fore.LIGHTYELLOW_EX + f"Usuario: {args.usuario}" + Style.RESET_ALL)
    print(Fore.LIGHTYELLOW_EX + f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + Style.RESET_ALL)

    # Construimos los argumentos extra (si el usuario puso "artistas canciones", se lo pasamos)
    argumentos_extra = args.opciones if args.opciones else []

    # Bucle que ejecuta cada script secuencialmente
    for script in SCRIPTS:
        comando = [sys.executable, script, args.usuario] + argumentos_extra
        
        try:
            # subprocess.run ejecuta el comando y espera a que termine
            resultado = subprocess.run(comando, check=True)
            
        except subprocess.CalledProcessError as e:
            # Si un script falla (ej. API Key incorrecta), abortamos el pipeline para evitar un efecto dominó
            print(Fore.LIGHTRED_EX + f"\n[!] ERROR CRÍTICO: El script {script} falló." + Style.RESET_ALL)
            print(Fore.LIGHTRED_EX + "Abortando la ejecución del pipeline para proteger los datos..." + Style.RESET_ALL)
            sys.exit(1)
            
        except KeyboardInterrupt:
            print(Fore.LIGHTRED_EX + "\n[!] Ejecución cancelada por el usuario." + Style.RESET_ALL)
            sys.exit(1)

    tiempo_total = time.time() - tiempo_inicio
    
    print(Fore.LIGHTCYAN_EX + "=" * 60)
    print("✨ PIPELINE EJECUTADO CON ÉXITO ✨".center(60))
    print("=" * 60 + Style.RESET_ALL)
    print(Fore.LIGHTGREEN_EX + f"Tiempo total de procesamiento end-to-end: {formatear_tiempo(tiempo_total)}\n" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
