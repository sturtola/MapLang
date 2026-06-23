"""
semantic.py — Validaciones semánticas básicas sobre el AST de MapLang
==========================================================================

La gramática formal de MapLang garantiza corrección *sintáctica*, pero
existen reglas adicionales de buena formación que no pueden expresarse
mediante una GLC libre de contexto puro (o que resultaría engorroso
expresar) y que se verifican aquí mediante un recorrido del AST:

    S1. Las coordenadas (x, y) de cada sala deben estar dentro de los
        límites declarados por SIZE NxM del mapa.
    S2. No puede haber dos salas declaradas en la misma coordenada (x, y).
    S3. Toda CONNECT debe referenciar coordenadas de salas existentes
        (tanto origen como destino).
    S4. Un atributo no puede repetirse dentro de la misma sala (ej. dos
        TYPE= en la misma ROOM).

Estas reglas son intencionalmente "semánticas" (dependen del contexto
global del mapa, no de una única producción) y se reportan con el mismo
estilo de mensaje orientado al usuario que los errores léxicos/sintácticos.
"""

from __future__ import annotations
from typing import List
from ast_nodes import Programa, Mapa, TipoSala, Salidas, Enemigo, Nivel, Item, Npc


class SemanticError(Exception):
    def __init__(self, message: str, line: int = 0):
        loc = f" (línea {line})" if line else ""
        super().__init__(f"Error semántico{loc}: {message}")
        self.line = line
        self.message = message


def _attr_kind(attr) -> str:
    return type(attr).__name__


def check_mapa(mapa: Mapa) -> List[SemanticError]:
    errors: List[SemanticError] = []
    seen_coords = {}

    for sala in mapa.salas():
        # S1: límites del mapa
        if not (0 <= sala.x < mapa.ancho and 0 <= sala.y < mapa.alto):
            errors.append(SemanticError(
                f"la sala ({sala.x},{sala.y}) está fuera de los límites "
                f"del mapa '{mapa.nombre}' ({mapa.ancho}x{mapa.alto})",
                sala.line,
            ))

        # S2: coordenadas duplicadas
        key = (sala.x, sala.y)
        if key in seen_coords:
            errors.append(SemanticError(
                f"ya existe una sala declarada en ({sala.x},{sala.y}) "
                f"(primera declaración en línea {seen_coords[key]})",
                sala.line,
            ))
        else:
            seen_coords[key] = sala.line

        # S4: atributos repetidos dentro de la misma sala
        kinds_seen = set()
        for attr in sala.atributos:
            k = _attr_kind(attr)
            if k in kinds_seen:
                errors.append(SemanticError(
                    f"la sala ({sala.x},{sala.y}) repite el atributo {k}",
                    sala.line,
                ))
            kinds_seen.add(k)

    sala_coords = set(seen_coords.keys())
    for conexion in mapa.conexiones():
        # S3: extremos deben ser salas existentes
        if conexion.origen not in sala_coords:
            errors.append(SemanticError(
                f"CONNECT referencia la sala de origen {conexion.origen} "
                f"que no fue declarada en el mapa '{mapa.nombre}'",
                conexion.line,
            ))
        if conexion.destino not in sala_coords:
            errors.append(SemanticError(
                f"CONNECT referencia la sala de destino {conexion.destino} "
                f"que no fue declarada en el mapa '{mapa.nombre}'",
                conexion.line,
            ))

    return errors


def check_programa(programa: Programa) -> List[SemanticError]:
    errors: List[SemanticError] = []
    nombres = {}
    for mapa in programa.mapas:
        if mapa.nombre in nombres:
            errors.append(SemanticError(
                f"el nombre de mapa '{mapa.nombre}' ya fue usado "
                f"(línea {nombres[mapa.nombre]})", mapa.line,
            ))
        else:
            nombres[mapa.nombre] = mapa.line
        errors.extend(check_mapa(mapa))
    return errors
