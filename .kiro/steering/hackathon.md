---
title: Reto ONCE — reglas del proyecto
inclusion: always
---

# Lector de diagramas de ajedrez para personas ciegas · Reto ONCE

Transcribe la imagen de un diagrama de ajedrez a los **dos formatos oficiales
que usa la ONCE**: la notación braille del Documento Técnico B8 de la Comisión
Braille Española, y la descripción en audio del libro adaptado.

No inventamos un formato de salida. Reproducimos el suyo, carácter a carácter.

---

## REGLAS NUMERADAS

### Salida

**R1.** La salida principal es la transcripción braille del Documento Técnico
B8, con esta forma exacta y en este orden:
`Blancas: Re⠂ Dd⠂ Ta⠂ Th⠂ Cc⠒ Cf⠒ Ac⠲ Ag⠒ a⠆ b⠆ c⠆ d⠒ e⠲ f⠆ g⠆ h⠆`

**R2.** Las filas se escriben con los números braille en posición baja:
1 ⠂ · 2 ⠆ · 3 ⠒ · 4 ⠲ · 5 ⠢ · 6 ⠖ · 7 ⠶ · 8 ⠦
Nunca con dígitos ASCII.

**R3.** Las piezas usan la inicial española: R rey, D dama, T torre, C caballo,
A alfil, P peón.

**R4.** En braille el orden dentro de cada color es **R, D, T, C, A y peones**.
Los peones van sin la P, solo columna y fila: `a⠆ b⠆ c⠆`.

**R5.** En audio el orden dentro de cada color es **Rey, Dama, Torres, Alfiles,
Caballos, Peones**, con singular o plural según el número de piezas y la
conjunción "y" antes de la última casilla:
`Blancas: Rey en E2, Dama en A4, Torres en C1 y H1, Alfil en B5, Caballos en C3 y F3, Peones en A2, B2, D2, F2, G2 y H2.`

**R6.** Las casillas resaltadas se detectan por color y se escriben aparte, al
final, indicando el color: `)Resaltadas en amarillo las casillas g⠒ y h⠲(`

**R7.** Nunca se lee un FEN en voz alta ni se muestra como salida principal. El
FEN es representación interna.

### Reconocimiento

**R8.** El modelo clasifica cada una de las 64 casillas en 13 clases: vacía más
seis piezas por dos colores. Es un modelo entrenado por nosotros, no un modelo
de lenguaje mirando la imagen.

**R9.** El dataset se genera componiendo tableros sintéticos con los sprites de
pieza recortados de los propios diagramas de la ONCE, y se etiqueta solo. No se
descargan datasets externos.

**R10.** El dataset cubre los **dos estilos visuales** de los ejemplos: tablero
moderno en color con coordenadas, y diagrama de libro escaneado en blanco y
negro con casillas rayadas. Entrenar solo con uno hace fallar el otro.

**R11.** La detección de casilla resaltada es por color medio de la casilla, no
por el modelo.

### Ingeniería

**R12.** Después de cada tarea la aplicación tiene que arrancar y la demo tiene
que poder darse. Si un cambio puede romper lo que funciona, avisa antes.

**R13.** Todo en Python: Streamlit para la interfaz, Pillow y OpenCV para
imagen, python-chess para la lógica de ajedrez, PyTorch en CPU para el modelo.
Si PyTorch no instala en cinco minutos, MLPClassifier de scikit-learn y seguir.

**R14.** Las reglas de ajedrez no se reimplementan. python-chess ya resuelve
jaque, mate, enroques, ataques y defensas.

**R15.** Toda llamada a AWS va detrás de `DEMO_MODE`. Sin red o sin
credenciales, la app muestra el texto y sigue funcionando.

**R16.** El modelo entrenado se guarda en disco y la app carga los pesos. La
app nunca entrena al arrancar.

**R17.** Un archivo, una responsabilidad. Si uno pasa de 200 líneas, avisa.

**R18.** No añadir autenticación, base de datos, Docker, CI/CD ni tests
unitarios. No refactorizar de paso. No instalar dependencias sin avisar.

---

## JUSTIFICACIÓN (una línea por regla, misma numeración)

**R1.** Es el formato que la ONCE ya usa e imprime con Ebrai; reproducirlo hace
la herramienta utilizable el primer día, sin adaptación.
**R2.** Los números en posición baja distinguen fila de pieza en braille; usar
dígitos normales rompe la lectura táctil.
**R3.** La signografía del B8 está en español y los usuarios ya la conocen.
**R4.** El orden R-D-T-C-A es el del documento técnico; alterarlo obliga al
lector a recolocar mentalmente la posición.
**R5.** El audio del libro adaptado usa otro orden que el braille; respetar cada
uno demuestra que hemos leído la fuente y no hemos unificado por comodidad.
**R6.** Los resaltados llevan información de la explicación del libro; perderlos
deja la transcripción incompleta.
**R7.** Un FEN es ruido para quien escucha: no aporta nada y ocupa la atención.
**R8.** El reto pide entrenar un modelo; 64 clasificaciones independientes es el
planteamiento más simple que resuelve el problema entero.
**R9.** Usar los sprites reales de los ejemplos hace que el dominio de
entrenamiento coincida con el de la prueba, y da etiquetas perfectas gratis.
**R10.** Los ejemplos de la ONCE incluyen diagramas modernos y escaneos de
libro; un modelo entrenado en un solo estilo falla con la mitad del material.
**R11.** El color es un dato exacto y barato; pedírselo al modelo añadiría
clases y error sin necesidad.
**R12.** Hay tres puntos de control evaluados: una demo rota en cualquiera de
ellos cuesta más que cualquier funcionalidad añadida.
**R13.** Un solo lenguaje y librerías conocidas reducen el tiempo de depuración,
que es el recurso escaso en un día.
**R14.** python-chess está probado; reimplementar reglas introduce errores en la
parte que el usuario no puede verificar.
**R15.** La demo no puede depender del wifi de la sede.
**R16.** Entrenar al arrancar haría la demo lenta e impredecible.
**R17.** Archivos pequeños permiten revertir un cambio sin arrastrar el resto.
**R18.** Todo lo que no se demuestra no suma, y sí consume tiempo.
