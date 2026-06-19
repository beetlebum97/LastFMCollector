# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(
    title="Last.fm Data API",
    description="API híbrida (PostgreSQL + JSON Fallback) para datos de Last.fm",
    version="2.0.2"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AJUSTE DE RUTAS: Al estar api.py en la raíz de backend junto al docker-compose, 
# calculamos las rutas subiendo un solo nivel de forma segura.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_CURATED = os.path.abspath(os.path.join(BASE_DIR, "../storage/curated"))
RUTA_FRONTEND = os.path.abspath(os.path.join(BASE_DIR, "../frontend"))

DB_CONFIG = {
    "dbname": "lastfm_data",
    "user": "lastfm_user",
    "password": "lastfm_password123",
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": "5432"
}

def leer_json(usuario: str, entidad: str):
    ruta_archivo = f"{RUTA_CURATED}/{usuario}/{entidad}_curated.json"
    if not os.path.exists(ruta_archivo):
        raise HTTPException(status_code=404, detail=f"No se encontraron datos de {entidad} para el usuario {usuario}.")
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        return json.load(f)

def obtener_datos(usuario: str, entidad: str, page: int = 1, limit: int = 10, q: str = None):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        base_query = f"SELECT * FROM {entidad} WHERE username = %s"
        count_query = f"SELECT COUNT(*) FROM {entidad} WHERE username = %s"
        params = [usuario]

        if q:
            base_query += " AND artist_name ILIKE %s"
            count_query += " AND artist_name ILIKE %s"
            params.append(f"%{q}%")

        cursor.execute(count_query, params)
        total = cursor.fetchone()['count']

        if entidad == "scrobbles":
            base_query += " ORDER BY date_time DESC"
        else:
            base_query += " ORDER BY rank ASC"

        base_query += " OFFSET %s LIMIT %s"
        params.extend([(page - 1) * limit, limit])

        cursor.execute(base_query, params)
        data = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "data": data,
            "total": total,
            "page": page,
            "limit": limit,
            "fuente": "PostgreSQL (Rápido)"
        }

    except psycopg2.OperationalError:
        print(f"⚠️ Aviso: Base de datos no disponible. Usando fallback JSON para {entidad}...")

        data = leer_json(usuario, entidad)
        if q:
            data = [item for item in data if q.lower() in item.get("artist_name", "").lower()]

        start = (page - 1) * limit
        return {
            "data": data[start:start + limit],
            "total": len(data),
            "page": page,
            "limit": limit,
            "fuente": "JSON Local (Respaldo)"
        }

# --- ENDPOINTS ---

@app.get("/")
def serve_frontend():
    ruta_index = os.path.join(RUTA_FRONTEND, "index.html")
    if os.path.exists(ruta_index):
        return FileResponse(ruta_index)
    return {"mensaje": f"El frontend no se encuentra en la ruta esperada: {ruta_index}"}

@app.get("/api/v1/{usuario}/stats")
def get_user_stats(usuario: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
        SELECT 
            (SELECT COUNT(*) FROM scrobbles   WHERE username = %s) as s_count,
            (SELECT COUNT(*) FROM top_artists WHERE username = %s) as art_count,
            (SELECT COUNT(*) FROM top_albums  WHERE username = %s) as alb_count,
            (SELECT COUNT(*) FROM top_tracks  WHERE username = %s) as trk_count;
        """
        cursor.execute(query, (usuario, usuario, usuario, usuario))
        totales = cursor.fetchone()
        conn.close()

        return {
            "usuario": usuario,
            "total_scrobbles": totales['s_count'],
            "total_artistas": totales['art_count'],
            "total_albums": totales['alb_count'],
            "total_canciones": totales['trk_count'],
            "fuente": "PostgreSQL"
        }
    except psycopg2.OperationalError:
        try:
            return {
                "usuario": usuario,
                "total_scrobbles": len(leer_json(usuario, "scrobbles")),
                "total_artistas": len(leer_json(usuario, "top_artists")),
                "total_albums": len(leer_json(usuario, "top_albums")),
                "total_canciones": len(leer_json(usuario, "top_tracks")),
                "fuente": "JSON Local"
            }
        except HTTPException:
            raise HTTPException(status_code=404, detail="Usuario sin datos.")

@app.get("/api/v1/{usuario}/top-artists")
def get_top_artists(usuario: str, page: int = 1, limit: int = 10, q: str = None):
    return obtener_datos(usuario, "top_artists", page, limit, q)

@app.get("/api/v1/{usuario}/top-albums")
def get_top_albums(usuario: str, page: int = 1, limit: int = 10, q: str = None):
    return obtener_datos(usuario, "top_albums", page, limit, q)

@app.get("/api/v1/{usuario}/top-tracks")
def get_top_tracks(usuario: str, page: int = 1, limit: int = 10, q: str = None):
    return obtener_datos(usuario, "top_tracks", page, limit, q)

@app.get("/api/v1/{usuario}/recent-scrobbles")
def get_recent_scrobbles(usuario: str, page: int = 1, limit: int = 10, q: str = None):
    return obtener_datos(usuario, "scrobbles", page, limit, q)
