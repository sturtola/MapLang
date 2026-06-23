"""
test_integration.py — Pruebas de integración end-to-end de MapLang
========================================================================

Ejecuta el pipeline completo (lexer -> parser -> semántica -> render) sobre
los archivos de caso almacenados en tests/casos/, verificando que los casos
"valido_*" terminen sin errores y que los casos "invalido_*" produzcan al
menos un error en la etapa correspondiente (léxica, sintáctica o semántica).
"""

import sys
import os
import glob
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lexer import tokenize, LexError
from parser import Parser, ParseError
from semantic import check_programa
from renderer import render_mapa

CASOS_DIR = os.path.join(os.path.dirname(__file__), "casos")


def run_pipeline(path: str):
    """Ejecuta el pipeline completo sobre un archivo y devuelve
    ('ok', ast) o ('lex'|'syntax'|'semantic', [errores])."""
    with open(path, encoding="utf-8") as f:
        source = f.read()
    try:
        tokens = tokenize(source)
    except LexError as e:
        return "lex", [e]

    p = Parser(tokens, collect_errors=True)
    try:
        ast = p.parse_programa()
    except ParseError as e:
        return "syntax", [e]
    if p.errors:
        return "syntax", p.errors

    sem_errors = check_programa(ast)
    if sem_errors:
        return "semantic", sem_errors

    return "ok", ast


class TestValidCases(unittest.TestCase):
    """Todos los archivos valido_*.maplang deben procesarse sin errores."""

    def test_all_valid_cases_pass(self):
        files = sorted(glob.glob(os.path.join(CASOS_DIR, "valido_*.maplang")))
        self.assertGreaterEqual(len(files), 8, "se requieren al menos 8 casos válidos")
        for path in files:
            with self.subTest(caso=os.path.basename(path)):
                status, result = run_pipeline(path)
                self.assertEqual(status, "ok",
                                  f"{os.path.basename(path)} falló: {result}")


class TestInvalidCases(unittest.TestCase):
    """Todos los archivos invalido_*.maplang deben producir al menos un error."""

    def test_all_invalid_cases_fail(self):
        files = sorted(glob.glob(os.path.join(CASOS_DIR, "invalido_*.maplang")))
        self.assertGreaterEqual(len(files), 3, "se requieren al menos 3 casos inválidos")
        for path in files:
            with self.subTest(caso=os.path.basename(path)):
                status, result = run_pipeline(path)
                self.assertIn(status, ("lex", "syntax", "semantic"),
                               f"{os.path.basename(path)} debería haber fallado")
                self.assertTrue(len(result) >= 1)


class TestRendererIntegration(unittest.TestCase):
    """Verifica que el renderer pueda generar una imagen a partir de cada
    caso válido, sin lanzar excepciones, y que el archivo resultante exista
    y tenga contenido."""

    def test_render_all_valid_cases(self):
        files = sorted(glob.glob(os.path.join(CASOS_DIR, "valido_*.maplang")))
        with tempfile.TemporaryDirectory() as tmpdir:
            for path in files:
                status, ast = run_pipeline(path)
                self.assertEqual(status, "ok")
                with self.subTest(caso=os.path.basename(path)):
                    for mapa in ast.mapas:
                        out_path = os.path.join(tmpdir, f"{mapa.nombre}.png")
                        render_mapa(mapa, out_path)
                        self.assertTrue(os.path.isfile(out_path))
                        self.assertGreater(os.path.getsize(out_path), 0)


class TestEndToEndDemoMap(unittest.TestCase):
    """Reproduce el ejemplo de la 'Mazmorra del Dragón' usado en el Avance 1
    y verifica que el AST resultante tenga exactamente la estructura
    esperada en términos de salas y conexiones."""

    def test_dragon_dungeon_structure(self):
        src = '''MAP "Mazmorra_del_Dragon" SIZE 8x8 {
            ROOM(0,0) TYPE=entrada EXITS=[este, sur]
            ROOM(1,0) TYPE=combate ENEMY=goblin LEVEL=2
            ROOM(2,0) TYPE=tesoro ITEM=pocion_vida
            ROOM(3,0) TYPE=jefe ENEMY=dragon LEVEL=10
            CONNECT (0,0)->(1,0) via "corredor_este"
            CONNECT (1,0)->(2,0) via "puerta_madera"
            CONNECT (2,0)->(3,0) via "puerta_secreta"
        }'''
        tokens = tokenize(src)
        p = Parser(tokens, collect_errors=True)
        ast = p.parse_programa()
        self.assertEqual(p.errors, [])

        mapa = ast.mapas[0]
        self.assertEqual(len(mapa.salas()), 4)
        self.assertEqual(len(mapa.conexiones()), 3)
        self.assertEqual(mapa.salas()[3].tipo(), "jefe")
        self.assertEqual(mapa.salas()[3].enemigo(), "dragon")
        self.assertEqual(mapa.salas()[3].nivel(), 10)

        sem_errors = check_programa(ast)
        self.assertEqual(sem_errors, [])


if __name__ == "__main__":
    unittest.main()
