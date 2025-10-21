# 🚀 Despliegue Azure :cloud:
Esta guía explica cómo desplegar la aplicación **LastFMCollector en Microsoft Azure** utilizando infraestructura como código (Terraform), gestión de configuración (Ansible) y contenedores (Docker). El despliegue automatiza la creación de un entorno completo que incluye:

- Máquina Virtual (Debian 12) con IP pública
- Base de Datos (contenedores de MySQL y PostgreSQL)
- Aplicación Web (Frontend Flask + Nginx como proxy inverso)
- Pipeline de Datos (Integración con API de Last.fm)

**[ ARQUITECTURA ]**

Azure Cloud Shell → Terraform → VM Debian → Ansible → Docker (MySQL / PostgreSQL - Nginx) → Aplicación Flask

**[ REQUISITOS ]**

- Cuenta de Azure activa con suscripción válida
- Acceso al Portal Azure (portal.azure.com)
- Cloud Shell habilitado (Bash)
- Clave API de Last.fm 


## 1. INICIO
### ACCESO A AZURE CLOUD SHELL

1.1 Iniciar sesión en [Portal Azure](https://portal.azure.com/)

1.2 Abrir Cloud Shell (icono >_ en la barra superior).

1.3 Seleccionar entorno Bash.

### DESCARGAR Y EJECUTAR SCRIPT DE DESPLIEGUE

**lastfm_azure.sh** ejecuta todas las acciones. Para lanzarlo ejecutar:
```
curl -L https://raw.githubusercontent.com/beetlebum97/LastFMCollector/main/cloud/azure/lastfm_azure.sh -o lastfm_azure.sh
chmod 755 lastfm_azure.sh
./lastfm_azure.sh
```
Genera la estructura de archivos que implant de la aplicación:

```
.
├── ansible
│   ├── app
│   │   └── app.py
│   ├── frontend.yml
│   ├── inventario.ini
│   └── site.yml
├── lastfm_azure.sh
├── python
│   ├── lastfm.py
│   └── lastfm_db.py
└── terraform
    ├── main.tf
    ├── outputs.tf
    ├── providers.tf
    └── variables.tf
```

## 2. PROCESO AUTOMATIZADO
### FASE 1 - INFRAESTRUCTURA (Terraform)
**Tareas:**
- Creación de Resource Group
- Configuración de red y seguridad
- Implementación de VM Debian 12
- Asignación de IP pública

**Archivos:** main.tf, providers.tf, variables.tf y outputs.tf

**Instrucción principal:** ```terraform init``` ```terraform apply -auto-approve -input=false```

Una vez finalice la creación de infraestructura, estará habilitado el acceso remoto con el usuario azureuser.

```
ssh -i ~/.ssh/id_rsa azureuser@$IP_SERVIDOR
```

``` 
✓ Infraestructura desplegada correctamente
• Resource Group: rg-thankful-marten
• IP del servidor: 23.97.200.242
Agregando 23.97.200.242 a known_hosts...
Pseudo-terminal will not be allocated because stdin is not a terminal.
Linux vm-tf 6.1.0-40-cloud-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.153-1 (2025-09-20) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Ejecutando comandos en el servidor remoto...
vm-tf
Filesystem      Size  Used Avail Use% Mounted on
udev            444M     0  444M   0% /dev
tmpfs            91M  628K   91M   1% /run
/dev/sda1        30G  700M   28G   3% /
tmpfs           455M     0  455M   0% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
/dev/sda15      124M   12M  113M  10% /boot/efi
/dev/sdb1       3.9G   24K  3.7G   1% /mnt
tmpfs            91M     0   91M   0% /run/user/1000
Conexión remota correcta.
```
### FASE 2 - CONFIGURACIÓN (Ansible)
**Tareas:**
- Instalación de Docker y dependencias
- Despliegue de contenedores:
    - MySQL (puerto 3306)
    - PostgreSQL (puerto 5432)
    - Nginx (puerto 80)

**Archivos:** inventario.ini, site.yml

**Instrucción principal:** ```ansible-playbook -i inventario.ini site.yml```

```
=== ANSIBLE  ===
23.97.200.242 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
0

PLAY [debian12] ************************************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [23.97.200.242]

TASK [Instala dependencias y Docker] ***************************************************************************************************************************************
changed: [23.97.200.242]

TASK [Añade clave GPG oficial de Docker] ***********************************************************************************************************************************
changed: [23.97.200.242]

TASK [Añade el repositorio de Docker] **************************************************************************************************************************************
changed: [23.97.200.242]

TASK [Instala docker-ce] ***************************************************************************************************************************************************
changed: [23.97.200.242]

TASK [Asegura que Docker está activo] **************************************************************************************************************************************
ok: [23.97.200.242]

TASK [Lanza nginx con Docker] **********************************************************************************************************************************************
changed: [23.97.200.242]

TASK [Lanza MySQL con Docker] **********************************************************************************************************************************************
changed: [23.97.200.242]

TASK [Esperar hasta que MySQL esté listo para conexiones (máx 60s)] ********************************************************************************************************
changed: [23.97.200.242]

TASK [Crea usuario en MySQL usando shell] **********************************************************************************************************************************
changed: [23.97.200.242]

TASK [Lanza PostgreSQL con Docker] *****************************************************************************************************************************************
changed: [23.97.200.242]

TASK [Esperar hasta que PostgreSQL esté listo para conexiones (máx 60s)] ***************************************************************************************************
changed: [23.97.200.242]

TASK [Crea usuario en PostgreSQL usando shell] *****************************************************************************************************************************
changed: [23.97.200.242]

PLAY RECAP *****************************************************************************************************************************************************************
23.97.200.242              : ok=13   changed=11   unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

### FASE 3 - APLICACIÓN (Python)
**Tareas:**
- Instalación de dependencias Python
- Configuración de clave API de Last.fm
- Descarga de datos del usuario
- Almacenamiento en base de datos

**Archivos:** lastfm_db.py

**Instrucción principal:** ```python lastfm_db.py $usuario $motor $IP_SERVIDOR $puerto david 1234```

El script solicitará la clave API, usuario de lastfm y motor de base de datos para proceder a descargar y guardar los registros. david es el usuario de la bbdd.

```
Introduce usuario de LastFM: hayman3030
Introduce motor BBDD (mysql o postgresql): postgresql
✅ Motor seleccionado: postgresql con puerto 5432
✅ Usuario: hayman3030
✅ Motor seleccionado: postgresql
✅ Puerto asignado: 5432
Comenzando descarga de registros LastFM...
============================================================
Last.FM Collector BBDD Script
============================================================
[Inicio] 2025-09-28 16:31:44

Introduce tu API key de Last.fm (intento 1/3):
API key: 
✓ API key válida y verificada

Verificando usuario 'hayman3030' en Last.fm...
✔ Usuario encontrado

Verificando y creando base de datos si es necesario...
✔ Base de datos 'lastfm' creada en PostgreSQL

Conectando a la base de datos 'lastfm' (postgresql)...
✔ Conexión a la base de datos exitosa

============================================================
INICIANDO EXTRACCIÓN DE DATOS
============================================================

--- Procesando ARTISTAS ---
✔ Tabla 'artistas' creada/verificada
Total de artistas: 450 en 3 páginas
Procesando: 100.0% (3/3) - Insertados: 450
✔ Completado: 450 registros insertados en la tabla 'artistas'

--- Procesando DISCOS ---
✔ Tabla 'discos' creada/verificada
Total de discos: 1.175 en 6 páginas
Procesando: 100.0% (6/6) - Insertados: 1.175
✔ Completado: 1.175 registros insertados en la tabla 'discos'

--- Procesando CANCIONES ---
✔ Tabla 'canciones' creada/verificada
Total de canciones: 10.580 en 53 páginas
Procesando: 100.0% (53/53) - Insertados: 10.580
✔ Completado: 10.580 registros insertados en la tabla 'canciones'

--- Procesando SCROBBLES ---
✔ Tabla 'scrobbles' creada/verificada
Total de scrobbles: 39.698 en 199 páginas
Procesando: 100.0% (199/199) - Insertados: 39.698
✔ Completado: 39.698 registros insertados en la tabla 'scrobbles'

============================================================
RESUMEN FINAL
============================================================
Usuario: hayman3030
Total registros insertados: 51.903
Duración: 0:04:58
[Fin] 2025-09-28 16:36:42
============================================================
 Artistas | Discos | Canciones | Scrobbles 
----------+--------+-----------+-----------
      450 |   1175 |     10580 |     39698
(1 row)
```

### FASE 4 - FRONTEND (Ansible)
**Tareas:**
- Despliegue de aplicación web
- Configuración de Nginx como proxy inverso
- Exposición en puerto 80

**Archivos:** inventario.ini, frontend.yml

**Instrucción principal**: ```ansible-playbook -i inventario.ini frontend.yml```

```
PLAY [debian12] ************************************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [23.97.200.242]

TASK [Crear directorio de la app en el host] *******************************************************************************************************************************
changed: [23.97.200.242]

TASK [Copiar aplicación Flask] *********************************************************************************************************************************************
changed: [23.97.200.242]

TASK [Crear red docker para lastfm] ****************************************************************************************************************************************
changed: [23.97.200.242]

TASK [Crear contenedor frontend (Flask)] ***********************************************************************************************************************************
changed: [23.97.200.242]

TASK [Crear directorio de configuración nginx en el host] ******************************************************************************************************************
changed: [23.97.200.242]

TASK [Copiar configuración nginx para /lastfm] *****************************************************************************************************************************
changed: [23.97.200.242]

TASK [Recrear contenedor nginx con config custom] **************************************************************************************************************************
changed: [23.97.200.242]

PLAY RECAP *****************************************************************************************************************************************************************
23.97.200.242              : ok=8    changed=7    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

⏳ Verificando despliegue del frontend...
Pseudo-terminal will not be allocated because stdin is not a terminal.
Linux vm-tf 6.1.0-40-cloud-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.153-1 (2025-09-20) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
👉 Contenedores activos:
NAMES             STATUS          PORTS
nginx             Up 3 seconds    0.0.0.0:80->80/tcp
lastfm-frontend   Up 13 seconds   0.0.0.0:5000->5000/tcp
postgres          Up 8 minutes    0.0.0.0:5432->5432/tcp
mysql             Up 10 minutes   0.0.0.0:3306->3306/tcp, 33060/tcp
```

Si todo es correcto, podremos ver los resultados en la URL **http://$IP_SERVIDOR/lastfm/**

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/LastFMCollector/refs/heads/main/screenshoots/cloud_portada.png)

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/LastFMCollector/refs/heads/main/screenshoots/cloud_artistas.png)

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/LastFMCollector/refs/heads/main/screenshoots/cloud_artistas2.png)

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/LastFMCollector/refs/heads/main/screenshoots/cloud_discos.png)

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/LastFMCollector/refs/heads/main/screenshoots/cloud_canciones.png)

![N|Diagrama](https://raw.githubusercontent.com/beetlebum97/LastFMCollector/refs/heads/main/screenshoots/cloud_scrobbles.png)

## 3. GESTIÓN

### Acceso a la aplicación
- URL de la aplicación: http://IP_SERVIDOR_AZURE/lastfm/
- Puertos abiertos: 22 (SSH), 80 (HTTP), 3306 (MySQL), 5432 (PostgreSQL)

### Limpieza de recursos
- OPCIÓN 1: Ver recursos en Azure Portal > Resource Groups > Recurso: Eliminar
- OPCIÓN 2: ```terraform destroy -auto-approve``` # Desde Cloud Shell en el directorio terraform

### Coste ###
- Los recursos tienen un coste. Apagar máquina virtual mientras no se usen o eliminar infraestructura para evitar gastos innecesarios. 

Nota: Esta implementación está diseñada para entornos de desarrollo y testing. Para entornos productivos, implementar medidas adicionales de seguridad y alta disponibilidad.


