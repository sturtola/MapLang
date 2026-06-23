"""
lexer.py — Analizador léxico (tokenizador) de MapLang
========================================================

Implementación manual (sin Flex/PLY/ANTLR) de un analizador léxico para el
lenguaje MapLang, un DSL para describir mapas de videojuegos tipo
dungeon-crawler.

Categorías de token reconocidas:
    KEYWORD      Palabras reservadas: MAP, ROOM, CONNECT, SIZE, TYPE, EXITS,
                 ENEMY, LEVEL, ITEM, NPC, via
    TYPE_VAL     Valores de tipo de sala: entrada, pasillo, combate, tesoro,
                 jefe, tienda, trampa
    DIRECTION    Direcciones cardinales: norte, sur, este, oeste, arriba, abajo
    STRING       Literal de cadena entre comillas dobles: "texto"
    INTEGER      Literal entero no negativo: [0-9]+
    IDENTIFIER   Identificador genérico: [a-zA-Z_][a-zA-Z0-9_]*
    PUNCT        Símbolos estructurales: { } ( ) [ ] = , -> x

El lexer ignora espacios en blanco y comentarios de línea ("// ...").
Cada token registra su número de línea y columna para el reporte de errores.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional


# ---------------------------------------------------------------------------
# Conjuntos de palabras reservadas
# ---------------------------------------------------------------------------

KEYWORDS = {
    "MAP", "ROOM", "CONNECT", "SIZE",
    "TYPE", "EXITS", "ENEMY", "LEVEL", "ITEM", "NPC", "via",
}

TYPE_VALS = {
    "entrada", "pasillo", "combate", "tesoro", "jefe", "tienda", "trampa",
}

DIRECTIONS = {
    "norte", "sur", "este", "oeste", "arriba", "abajo",
}

# Símbolos de puntuación de un solo carácter
SINGLE_PUNCT = set("{}()[]=,")


@dataclass
class Token:
    """Representa un token producido por el lexer."""
    type: str
    value: str
    line: int
    column: int

    def __repr__(self) -> str:  # pragma: no cover - sólo para debugging
        return f"Token({self.type}, {self.value!r}, L{self.line}:C{self.column})"


class LexError(Exception):
    """Error léxico: carácter inesperado o cadena sin cerrar."""

    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Error léxico en línea {line}, columna {column}: {message}")
        self.line = line
        self.column = column
        self.message = message


class Lexer:
    """Analizador léxico de MapLang.

    Recorre el código fuente carácter a carácter (sin usar expresiones
    regulares para el escaneo principal, salvo para reconocer prefijos
    de identificadores y números) y produce una lista de objetos Token.
    """

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: List[Token] = []

    # -- utilidades internas -------------------------------------------------

    def _peek(self, offset: int = 0) -> Optional[str]:
        idx = self.pos + offset
        if idx < len(self.source):
            return self.source[idx]
        return None

    def _advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _add(self, type_: str, value: str, line: int, col: int) -> None:
        self.tokens.append(Token(type_, value, line, col))

    # -- método principal ------------------------------------------------------

    def tokenize(self) -> List[Token]:
        """Recorre todo el código fuente y devuelve la lista de tokens."""
        while self.pos < len(self.source):
            ch = self._peek()

            # 1) Espacios en blanco: se ignoran
            if ch is not None and ch.isspace():
                self._advance()
                continue

            # 2) Comentarios de línea: // hasta fin de línea
            if ch == "/" and self._peek(1) == "/":
                while self._peek() is not None and self._peek() != "\n":
                    self._advance()
                continue

            start_line, start_col = self.line, self.col

            # 3) Cadenas: "..."
            if ch == '"':
                self._tokenize_string(start_line, start_col)
                continue

            # 4) Operador de flecha: ->
            if ch == "-" and self._peek(1) == ">":
                self._advance()
                self._advance()
                self._add("PUNCT", "->", start_line, start_col)
                continue

            # 5) Números (enteros, posiblemente seguidos de 'x' para dimensión)
            if ch is not None and ch.isdigit():
                self._tokenize_number(start_line, start_col)
                continue

            # 6) Identificadores / palabras clave / tipos / direcciones
            if ch is not None and (ch.isalpha() or ch == "_"):
                self._tokenize_word(start_line, start_col)
                continue

            # 7) Puntuación simple
            if ch in SINGLE_PUNCT:
                self._advance()
                self._add("PUNCT", ch, start_line, start_col)
                continue

            # 8) Carácter no reconocido -> error léxico
            raise LexError(f"carácter inesperado {ch!r}", start_line, start_col)

        # Token centinela de fin de entrada, simplifica el parser (lookahead seguro)
        self._add("EOF", "", self.line, self.col)
        return self.tokens

    # -- sub-tokenizadores ----------------------------------------------------

    def _tokenize_string(self, line: int, col: int) -> None:
        self._advance()  # consume comilla de apertura
        chars = []
        while True:
            ch = self._peek()
            if ch is None or ch == "\n":
                raise LexError("cadena sin cerrar (falta comilla de cierre)", line, col)
            if ch == '"':
                self._advance()  # consume comilla de cierre
                break
            chars.append(self._advance())
        value = "".join(chars)
        self._add("STRING", value, line, col)

    def _tokenize_number(self, line: int, col: int) -> None:
        digits = []
        while self._peek() is not None and self._peek().isdigit():
            digits.append(self._advance())
        first_num = "".join(digits)

        # ¿Es una dimensión NxM? (entero, 'x', entero, sin espacios)
        if self._peek() == "x" and self._peek(1) is not None and self._peek(1).isdigit():
            self._advance()  # consume 'x'
            second_digits = []
            while self._peek() is not None and self._peek().isdigit():
                second_digits.append(self._advance())
            second_num = "".join(second_digits)
            self._add("SIZE", f"{first_num}x{second_num}", line, col)
            return

        self._add("INTEGER", first_num, line, col)

    def _tokenize_word(self, line: int, col: int) -> None:
        chars = []
        while self._peek() is not None and (self._peek().isalnum() or self._peek() == "_"):
            chars.append(self._advance())
        word = "".join(chars)

        if word in KEYWORDS:
            kind = "KEYWORD"
        elif word in TYPE_VALS:
            kind = "TYPE_VAL"
        elif word in DIRECTIONS:
            kind = "DIRECTION"
        else:
            kind = "IDENTIFIER"
        self._add(kind, word, line, col)


def tokenize(source: str) -> List[Token]:
    """Función de conveniencia: tokeniza una cadena fuente completa."""
    return Lexer(source).tokenize()


if __name__ == "__main__":  # pragma: no cover - demo manual
    demo = '''MAP "Demo" SIZE 3x3 {
        ROOM(0,0) TYPE=entrada EXITS=[este]
    }'''
    for t in tokenize(demo):
        print(t)
