#!/usr/bin/env bash

# ========================================== #
# CONFIGURACIÓN ROBUSTA DEL SCRIPT ($? !=0)  #
# ========================================== #
set -eo pipefail

echo "=========================================="
echo "🚀 LAST.FM COLLECTOR - DESPLIEGUE AZURE   "
echo "=========================================="
echo "Fecha: $(date)"
echo "IP Pública origen: $(curl -s --connect-timeout 2 https://checkip.amazonaws.com || echo 'No disponible')"
echo "=========================================="

# ====================== #
# VERIFICACIONES PREVIAS #
# ====================== #
command -v terraform >/dev/null 2>&1 || { echo "❌ Terraform no instalado"; exit 1; }
command -v ansible >/dev/null 2>&1 || { echo "❌ Ansible no instalado"; exit 1; }

# ==================================================== #
# DESCARGAR REPOSITORIO (RAMA DEVELOP)                 #
# ==================================================== #
echo "=== 1. DESCARGA DEL CÓDIGO ==="
rm -rf /tmp/LastFMCollector
git clone -b develop https://github.com/beetlebum97/LastFMCollector.git /tmp/LastFMCollector
cd /tmp/LastFMCollector/cloud/azure

# ====================================================== #
# CREAR CLAVE SSH PARA AZURE                             #
# ====================================================== #
echo "=== 2. CLAVE SSH ==="
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "Generando nueva clave SSH RSA 4096..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N "" -q
    chmod 600 ~/.ssh/id_rsa
    chmod 644 ~/.ssh/id_rsa.pub
    echo "✓ Clave SSH generada"
else
    echo "✓ Clave SSH ya existe"
fi

# ===========================#
# TERRAFORM: INFRAESTRUCTURA #
# ===========================#
echo "=== 3. TERRAFORM (INFRAESTRUCTURA) ==="
cd terraform
terraform init
terraform apply -auto-approve

IP_SERVIDOR=$(terraform output -raw public_ip_address)
if [ -z "$IP_SERVIDOR" ] || [ "$IP_SERVIDOR" = "null" ]; then
    echo "❌ Error: No se pudo obtener la IP."
    exit 1
fi
cd ..
echo "✓ Infraestructura creada. IP: $IP_SERVIDOR"

# =================================== #
# ANSIBLE: CONFIGURACIÓN DEL SERVIDOR #
# =================================== #
echo "=== 4. ANSIBLE (CONFIGURACIÓN) ==="
mkdir -p ansible
cat > ansible/inventario.ini <<EOF
[debian12]
$IP_SERVIDOR ansible_user=azureuser ansible_ssh_private_key_file=~/.ssh/id_rsa ansible_ssh_common_args='-o StrictHostKeyChecking=no'
EOF

echo "⏳ Esperando a que el servidor SSH responda..."
sleep 30

# Ansible instalará Docker, clonará el repo y arrancará docker-compose (BD + FastAPI)
ansible-playbook -i ansible/inventario.ini ansible/deploy.yml

# =================================== #
# PYTHON: PIPELINE INTERACTIVO        #
# =================================== #
echo "=== 5. PIPELINE LAST.FM (INTERACTIVO) ==="
echo "Conectando al contenedor para iniciar la descarga de datos..."
echo "--------------------------------------------------------"

# Nos conectamos por SSH en modo TTY (-t) y ejecutamos el script de Python dentro del Docker.
# Esto hará que los input() de Python aparezcan en la pantalla actual.
ssh -t -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa azureuser@$IP_SERVIDOR << 'EOF'
  # Ejecutamos el pipeline (Preguntará API Key y Usuario)
  sudo docker exec -it -w /app/data-pipeline lastfm_fastapi_prod bash -c "python run-pipeline.py"
  
  echo "--------------------------------------------------------"
  echo "📥 Inyectando los datos descargados en PostgreSQL..."
  sudo docker exec -w /app/backend lastfm_fastapi_prod bash -c "DB_HOST=lastfm_postgres_prod python load_database.py"
EOF

# ================= #
# RESUMEN FINAL     #
# ================= #
echo "=========================================="
echo "🎉 ¡DESPLIEGUE Y PROCESAMIENTO COMPLETADO!"
echo "=========================================="
echo "🌐 Abre tu Dashboard interactivo en:"
echo "👉 http://$IP_SERVIDOR:8000"
echo "=========================================="
