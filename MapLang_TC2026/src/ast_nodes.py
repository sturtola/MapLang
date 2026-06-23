"""
ast_nodes.py — Definición de los nodos del Árbol Sintáctico Abstracto (AST)
=============================================================================

Cada clase representa un no-terminal (o construcción semánticamente
relevante) de la gramática de MapLang. Se modelan como dataclasses para
obtener automáticamente `__repr__`, comparación estructural e inmutabilidad
opcional, lo cual facilita tanto el testing como la serialización a JSON.

Todas las clases exponen un método `to_dict()` que produce una representación
serializable (usada por main.py para exportar el AST en formato JSON y por
renderer.py para construir la imagen del mapa).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Union


# ---------------------------------------------------------------------------
# Nodos de atributos de sala
# ---------------------------------------------------------------------------

@dataclass
class TipoSala:
    valor: str  # entrada | pasillo | combate | tesoro | jefe | tienda | trampa

    def to_dict(self) -> dict:
        return {"node": "TipoSala", "valor": self.valor}


@dataclass
class Salidas:
    direcciones: List[str]

    def to_dict(self) -> dict:
        return {"node": "Salidas", "direcciones": self.direcciones}


@dataclass
class Enemigo:
    identificador: str

    def to_dict(self) -> dict:
        return {"node": "Enemigo", "identificador": self.identificador}


@dataclass
class Nivel:
    valor: int

    def to_dict(self) -> dict:
        return {"node": "Nivel", "valor": self.valor}


@dataclass
class Item:
    identificador: str

    def to_dict(self) -> dict:
        return {"node": "Item", "identificador": self.identificador}


@dataclass
class Npc:
    identificador: str

    def to_dict(self) -> dict:
        return {"node": "Npc", "identificador": self.identificador}


# Tipo unión para cualquier atributo válido de una sala
Atributo = Union[TipoSala, Salidas, Enemigo, Nivel, Item, Npc]


# ---------------------------------------------------------------------------
# Nodos de declaraciones (sala / conexión)
# ---------------------------------------------------------------------------

@dataclass
class Sala:
    x: int
    y: int
    atributos: List[Atributo] = field(default_factory=list)
    line: int = 0

    # -- accesos convenientes a los atributos, usados por el renderer --------
    def tipo(self) -> Optional[str]:
        for a in self.atributos:
            if isinstance(a, TipoSala):
                return a.valor
        return None

    def salidas(self) -> List[str]:
        for a in self.atributos:
            if isinstance(a, Salidas):
                return a.direcciones
        return []

    def enemigo(self) -> Optional[str]:
        for a in self.atributos:
            if isinstance(a, Enemigo):
                return a.identificador
        return None

    def nivel(self) -> Optional[int]:
        for a in self.atributos:
            if isinstance(a, Nivel):
                return a.valor
        return None

    def item(self) -> Optional[str]:
        for a in self.atributos:
            if isinstance(a, Item):
                return a.identificador
        return None

    def npc(self) -> Optional[str]:
        for a in self.atributos:
            if isinstance(a, Npc):
                return a.identificador
        return None

    def to_dict(self) -> dict:
        return {
            "node": "Sala",
            "x": self.x,
            "y": self.y,
            "atributos": [a.to_dict() for a in self.atributos],
            "line": self.line,
        }


@dataclass
class Conexion:
    origen: tuple  # (x, y)
    destino: tuple  # (x, y)
    etiqueta: Optional[str] = None
    line: int = 0

    def to_dict(self) -> dict:
        return {
            "node": "Conexion",
            "origen": list(self.origen),
            "destino": list(self.destino),
            "etiqueta": self.etiqueta,
            "line": self.line,
        }


Declaracion = Union[Sala, Conexion]


# ---------------------------------------------------------------------------
# Nodos de nivel superior
# ---------------------------------------------------------------------------

@dataclass
class Mapa:
    nombre: str
    ancho: int
    alto: int
    declaraciones: List[Declaracion] = field(default_factory=list)
    line: int = 0

    def salas(self) -> List[Sala]:
        return [d for d in self.declaraciones if isinstance(d, Sala)]

    def conexiones(self) -> List[Conexion]:
        return [d for d in self.declaraciones if isinstance(d, Conexion)]

    def to_dict(self) -> dict:
        return {
            "node": "Mapa",
            "nombre": self.nombre,
            "ancho": self.ancho,
            "alto": self.alto,
            "declaraciones": [d.to_dict() for d in self.declaraciones],
            "line": self.line,
        }


@dataclass
class Programa:
    mapas: List[Mapa] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"node": "Programa", "mapas": [m.to_dict() for m in self.mapas]}
