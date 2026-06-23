"""
test_semantic.py — Pruebas unitarias de las validaciones semánticas de MapLang
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from parser import parse
from semantic import check_programa


def _check(src: str):
    ast, parse_errors = parse(src, collect_errors=True)
    assert parse_errors == [], f"se esperaba que el parseo fuera correcto: {parse_errors}"
    return check_programa(ast)


class TestSemanticValid(unittest.TestCase):

    def test_no_errors_on_well_formed_map(self):
        src = '''MAP "M" SIZE 2x2 {
            ROOM(0,0) TYPE=entrada
            ROOM(1,1) TYPE=jefe
            CONNECT (0,0)->(1,1)
        }'''
        errors = _check(src)
        self.assertEqual(errors, [])

    def test_room_at_boundary_is_valid(self):
        # límite superior válido: SIZE NxM admite coordenadas hasta (N-1, M-1)
        src = 'MAP "M" SIZE 3x3 { ROOM(2,2) TYPE=jefe }'
        errors = _check(src)
        self.assertEqual(errors, [])


class TestSemanticErrors(unittest.TestCase):

    def test_room_out_of_bounds_x(self):
        src = 'MAP "M" SIZE 2x2 { ROOM(2,0) TYPE=entrada }'
        errors = _check(src)
        self.assertEqual(len(errors), 1)
        self.assertIn("fuera de los límites", errors[0].message)

    def test_room_out_of_bounds_y(self):
        src = 'MAP "M" SIZE 2x2 { ROOM(0,2) TYPE=entrada }'
        errors = _check(src)
        self.assertEqual(len(errors), 1)

    def test_duplicate_room_coordinates(self):
        src = '''MAP "M" SIZE 2x2 {
            ROOM(0,0) TYPE=entrada
            ROOM(0,0) TYPE=combate
        }'''
        errors = _check(src)
        self.assertEqual(len(errors), 1)
        self.assertIn("ya existe una sala", errors[0].message)

    def test_connect_to_nonexistent_room(self):
        src = '''MAP "M" SIZE 2x2 {
            ROOM(0,0) TYPE=entrada
            CONNECT (0,0)->(1,1)
        }'''
        errors = _check(src)
        self.assertEqual(len(errors), 1)
        self.assertIn("no fue declarada", errors[0].message)

    def test_connect_from_nonexistent_room(self):
        src = '''MAP "M" SIZE 2x2 {
            ROOM(1,1) TYPE=entrada
            CONNECT (0,0)->(1,1)
        }'''
        errors = _check(src)
        self.assertEqual(len(errors), 1)

    def test_duplicate_attribute_in_same_room(self):
        src = 'MAP "M" SIZE 2x2 { ROOM(0,0) TYPE=entrada TYPE=combate }'
        errors = _check(src)
        self.assertEqual(len(errors), 1)
        self.assertIn("repite el atributo", errors[0].message)

    def test_duplicate_map_name(self):
        src = '''
        MAP "A" SIZE 1x1 { ROOM(0,0) TYPE=entrada }
        MAP "A" SIZE 1x1 { ROOM(0,0) TYPE=jefe }
        '''
        errors = _check(src)
        self.assertEqual(len(errors), 1)
        self.assertIn("ya fue usado", errors[0].message)

    def test_multiple_semantic_errors_all_reported(self):
        src = '''MAP "M" SIZE 2x2 {
            ROOM(0,0) TYPE=entrada
            ROOM(0,0) TYPE=combate
            ROOM(9,9) TYPE=tesoro
            CONNECT (0,0)->(8,8)
        }'''
        errors = _check(src)
        # duplicado + fuera de límites + conexión a sala inexistente = 3
        self.assertEqual(len(errors), 3)


if __name__ == "__main__":
    unittest.main()
