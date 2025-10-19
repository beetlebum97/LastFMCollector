# 🎧 LastFMCollector  
> **DataOps & Cloud Project** — Extracción, almacenamiento y visualización de datos musicales de [Last.fm](https://www.last.fm/) con despliegue automatizado en **Microsoft Azure**.

---

## 🌐 Demo
- **GitHub Pages:** [beetlebum97.github.io/LastFMCollector](https://beetlebum97.github.io/LastFMCollector/)  
- **YouTube (demo próximamente):** *en preparación*

---

## 📖 Descripción

**LastFMCollector** es un proyecto personal orientado a *Data Engineering / Cloud Automation*, que combina desarrollo en **Python**, gestión de **bases de datos relacionales**, e **infraestructura como código** en **Azure**.

El sistema permite **recopilar y analizar la actividad musical de usuarios de Last.fm**, almacenando la información en **MySQL o PostgreSQL** y desplegando el entorno completo con **Terraform + Ansible + Docker**.

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










