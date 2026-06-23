"""
parser.py — Analizador sintáctico descendente recursivo de MapLang
=======================================================================

Implementa un parser LL(1) descendente recursivo: cada no-terminal de la
gramática (ver GRAMMAR.md) se traduce en un método de la clase `Parser`.
La elección de esta estrategia se justifica porque la gramática de MapLang
es LL(1) (cada alternativa de cada producción se reconoce de forma única
mirando el primer token, sin necesidad de backtracking) lo cual permite una
implementación manual simple y con buen control sobre el reporte de errores.

Manejo de errores
------------------
Ante un error sintáctico se lanza `ParseError`, que incluye número de línea,
columna y un mensaje orientado al usuario. El parser implementa además una
estrategia de **recuperación en modo pánico**: tras reportar un error dentro
de una `<sala>` o `<conexion>`, descarta tokens hasta encontrar el inicio de
la siguiente declaración (ROOM/CONNECT) o el cierre de bloque ("}"), de modo
que el análisis pueda continuar e informar más de un error por ejecución.
"""

from __future__ import annotations
from typing import List, Optional

from lexer import Token, tokenize, LexError
from ast_nodes import (
    Programa, Mapa, Sala, Conexion,
    TipoSala, Salidas, Enemigo, Nivel, Item, Npc,
)


class ParseError(Exception):
    """Error sintáctico con información de posición para el usuario."""

    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Error de sintaxis en línea {line}, columna {column}: {message}")
        self.line = line
        self.column = column
        self.message = message


# Palabras clave que inician cada atributo de sala (usadas para FIRST(<atributo>))
ATTR_KEYWORDS = {"TYPE", "EXITS", "ENEMY", "LEVEL", "ITEM", "NPC"}
# Palabras clave que inician una declaración (usadas para sincronización de errores)
DECL_KEYWORDS = {"ROOM", "CONNECT"}


class Parser:
    """Parser descendente recursivo para MapLang.

    Cada método `parse_X` corresponde al no-terminal <X> de la gramática y
    devuelve el nodo de AST correspondiente (ver ast_nodes.py), consumiendo
    de la lista de tokens los símbolos que reconoce.
    """

    def __init__(self, tokens: List[Token], collect_errors: bool = False):
        self.tokens = tokens
        self.pos = 0
        self.collect_errors = collect_errors
        self.errors: List[ParseError] = []

    # -- utilidades básicas de acceso a tokens --------------------------------

    def peek(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def at_end(self) -> bool:
        return self.peek().type == "EOF"

    def check_keyword(self, value: str) -> bool:
        t = self.peek()
        return t.type == "KEYWORD" and t.value == value

    def check_type(self, type_: str) -> bool:
        return self.peek().type == type_

    def advance(self) -> Token:
        t = self.peek()
        if t.type != "EOF":
            self.pos += 1
        return t

    def expect_keyword(self, value: str) -> Token:
        t = self.peek()
        if t.type == "KEYWORD" and t.value == value:
            return self.advance()
        raise ParseError(
            f"se esperaba la palabra clave '{value}' pero se encontró "
            f"{self._describe(t)}", t.line, t.column,
        )

    def expect_type(self, type_: str, description: str) -> Token:
        t = self.peek()
        if t.type == type_:
            return self.advance()
        raise ParseError(
            f"se esperaba {description} pero se encontró {self._describe(t)}",
            t.line, t.column,
        )

    def expect_punct(self, value: str) -> Token:
        t = self.peek()
        if t.type == "PUNCT" and t.value == value:
            return self.advance()
        raise ParseError(
            f"se esperaba '{value}' pero se encontró {self._describe(t)}",
            t.line, t.column,
        )

    @staticmethod
    def _describe(t: Token) -> str:
        if t.type == "EOF":
            return "fin de la entrada"
        return f"'{t.value}' ({t.type})"

    # -- sincronización para recuperación de errores --------------------------

    def _synchronize_to_declaration_or_close(self) -> None:
        """Avanza tokens hasta encontrar ROOM, CONNECT, '}' o EOF.

        Se utiliza tras capturar un ParseError dentro de <sala> o <conexion>
        para que el análisis pueda continuar con la siguiente declaración,
        permitiendo reportar múltiples errores en una sola pasada.
        """
        while not self.at_end():
            t = self.peek()
            if t.type == "KEYWORD" and t.value in DECL_KEYWORDS:
                return
            if t.type == "PUNCT" and t.value == "}":
                return
            self.advance()

    # -- producciones de la gramática -----------------------------------------

    def parse_programa(self) -> Programa:
        """<programa> ::= <mapa>+"""
        mapas = []
        while not self.at_end():
            mapas.append(self.parse_mapa())
        if not mapas:
            t = self.peek()
            raise ParseError("el programa no contiene ningún mapa (se esperaba 'MAP')",
                              t.line, t.column)
        return Programa(mapas=mapas)

    def parse_mapa(self) -> Mapa:
        """<mapa> ::= "MAP" <cadena> "SIZE" <dimension> "{" <cuerpo> "}" """
        map_tok = self.expect_keyword("MAP")
        name_tok = self.expect_type("STRING", "una cadena (nombre del mapa)")
        self.expect_keyword("SIZE")
        size_tok = self.expect_type("SIZE", "una dimensión del tipo NxM (ej. 8x8)")
        ancho_str, alto_str = size_tok.value.split("x")
        self.expect_punct("{")
        declaraciones = self.parse_cuerpo()
        self.expect_punct("}")
        return Mapa(
            nombre=name_tok.value,
            ancho=int(ancho_str),
            alto=int(alto_str),
            declaraciones=declaraciones,
            line=map_tok.line,
        )

    def parse_cuerpo(self) -> List:
        """<cuerpo> ::= <declaracion>+"""
        declaraciones = []
        while self.check_keyword("ROOM") or self.check_keyword("CONNECT"):
            try:
                declaraciones.append(self.parse_declaracion())
            except ParseError as e:
                if self.collect_errors:
                    self.errors.append(e)
                    self._synchronize_to_declaration_or_close()
                else:
                    raise
        if not declaraciones and not self.errors:
            t = self.peek()
            raise ParseError(
                "el cuerpo del mapa está vacío (se esperaba al menos una "
                "declaración ROOM o CONNECT)", t.line, t.column,
            )
        return declaraciones

    def parse_declaracion(self):
        """<declaracion> ::= <sala> | <conexion>"""
        if self.check_keyword("ROOM"):
            return self.parse_sala()
        if self.check_keyword("CONNECT"):
            return self.parse_conexion()
        t = self.peek()
        raise ParseError(
            f"se esperaba 'ROOM' o 'CONNECT' pero se encontró {self._describe(t)}",
            t.line, t.column,
        )

    def parse_sala(self) -> Sala:
        """<sala> ::= "ROOM" "(" <entero_pos> "," <entero_pos> ")" <atributo>+"""
        room_tok = self.expect_keyword("ROOM")
        self.expect_punct("(")
        x_tok = self.expect_type("INTEGER", "un entero (coordenada x)")
        self.expect_punct(",")
        y_tok = self.expect_type("INTEGER", "un entero (coordenada y)")
        self.expect_punct(")")

        atributos = []
        while self.check_attr_start():
            atributos.append(self.parse_atributo())

        if not atributos:
            t = self.peek()
            raise ParseError(
                "la sala no tiene ningún atributo (se esperaba al menos "
                "TYPE, EXITS, ENEMY, LEVEL, ITEM o NPC)", t.line, t.column,
            )

        return Sala(x=int(x_tok.value), y=int(y_tok.value),
                     atributos=atributos, line=room_tok.line)

    def check_attr_start(self) -> bool:
        t = self.peek()
        return t.type == "KEYWORD" and t.value in ATTR_KEYWORDS

    def parse_atributo(self):
        """<atributo> ::= <tipo_sala> | <salidas> | <enemigo> | <nivel> | <item> | <npc>"""
        t = self.peek()
        if t.value == "TYPE":
            return self.parse_tipo_sala()
        if t.value == "EXITS":
            return self.parse_salidas()
        if t.value == "ENEMY":
            return self.parse_enemigo()
        if t.value == "LEVEL":
            return self.parse_nivel()
        if t.value == "ITEM":
            return self.parse_item()
        if t.value == "NPC":
            return self.parse_npc()
        raise ParseError(f"atributo de sala no reconocido: '{t.value}'", t.line, t.column)

    def parse_tipo_sala(self) -> TipoSala:
        """<tipo_sala> ::= "TYPE" "=" <tipo_valor>"""
        self.expect_keyword("TYPE")
        self.expect_punct("=")
        t = self.expect_type("TYPE_VAL", "un tipo de sala válido (entrada, pasillo, "
                                          "combate, tesoro, jefe, tienda o trampa)")
        return TipoSala(valor=t.value)

    def parse_salidas(self) -> Salidas:
        """<salidas> ::= "EXITS" "=" "[" <lista_dir> "]" """
        self.expect_keyword("EXITS")
        self.expect_punct("=")
        self.expect_punct("[")
        direcciones = self.parse_lista_dir()
        self.expect_punct("]")
        return Salidas(direcciones=direcciones)

    def parse_lista_dir(self) -> List[str]:
        """<lista_dir> ::= <direccion> ("," <direccion>)*"""
        direcciones = [self.parse_direccion()]
        while self.check_type("PUNCT") and self.peek().value == ",":
            self.advance()
            direcciones.append(self.parse_direccion())
        return direcciones

    def parse_direccion(self) -> str:
        """<direccion> ::= "norte" | "sur" | "este" | "oeste" | "arriba" | "abajo" """
        t = self.expect_type("DIRECTION", "una dirección válida (norte, sur, este, "
                                           "oeste, arriba o abajo)")
        return t.value

    def parse_enemigo(self) -> Enemigo:
        """<enemigo> ::= "ENEMY" "=" <identificador>"""
        self.expect_keyword("ENEMY")
        self.expect_punct("=")
        t = self.expect_type("IDENTIFIER", "un identificador (nombre de enemigo)")
        return Enemigo(identificador=t.value)

    def parse_nivel(self) -> Nivel:
        """<nivel> ::= "LEVEL" "=" <entero_pos>"""
        self.expect_keyword("LEVEL")
        self.expect_punct("=")
        t = self.expect_type("INTEGER", "un entero (nivel de dificultad)")
        return Nivel(valor=int(t.value))

    def parse_item(self) -> Item:
        """<item> ::= "ITEM" "=" <identificador>"""
        self.expect_keyword("ITEM")
        self.expect_punct("=")
        t = self.expect_type("IDENTIFIER", "un identificador (nombre de ítem)")
        return Item(identificador=t.value)

    def parse_npc(self) -> Npc:
        """<npc> ::= "NPC" "=" <identificador>"""
        self.expect_keyword("NPC")
        self.expect_punct("=")
        t = self.expect_type("IDENTIFIER", "un identificador (nombre de NPC)")
        return Npc(identificador=t.value)

    def parse_conexion(self) -> Conexion:
        """<conexion> ::= "CONNECT" "(" <entero_pos> "," <entero_pos> ")" "->"
                           "(" <entero_pos> "," <entero_pos> ")" [ "via" <cadena> ]"""
        connect_tok = self.expect_keyword("CONNECT")
        self.expect_punct("(")
        x1 = self.expect_type("INTEGER", "un entero (coordenada x de origen)")
        self.expect_punct(",")
        y1 = self.expect_type("INTEGER", "un entero (coordenada y de origen)")
        self.expect_punct(")")
        self.expect_punct("->")
        self.expect_punct("(")
        x2 = self.expect_type("INTEGER", "un entero (coordenada x de destino)")
        self.expect_punct(",")
        y2 = self.expect_type("INTEGER", "un entero (coordenada y de destino)")
        self.expect_punct(")")

        etiqueta = None
        # Decisión LL(1): "via" no pertenece a FOLLOW(<conexion>), por lo que
        # un único token de lookahead basta para decidir si la parte opcional
        # está presente.
        if self.check_keyword("via"):
            self.advance()
            etiqueta_tok = self.expect_type("STRING", "una cadena (etiqueta de la conexión)")
            etiqueta = etiqueta_tok.value

        return Conexion(
            origen=(int(x1.value), int(y1.value)),
            destino=(int(x2.value), int(y2.value)),
            etiqueta=etiqueta,
            line=connect_tok.line,
        )


def parse(source: str, collect_errors: bool = False):
    """Función de conveniencia: tokeniza y parsea una cadena fuente completa.

    Si `collect_errors` es True, el parser intenta recuperarse de errores
    sintácticos dentro del cuerpo de un mapa y acumula todos los encontrados
    en `parser.errors` en lugar de abortar en el primero. Devuelve la tupla
    (Programa | None, lista_de_errores).
    """
    tokens = tokenize(source)
    p = Parser(tokens, collect_errors=collect_errors)
    try:
        ast = p.parse_programa()
        return ast, p.errors
    except ParseError as e:
        if collect_errors:
            p.errors.append(e)
            return None, p.errors
        raise


if __name__ == "__main__":  # pragma: no cover - demo manual
    demo = '''MAP "Demo" SIZE 3x3 {
        ROOM(0,0) TYPE=entrada EXITS=[este]
        ROOM(1,0) TYPE=combate ENEMY=goblin LEVEL=2
        CONNECT (0,0)->(1,0) via "pasillo_1"
    }'''
    ast, errors = parse(demo, collect_errors=True)
    if ast:
        print(ast)
    for e in errors:
        print(e)
