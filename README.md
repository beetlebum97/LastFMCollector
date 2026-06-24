# 🎵 LastFMCollector

Pipeline ETL completo para extraer, procesar y visualizar tu historial de escuchas de Last.fm. Descarga tus scrobbles y top artistas/álbumes/canciones, los transforma en capas medallion (Raw → Staging → Curated) y los expone a través de un dashboard interactivo.

**[🌐 Ver demo en vivo](https://beetlebum97.github.io/LastFMCollector/)** — datos reales de `hayman3030`

---

## ✨ Características

- **Pipeline ETL Medallion** — Raw → Staging → Curated en tres pasos desacoplados
- **Multi-usuario** — procesa y almacena varios usuarios de Last.fm sin pisarse los datos
- **Dashboard interactivo** — top artistas, álbumes, canciones y scrobbles con paginación y filtro en tiempo real
- **Modo claro/oscuro** — con preferencia guardada en el navegador
- **Backend dual** — PostgreSQL como fuente principal con fallback automático a JSON local
- **Despliegue cloud** — infraestructura en Azure con Terraform + Ansible + Docker en un solo comando
- **Despliegue local** — script que levanta todo el entorno desde cero

---

## 🏗️ Arquitectura

```
LastFMCollector/
├── data-pipeline/
│   ├── run-pipeline.py          # Orquestador ETL
│   └── src/
│       ├── download_raw.py      # Capa RAW — descarga desde la API de Last.fm
│       ├── process_staging.py   # Capa STAGING — normalización y limpieza
│       └── transform_curated.py # Capa CURATED — transformación final
├── backend/
│   ├── api.py                   # FastAPI (PostgreSQL + fallback JSON)
│   ├── load_database.py         # Inyección de datos en PostgreSQL
│   └── docker-compose.yml       # PostgreSQL local
├── cloud/azure/
│   ├── lastfm_azure.sh          # Script de despliegue cloud (un solo comando)
│   ├── docker-compose.prod.yml  # PostgreSQL + FastAPI en producción
│   ├── ansible/deploy.yml       # Configuración del servidor
│   └── terraform/               # Infraestructura Azure (VM, NSG, IP pública)
├── deploy/
│   └── deploy_local.sh          # Script de despliegue local
├── docs/                        # GitHub Pages (dashboard estático)
│   ├── index.html
│   └── data/{usuario}/          # JSONs curated por usuario
├── frontend/
│   └── index.html               # Dashboard dinámico (conectado a la API)
├── stats/
│   └── user_stats.py            # Informe de estadísticas en texto
└── storage/
    ├── raw/                     # JSONs crudos de la API
    ├── staging/                 # JSONs normalizados
    └── curated/                 # JSONs listos para consumir
```

---

## 🚀 Despliegue rápido en Azure

Desde Azure Cloud Shell, en un solo comando:

```bash
wget -qO- https://raw.githubusercontent.com/beetlebum97/LastFMCollector/main/cloud/azure/lastfm_azure.sh | bash
```

El script se encarga de todo:

1. Clona el repositorio
2. Genera la clave SSH
3. Crea la infraestructura en Azure con **Terraform** (VM, IP pública, NSG)
4. Configura el servidor con **Ansible** (Docker, PostgreSQL, FastAPI)
5. Lanza el pipeline ETL de forma interactiva para los usuarios que quieras
6. Inyecta los datos en PostgreSQL
7. Muestra la URL del dashboard

**Requisitos previos:** Terraform y Ansible instalados en Azure Cloud Shell, y una API key de Last.fm ([obtener aquí](https://www.last.fm/api/account/create)).

---

## 💻 Despliegue local

**Requisitos:** Python 3.x y Docker instalados.

```bash
wget -qO- https://raw.githubusercontent.com/beetlebum97/LastFMCollector/main/deploy/deploy_local.sh | bash
```

El script crea el entorno virtual, instala dependencias, lanza PostgreSQL en Docker, ejecuta el pipeline y levanta la API. El dashboard queda disponible en `http://<tu-ip-local>:8000`.

---

## 🔄 Pipeline ETL

El pipeline sigue la arquitectura medallion en tres capas:

| Capa | Script | Descripción |
|---|---|---|
| **RAW** | `download_raw.py` | Descarga paginada desde la API de Last.fm con reintentos |
| **STAGING** | `process_staging.py` | Normalización de campos, timestamps UTC, flag `nowplaying` |
| **CURATED** | `transform_curated.py` | Cálculo de porcentajes, formato de fechas, filtrado de scrobbles en curso |

Se puede lanzar manualmente para un usuario:

```bash
cd data-pipeline
python run-pipeline.py <usuario>
```

---

## 🗄️ Base de datos

PostgreSQL con esquema multi-usuario — cada tabla incluye una columna `username` que permite almacenar y consultar varios usuarios de forma independiente.

```
top_artists  (username, rank, artist_name, playcount, playcount_pct)
top_albums   (username, rank, album_name, artist_name, playcount)
top_tracks   (username, rank, track_name, artist_name, playcount)
scrobbles    (username, artist_name, track_name, album_name, loved, date_time)
```

La API (`api.py`) conecta a PostgreSQL con `DB_HOST` configurable por variable de entorno, con fallback automático a los JSONs curated si la base de datos no está disponible.

---

## 🌐 GitHub Pages

El directorio `docs/` contiene una versión estática del dashboard que funciona sin backend, leyendo los JSONs directamente desde `docs/data/{usuario}/`.

Para añadir un usuario a la demo estática, basta con copiar sus ficheros curated a `docs/data/<usuario>/` y hacer commit.

---

## 🔑 API key de Last.fm

El pipeline solicita la API key de forma interactiva en cada ejecución (no se almacena en ningún fichero). Puedes obtener una gratis en [last.fm/api](https://www.last.fm/api/account/create).

---

## 📦 Dependencias

```
requests
colorama
fastapi
uvicorn
psycopg2-binary
```

```bash
pip install -r requirements.txt
```
