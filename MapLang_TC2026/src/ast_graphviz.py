"""
ast_graphviz.py — Exportador del AST de MapLang a diagrama Graphviz
==========================================================================

Construye una representación visual del Árbol Sintáctico Abstracto usando
la biblioteca `graphviz`, útil para la documentación del informe técnico y
para la exposición oral (alternativa complementaria al árbol textual y al
JSON ya soportados por main.py).

Uso:
    python3 ast_graphviz.py archivo.maplang salida.png
"""

from __future__ import annotations
import sys

import graphviz

from lexer import tokenize
from parser import Parser
from ast_nodes import (
    Programa, Mapa, Sala, Conexion,
    TipoSala, Salidas, Enemigo, Nivel, Item, Npc,
)

NODE_STYLE = dict(style="filled", fontname="Helvetica", fontsize="10")
COLORS = {
    "Programa": "#2c3e50", "Mapa": "#34495e", "Sala": "#27ae60",
    "Conexion": "#e67e22", "TipoSala": "#16a085", "Salidas": "#2980b9",
    "Enemigo": "#c0392b", "Nivel": "#8e44ad", "Item": "#f39c12", "Npc": "#7f8c8d",
}


def _label(node) -> str:
    if isinstance(node, Programa):
        return "programa"
    if isinstance(node, Mapa):
        return f"mapa\\n{node.nombre} ({node.ancho}x{node.alto})"
    if isinstance(node, Sala):
        return f"sala\\n({node.x},{node.y})"
    if isinstance(node, Conexion):
        label = f"conexion\\n{node.origen}->{node.destino}"
        if node.etiqueta:
            label += f"\\nvia {node.etiqueta!r}"
        return label
    if isinstance(node, TipoSala):
        return f"TYPE={node.valor}"
    if isinstance(node, Salidas):
        return f"EXITS={node.direcciones}"
    if isinstance(node, Enemigo):
        return f"ENEMY={node.identificador}"
    if isinstance(node, Nivel):
        return f"LEVEL={node.valor}"
    if isinstance(node, Item):
        return f"ITEM={node.identificador}"
    if isinstance(node, Npc):
        return f"NPC={node.identificador}"
    return type(node).__name__


def build_graph(programa: Programa) -> graphviz.Digraph:
    dot = graphviz.Digraph("AST_MapLang", format="png")
    dot.attr(rankdir="TB", bgcolor="#1b1b1f")
    dot.attr("node", fontcolor="white", **NODE_STYLE)
    dot.attr("edge", color="#d4af37")

    counter = [0]

    def new_id() -> str:
        counter[0] += 1
        return f"n{counter[0]}"

    def add(node) -> str:
        nid = new_id()
        kind = type(node).__name__
        color = COLORS.get(kind, "#555555")
        dot.node(nid, _label(node), fillcolor=color)
        return nid

    def visit(node) -> str:
        nid = add(node)
        if isinstance(node, Programa):
            for m in node.mapas:
                cid = visit(m)
                dot.edge(nid, cid)
        elif isinstance(node, Mapa):
            for d in node.declaraciones:
                cid = visit(d)
                dot.edge(nid, cid)
        elif isinstance(node, Sala):
            for a in node.atributos:
                cid = visit(a)
                dot.edge(nid, cid)
        # Conexion y los nodos de atributo son hojas
        return nid

    visit(programa)
    return dot


def export(source_path: str, output_path: str) -> str:
    with open(source_path, encoding="utf-8") as f:
        source = f.read()
    tokens = tokenize(source)
    p = Parser(tokens, collect_errors=True)
    ast = p.parse_programa()
    if p.errors:
        raise RuntimeError(f"el archivo contiene errores sintácticos: {p.errors}")

    dot = build_graph(ast)
    base = output_path.rsplit(".", 1)[0]
    rendered = dot.render(base, cleanup=True)
    return rendered


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 ast_graphviz.py archivo.maplang salida.png")
        sys.exit(1)
    out = export(sys.argv[1], sys.argv[2])
    print(f"Diagrama generado en: {out}")
