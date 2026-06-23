#!/usr/bin/env bash

# ========================================== #
# CONFIGURACIÓN ROBUSTA DEL SCRIPT ($? !=0)  #
# ========================================== #
set -eo pipefail

echo "=========================================="
echo "💻 LAST.FM COLLECTOR - DESPLIEGUE LOCAL   "
echo "=========================================="

# =================================== #
# 1. VERIFICACIONES PREVIAS           #
# =================================== #
echo "=== 1. VERIFICANDO DEPENDENCIAS ==="
MISSING_DEPS=0

command -v python3 >/dev/null 2>&1 || { echo "❌ python3 no está instalado."; MISSING_DEPS=1; }
command -v pip3 >/dev/null 2>&1 || command -v pip >/dev/null 2>&1 || { echo "❌ pip no está instalado."; MISSING_DEPS=1; }
command -v docker >/dev/null 2>&1 || { echo "❌ docker no está instalado."; MISSING_DEPS=1; }
docker compose version >/dev/null 2>&1 || { echo "❌ docker compose no está instalado."; MISSING_DEPS=1; }

if [ $MISSING_DEPS -eq 1 ]; then
    echo "⚠️ Faltan dependencias en tu sistema. El script podría fallar."
    read -p "¿Deseas continuar de todos modos? (s/n): " RESP < /dev/tty || true
    if [[ ! "$RESP" =~ ^[sS]$ ]]; then
        echo "Saliendo del instalador..."
        exit 1
    fi
else
    echo "✅ Todas las dependencias base están instaladas."
fi

# ==================================================== #
# 2. DESCARGAR REPOSITORIO Y PREPARAR DIRECTORIO       #
# ==================================================== #
echo -e "\n=== 2. DIRECTORIO DE INSTALACIÓN ==="
# Usamos $PWD para que por defecto se instale en la carpeta actual de la terminal
read -p "📂 Introduce la ruta base o destino (por defecto: $PWD/LastFMCollector): " INPUT_DIR < /dev/tty || true
INPUT_DIR=${INPUT_DIR:-$PWD/LastFMCollector}

# Resolver la tilde (~) en caso de que el usuario la escriba manualmente (ej: ~/Descargas)
INPUT_DIR="${INPUT_DIR/#\~/$HOME}"

# Auto-completar la carpeta: nos aseguramos de que termine siempre en /LastFMCollector
if [[ "$(basename "$INPUT_DIR")" != "LastFMCollector" ]]; then
    # Quitamos la posible barra final del input y añadimos la carpeta
    INSTALL_DIR="${INPUT_DIR%/}/LastFMCollector"
else
    INSTALL_DIR="$INPUT_DIR"
fi

# Borramos la carpeta específica del proyecto (si no existe, no da error gracias a -f)
echo "🧹 Limpiando instalación previa en '$INSTALL_DIR' (si existe)..."
rm -rf "$INSTALL_DIR"

echo "📥 Clonando el repositorio desde la rama 'develop' en '$INSTALL_DIR'..."
git clone -b develop https://github.com/beetlebum97/LastFMCollector.git "$INSTALL_DIR"
cd "$INSTALL_DIR"

# =================================== #
# 3. ENTORNO VIRTUAL Y DEPENDENCIAS   #
# =================================== #
echo -e "\n=== 3. ENTORNO VIRTUAL Y DEPENDENCIAS (PYTHON) ==="
if [ ! -d "venv" ]; then
    echo "⚙️  Creando entorno virtual (venv)..."
    python3 -m venv venv
fi

echo "🟢 Activando entorno virtual..."
source venv/bin/activate

echo "📦 Instalando dependencias (requirements.txt)..."
pip install -r requirements.txt -q
echo "✅ Dependencias instaladas."

# =================================== #
# 4. DESCARGA DE DATOS (PIPELINE)     #
# =================================== #
echo -e "\n=== 4. PIPELINE LAST.FM (DESCARGA LOCAL) ==="

USUARIOS_PROCESADOS=()

while true; do
    echo "--------------------------------------------------------"
    read -p "👤 Introduce el usuario de Last.fm a procesar: " LASTFM_USER < /dev/tty || true
    
    echo "🚀 Ejecutando pipeline ETL para $LASTFM_USER..."
    
    if python3 data-pipeline/run-pipeline.py "$LASTFM_USER"; then
        USUARIOS_PROCESADOS+=("$LASTFM_USER")
    else
        echo "⚠️ Hubo un problema al descargar a '$LASTFM_USER'."
    fi
    
    echo "--------------------------------------------------------"
    while true; do
        read -p "🔄 ¿Quieres descargar otro usuario? (s/n): " RESPUESTA < /dev/tty || true
        
        if [[ "$RESPUESTA" == "s" || "$RESPUESTA" == "S" ]]; then
            break 
        elif [[ "$RESPUESTA" == "n" || "$RESPUESTA" == "N" ]]; then
            echo "Finalizando recolección de usuarios..."
            break 2 
        else
            echo "❌ Respuesta no válida. Por favor, introduce 's' para Sí o 'n' para No."
        fi
    done
done

if [ ${#USUARIOS_PROCESADOS[@]} -eq 0 ]; then
    echo "❌ No se procesó ningún usuario con éxito. Saliendo del script..."
    exit 0
fi

# =================================== #
# 5. LEVANTAR BASE DE DATOS DOCKER    #
# =================================== #
echo -e "\n=== 5. LEVANTANDO BASE DE DATOS (DOCKER) ==="

if [ "$(docker ps -q -f name=lastfm_postgres)" ]; then
    echo "✅ El contenedor 'lastfm_postgres' ya está corriendo. Saltando inicialización..."
else
    echo "🚀 Levantando contenedor de PostgreSQL..."
    docker compose -f backend/docker-compose.yml up -d
    
    echo "⏳ Esperando 5 segundos a que PostgreSQL esté listo..."
    sleep 5
fi

# =================================== #
# 6. CARGAR DATOS EN POSTGRESQL       #
# =================================== #
echo -e "\n=== 6. INYECTANDO DATOS EN POSTGRESQL ==="

for u in "${USUARIOS_PROCESADOS[@]}"; do
    echo "📥 Procesando inyección para: $u"
    python3 backend/load_database.py "$u"
done

# =================================== #
# 7. RESUMEN FINAL                    #
# =================================== #
echo -e "\n=========================================="
echo "🎉 ¡DESPLIEGUE LOCAL COMPLETADO!"
echo "=========================================="
echo "📋 Usuarios procesados e inyectados con éxito:"

for u in "${USUARIOS_PROCESADOS[@]}"; do
    echo "   ✅ $u"
done

IP_LOCAL=$(hostname -I | awk '{print $1}')

echo "=========================================="
echo "🌐 Abre tu Dashboard interactivo en:"
echo "👉 http://$IP_LOCAL:8000"
echo "=========================================="

# =================================== #
# 8. LEVANTAR FRONTEND / API          #
# =================================== #
echo -e "\n🚀 Levantando servidor FastAPI... (Pulsa Ctrl+C para detener la aplicación)"
uvicorn api:app --host 0.0.0.0 --port 8000 --reload --app-dir backend
