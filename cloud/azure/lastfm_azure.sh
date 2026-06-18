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

ansible-playbook -i ansible/inventario.ini ansible/deploy.yml


# =================================== #
# PYTHON: PIPELINE INTERACTIVO        #
# =================================== #
echo "=== 5. PIPELINE LAST.FM (INTERACTIVO) ==="
echo "⚙️ El contenedor está instalando en segundo plano las dependencias..."

# El cronómetro SOLO se ejecuta la primera vez
for i in {60..1}; do
    echo -ne "⏳ Por favor, espera $i segundos... \r"
    sleep 1
done
echo -e "\n✅ Dependencias instaladas con éxito."

# Creamos la lista (array) para guardar los usuarios exitosos
USUARIOS_PROCESADOS=()

# INICIO DEL BUCLE PRINCIPAL
while true; do
    echo "--------------------------------------------------------"
    read -p "👤 Introduce el usuario de Last.fm a procesar: " LASTFM_USER < /dev/tty
    
    echo "Conectando al contenedor y ejecutando el código..."
    
    # Envolvemos la llamada a Python en un IF. Si Python falla, Bash NO explotará.
    if ssh -tt -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa azureuser@$IP_SERVIDOR "sudo docker exec -it -w /app/data-pipeline lastfm_fastapi_prod python run-pipeline.py $LASTFM_USER" < /dev/tty; then
        
        # Este bloque SOLO se ejecuta si run-pipeline.py termina con ÉXITO
        echo "--------------------------------------------------------"
        echo "📥 Inyectando los datos de $LASTFM_USER en PostgreSQL..."
        ssh -n -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa azureuser@$IP_SERVIDOR "sudo docker exec -w /app/backend lastfm_fastapi_prod bash -c 'DB_HOST=lastfm_postgres_prod python load_database.py $LASTFM_USER'"
        
        # Añadimos el usuario a nuestra lista de éxitos
        USUARIOS_PROCESADOS+=("$LASTFM_USER")
        
    else
        # Este bloque se ejecuta si el usuario NO EXISTE o la API Key falla
        echo "--------------------------------------------------------"
        echo "⚠️ Hubo un problema al descargar a '$LASTFM_USER' (revisa los errores arriba)."
        echo "⏭️ Saltando la inyección en base de datos para proteger el sistema..."
    fi
    
    echo "--------------------------------------------------------"
    # Mini-bucle para validar la respuesta exacta (s o n)
    while true; do
        read -p "🔄 ¿Quieres descargar y procesar otro usuario? (s/n): " RESPUESTA < /dev/tty
        
        if [[ "$RESPUESTA" == "s" || "$RESPUESTA" == "S" ]]; then
            break # Sale de este mini-bucle y vuelve arriba a pedir el usuario
            
        elif [[ "$RESPUESTA" == "n" || "$RESPUESTA" == "N" ]]; then
            echo "Saliendo del procesador de usuarios..."
            break 2 # Rompe el mini-bucle y TAMBIÉN el bucle principal
            
        else
            echo "❌ Respuesta no válida. Por favor, introduce 's' para Sí o 'n' para No."
        fi
    done
done

# ================= #
# RESUMEN FINAL     #
# ================= #
echo "=========================================="
echo "🎉 ¡DESPLIEGUE Y PROCESAMIENTO COMPLETADO!"
echo "=========================================="
echo "📋 Usuarios procesados e inyectados con éxito:"

# Bucle para imprimir cada usuario de la lista
if [ ${#USUARIOS_PROCESADOS[@]} -eq 0 ]; then
    echo "   (Ninguno)"
else
    for u in "${USUARIOS_PROCESADOS[@]}"; do
        echo "   ✅ $u"
    done
fi

echo "=========================================="
echo "🌐 Abre tu Dashboard interactivo en:"
echo "👉 http://$IP_SERVIDOR:8000"
echo "=========================================="
