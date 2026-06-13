# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import json
import os

app = FastAPI(
    title="Last.fm Data API",
    description="API con paginación para servir datos Curated de Last.fm",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RUTA_CURATED = "../storage/curated"
RUTA_FRONTEND = "../frontend"

def leer_json(usuario: str, entidad: str):
    ruta_archivo = f"{RUTA_CURATED}/{usuario}/{entidad}_curated.json"
    if not os.path.exists(ruta_archivo):
        raise HTTPException(status_code=404, detail=f"No se encontraron datos de {entidad} para el usuario {usuario}.")
    
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        return json.load(f)

# --- ENDPOINTS ---

@app.get("/")
def serve_frontend():
    ruta_index = f"{RUTA_FRONTEND}/index.html"
    if os.path.exists(ruta_index):
        return FileResponse(ruta_index)
    return {"mensaje": "El archivo index.html no se encuentra en la ruta especificada."}

@app.get("/api/v1/{usuario}/stats")
def get_user_stats(usuario: str):
    try:
        scrobbles = leer_json(usuario, "scrobbles")
        artistas = leer_json(usuario, "top_artists")
        albums = leer_json(usuario, "top_albums")
        canciones = leer_json(usuario, "top_tracks")
        
        return {
            "usuario": usuario,
            "total_scrobbles": len(scrobbles),
            "total_artistas": len(artistas),
            "total_albums": len(albums),
            "total_canciones": len(canciones)
        }
    except HTTPException:
        raise HTTPException(status_code=404, detail="El usuario no tiene datos procesados.")

@app.get("/api/v1/{usuario}/top-artists")
def get_top_artists(usuario: str, page: int = 1, limit: int = 10):
    data = leer_json(usuario, "top_artists")
    start = (page - 1) * limit
    return {
        "data": data[start:start + limit],
        "total": len(data),
        "page": page,
        "limit": limit
    }

@app.get("/api/v1/{usuario}/top-albums")
def get_top_albums(usuario: str, page: int = 1, limit: int = 10):
    data = leer_json(usuario, "top_albums")
    start = (page - 1) * limit
    return {
        "data": data[start:start + limit],
        "total": len(data),
        "page": page,
        "limit": limit
    }

# ESTE ES EL ENDPOINT QUE FALTABA
@app.get("/api/v1/{usuario}/top-tracks")
def get_top_tracks(usuario: str, page: int = 1, limit: int = 10):
    data = leer_json(usuario, "top_tracks")
    start = (page - 1) * limit
    return {
        "data": data[start:start + limit],
        "total": len(data),
        "page": page,
        "limit": limit
    }

@app.get("/api/v1/{usuario}/recent-scrobbles")
def get_recent_scrobbles(usuario: str, page: int = 1, limit: int = 10):
    data = leer_json(usuario, "scrobbles")
    start = (page - 1) * limit
    return {
        "data": data[start:start + limit],
        "total": len(data),
        "page": page,
        "limit": limit
    }
