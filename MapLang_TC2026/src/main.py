#!/usr/bin/env python3
"""
main.py — Punto de entrada del sistema MapLang
====================================================

Integra el analizador léxico, el analizador sintáctico, las validaciones
semánticas, la exportación del AST y el renderizado del mapa.

Modo de uso
-----------
    python3 main.py archivo.maplang [opciones]

Opciones:
    --ast-json RUTA      Exporta el AST completo en formato JSON a RUTA.
    --ast-tree           Imprime el AST como árbol textual en stdout.
    --render RUTA        Genera la imagen PNG del primer mapa en RUTA.
    --render-all DIR     Genera una imagen PNG por cada mapa del programa
                          en el directorio DIR (nombre_mapa.png).
    --no-semantic        Omite las validaciones semánticas.
    --quiet              No imprime mensajes informativos en stdout.

Códigos de salida:
    0  Éxito (sin errores léxicos, sintácticos ni semánticos)
    1  Error léxico
    2  Error(es) sintáctico(s)
    3  Error(es) semántico(s)
"""

from __future__ import annotations
import argparse
import json
import os
import sys

from lexer import tokenize, LexError
from parser import Parser, ParseError
from semantic import check_programa
from renderer import render_mapa


def print_tree(node, indent: str = "") -> None:
    """Imprime el AST como árbol textual indentado (opción --ast-tree)."""
    d = node.to_dict()
    _print_dict_tree(d, indent)


def _print_dict_tree(d, indent: str = "") -> None:
    if isinstance(d, dict):
        label = d.get("node", "?")
        details = {k: v for k, v in d.items() if k not in ("node",) and not isinstance(v, (dict, list))}
        detail_str = " ".join(f"{k}={v!r}" for k, v in details.items())
        print(f"{indent}{label} {detail_str}".rstrip())
        for k, v in d.items():
            if isinstance(v, list):
                for item in v:
                    _print_dict_tree(item, indent + "  ")
            elif isinstance(v, dict):
                _print_dict_tree(v, indent + "  ")
    else:
        print(f"{indent}{d!r}")


def run(argv=None) -> int:
    arg_parser = argparse.ArgumentParser(
        prog="main.py",
        description="MapLang — analizador léxico-sintáctico y renderizador de mapas de videojuegos.",
    )
    arg_parser.add_argument("archivo", help="Ruta al archivo fuente .maplang")
    arg_parser.add_argument("--ast-json", metavar="RUTA",
                             help="Exporta el AST en formato JSON a RUTA")
    arg_parser.add_argument("--ast-tree", action="store_true",
                             help="Imprime el AST como árbol textual")
    arg_parser.add_argument("--render", metavar="RUTA",
                             help="Genera la imagen PNG del primer mapa en RUTA")
    arg_parser.add_argument("--render-all", metavar="DIR",
                             help="Genera una imagen PNG por cada mapa en el directorio DIR")
    arg_parser.add_argument("--no-semantic", action="store_true",
                             help="Omite las validaciones semánticas")
    arg_parser.add_argument("--quiet", action="store_true",
                             help="No imprime mensajes informativos")
    args = arg_parser.parse_args(argv)

    def info(msg: str) -> None:
        if not args.quiet:
            print(msg)

    if not os.path.isfile(args.archivo):
        print(f"Error: no se encontró el archivo '{args.archivo}'", file=sys.stderr)
        return 1

    with open(args.archivo, "r", encoding="utf-8") as f:
        source = f.read()

    # -- 1) Análisis léxico ---------------------------------------------------
    try:
        tokens = tokenize(source)
    except LexError as e:
        print(str(e), file=sys.stderr)
        return 1
    info(f"[OK] Análisis léxico: {len(tokens) - 1} tokens generados.")

    # -- 2) Análisis sintáctico -------------------------------------------------
    p = Parser(tokens, collect_errors=True)
    try:
        ast = p.parse_programa()
    except ParseError as e:
        print(str(e), file=sys.stderr)
        return 2

    if p.errors:
        for err in p.errors:
            print(str(err), file=sys.stderr)
        return 2
    info(f"[OK] Análisis sintáctico: {len(ast.mapas)} mapa(s) reconocido(s).")

    # -- 3) Análisis semántico ---------------------------------------------------
    if not args.no_semantic:
        sem_errors = check_programa(ast)
        if sem_errors:
            for err in sem_errors:
                print(str(err), file=sys.stderr)
            return 3
        info("[OK] Validación semántica: sin observaciones.")

    # -- 4) Exportación del AST ----------------------------------------------
    if args.ast_json:
        with open(args.ast_json, "w", encoding="utf-8") as f:
            json.dump(ast.to_dict(), f, indent=2, ensure_ascii=False)
        info(f"[OK] AST exportado en formato JSON a '{args.ast_json}'.")

    if args.ast_tree:
        print_tree(ast)

    # -- 5) Renderizado --------------------------------------------------------
    if args.render:
        render_mapa(ast.mapas[0], args.render)
        info(f"[OK] Imagen del mapa '{ast.mapas[0].nombre}' generada en '{args.render}'.")

    if args.render_all:
        os.makedirs(args.render_all, exist_ok=True)
        for mapa in ast.mapas:
            out_path = os.path.join(args.render_all, f"{mapa.nombre}.png")
            render_mapa(mapa, out_path)
            info(f"[OK] Imagen del mapa '{mapa.nombre}' generada en '{out_path}'.")

    return 0


if __name__ == "__main__":
    sys.exit(run())
