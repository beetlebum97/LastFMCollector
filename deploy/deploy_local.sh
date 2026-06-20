#!/usr/bin/env bash

# ========================================== #
# CONFIGURACIÓN ROBUSTA DEL SCRIPT ($? !=0)  #
# ========================================== #
set -eo pipefail

echo "=========================================="
echo "💻 LAST.FM COLLECTOR - DESPLIEGUE LOCAL   "
echo "=========================================="

# =================================== #
# 1. ENTORNO VIRTUAL Y DEPENDENCIAS   #
# =================================== #
echo "=== 1. ENTORNO VIRTUAL Y DEPENDENCIAS ==="
if [ ! -d "venv" ]; then
    echo "⚙️  Creando entorno virtual (venv)..."
    python3 -m venv venv
fi

echo "🟢 Activando entorno virtual..."
source venv/bin/activate

echo "📦 Instalando dependencias (requirements.txt)..."
# Asegúrate de tener un requirements.txt en la raíz del proyecto
pip install -r requirements.txt -q
echo "✅ Dependencias instaladas."

# =================================== #
# 2. DESCARGA DE DATOS (PIPELINE)     #
# =================================== #
echo -e "\n=== 2. PIPELINE LAST.FM (DESCARGA LOCAL) ==="

USUARIOS_PROCESADOS=()

while true; do
    echo "--------------------------------------------------------"
    read -p "👤 Introduce el usuario de Last.fm a procesar: " LASTFM_USER || true
    
    echo "🚀 Ejecutando pipeline ETL para $LASTFM_USER..."
    
    # Gracias a pathlib, podemos lanzarlo directamente desde la raíz
    if python3 data-pipeline/run-pipeline.py "$LASTFM_USER"; then
        # Si tiene éxito, lo guardamos en la lista
        USUARIOS_PROCESADOS+=("$LASTFM_USER")
    else
        echo "⚠️ Hubo un problema al descargar a '$LASTFM_USER'."
    fi
    
    echo "--------------------------------------------------------"
    # Mini-bucle para validar la respuesta exacta (s o n)
    while true; do
        read -p "🔄 ¿Quieres descargar otro usuario? (s/n): " RESPUESTA || true
        
        if [[ "$RESPUESTA" == "s" || "$RESPUESTA" == "S" ]]; then
            break # Sale de este mini-bucle y vuelve a pedir usuario
            
        elif [[ "$RESPUESTA" == "n" || "$RESPUESTA" == "N" ]]; then
            echo "Finalizando recolección de usuarios..."
            break 2 # Rompe ambos bucles
            
        else
            echo "❌ Respuesta no válida. Por favor, introduce 's' para Sí o 'n' para No."
        fi
    done
done

# Verificamos si al menos hay un usuario procesado
if [ ${#USUARIOS_PROCESADOS[@]} -eq 0 ]; then
    echo "❌ No se procesó ningún usuario con éxito. Saliendo del script..."
    exit 0
fi

# =================================== #
# 3. LEVANTAR BASE DE DATOS DOCKER    #
# =================================== #
echo -e "\n=== 3. LEVANTANDO BASE DE DATOS (DOCKER) ==="

# Comprobamos si el contenedor ya está en ejecución
if [ "$(docker ps -q -f name=lastfm_postgres)" ]; then
    echo "✅ El contenedor 'lastfm_postgres' ya está corriendo. Saltando inicialización..."
else
    echo "🚀 Levantando contenedor de PostgreSQL..."
    docker compose -f backend/docker-compose.yml up -d
    
    # Pequeña pausa SOLO si lo acabamos de levantar
    echo "⏳ Esperando 5 segundos a que PostgreSQL esté listo..."
    sleep 5
fi

# =================================== #
# 4. CARGAR DATOS EN POSTGRESQL       #
# =================================== #
echo -e "\n=== 4. INYECTANDO DATOS EN POSTGRESQL ==="

for u in "${USUARIOS_PROCESADOS[@]}"; do
    echo "📥 Procesando inyección para: $u"
    # Gracias a pathlib, ya no necesitamos hacer cd backend
    python3 backend/load_database.py "$u"
done

# =================================== #
# 5. RESUMEN FINAL                    #
# =================================== #
# Imprimimos el resumen ANTES de levantar FastAPI, ya que uvicorn bloquea la terminal
echo -e "\n=========================================="
echo "🎉 ¡DESPLIEGUE LOCAL COMPLETADO!"
echo "=========================================="
echo "📋 Usuarios procesados e inyectados con éxito:"

for u in "${USUARIOS_PROCESADOS[@]}"; do
    echo "   ✅ $u"
done

# Capturamos la IP local de la máquina (ej: 192.168.1.50)
IP_LOCAL=$(hostname -I | awk '{print $1}')

echo "=========================================="
echo "🌐 Abre tu Dashboard interactivo en:"
echo "👉 http://$IP_LOCAL:8000"
echo "=========================================="

# =================================== #
# 6. LEVANTAR FRONTEND / API          #
# =================================== #
echo -e "\n🚀 Levantando servidor FastAPI... (Pulsa Ctrl+C para detener la aplicación)"
# Gracias a pathlib, uvicorn entiende el módulo directamente desde la raíz
uvicorn api:app --host 0.0.0.0 --port 8000 --reload --app-dir backend
