# -*- coding: utf-8 -*-
import json
import psycopg2
from psycopg2 import sql
import os
import sys
from pathlib import Path

# Configuración de la base de datos (La que definimos en el docker-compose.yml)
DB_CONFIG = {
    "dbname": "lastfm_data",
    "user": "lastfm_user",
    "password": "lastfm_password123",
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": "5432"
}

if len(sys.argv) < 2:
    print("Error: Uso: python load_database.py <usuario>")
    sys.exit(1)

USUARIO = sys.argv[1]

# RUTAS DINÁMICAS (Sube 1 nivel: backend -> raíz)
BASE_DIR = Path(__file__).resolve().parents[1]
RUTA_CURATED = str(BASE_DIR / "storage" / "curated" / USUARIO)

def conectar_db():
    print("🔌 Conectando a PostgreSQL...")
    return psycopg2.connect(**DB_CONFIG)

def crear_tablas(cursor):
    print("🏗️ Verificando/Creando tablas en la base de datos (si no existen)...")

    tablas_sql = """
    CREATE TABLE IF NOT EXISTS top_artists (
        username TEXT,
        rank INTEGER,
        artist_name TEXT,
        playcount INTEGER,
        playcount_pct NUMERIC
    );

    CREATE TABLE IF NOT EXISTS top_albums (
        username TEXT,
        rank INTEGER,
        album_name TEXT,
        artist_name TEXT,
        playcount INTEGER
    );

    CREATE TABLE IF NOT EXISTS top_tracks (
        username TEXT,
        rank INTEGER,
        track_name TEXT,
        artist_name TEXT,
        playcount INTEGER
    );

    CREATE TABLE IF NOT EXISTS scrobbles (
        username TEXT,
        artist_name TEXT,
        track_name TEXT,
        album_name TEXT,
        loved INTEGER,
        date_time TIMESTAMP
    );
    """
    cursor.execute(tablas_sql)


def borrar_datos_usuario(cursor, usuario):
    print(f"🧹 Eliminando datos previos de '{usuario}' (si existían)...")
    for tabla in ("top_artists", "top_albums", "top_tracks", "scrobbles"):
        cursor.execute(
            sql.SQL("DELETE FROM {} WHERE username = %s").format(sql.Identifier(tabla)),
            (usuario,)
        )

def insertar_datos(cursor, tabla, ruta_archivo, query_insercion, usuario):
    if not os.path.exists(ruta_archivo):
        print(f"⚠️ Archivo no encontrado: {ruta_archivo}")
        return

    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        datos = json.load(f)

    # Inyectamos el username en cada registro para poder filtrar luego
    for d in datos:
        d['username'] = usuario

    print(f"📥 Insertando {len(datos)} registros en la tabla '{tabla}'...")
    
    # Inserción masiva usando executemany
    cursor.executemany(query_insercion, datos)

def main():
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        crear_tablas(cursor)
        borrar_datos_usuario(cursor, USUARIO)

        # 1. Cargar Top Artists
        insertar_datos(
            cursor, "top_artists", f"{RUTA_CURATED}/top_artists_curated.json",
            "INSERT INTO top_artists (username, rank, artist_name, playcount, playcount_pct) VALUES (%(username)s, %(rank)s, %(artist_name)s, %(playcount)s, %(playcount_pct)s)",
            USUARIO
        )

        # 2. Cargar Top Albums
        insertar_datos(
            cursor, "top_albums", f"{RUTA_CURATED}/top_albums_curated.json",
            "INSERT INTO top_albums (username, rank, album_name, artist_name, playcount) VALUES (%(username)s, %(rank)s, %(album_name)s, %(artist_name)s, %(playcount)s)",
            USUARIO
        )

        # 3. Cargar Top Tracks
        insertar_datos(
            cursor, "top_tracks", f"{RUTA_CURATED}/top_tracks_curated.json",
            "INSERT INTO top_tracks (username, rank, track_name, artist_name, playcount) VALUES (%(username)s, %(rank)s, %(track_name)s, %(artist_name)s, %(playcount)s)",
            USUARIO
        )

        # 4. Cargar Scrobbles
        # Nos aseguramos de leer cualquiera de las claves de fecha que vengan en el JSON
        ruta_scrobbles = f"{RUTA_CURATED}/scrobbles_curated.json"
        if os.path.exists(ruta_scrobbles):
            with open(ruta_scrobbles, 'r', encoding='utf-8') as f:
                scrobbles_data = json.load(f)
            
            # Normalizar la clave de la fecha para la BBDD e inyectar el username
            for s in scrobbles_data:
                s['username'] = USUARIO
                s['date_time'] = s.get('date_time') or s.get('timestamp_iso') or s.get('fecha_hora')
                # Limpiar la 'T' si viene en formato ISO antiguo
                if s['date_time'] and 'T' in s['date_time']:
                    s['date_time'] = s['date_time'].replace('T', ' ').split('+')[0]
            
            print(f"📥 Insertando {len(scrobbles_data)} registros en la tabla 'scrobbles'...")
            query_scrobbles = "INSERT INTO scrobbles (username, artist_name, track_name, album_name, loved, date_time) VALUES (%(username)s, %(artist_name)s, %(track_name)s, %(album_name)s, %(loved)s, %(date_time)s)"
            cursor.executemany(query_scrobbles, scrobbles_data)
        else:
            print(f"⚠️ Archivo no encontrado: {ruta_scrobbles}")

        # Guardar (hacer commit) de todos los cambios
        conn.commit()
        print("✅ ¡Todos los datos han sido migrados a PostgreSQL exitosamente!")

    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")
    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    main()
