#!/usr/bin/env bash

# ========================================== #
# CONFIGURACIÓN ROBUSTA DEL SCRIPT ($? !=0)  #
# ========================================== #

set -eo pipefail  # Se detiene ante cualquier error

# ======================= #
# INFORMACIÓN DEL ENTORNO #
# ======================= #

echo "=== INICIO DE DESPLIEGUE ==="
echo "Fecha: $(date)"
echo "IP Pública: $(curl -s --connect-timeout 2 https://checkip.amazonaws.com || echo 'No disponible')"
echo "Directorio: $(pwd)"
echo "Sistema: $(uname -srmo)"

# ====================== #
# VERIFICACIONES PREVIAS #
# ====================== #

# Verificar que las herramientas principales estén instaladas
command -v terraform >/dev/null 2>&1 || { echo "Terraform no instalado"; exit 1; }
command -v ansible >/dev/null 2>&1 || { echo "Ansible no instalado"; exit 1; }
command -v python >/dev/null 2>&1 || { echo "Python no instalado"; exit 1; }

# ==================================================== #
# CREAR ESTRUCTURA DE DIRECTORIOS Y DESCARGAR ARCHIVOS #
# ==================================================== #

echo "=== DIRECTORIOS Y ARCHIVOS  ==="

echo "Creando carpetas Python (Data), Terraform (Infraestructura) y Ansible (Configuración)..."
mkdir -p python terraform ansible/app

BASE_URL="https://raw.githubusercontent.com/beetlebum97/LastFMCollector/main"

echo "Descargando scripts LastFMCollector..."
curl -sL "${BASE_URL}/lastfm.py" -o "python/lastfm.py"
curl -sL "${BASE_URL}/lastfm_db.py" -o "python/lastfm_db.py"
chmod 755 python/lastfm*

echo "Descargando archivos de Terraform (Infraestructura)..."
curl -L "${BASE_URL}/azure/terraform/main.tf" -o "terraform/main.tf"
curl -L "${BASE_URL}/azure/terraform/outputs.tf" -o "terraform/outputs.tf"
curl -L "${BASE_URL}/azure/terraform/providers.tf" -o "terraform/providers.tf"
curl -L "${BASE_URL}/azure/terraform/variables.tf" -o "terraform/variables.tf"

echo "Descargando archivos de Ansible (Configuración)..."
curl -L "${BASE_URL}/azure/ansible/site.yml" -o "ansible/site.yml"
curl -L "${BASE_URL}/azure/ansible/frontend.yml" -o "ansible/frontend.yml"
curl -L "${BASE_URL}/azure/ansible/app/app.py" -o "ansible/app/app.py"

# ====================================================== #
# CREAR CLAVE SSH PARA AZURE - CONSIDERANDO CLOUD SHELL  #
# ====================================================== #

echo "=== CLAVE SSH  ==="

# Verificar si ya existe la clave (para no regenerarla innecesariamente)
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "Generando nueva clave SSH RSA 4096..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N "" -q  # -q equivale a > /dev/null
    chmod 600 ~/.ssh/id_rsa
    chmod 644 ~/.ssh/id_rsa.pub
    echo "✓ Clave SSH generada en ~/.ssh/id_rsa"
else
    echo "✓ Clave SSH ya existe en ~/.ssh/id_rsa"
fi

# ===========================#
# TERRAFORM: INFRAESTRUCTURA #
# ===========================#

echo "=== TERRAFORM  ==="

echo "Creando infraestructura: servidor Debian..."
cd terraform

# Inicializar y aplicar
terraform init
terraform apply -auto-approve -input=false

# Actualizar estado
terraform apply -refresh-only -auto-approve -input=false > /dev/null 2>&1

# Obtener outputs
NOMBRE_RG=$(terraform output -raw resource_group_name)
IP_SERVIDOR=$(terraform output -raw public_ip_address)

# Verificación final
if [ -z "$IP_SERVIDOR" ] || [ "$IP_SERVIDOR" = "null" ]; then
    echo "Error: No se pudo obtener la IP después"
    exit 1
fi

echo "✓ Infraestructura desplegada correctamente"
echo "• Resource Group: $NOMBRE_RG"
echo "• IP del servidor: $IP_SERVIDOR"

# Agregar al known_hosts (seguro) 
echo "Agregando $IP_SERVIDOR a known_hosts..."
for i in {1..5}; do
    ssh-keyscan -H $IP_SERVIDOR >> ~/.ssh/known_hosts 2>/dev/null && break
    sleep 2
done

# Conexión SSH para ejecutar comandos y salir automáticamente
ssh -o ConnectTimeout=10 -i ~/.ssh/id_rsa azureuser@$IP_SERVIDOR << 'REMOTE_CMDS'
  echo "Ejecutando comandos en el servidor remoto..."
  hostname
  df -h
  exit
REMOTE_CMDS
echo "Conexión remota correcta."

# =================================== #
# ANSIBLE: CONFIGURACIÓN DEL SERVIDOR #
# =================================== #

echo "=== ANSIBLE  ==="

# Crear inventario
cd ../ansible
cat > inventario.ini <<EOF
[debian12]
$IP_SERVIDOR ansible_user=azureuser ansible_ssh_private_key_file=~/.ssh/id_rsa ansible_python_interpreter=/usr/bin/python3 ansible_port=22
EOF

# Probar conexión remota
ansible debian12 -i inventario.ini -m ping
echo $?

# Ejecutar configuración (docker, nginx y mysql)
ansible-playbook -i inventario.ini site.yml

# ================================== #
# PYTHON: APLICACIÓN LASTFMCOLLECTOR #
# ================================== #

echo "=== PYTHON - LASTFMCOLLECTOR  ==="

# Instalar módulos
cd ../python
echo "Instalando dependencias Python..."
pip install --user requests sqlalchemy pymysql psycopg2

# Función para validar entrada no vacía
validar_entrada() {
    local prompt="$1"
    local intentos=0
    local max_intentos=5
    local valor=""

    while [ $intentos -lt $max_intentos ]; do
        read -p "$prompt" valor
        if [ -n "$valor" ]; then
            echo "$valor"
            return 0
        fi
        echo "❌ Error: Este campo no puede estar vacío."
        ((intentos++))
    done

    echo "❌ Demasiados intentos fallidos. Abortando."
    exit 1
}

# Solicitar usuario de LastFM con validación
usuario=$(validar_entrada "Introduce usuario de LastFM: ")

# Reiniciar contador de intentos
intentos=0
max_intentos=5
puerto=""
motor=""

# Solicitar motor de BBDD con validación
while [ $intentos -lt $max_intentos ]; do
  read -p "Introduce motor BBDD (mysql o postgresql): " motor

  # Validar entrada vacía o inválida
  if [ -z "$motor" ]; then
    echo "❌ Entrada vacía. Introducir 'mysql' o 'postgresql'."
    ((intentos++))
    continue
  fi

  case "$motor" in
    mysql)
      puerto=3306
      break
      ;;
    postgresql)
      puerto=5432
      break
      ;;
    *)
      echo "❌ Motor no válido. Debe ser 'mysql' o 'postgresql'."
      ((intentos++))
      ;;
  esac
done

# Resultado final
if [ -n "$puerto" ]; then
  echo "✅ Motor seleccionado: $motor con puerto $puerto"
else
  echo "🚫 Se alcanzó el número máximo de intentos sin seleccionar un motor válido."
fi

# Mostrar resultados
echo "✅ Usuario: $usuario"
echo "✅ Motor seleccionado: $motor"
echo "✅ Puerto asignado: $puerto"

echo "Comenzando descarga de registros LastFM..."
python lastfm_db.py $usuario $motor $IP_SERVIDOR $puerto david 1234

if [ "$motor" = "mysql" ]; then
	mysql -h $IP_SERVIDOR -u david -p1234 -e "\
	USE lastfm; \
	SELECT
	  (SELECT COUNT(*) FROM artistas) AS 'Artistas',
	  (SELECT COUNT(*) FROM discos) AS 'Discos',
	  (SELECT COUNT(*) FROM canciones) AS 'Canciones',
	  (SELECT COUNT(*) FROM scrobbles) AS 'Scrobbles';"
else
	export PGPASSWORD="1234"
	psql -h $IP_SERVIDOR -U david -d lastfm -c "\
	SELECT
	  (SELECT COUNT(*) FROM artistas) AS \"Artistas\",
	  (SELECT COUNT(*) FROM discos) AS \"Discos\",
	  (SELECT COUNT(*) FROM canciones) AS \"Canciones\",
	  (SELECT COUNT(*) FROM scrobbles) AS \"Scrobbles\";"
	unset PGPASSWORD
fi

# ================= #
# ANSIBLE: FRONTEND #
# ================= #
# Exportar variable DB_DRIVER según el motor elegido
echo " === ANSIBLE: FRONTEND ==="
if [ "$motor" = "mysql" ]; then
  export DB_DRIVER="mysql+pymysql"
else
  export DB_DRIVER="postgresql+psycopg2"
fi

# Ejecutar el playbook deL frontend
cd ../ansible
ansible-playbook -i inventario.ini frontend.yml

# Verificación Frontend

echo "⏳ Verificando despliegue del frontend..."

# Revisar que los contenedores estén corriendo
ssh -i ~/.ssh/id_rsa azureuser@$IP_SERVIDOR <<'EOF'
  echo "👉 Contenedores activos:"
  sudo docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

  echo "👉 Logs últimos 20s de lastfm-frontend:"
  sudo docker logs --since 20s lastfm-frontend || echo "⚠️ No hay logs aún."

  echo "👉 Logs últimos 20s de nginx:"
  sudo docker logs --since 20s nginx || echo "⚠️ No hay logs aún."
EOF

echo "✅ Si todo está correcto, abre en tu navegador: http://$IP_SERVIDOR/lastfm/"
