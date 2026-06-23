# MapLang — Analizador Léxico-Sintáctico para Mapas de Videojuegos

Trabajo Integrador — Teoría de la Computación — 4.° año, Licenciatura en
Sistemas de Información — FaCENA, UNNE.

**Grupo 50 / SIC-UNNE**
Riveros, Lautaro · Riveros, Maximo · Scetti, Santiago · Turtola, Sabrina

## Descripción

MapLang es un lenguaje de dominio específico (DSL) diseñado para describir,
en formato de texto plano, mapas de videojuegos de tipo *dungeon-crawler*:
habitaciones con atributos (tipo, salidas, enemigo, nivel, ítem, NPC) y
conexiones entre ellas. Este repositorio contiene la implementación completa
de su analizador léxico, su analizador sintáctico (parser descendente
recursivo), un módulo de validaciones semánticas, la construcción del Árbol
Sintáctico Abstracto (AST) y un renderizador que produce una imagen del mapa.

## Requisitos

- Python 3.10 o superior
- Dependencias listadas en `requirements.txt` (sólo `matplotlib`, usada por
  el renderizador)

## Instalación

```bash
cd maplang
pip install -r requirements.txt
```

## Estructura del repositorio

```
maplang/
├── README.md                  Este archivo
├── GRAMMAR.md                 Gramática formal completa en BNF
├── requirements.txt           Dependencias de Python
├── src/
│   ├── lexer.py                Analizador léxico (tokenizador)
│   ├── parser.py                Analizador sintáctico (descendente recursivo)
│   ├── ast_nodes.py             Definición de los nodos del AST
│   ├── semantic.py              Validaciones semánticas post-parsing
│   ├── renderer.py              Renderizador del mapa (matplotlib)
│   └── main.py                  Punto de entrada / CLI
├── tests/
│   ├── test_lexer.py             Pruebas unitarias del lexer (20 casos)
│   ├── test_parser.py            Pruebas unitarias del parser (18 casos)
│   ├── test_semantic.py          Pruebas unitarias de semántica (10 casos)
│   ├── test_integration.py       Pruebas end-to-end (4 casos)
│   ├── casos/                    Archivos .maplang de prueba (8 válidos + 6 inválidos)
│   └── casos_resultados_esperados.txt   Entradas y salidas esperadas en texto plano
└── docs/
    └── (informe técnico, presentación, diagramas)
```

## Prototipo visual (interfaz web local)

Además del CLI, el proyecto incluye una pequeña interfaz web para escribir
código MapLang y ver el resultado (árbol AST, tokens, errores y el mapa
renderizado) sin usar la terminal para cada prueba. No requiere instalar
nada adicional: usa sólo la biblioteca estándar de Python para el servidor.

```bash
cd src
python3 server.py
```

Esto abre automáticamente `http://localhost:8765` en el navegador. Si no se
abre solo, hay que pegar esa dirección manualmente en el navegador.

En la página:
- Escribís o pegás código `.maplang` en el panel izquierdo (hay ejemplos
  precargados en el menú desplegable).
- Apretás **▶ Generar mapa** (o Ctrl/Cmd + Enter).
- A la derecha aparece el mapa renderizado, el árbol AST, la lista de
  tokens, o los errores encontrados, según corresponda.

Para detener el servidor, volver a la terminal y presionar `Ctrl+C`.

## Uso del CLI (`main.py`)

```bash
cd src

# Validación simple (sólo reporta éxito/error por código de salida)
python3 main.py archivo.maplang

# Exportar el AST en formato JSON
python3 main.py archivo.maplang --ast-json salida.json

# Imprimir el AST como árbol textual en la terminal
python3 main.py archivo.maplang --ast-tree

# Generar la imagen del primer mapa del archivo
python3 main.py archivo.maplang --render mapa.png

# Generar una imagen por cada MAP del archivo, en un directorio
python3 main.py archivo.maplang --render-all salida_imagenes/

# Combinar varias opciones
python3 main.py archivo.maplang --ast-json out.json --render mapa.png --quiet
```

### Códigos de salida

| Código | Significado            |
|--------|-------------------------|
| 0      | Éxito, sin errores       |
| 1      | Error léxico              |
| 2      | Error(es) sintáctico(s)    |
| 3      | Error(es) semántico(s)      |

### Ejemplo rápido

```bash
cd src
cat > /tmp/demo.maplang << 'EOF'
MAP "Mazmorra_del_Dragon" SIZE 4x1 {
    ROOM(0,0) TYPE=entrada EXITS=[este]
    ROOM(1,0) TYPE=combate ENEMY=goblin LEVEL=2 EXITS=[este, oeste]
    ROOM(2,0) TYPE=tesoro ITEM=pocion_vida EXITS=[este, oeste]
    ROOM(3,0) TYPE=jefe ENEMY=dragon LEVEL=10 EXITS=[oeste]
    CONNECT (0,0)->(1,0) via "corredor_este"
    CONNECT (1,0)->(2,0) via "puerta_madera"
    CONNECT (2,0)->(3,0) via "puerta_secreta"
}
EOF
python3 main.py /tmp/demo.maplang --render /tmp/mapa.png
```

## Ejecutar la suite de pruebas

```bash
cd tests
python3 -m unittest discover -v
```

Esto ejecuta las 52 pruebas automatizadas (lexer, parser, semántica e
integración end-to-end, incluyendo el renderizado de los 8 casos válidos).

Para ejecutar manualmente los casos de prueba de `tests/casos/` y comparar
contra `tests/casos_resultados_esperados.txt`:

```bash
cd src
for f in ../tests/casos/*.maplang; do
    echo "=== $f ==="
    python3 main.py "$f" --quiet
    echo "exit=$?"
done
```

## Resumen de la gramática

Ver `GRAMMAR.md` para la especificación BNF completa (20 producciones).
La gramática es una **Gramática Libre de Contexto (GLC)** que cumple la
condición **LL(1)**, lo que habilita la implementación de un parser
descendente recursivo sin necesidad de backtracking.
