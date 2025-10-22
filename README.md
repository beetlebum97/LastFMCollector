# 🎧 LastFMCollector  
> **DataOps & Cloud Project** — Extracción, almacenamiento y visualización de datos musicales de [Last.fm](https://www.last.fm/) con despliegue automatizado en **Microsoft Azure**.

---

## 📖 Descripción

**LastFMCollector** es un proyecto personal orientado a *Data Engineering / Cloud Automation*, que combina desarrollo en **Python**, gestión de **bases de datos relacionales**, e **infraestructura como código** en **Azure**.

El sistema permite **recopilar y analizar la actividad musical de usuarios de Last.fm**, almacenando la información en **MySQL o PostgreSQL** y desplegando el entorno completo con **Terraform + Ansible + Docker**.

---

## 🎥 Video Demostración

### ☁️ Azure Cloud Deployment
<a href="https://youtu.be/_op3gsFmq9Y" target="_blank">
  <img src="https://raw.githubusercontent.com/beetlebum97/LastFMCollector/refs/heads/main/screenshoots/cloud_portada.png" 
       alt="LastFMCollector - Despliegue Cloud Azure" 
       width="500" style="border-radius: 8px; border: 1px solid #ddd;">
</a>

- **00:00** - [Script de despliegue automatizado](https://youtu.be/_op3gsFmq9Y?t=0)
- **00:30** - [Infraestructura Terraform](https://youtu.be/_op3gsFmq9Y?t=30)
- **02:30** - [Configuración Ansible](https://youtu.be/_op3gsFmq9Y?t=150)
- **06:33** - [Instalación dependencias Python](https://youtu.be/_op3gsFmq9Y?t=393)
- **06:50** - [Extracción datos LastFM](https://youtu.be/_op3gsFmq9Y?t=410)
- **12:10** - [Despliegue Frontend Flask](https://youtu.be/_op3gsFmq9Y?t=730)
- **12:50** - [Verificación final](https://youtu.be/_op3gsFmq9Y?t=770)

### 🔧 Backend ETL Pipeline
<a href="https://youtu.be/C0AgQBKnWRM" target="_blank">
  <img src="https://raw.githubusercontent.com/beetlebum97/LastFMCollector/refs/heads/main/screenshoots/03.backend-descargas.png" 
       alt="LastFMCollector - Pipeline ETL Backend" 
       width="500" style="border-radius: 8px; border: 1px solid #ddd;">
</a>

- **00:00** - [Presentación y estadísticas rápidas](https://youtu.be/C0AgQBKnWRM?t=0)
- **00:40** - [Ejecución completa ETL (40,000+ registros)](https://youtu.be/C0AgQBKnWRM?t=40)
- **08:45** - [Inspección archivos JSON/CSV](https://youtu.be/C0AgQBKnWRM?t=525)
- **10:20** - [Extracción selectiva de datos](https://youtu.be/C0AgQBKnWRM?t=620)
- **11:50** - [Manejo de errores y validación](https://youtu.be/C0AgQBKnWRM?t=710)

### 🗄️ MySQL Backend  
<a href="https://youtu.be/0Whv_vm9HJI" target="_blank">
  <img src="https://raw.githubusercontent.com/beetlebum97/LastFMCollector/refs/heads/main/screenshoots/09.backend-mysql-conexion.png" 
       alt="LastFMCollector - Backend MySQL" 
       width="500" style="border-radius: 8px; border: 1px solid #ddd;">
</a>

- **00:00** - [Presentación y ejecución completa](https://youtu.be/0Whv_vm9HJI?t=0)
- **08:35** - [Verificación de tablas y estructura](https://youtu.be/0Whv_vm9HJI?t=515)
- **09:40** - [Consultas SQL de validación](https://youtu.be/0Whv_vm9HJI?t=580)

### 🗄️ PostgreSQL Backend
<a href="https://youtu.be/WV4gOHo5gAE" target="_blank">
  <img src="https://raw.githubusercontent.com/beetlebum97/LastFMCollector/refs/heads/main/screenshoots/14.backend-postgresql-tablas.png" 
       alt="LastFMCollector - Backend PostgreSQL" 
       width="500" style="border-radius: 8px; border: 1px solid #ddd;">
</a>

- **00:00** - [Presentación y ejecución completa](https://youtu.be/WV4gOHo5gAE?t=0)
- **07:45** - [Verificación de tablas y estructura](https://youtu.be/WV4gOHo5gAE?t=465)
- **08:42** - [Consultas SQL de validación](https://youtu.be/WV4gOHo5gAE?t=522)

---

## 🌐 Muestra de datos
- **GitHub Pages:** [Visualización de registros](https://beetlebum97.github.io/LastFMCollector/)  
  *→ Ejemplo de los datos extraídos y procesados por el pipeline*

---

## 🧩 Arquitectura General

Last.fm API → Python ETL (lastfm.py / lastfm_db.py) → BBDD (MySQL/PostgreSQL)
- Flask App + Nginx → Azure VM (Terraform + Ansible)
- Visualización en GitHub Pages
---

**Componentes principales:**
- **Backend:** scripts Python para extracción y almacenamiento de datos desde la API de Last.fm.  
- **Cloud:** despliegue automático en Azure mediante *Terraform* y *Ansible*.  
- **Frontend:** aplicación Flask servida por *Nginx* con contenedores Docker.  
- **Visualización:** datos expuestos en tablas interactivas a través de *GitHub Pages*.  

---

## ⚙️ Stack Tecnológico

| Categoría | Tecnologías |
|------------|-------------|
| Lenguaje | Python, Bash |
| Infraestructura | Azure Cloud, Terraform, Ansible |
| Contenedores | Docker |
| Bases de datos | MySQL, PostgreSQL |
| Web | Flask, Nginx |
| Otros | API REST, Pandas, JSON, CSV, HTML5, CSS3 |

---

## 🚀 Despliegue Cloud (Azure)

El proyecto incluye automatización completa de infraestructura en **Azure**:

- **Terraform:** crea la red, máquina virtual Debian 12 y seguridad.  
- **Ansible:** instala Docker y lanza contenedores (MySQL, PostgreSQL, Nginx, Flask).  
- **Python:** extrae los datos de Last.fm y los carga en las bases de datos.  

> 📘 Ver detalles en [`cloud/azure/README_AZURE.md`](https://github.com/beetlebum97/LastFMCollector/blob/main/cloud/azure/README_AZURE.md)

---

## 🖥️ Estructura del repositorio
```
├── backend/            # Scripts Python (extracción y carga de datos)
├── cloud/azure/        # Terraform + Ansible para despliegue automatizado
├── docs/               # GitHub Pages (visualización de datos)
├── logs/               # Salidas de los procesos
├── screenshoots/       # Capturas del sistema y despliegue
└── README.md
```

---

## 📊 Ejemplo de resultados

Imágenes del dashboard y despliegue en Azure:

| ![Portada](https://raw.githubusercontent.com/beetlebum97/LastFMCollector/refs/heads/main/screenshoots/cloud_portada.png) | ![Artistas](https://raw.githubusercontent.com/beetlebum97/LastFMCollector/refs/heads/main/screenshoots/cloud_artistas.png) |
|:--:|:--:|
| *Frontend - portada Flask* | *Visualización de artistas* |

| ![Canciones](https://raw.githubusercontent.com/beetlebum97/LastFMCollector/refs/heads/main/screenshoots/cloud_canciones.png) | ![Scrobbles](https://raw.githubusercontent.com/beetlebum97/LastFMCollector/refs/heads/main/screenshoots/cloud_scrobbles.png) |
|:--:|:--:|
| *Canciones registradas* | *Historial de reproducciones* |

---

## 🧠 Aprendizajes clave

- Diseño de **pipelines de datos reproducibles** (ETL real con Python y SQL).  
- Automatización de infraestructura cloud mediante **Terraform y Ansible**.  
- Integración de **contenedores Docker** para aplicaciones y bases de datos.  
- Publicación de resultados y visualizaciones con **GitHub Pages**.

---

## 👤 Autor

**David Vázquez Rodríguez**  
📍 Madrid, España  
💼 [LinkedIn](https://www.linkedin.com/in/dvazrod)  
💻 [GitHub](https://github.com/beetlebum97)  

---

> © 2025 - Proyecto personal orientado a aprendizaje y portfolio profesional.


















