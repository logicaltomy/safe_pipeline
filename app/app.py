import sqlite3
import time
from pathlib import Path

from flask import Flask, jsonify, make_response, request
from markupsafe import escape
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from werkzeug.serving import WSGIRequestHandler


app = Flask(__name__)
DB_PATH = Path("lab.db")
REQUEST_COUNT = Counter(
    "safe_pipeline_http_requests_total",
    "Cantidad total de solicitudes HTTP",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "safe_pipeline_http_request_duration_seconds",
    "Latencia de solicitudes HTTP",
    ["endpoint"],
)
SECURITY_EVENTS = Counter(
    "safe_pipeline_security_events_total",
    "Eventos de seguridad detectados por patrones basicos",
    ["type"],
)


class SafeRequestHandler(WSGIRequestHandler):
    server_version = "SafePipeline"
    sys_version = ""

    def version_string(self):
        return self.server_version


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL
        )
        """
    )

    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO users (username, email, role) VALUES (?, ?, ?)",
            [
                ("admin", "admin@safe-pipeline.local", "admin"),
                ("analista", "analista@safe-pipeline.local", "security"),
                ("dev", "dev@safe-pipeline.local", "developer"),
            ],
        )
    conn.commit()
    conn.close()


def track_security_patterns():
    values = " ".join(request.args.values()).lower()
    if any(token in values for token in ["<script", "javascript:", "onerror="]):
        SECURITY_EVENTS.labels(type="xss_attempt").inc()
    if any(token in values for token in ["' or '1'='1", "'--", "union select", " or 1=1"]):
        SECURITY_EVENTS.labels(type="sqli_attempt").inc()


@app.before_request
def before_request_metrics():
    request._start_time = time.perf_counter()
    track_security_patterns()


@app.after_request
def apply_security_headers(response):
    endpoint = request.endpoint or "unknown"
    duration = time.perf_counter() - getattr(request, "_start_time", time.perf_counter())
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status=str(response.status_code),
    ).inc()

    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; object-src 'none'; "
        "base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
    )
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Server"] = "SafePipeline"
    return response


@app.get("/")
def index():
    return make_response(
        """
        <h1>Safe Pipeline Vulnerable Lab</h1>
        <p>Aplicacion de laboratorio local para pruebas DAST.</p>
        <ul>
          <li><a href="/health">/health</a></li>
          <li><a href="/search?name=dev">/search?name=dev</a></li>
          <li><a href="/comment?message=Hola">/comment?message=Hola</a></li>
        </ul>
        """,
        200,
    )


@app.get("/health")
def health():
    return jsonify({"status": "healthy"})


@app.get("/metrics")
def metrics():
    return make_response(generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST})


@app.get("/search")
def search():
    init_db()
    name = request.args.get("name", "")
    like_value = f"%{name}%"

    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, username, email, role FROM users WHERE username LIKE ?",
        (like_value,),
    ).fetchall()
    conn.close()

    return jsonify(
        {
            "query": "SELECT id, username, email, role FROM users WHERE username LIKE ?",
            "results": [
                {
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "role": row[3],
                }
                for row in rows
            ],
        }
    )


@app.get("/comment")
def comment():
    message = request.args.get("message", "Sin comentario")
    safe_message = escape(message)
    html = f"""
    <h1>Comentario recibido</h1>
    <p>Mensaje: {safe_message}</p>
    <a href="/">Volver</a>
    """
    return make_response(html, 200)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False, request_handler=SafeRequestHandler)
