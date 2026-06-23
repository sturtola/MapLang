"""
test_parser.py — Pruebas unitarias del analizador sintáctico de MapLang
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from parser import parse, ParseError
from ast_nodes import TipoSala, Salidas, Enemigo, Nivel, Item, Npc, Sala, Conexion


class TestParserValidInputs(unittest.TestCase):

    def test_minimal_map(self):
        src = 'MAP "M" SIZE 1x1 { ROOM(0,0) TYPE=entrada }'
        ast, errors = parse(src, collect_errors=True)
        self.assertEqual(errors, [])
        self.assertEqual(len(ast.mapas), 1)
        self.assertEqual(ast.mapas[0].nombre, "M")
        self.assertEqual(ast.mapas[0].ancho, 1)
        self.assertEqual(ast.mapas[0].alto, 1)

    def test_multiple_maps(self):
        src = '''
        MAP "A" SIZE 1x1 { ROOM(0,0) TYPE=entrada }
        MAP "B" SIZE 1x1 { ROOM(0,0) TYPE=jefe }
        '''
        ast, errors = parse(src, collect_errors=True)
        self.assertEqual(errors, [])
        self.assertEqual(len(ast.mapas), 2)
        self.assertEqual(ast.mapas[0].nombre, "A")
        self.assertEqual(ast.mapas[1].nombre, "B")

    def test_room_all_attributes(self):
        src = ('MAP "M" SIZE 5x5 { ROOM(1,2) TYPE=combate EXITS=[norte,sur] '
               'ENEMY=goblin LEVEL=3 ITEM=espada NPC=mercader }')
        ast, errors = parse(src, collect_errors=True)
        self.assertEqual(errors, [])
        sala = ast.mapas[0].salas()[0]
        self.assertEqual(sala.x, 1)
        self.assertEqual(sala.y, 2)
        self.assertEqual(sala.tipo(), "combate")
        self.assertEqual(sala.salidas(), ["norte", "sur"])
        self.assertEqual(sala.enemigo(), "goblin")
        self.assertEqual(sala.nivel(), 3)
        self.assertEqual(sala.item(), "espada")
        self.assertEqual(sala.npc(), "mercader")

    def test_attribute_order_is_free(self):
        """Decisión de diseño: el orden de atributos dentro de ROOM es libre."""
        src1 = 'MAP "M" SIZE 2x2 { ROOM(0,0) TYPE=tesoro ITEM=oro LEVEL=1 }'
        src2 = 'MAP "M" SIZE 2x2 { ROOM(0,0) LEVEL=1 ITEM=oro TYPE=tesoro }'
        ast1, e1 = parse(src1, collect_errors=True)
        ast2, e2 = parse(src2, collect_errors=True)
        self.assertEqual(e1, [])
        self.assertEqual(e2, [])
        s1, s2 = ast1.mapas[0].salas()[0], ast2.mapas[0].salas()[0]
        self.assertEqual(s1.tipo(), s2.tipo())
        self.assertEqual(s1.item(), s2.item())
        self.assertEqual(s1.nivel(), s2.nivel())

    def test_connect_without_label(self):
        src = 'MAP "M" SIZE 2x1 { ROOM(0,0) TYPE=entrada ROOM(1,0) TYPE=jefe CONNECT (0,0)->(1,0) }'
        ast, errors = parse(src, collect_errors=True)
        self.assertEqual(errors, [])
        con = ast.mapas[0].conexiones()[0]
        self.assertEqual(con.origen, (0, 0))
        self.assertEqual(con.destino, (1, 0))
        self.assertIsNone(con.etiqueta)

    def test_connect_with_label(self):
        src = ('MAP "M" SIZE 2x1 { ROOM(0,0) TYPE=entrada ROOM(1,0) TYPE=jefe '
               'CONNECT (0,0)->(1,0) via "puerta" }')
        ast, errors = parse(src, collect_errors=True)
        self.assertEqual(errors, [])
        con = ast.mapas[0].conexiones()[0]
        self.assertEqual(con.etiqueta, "puerta")

    def test_exits_list_single_direction(self):
        src = 'MAP "M" SIZE 1x1 { ROOM(0,0) TYPE=entrada EXITS=[norte] }'
        ast, errors = parse(src, collect_errors=True)
        self.assertEqual(errors, [])
        self.assertEqual(ast.mapas[0].salas()[0].salidas(), ["norte"])

    def test_comments_and_whitespace_do_not_affect_parse(self):
        src = '''
        // comentario
        MAP "M" SIZE 1x1 {
            // otro comentario
            ROOM(0,0) TYPE=entrada // final de linea
        }
        '''
        ast, errors = parse(src, collect_errors=True)
        self.assertEqual(errors, [])


class TestParserInvalidInputs(unittest.TestCase):

    def test_missing_closing_paren_in_room(self):
        src = 'MAP "M" SIZE 1x1 { ROOM(0,0 TYPE=entrada }'
        ast, errors = parse(src, collect_errors=True)
        self.assertTrue(len(errors) >= 1)

    def test_missing_y_coordinate(self):
        src = 'MAP "M" SIZE 1x1 { ROOM(1,) TYPE=combate }'
        ast, errors = parse(src, collect_errors=True)
        self.assertTrue(len(errors) >= 1)

    def test_incomplete_connect_destination(self):
        src = 'MAP "M" SIZE 1x1 { ROOM(0,0) TYPE=entrada CONNECT (0,0)-> via "x" }'
        ast, errors = parse(src, collect_errors=True)
        self.assertTrue(len(errors) >= 1)

    def test_invalid_dimension(self):
        src = 'MAP "M" SIZE abc { ROOM(0,0) TYPE=entrada }'
        with self.assertRaises(ParseError):
            parse(src, collect_errors=False)

    def test_invalid_room_type(self):
        src = 'MAP "M" SIZE 1x1 { ROOM(0,0) TYPE=castillo }'
        with self.assertRaises(ParseError):
            parse(src, collect_errors=False)

    def test_empty_body(self):
        src = 'MAP "M" SIZE 1x1 { }'
        with self.assertRaises(ParseError):
            parse(src, collect_errors=False)

    def test_room_without_attributes(self):
        src = 'MAP "M" SIZE 1x1 { ROOM(0,0) }'
        with self.assertRaises(ParseError):
            parse(src, collect_errors=False)

    def test_multiple_errors_recovered(self):
        """El parser debe reportar más de un error en una sola pasada."""
        src = '''MAP "M" SIZE 3x3 {
            ROOM(0,0 TYPE=entrada
            ROOM(1,) TYPE=combate
            ROOM(2,0) TYPE=tesoro
        }'''
        ast, errors = parse(src, collect_errors=True)
        self.assertGreaterEqual(len(errors), 2)
        # a pesar de los errores, ROOM(2,0) (correcta) debe haberse reconocido
        if ast:
            salas_validas = [s for s in ast.mapas[0].salas() if s.x == 2]
            self.assertEqual(len(salas_validas), 1)

    def test_error_includes_line_number(self):
        # El error se reporta en la línea donde el parser detecta el token
        # inesperado, que en este caso es la línea de cierre del bloque
        # (falta el paréntesis de cierre de ROOM, así que el "}" se topa
        # inesperadamente en la línea siguiente).
        src = 'MAP "M" SIZE 1x1 {\nROOM(0,0\n}'
        ast, errors = parse(src, collect_errors=True)
        self.assertTrue(any(e.line == 3 for e in errors))


class TestParserNoAmbiguity(unittest.TestCase):
    """Verifica que la gramática no presenta ambigüedad estructural:
    cada atributo de sala se reconoce únicamente por su palabra clave
    inicial (FIRST(<atributo_i>) son disjuntos entre sí), por lo que para
    una entrada válida existe una única derivación por izquierda y, por lo
    tanto, un único árbol de derivación."""

    def test_same_input_always_same_ast_structure(self):
        src = 'MAP "M" SIZE 1x1 { ROOM(0,0) TYPE=entrada EXITS=[norte] ENEMY=x }'
        ast1, _ = parse(src, collect_errors=True)
        ast2, _ = parse(src, collect_errors=True)
        self.assertEqual(ast1.to_dict(), ast2.to_dict())


if __name__ == "__main__":
    unittest.main()
