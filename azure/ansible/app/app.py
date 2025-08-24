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
    per_page = 100
    query = None

    if option in ["artistas", "discos", "canciones", "scrobbles"]:
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

        # Paginación alineada a la izquierda
        pagination = ""
        if total_pages > 1:
            pagination += '<div class="pagination">'
            for p in range(1, total_pages + 1):
                if p == page:
                    pagination += f'<span class="page-link active">{p}</span>'
                else:
                    pagination += f"""<a class="page-link" href='?tabla={option}&page={p}'>{p}</a>"""
            pagination += '</div>'

        html = """
        <html>
        <head>
        <title>Last.fm</title>
        <style>
        body {
            font-family: Arial, sans-serif;
            min-height:100vh;
            margin:0;
            padding:0;
            background: linear-gradient(135deg,#ffe1e8 0%, #f7f7fa 100%);
        }
        h2 { color:#c00; margin-top:1rem;}
        a.volver { display:block; margin:1em 0; color:#c00; font-weight:bold; text-decoration:none;}
        a.volver:hover { text-decoration:underline; }
        table {
            border-collapse: collapse;
            width: auto;
            background:#fff;
            margin-bottom:2em;
            margin-left:0;
            margin-right:0;
            box-shadow:0 2px 10px #0001;
        }
        th { background: #c00; color:#fff; padding: 7px;}
        td { padding: 6px; text-align:left;}
        tr:nth-child(even) { background:#faf4f6;}
        tr:hover { background:#ffe1e8;}
        .pagination { margin:18px 0 0 0; }
        .page-link {
            color:#c00;
            background:none;
            margin:0 3px;
            padding:5px 12px;
            border-radius:5px;
            border:1px solid #ffdce2;
            text-decoration:none;
            display:inline-block;
        }
        .page-link.active, .page-link:active {
            background:#c00;
            color:#fff !important;
            font-weight:bold;
            border: 1px solid #c00;
        }
        </style>
        </head>
        <body>
            <a class="volver" href="/lastfm">&larr; Volver</a>
            <h2>{{tabla.title()}}</h2>
            <table border=1>
              <tr>{% for h in headers %}<th>{{h}}</th>{% endfor %}</tr>
              {% for row in rows %}
                <tr>{% for v in row %}<td>{{v}}</td>{% endfor %}</tr>
              {% endfor %}
            </table>
            {{pagination|safe}}
        </body>
        </html>
        """
        return render_template_string(html, rows=rows, headers=headers, tabla=option, pagination=pagination)

    # Portada con logo y enlaces grandes
    portada = """
    <html>
    <head>
    <title>Last.fm</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    body {
        margin:0;
        padding:0;
        font-family: Arial, sans-serif;
        background: linear-gradient(115deg,#ffe1e8 0%, #f7f7fa 100%);
        min-height:100vh;
        display:flex;
        flex-direction:column;
        align-items:center;
        justify-content:center;
    }
    .logo {
        margin:30px 0 22px 0;
        max-width:340px;
        width:70vw;
        display:block;
    }
    .main-menu {
        display:flex;
        flex-direction:column;
        gap:20px;
        width:320px;
        max-width:95vw;
        align-items:stretch;
        margin:0 auto;
        box-sizing: border-box;
    }
    .menu-link {
        background:#c00;
        color:#fff;
        font-size: 2rem;
        text-decoration:none;
        text-align:center;
        font-weight:bold;
        border-radius:15px;
        border:2px solid #fff;
        padding:22px 0;
        box-shadow: 0 3px 15px #0002;
        transition: background 0.14s, color 0.13s;
        letter-spacing:0.03em;
        cursor:pointer;
    }
    .menu-link:hover {
        background:#900;
        color:#fffbea;
    }
    @media (max-width: 600px) {
        .main-menu { width:97vw; }
        .menu-link { font-size: 1.23rem; padding:16px 0;}
    }
    </style>
    </head>
    <body>
        <img src="https://www.last.fm/static/images/lastfm_logo_facebook.15d8133be114.png" class="logo" alt="last.fm logo">
        <nav class="main-menu">
          <a class="menu-link" href='?tabla=artistas'>Artistas</a>
          <a class="menu-link" href='?tabla=discos'>Discos</a>
          <a class="menu-link" href='?tabla=canciones'>Canciones</a>
          <a class="menu-link" href='?tabla=scrobbles'>Scrobbles</a>
        </nav>
    </body>
    </html>
    """
    return portada