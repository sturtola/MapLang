#!/usr/bin/env python3
"""
server.py — Servidor local para el prototipo visual de MapLang
====================================================================

Levanta un servidor HTTP simple (usando sólo la biblioteca estándar de
Python, sin dependencias adicionales) que expone el pipeline completo de
MapLang (lexer -> parser -> semántica -> renderer) a una página web local.

La página web (index.html) envía el código MapLang escrito por el usuario
a este servidor, que lo procesa con el sistema real (los mismos
lexer.py/parser.py/semantic.py/renderer.py del proyecto) y devuelve:
  - el AST en formato de árbol textual,
  - la lista de errores (léxicos, sintácticos o semánticos) si los hay,
  - la imagen del mapa renderizado en base64, si no hay errores.

Uso:
    cd src
    python3 server.py
    (o python server.py en Windows)

Luego abrir http://localhost:8765 en el navegador.
"""

from __future__ import annotations
import base64
import io
import json
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Timer

from lexer import tokenize, LexError
from parser import Parser, ParseError
from semantic import check_programa
from renderer import render_mapa

PORT = 8765


def process_source(source: str) -> dict:
    """Ejecuta el pipeline completo sobre el código fuente y devuelve un
    diccionario serializable a JSON con el resultado, listo para la UI."""

    # -- 1) Análisis léxico --------------------------------------------------
    try:
        tokens = tokenize(source)
    except LexError as e:
        return {
            "stage": "lexico",
            "ok": False,
            "errors": [{"line": e.line, "column": e.column, "message": e.message}],
        }

    # -- 2) Análisis sintáctico -----------------------------------------------
    p = Parser(tokens, collect_errors=True)
    try:
        ast = p.parse_programa()
    except ParseError as e:
        return {
            "stage": "sintactico",
            "ok": False,
            "errors": [{"line": e.line, "column": e.column, "message": e.message}],
        }

    if p.errors:
        return {
            "stage": "sintactico",
            "ok": False,
            "errors": [{"line": err.line, "column": err.column, "message": err.message}
                       for err in p.errors],
        }

    # -- 3) Análisis semántico -------------------------------------------------
    sem_errors = check_programa(ast)
    if sem_errors:
        return {
            "stage": "semantico",
            "ok": False,
            "errors": [{"line": err.line, "column": 0, "message": err.message}
                       for err in sem_errors],
        }

    # -- 4) Construcción de salida exitosa: árbol + imágenes --------------------
    tokens_view = [
        {"type": t.type, "value": t.value, "line": t.line, "column": t.column}
        for t in tokens if t.type != "EOF"
    ]

    tree_lines = []
    _render_tree(ast.to_dict(), tree_lines, "")

    images_b64 = []
    for mapa in ast.mapas:
        buf = io.BytesIO()
        _render_to_buffer(mapa, buf)
        images_b64.append({
            "nombre": mapa.nombre,
            "data": base64.b64encode(buf.getvalue()).decode("ascii"),
        })

    return {
        "stage": "ok",
        "ok": True,
        "errors": [],
        "tokens": tokens_view,
        "tree": "\n".join(tree_lines),
        "images": images_b64,
        "num_mapas": len(ast.mapas),
        "num_salas": sum(len(m.salas()) for m in ast.mapas),
        "num_conexiones": sum(len(m.conexiones()) for m in ast.mapas),
    }


def _render_to_buffer(mapa, buf: io.BytesIO) -> None:
    """Genera la imagen del mapa directamente en un buffer en memoria,
    reutilizando render_mapa pero apuntando a un archivo temporal, ya que
    matplotlib necesita una ruta de archivo o un objeto file-like."""
    import matplotlib.pyplot as plt  # import local: evita carga si no se usa
    # render_mapa ya acepta cualquier "file-like" porque internamente usa
    # fig.savefig(output_path, ...) y savefig admite tanto rutas como buffers.
    render_mapa(mapa, buf)


def _render_tree(d, lines: list, indent: str) -> None:
    if isinstance(d, dict):
        label = d.get("node", "?")
        details = {k: v for k, v in d.items() if k != "node" and not isinstance(v, (dict, list))}
        detail_str = " ".join(f"{k}={v!r}" for k, v in details.items())
        lines.append(f"{indent}{label} {detail_str}".rstrip())
        for k, v in d.items():
            if isinstance(v, list):
                for item in v:
                    _render_tree(item, lines, indent + "  ")
            elif isinstance(v, dict):
                _render_tree(v, lines, indent + "  ")
    else:
        lines.append(f"{indent}{d!r}")


class Handler(BaseHTTPRequestHandler):
    def _set_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self._serve_file("index.html", "text/html")
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_file(self, filename, content_type):
        try:
            with open(filename, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type + "; charset=utf-8")
            self._set_cors()
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path != "/run":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body.decode("utf-8"))
            source = payload.get("source", "")
        except (json.JSONDecodeError, UnicodeDecodeError):
            source = ""

        try:
            result = process_source(source)
        except Exception as e:  # protección general ante cualquier fallo inesperado
            result = {
                "stage": "interno",
                "ok": False,
                "errors": [{"line": 0, "column": 0, "message": f"Error interno: {e}"}],
            }

        response = json.dumps(result).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self._set_cors()
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format, *args):
        # Silencia el log default de BaseHTTPRequestHandler para una consola limpia
        pass


def main():
    server = HTTPServer(("localhost", PORT), Handler)
    url = f"http://localhost:{PORT}"
    print("=" * 60)
    print("  MapLang — Prototipo visual")
    print("=" * 60)
    print(f"  Servidor corriendo en: {url}")
    print("  Presioná Ctrl+C para detenerlo.")
    print("=" * 60)
    Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")


if __name__ == "__main__":
    main()
