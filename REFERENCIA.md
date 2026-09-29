# TABLEROS DE REFERENCIA — verdad de referencia oficial de la ONCE

Diez diagramas extraídos del documento de la ONCE, cada uno con su
transcripción exacta. **Esto es tu conjunto de validación**: si tu herramienta
reproduce estas diez salidas carácter a carácter, has resuelto el reto.

## Dos estilos visuales distintos — importante

- **tablero1 … tablero6**: tablero moderno en color (verde y crema), piezas
  estándar, coordenadas en los bordes, casillas resaltadas en amarillo o rojo.
- **diagrama01, 02, 05, 23**: diagrama de libro escaneado, blanco y negro,
  casillas oscuras rayadas, piezas de imprenta antigua, baja resolución.

**Un modelo entrenado solo con el primer estilo falla con el segundo.** El
dataset tiene que cubrir los dos.

---

## Notación braille (tableros 1 a 6)

Filas en números braille de posición baja:
`1 ⠂ · 2 ⠆ · 3 ⠒ · 4 ⠲ · 5 ⠢ · 6 ⠖ · 7 ⠶ · 8 ⠦`

Piezas: `R` rey · `D` dama · `T` torre · `C` caballo · `A` alfil · `P` peón
Orden dentro de cada color: **R, D, T, C, A, peones**. Los peones pueden ir sin
la `P`, solo columna y fila.

### tablero1.png
```
Blancas: Re⠂ Dd⠂ Ta⠂ Th⠂ Cc⠒ Cf⠒ Ac⠲ Ag⠒ a⠆ b⠆ c⠆ d⠒ e⠲ f⠆ g⠆ h⠆
Negras: Re⠦ Dd⠦ Ta⠦ Th⠦ Cc⠖ Cf⠖ Ac⠢ Ac⠦ a⠶ b⠶ c⠶ d⠖ e⠢ f⠶ g⠢ h⠖
)Resaltadas en amarillo las casillas g⠒ y h⠲(
```

### tablero2.png
```
Blancas: Re⠂ Dd⠂ Ta⠂ Th⠂ Cc⠒ Af⠂ Af⠲ a⠆ b⠆ c⠆ e⠲ f⠆ g⠆ h⠆
Negras: Re⠦ Dd⠦ Ta⠦ Th⠦ Cg⠲ Ac⠦ Af⠦ a⠶ b⠶ d⠖ e⠢ f⠶ g⠶ h⠶
)Resaltadas en amarillo las casillas d⠂ y d⠲
Desde la casilla d⠲ sale una flecha que une con la casilla d⠂ d⠲¬⠒⠕¬d⠂(
```

### tablero3.png
```
Blancas: Re⠂ Dd⠂ Ta⠂ Th⠂ Cb⠂ Cf⠒ Af⠂ Ag⠢ a⠆ b⠆ c⠲ d⠲ e⠆ f⠆ g⠆ h⠆
Negras: Re⠦ Dd⠦ Ta⠦ Th⠦ Cb⠦ Cf⠖ Ac⠦ Af⠦ a⠶ b⠶ c⠶ d⠶ e⠖ f⠢ g⠶ h⠖
)Resaltadas en amarillo las casillas h⠶¬⠒⠕¬h⠖(
```

### tablero4.png
```
Blancas: Rh⠂ a⠲ b⠒ c⠆ f⠒ g⠲ h⠒
Negras: Ra⠦ a⠶ b⠖ f⠲ g⠢ h⠲
```

### tablero5.png
```
Blancas: Rg⠂ Dd⠒ Tc⠂ Cd⠆ Ch⠢ Ac⠒ c⠲ d⠢ e⠲ g⠆ h⠒
Negras: Rg⠦ Db⠦ Ta⠆ Tb⠖ Ad⠖ Ad⠶ c⠢ e⠢ f⠖ f⠶ h⠖
)Resaltadas en amarillo las casillas: g⠒ y h⠢ y, en rojo, f⠖
c⠂¬⠒⠕¬f⠂
d⠒¬⠒⠕¬g⠒
h⠢¬⠒⠕¬f⠖(
```

### tablero6.png
```
Blancas: Rg⠂ Dd⠂ Ta⠂ Te⠂ Cd⠆ Cf⠒ Ac⠂ Ac⠆ b⠲ c⠒ d⠢ e⠲ f⠆ g⠆ h⠒
Negras: Rg⠦ Dc⠶ Tb⠦ Tf⠦ Cb⠶ Cf⠖ Ac⠦ Ae⠶ b⠢ c⠢ d⠖ e⠢ f⠶ g⠶ h⠶
)Resaltadas en amarillo las casillas b⠶ y d⠦ y, en rojo, la casilla c⠂.
Desde la casilla d⠆ ocupada por el caballo salen flechas hacia las casillas b⠂ b⠒ y f⠂(
```

---

## Notación de audio (los cuatro diagramas de libro)

Orden dentro de cada color: **Rey, Dama, Torres, Alfiles, Caballos, Peones**.
Ojo: **no es el mismo orden que en braille.** Singular o plural según el número
de piezas, y "y" antes de la última casilla.

### diagrama01.png — pág. 15 del libro
```
Blancas: Rey en E2, Dama en A4, Torres en C1 y H1, Alfil en B5, Caballos en C3 y F3, Peones en A2, B2, D2, F2, G2 y H2.
Negras: Rey en E8, Dama en D7, Torres en A8 y H8, Alfiles en F8 y G4, Caballo en C6, Peones en A7, B7, C5, E7, F7, G7 y H7.
```

### diagrama02.png — pág. 17
```
Blancas: Rey en D2, Alfil en H6, Caballo en E1, Peones en A3, B2, G2 y H3.
Negras: Rey en E6, Alfil en C4, Caballo en C6, Peones en B7, B6, D5, G6 y H7.
```

### diagrama05.png — pág. 24
```
Blancas: Rey en G1, Dama en D1, Torres en A1 y E1, Alfiles en B3 y C1; Caballos en B1 y F3, Peones en A2, B2, C3, D4, E4, F2, G2 y H2.
Negras: Rey en G8, Dama en D8, Torres en A8 y F8, Alfiles en E7 y C4, Caballos en A6 y F6, Peones en A6, B5, C7, D6, E5, F7, G7 y H7.
```

### diagrama23.png — pág. 44
```
Blancas: Rey en H3, Dama en F5, Torre en F1, Caballo en E2, Peones en A6, C4, D5, G3 y G4.
Negras: Rey en H7, Dama en G6, Torre en E7, Alfil en E3, Peones en A7, C5, E4, G5 y H6.
```

---

## Otras convenciones del documento

- **Flechas**: se indican las casillas unidas con `⠒⠕` o `⠪⠒` según la
  dirección. Ejemplo: `d⠲¬⠒⠕¬d⠂`
- **Resaltados**: se escriben aparte, al final, indicando el color.
- Las filas se numeran siempre desde el lado de las blancas, y las casillas se
  nombran igual para los dos jugadores.
- El software de la ONCE para imprimir en braille se llama **Ebrai**.
