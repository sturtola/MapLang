# Gramática Formal de MapLang (Versión Final)

## Notación BNF

```
<programa>      ::= <mapa>+

<mapa>          ::= "MAP" <cadena> "SIZE" <dimension> "{" <cuerpo> "}"

<cuerpo>        ::= <declaracion>+

<declaracion>   ::= <sala> | <conexion>

<sala>          ::= "ROOM" "(" <entero_pos> "," <entero_pos> ")" <atributo>+

<atributo>      ::= <tipo_sala> | <salidas> | <enemigo> | <nivel> | <item> | <npc>

<tipo_sala>     ::= "TYPE" "=" <tipo_valor>

<tipo_valor>    ::= "entrada" | "pasillo" | "combate" | "tesoro" | "jefe" | "tienda" | "trampa"

<salidas>       ::= "EXITS" "=" "[" <lista_dir> "]"

<lista_dir>     ::= <direccion> ("," <direccion>)*

<direccion>     ::= "norte" | "sur" | "este" | "oeste" | "arriba" | "abajo"

<enemigo>       ::= "ENEMY" "=" <identificador>

<nivel>         ::= "LEVEL" "=" <entero_pos>

<item>          ::= "ITEM" "=" <identificador>

<npc>           ::= "NPC" "=" <identificador>

<conexion>      ::= "CONNECT" "(" <entero_pos> "," <entero_pos> ")" "->"
                     "(" <entero_pos> "," <entero_pos> ")" [ "via" <cadena> ]

<dimension>     ::= <entero_pos> "x" <entero_pos>

<cadena>        ::= '"' <caracter>* '"'

<identificador> ::= [a-zA-Z_][a-zA-Z0-9_]*

<entero_pos>    ::= [0-9]+
```

20 producciones, sin recursión izquierda, con recursividad por la derecha en
`<programa>`, `<cuerpo>`, `<lista_dir>`.
