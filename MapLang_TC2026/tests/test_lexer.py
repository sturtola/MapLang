"""
test_lexer.py — Pruebas unitarias del analizador léxico de MapLang
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lexer import tokenize, LexError, Lexer


class TestLexerTokens(unittest.TestCase):

    def test_keywords(self):
        tokens = tokenize("MAP ROOM CONNECT SIZE TYPE EXITS ENEMY LEVEL ITEM NPC via")
        types = [t.type for t in tokens if t.type != "EOF"]
        self.assertTrue(all(t == "KEYWORD" for t in types))

    def test_type_values(self):
        tokens = tokenize("entrada pasillo combate tesoro jefe tienda trampa")
        types = [t.type for t in tokens if t.type != "EOF"]
        self.assertTrue(all(t == "TYPE_VAL" for t in types))

    def test_directions(self):
        tokens = tokenize("norte sur este oeste arriba abajo")
        types = [t.type for t in tokens if t.type != "EOF"]
        self.assertTrue(all(t == "DIRECTION" for t in types))

    def test_identifier_not_keyword(self):
        tokens = tokenize("goblin")
        self.assertEqual(tokens[0].type, "IDENTIFIER")
        self.assertEqual(tokens[0].value, "goblin")

    def test_string_literal(self):
        tokens = tokenize('"Mazmorra_1"')
        self.assertEqual(tokens[0].type, "STRING")
        self.assertEqual(tokens[0].value, "Mazmorra_1")

    def test_size_literal(self):
        tokens = tokenize("8x8")
        self.assertEqual(tokens[0].type, "SIZE")
        self.assertEqual(tokens[0].value, "8x8")

    def test_integer_literal(self):
        tokens = tokenize("255")
        self.assertEqual(tokens[0].type, "INTEGER")
        self.assertEqual(tokens[0].value, "255")

    def test_integer_not_confused_with_size(self):
        # "5 x" con espacio NO debe interpretarse como SIZE (5x...)
        tokens = tokenize("5 x")
        self.assertEqual(tokens[0].type, "INTEGER")

    def test_punctuation(self):
        tokens = tokenize("{ } ( ) [ ] = , ->")
        values = [t.value for t in tokens if t.type != "EOF"]
        self.assertEqual(values, ["{", "}", "(", ")", "[", "]", "=", ",", "->"])

    def test_comments_ignored(self):
        tokens = tokenize("MAP // esto es un comentario\nROOM")
        types = [t.type for t in tokens if t.type != "EOF"]
        self.assertEqual(types, ["KEYWORD", "KEYWORD"])

    def test_whitespace_ignored(self):
        tokens = tokenize("MAP    \n\n\t  ROOM")
        types = [t.type for t in tokens if t.type != "EOF"]
        self.assertEqual(types, ["KEYWORD", "KEYWORD"])

    def test_line_and_column_tracking(self):
        tokens = tokenize("MAP\nROOM")
        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[1].line, 2)

    def test_eof_token_present(self):
        tokens = tokenize("MAP")
        self.assertEqual(tokens[-1].type, "EOF")


class TestLexerErrors(unittest.TestCase):

    def test_unclosed_string_raises(self):
        with self.assertRaises(LexError):
            tokenize('"sin cerrar')

    def test_unclosed_string_with_newline_raises(self):
        with self.assertRaises(LexError):
            tokenize('"linea1\nlinea2"')

    def test_invalid_character_raises(self):
        with self.assertRaises(LexError):
            tokenize("MAP @ ROOM")

    def test_error_reports_correct_line(self):
        try:
            tokenize("MAP\n@invalido")
            self.fail("se esperaba LexError")
        except LexError as e:
            self.assertEqual(e.line, 2)

    def test_dollar_sign_invalid(self):
        with self.assertRaises(LexError):
            tokenize("$variable")

    def test_hash_invalid(self):
        with self.assertRaises(LexError):
            tokenize("# comentario mal escrito")


class TestLexerFullExample(unittest.TestCase):

    def test_complete_room_tokenization(self):
        src = 'ROOM(0,0) TYPE=entrada EXITS=[este,sur]'
        tokens = tokenize(src)
        types = [t.type for t in tokens if t.type != "EOF"]
        expected = [
            "KEYWORD", "PUNCT", "INTEGER", "PUNCT", "INTEGER", "PUNCT",
            "KEYWORD", "PUNCT", "TYPE_VAL",
            "KEYWORD", "PUNCT", "PUNCT", "DIRECTION", "PUNCT", "DIRECTION", "PUNCT",
        ]
        self.assertEqual(types, expected)


if __name__ == "__main__":
    unittest.main()
