from flask import Flask, request, render_template_string
from sqlalchemy import create_engine, text
import os
import math

app = Flask(__name__)

DB_USER = "david"
DB_PASS = "1234"
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_NAME = "lastfm"
DB_DRIVER = os.environ.get("DB_DRIVER", "mysql+pymysql")

engine = create_engine(f"{DB_DRIVER}://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}")

@app.route("/lastfm")
@app.route("/lastfm/")
def index():
    option = request.args.get("tabla")
    page = int(request.args.get("page", 1))
    per_page = 50  # Reducido para mejor experiencia móvil
    query = None

    # Mapeo de tablas con íconos y colores
    table_config = {
        "artistas": {"icon": "🎤", "color": "#E91E63", "title": "Artistas"},
        "discos": {"icon": "💿", "color": "#9C27B0", "title": "Álbumes"},
        "canciones": {"icon": "🎵", "color": "#2196F3", "title": "Canciones"}, 
        "scrobbles": {"icon": "📈", "color": "#FF5722", "title": "Reproducciones"}
    }

    if option in table_config:
        query = f"SELECT * FROM {option} LIMIT {per_page} OFFSET {(page-1)*per_page}"
        count_query = f"SELECT COUNT(*) FROM {option}"

    if query:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            headers = result.keys()
            total_result = conn.execute(text(count_query))
            total_rows = total_result.scalar()
        total_pages = max(1, math.ceil(total_rows / per_page))
        config = table_config[option]

        # Paginación mejorada
        pagination = ""
        if total_pages > 1:
            pagination += '<div class="pagination">'
            # Botón anterior
            if page > 1:
                pagination += f'<a class="page-btn" href="?tabla={option}&page={page-1}">‹ Anterior</a>'
            
            # Páginas
            start_page = max(1, page - 2)
            end_page = min(total_pages, page + 2)
            
            if start_page > 1:
                pagination += f'<a class="page-link" href="?tabla={option}&page=1">1</a>'
                if start_page > 2:
                    pagination += '<span class="page-dots">...</span>'
            
            for p in range(start_page, end_page + 1):
                if p == page:
                    pagination += f'<span class="page-link active">{p}</span>'
                else:
                    pagination += f'<a class="page-link" href="?tabla={option}&page={p}">{p}</a>'
            
            if end_page < total_pages:
                if end_page < total_pages - 1:
                    pagination += '<span class="page-dots">...</span>'
                pagination += f'<a class="page-link" href="?tabla={option}&page={total_pages}">{total_pages}</a>'
            
            # Botón siguiente
            if page < total_pages:
                pagination += f'<a class="page-btn" href="?tabla={option}&page={page+1}">Siguiente ›</a>'
            
            pagination += '</div>'

        html = """
        <html>
        <head>
        <title>{{config.title}} - Last.fm</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin:0;
            padding:20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height:100vh;
            color:#333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        .header {
            display: flex;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid {{config.color}};
        }
        .header-icon {
            font-size: 3rem;
            margin-right: 20px;
        }
        .header-title {
            flex: 1;
        }
        .header h1 {
            color: {{config.color}};
            margin: 0;
            font-size: 2.5rem;
            font-weight: 300;
        }
        .stats {
            color: #666;
            margin: 10px 0;
            font-size: 1.1rem;
        }
        .back-btn {
            display: inline-flex;
            align-items: center;
            color: #666;
            text-decoration: none;
            font-weight: 500;
            padding: 12px 24px;
            border-radius: 25px;
            background: #f8f9fa;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }
        .back-btn:hover {
            background: {{config.color}};
            color: white;
            transform: translateX(-5px);
        }
        .table-container {
            overflow-x: auto;
            margin: 20px 0;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            font-size: 0.95rem;
        }
        th {
            background: linear-gradient(135deg, {{config.color}}, {{config.color}}dd);
            color: white;
            padding: 18px 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.85rem;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        td {
            padding: 15px;
            border-bottom: 1px solid #eee;
            vertical-align: top;
        }
        tr:hover {
            background: linear-gradient(90deg, {{config.color}}08, transparent);
            transform: scale(1.01);
            transition: all 0.2s ease;
        }
        tr:nth-child(even) {
            background: #fafafa;
        }
        .pagination {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 30px 0;
            gap: 8px;
            flex-wrap: wrap;
        }
        .page-link, .page-btn {
            color: {{config.color}};
            background: white;
            border: 2px solid {{config.color}};
            padding: 12px 18px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            min-width: 44px;
            text-align: center;
        }
        .page-btn {
            padding: 12px 24px;
        }
        .page-link.active {
            background: {{config.color}};
            color: white;
            transform: scale(1.1);
        }
        .page-link:hover:not(.active), .page-btn:hover {
            background: {{config.color}};
            color: white;
            transform: translateY(-2px);
        }
        .page-dots {
            color: #999;
            padding: 12px 8px;
        }
        @media (max-width: 768px) {
            body { padding: 10px; }
            .container { padding: 20px; border-radius: 15px; }
            .header { flex-direction: column; text-align: center; }
            .header-icon { margin: 0 0 10px 0; }
            .header h1 { font-size: 2rem; }
            table { font-size: 0.85rem; }
            th, td { padding: 12px 8px; }
            .pagination { gap: 5px; }
            .page-link, .page-btn { padding: 10px 12px; font-size: 0.9rem; }
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .no-data {
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }
        </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="header-icon">{{config.icon}}</div>
                    <div class="header-title">
                        <h1>{{config.title}}</h1>
                        <div class="stats">
                            {{total_rows}} registros total • Página {{page}} de {{total_pages}}
                        </div>
                    </div>
                    <a class="back-btn" href="/lastfm">← Volver al inicio</a>
                </div>
                
                {% if rows %}
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>{% for h in headers %}<th>{{h}}</th>{% endfor %}</tr>
                        </thead>
                        <tbody>
                            {% for row in rows %}
                            <tr>{% for v in row %}<td>{{v}}</td>{% endfor %}</tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {{pagination|safe}}
                {% else %}
                <div class="no-data">
                    <h3>No hay datos disponibles</h3>
                    <p>Esta tabla está vacía o no se pudo conectar con la base de datos.</p>
                </div>
                {% endif %}
            </div>
        </body>
        </html>
        """
        return render_template_string(html, 
            rows=rows, 
            headers=headers, 
            config=config, 
            pagination=pagination,
            page=page,
            total_pages=total_pages,
            total_rows=total_rows
        )

    # Portada mejorada con animaciones y diseño moderno
    portada = """
    <html>
    <head>
    <title>Last.fm Database Explorer</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    * { box-sizing: border-box; }
    body {
        margin:0;
        padding:0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height:100vh;
        display:flex;
        flex-direction:column;
        align-items:center;
        justify-content:center;
        overflow-x: hidden;
    }
    .hero {
        text-align: center;
        margin-bottom: 50px;
        animation: fadeInUp 1s ease;
    }
    .logo {
        max-width: 300px;
        width: 80vw;
        margin-bottom: 20px;
        filter: drop-shadow(0 10px 30px rgba(0,0,0,0.3));
        animation: float 6s ease-in-out infinite;
    }
    .title {
        color: white;
        font-size: 2.5rem;
        font-weight: 300;
        margin: 20px 0;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .subtitle {
        color: rgba(255,255,255,0.8);
        font-size: 1.2rem;
        margin-bottom: 30px;
    }
    .main-menu {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 25px;
        width: 100%;
        max-width: 800px;
        padding: 0 20px;
    }
    .menu-card {
        background: rgba(255,255,255,0.95);
        border-radius: 20px;
        padding: 30px;
        text-decoration: none;
        color: #333;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        position: relative;
        overflow: hidden;
    }
    .menu-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.6s;
    }
    .menu-card:hover::before {
        left: 100%;
    }
    .menu-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 25px 50px rgba(0,0,0,0.2);
    }
    .menu-icon {
        font-size: 3rem;
        margin-bottom: 15px;
        display: block;
    }
    .menu-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .menu-desc {
        color: #666;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .card-artistas { border-left: 5px solid #E91E63; }
    .card-discos { border-left: 5px solid #9C27B0; }
    .card-canciones { border-left: 5px solid #2196F3; }
    .card-scrobbles { border-left: 5px solid #FF5722; }
    
    .footer {
        position: fixed;
        bottom: 20px;
        right: 20px;
        color: rgba(255,255,255,0.7);
        font-size: 0.9rem;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    @media (max-width: 768px) {
        .title { font-size: 2rem; }
        .main-menu { 
            grid-template-columns: 1fr;
            max-width: 400px;
        }
        .menu-card { padding: 25px; }
        .footer { display: none; }
    }
    </style>
    </head>
    <body>
        <div class="hero">
            <img src="https://www.last.fm/static/images/lastfm_logo_facebook.15d8133be114.png" class="logo" alt="Last.fm Logo">
            <h1 class="title">Music Database Explorer</h1>
            <p class="subtitle">Explora tu colección musical</p>
        </div>
        
        <nav class="main-menu">
            <a class="menu-card card-artistas" href='?tabla=artistas'>
                <span class="menu-icon">🎤</span>
                <div class="menu-title">Artistas</div>
                <div class="menu-desc">Descubre todos los artistas de tu biblioteca musical</div>
            </a>
            
            <a class="menu-card card-discos" href='?tabla=discos'>
                <span class="menu-icon">💿</span>
                <div class="menu-title">Álbumes</div>
                <div class="menu-desc">Explora la discografía completa por álbumes</div>
            </a>
            
            <a class="menu-card card-canciones" href='?tabla=canciones'>
                <span class="menu-icon">🎵</span>
                <div class="menu-title">Canciones</div>
                <div class="menu-desc">Navega por todas las pistas de tu colección</div>
            </a>
            
            <a class="menu-card card-scrobbles" href='?tabla=scrobbles'>
                <span class="menu-icon">📈</span>
                <div class="menu-title">Reproducciones</div>
                <div class="menu-desc">Analiza tu historial de escucha detallado</div>
            </a>
        </nav>
        
        <div class="footer">
            Powered by Last.fm API
        </div>
    </body>
    </html>
    """
    return portada