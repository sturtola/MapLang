"""
renderer.py — Renderizador visual de mapas MapLang
=========================================================

Recorre el AST de un `Mapa` y genera una representación gráfica utilizando
la biblioteca matplotlib. Cada sala se dibuja como una celda coloreada según
su tipo (TYPE=), anotada con sus atributos (enemigo, nivel, ítem, NPC), y
cada CONNECT se dibuja como una línea entre los centros de las salas
correspondientes, con su etiqueta si la tiene.

Esta es la salida visual central del sistema y el punto de la demostración
en vivo durante la exposición oral.
"""

from __future__ import annotations
from typing import Optional

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from ast_nodes import Mapa


# Paleta de colores por tipo de sala (tema oscuro / dorado, consistente con
# la identidad visual ya usada por el equipo en otros proyectos — POINTEX)
TYPE_COLORS = {
    "entrada": "#3ddc97",
    "pasillo": "#6c7a89",
    "combate": "#e74c3c",
    "tesoro":  "#f1c40f",
    "jefe":    "#8e44ad",
    "tienda":  "#3498db",
    "trampa":  "#d35400",
}

DEFAULT_COLOR = "#444444"
BG_COLOR = "#1b1b1f"
GRID_COLOR = "#33333a"
TEXT_COLOR = "#f5f5f5"
EDGE_COLOR = "#d4af37"  # dorado


def render_mapa(mapa: Mapa, output_path: str, cell_size: float = 1.6,
                 dpi: int = 150, show_grid: bool = True) -> str:
    """Genera una imagen PNG del mapa y la guarda en `output_path`.

    Devuelve la ruta del archivo generado.
    """
    fig_w = max(4.0, mapa.ancho * cell_size + 1.0)
    fig_h = max(3.2, mapa.alto * cell_size + 1.0)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    margin = 0.55
    ax.set_xlim(-margin, mapa.ancho - 1 + margin)
    ax.set_ylim(-margin, mapa.alto - 1 + margin)
    ax.invert_yaxis()  # (0,0) arriba a la izquierda, convención de mapas 2D
    ax.set_aspect("equal")

    if show_grid:
        for gx in range(mapa.ancho + 1):
            ax.axvline(gx - 0.5, color=GRID_COLOR, linewidth=0.6, zorder=0)
        for gy in range(mapa.alto + 1):
            ax.axhline(gy - 0.5, color=GRID_COLOR, linewidth=0.6, zorder=0)

    salas_por_coord = {(s.x, s.y): s for s in mapa.salas()}

    # -- dibujar conexiones primero (quedan debajo de las salas) -------------
    for con in mapa.conexiones():
        if con.origen in salas_por_coord and con.destino in salas_por_coord:
            x1, y1 = con.origen
            x2, y2 = con.destino
            ax.plot([x1, x2], [y1, y2], color=EDGE_COLOR, linewidth=2.5,
                     zorder=1, solid_capstyle="round")
            if con.etiqueta:
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                ax.text(mx, my, con.etiqueta, color=TEXT_COLOR, fontsize=7,
                         ha="center", va="center", zorder=4,
                         bbox=dict(boxstyle="round,pad=0.2", facecolor=BG_COLOR,
                                   edgecolor=EDGE_COLOR, linewidth=0.6))

    # -- dibujar salas ---------------------------------------------------------
    for sala in mapa.salas():
        color = TYPE_COLORS.get(sala.tipo(), DEFAULT_COLOR)
        rect = patches.FancyBboxPatch(
            (sala.x - 0.42, sala.y - 0.42), 0.84, 0.84,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            linewidth=1.4, edgecolor=EDGE_COLOR, facecolor=color, zorder=2,
        )
        ax.add_patch(rect)

        lines = [sala.tipo() or "?"]
        if sala.enemigo():
            lvl = f" (Lv.{sala.nivel()})" if sala.nivel() is not None else ""
            lines.append(f"E: {sala.enemigo()}{lvl}")
        if sala.item():
            lines.append(f"I: {sala.item()}")
        if sala.npc():
            lines.append(f"N: {sala.npc()}")

        ax.text(sala.x, sala.y, "\n".join(lines), color=TEXT_COLOR,
                 fontsize=6, ha="center", va="center", zorder=3, weight="bold")

        # Flechas pequeñas indicando salidas declaradas
        offsets = {
            "norte": (0, -0.38), "sur": (0, 0.38),
            "este": (0.38, 0), "oeste": (-0.38, 0),
        }
        for d in sala.salidas():
            if d in offsets:
                dx, dy = offsets[d]
                ax.annotate("", xy=(sala.x + dx, sala.y + dy),
                            xytext=(sala.x, sala.y),
                            arrowprops=dict(arrowstyle="->", color=EDGE_COLOR,
                                             lw=1.0), zorder=3)

    ax.set_title(f"{mapa.nombre}  ({mapa.ancho}x{mapa.alto})",
                  color=TEXT_COLOR, fontsize=12, weight="bold", pad=10)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.tight_layout()
    fig.savefig(output_path, facecolor=BG_COLOR)
    plt.close(fig)
    return output_path


if __name__ == "__main__":  # pragma: no cover - demo manual
    import sys
    sys.path.insert(0, ".")
    from parser import parse

    demo = '''MAP "Mazmorra_del_Dragon" SIZE 4x1 {
        ROOM(0,0) TYPE=entrada EXITS=[este]
        ROOM(1,0) TYPE=combate ENEMY=goblin LEVEL=2 EXITS=[este,oeste]
        ROOM(2,0) TYPE=tesoro ITEM=pocion_vida EXITS=[este,oeste]
        ROOM(3,0) TYPE=jefe ENEMY=dragon LEVEL=10 EXITS=[oeste]
        CONNECT (0,0)->(1,0) via "corredor_este"
        CONNECT (1,0)->(2,0) via "puerta_madera"
        CONNECT (2,0)->(3,0) via "puerta_secreta"
    }'''
    ast, errors = parse(demo, collect_errors=True)
    if ast:
        render_mapa(ast.mapas[0], "/tmp/demo_map.png")
        print("Imagen generada en /tmp/demo_map.png")
