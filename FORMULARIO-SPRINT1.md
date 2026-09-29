# FORMULARIO SPRINT 1 — texto listo para pegar

Rellena mientras Kiro genera las specs. Cada bloque está dentro de su límite.

---

## Campo 1 · Tu enfoque y qué lo distingue [Innovación] — máx. 4.000

```
La mayoría de herramientas de descripción de imágenes generan un texto libre
distinto cada vez. Para una persona ciega que estudia ajedrez eso es inservible:
necesita una notación estable que pueda releer, comparar y memorizar.

Mi enfoque parte de una observación: la ONCE no necesita que le inventemos un
formato, porque ya tiene el suyo. El Documento Técnico B8 de la Comisión Braille
Española define cómo se transcribe un tablero, y el libro adaptado define cómo
se describe en audio. Mi herramienta no propone una descripción propia:
reproduce esas dos notaciones oficiales carácter a carácter.

Eso cambia tres cosas:

1. La salida es verificable. No hay que opinar si una descripción es buena: se
compara contra la transcripción oficial y se cuentan los caracteres que
coinciden. Mi métrica es cuántos de los diez diagramas de ejemplo reproduzco
exactamente.

2. La salida es utilizable el primer día. El texto braille generado se puede
llevar directamente a Ebrai, el software que la ONCE ya usa para imprimir, sin
ninguna adaptación intermedia.

3. La salida respeta detalles que un enfoque genérico pierde. Dos ejemplos: las
filas se escriben con los números braille de posición baja (⠂⠆⠒⠲⠢⠖⠶⠦) y no con
dígitos, porque en braille un dígito normal se confundiría con una letra de
pieza. Y el orden de las piezas no es el mismo en los dos formatos: en braille
va Rey, Dama, Torres, Caballos, Alfiles, peones, mientras que en el audio del
libro va Rey, Dama, Torres, Alfiles, Caballos, Peones. Lo he comprobado en los
seis tableros y los cuatro diagramas de referencia. Unificar los dos órdenes
sería más cómodo de programar y rompería la costumbre de lectura del usuario.

Además transcribo las casillas resaltadas en amarillo y rojo y las flechas entre
casillas, que el documento de la ONCE indica aparte y que llevan la información
didáctica del libro. Una herramienta que solo leyera las piezas dejaría la
transcripción incompleta.
```

---

## Campo 2 · Arquitectura [Viabilidad] — máx. 4.000

```
QUÉ RECONOZCO

La imagen se normaliza y se divide en una rejilla de 8x8. Cada una de las 64
casillas se clasifica de forma independiente en 13 clases: vacía, más seis tipos
de pieza por dos colores. El color de fondo de cada casilla se analiza aparte,
por su color medio, para detectar los resaltados en amarillo y rojo sin cargar
esa tarea al modelo.

CÓMO ENTRENO

No descargo ningún dataset. Recorto los sprites de pieza de los propios
diagramas de ejemplo de la ONCE, que vienen con su transcripción y por tanto me
dicen qué pieza hay en cada casilla, y con ellos compongo miles de tableros
sintéticos con etiquetas perfectas. El dominio de entrenamiento coincide
exactamente con el de la prueba y las etiquetas no tienen error humano.

Un punto crítico: los ejemplos de la ONCE vienen en dos estilos visuales muy
distintos. Seis son tableros modernos en color con coordenadas, y cuatro son
escaneos de libro en blanco y negro, con las casillas oscuras rayadas, piezas de
imprenta antigua y baja resolución. Genero dataset de los dos estilos. Un modelo
entrenado con uno solo fallaría con la mitad del material real.

El clasificador es una red convolucional pequeña sobre recortes de 32x32,
entrenada en CPU en minutos.

QUÉ SALIDA DOY

De las 64 clasificaciones monto la posición interna con python-chess, y de ahí
genero las dos salidas oficiales:

- Transcripción braille según el Documento Técnico B8, con los números de fila
en posición baja, el orden Rey-Dama-Torres-Caballos-Alfiles-peones, y los
resaltados y flechas indicados aparte.
- Descripción en audio con el formato del libro adaptado, con su propio orden
de piezas, singulares y plurales correctos y la conjunción antes de la última
casilla. Se lee con Amazon Polly en voz neuronal española.

CÓMO COMPRUEBO QUE ACIERTA

Tengo diez diagramas con su transcripción oficial. El script de validación
compara mi salida contra ellas carácter a carácter y da dos números: porcentaje
de casillas correctas y número de diagramas reproducidos exactamente. No es una
métrica que me invente yo: es la transcripción que la ONCE ya publica.

Aparto dos diagramas que no uso durante el desarrollo, para poder probar al
final con material que el sistema no ha visto nunca.
```

---

## Campo 3a · Formato de salida accesible — marca una opción

```
Braille
```
(y audio como salida secundaria, si el formulario deja marcar varias)

---

## Campo 3b · Por qué ese formato encaja — máx. 4.000

```
Porque es el formato que la ONCE ya usa, no uno que yo proponga.

El braille es el único que da acceso no lineal. Con audio, para comprobar qué
hay en una casilla concreta hay que volver a escuchar toda la descripción. Con
una transcripción braille sobre papel, la persona recorre con el dedo, vuelve
atrás y compara dos posiciones a la vez. Para estudiar ajedrez, que consiste en
releer la misma posición muchas veces, eso es la diferencia entre poder
estudiar y no poder.

Además la salida braille que genero se puede llevar directamente a Ebrai, el
software del Centro de Tiflotecnología e Innovación de la ONCE, e imprimirse.
La herramienta encaja en un flujo de trabajo que ya existe en la organización en
lugar de pedirles que adopten uno nuevo.

Mantengo el audio como salida secundaria porque cubre el caso de uso rápido, el
de alguien que quiere hacerse una idea de la posición sin tener el papel
delante, y porque el libro adaptado ya define ese formato. Los dos son
oficiales, los dos son necesarios, y por eso genero los dos.

La aplicación muestra siempre el texto además del audio, de forma seleccionable,
para que funcione también con el lector de pantalla que la persona ya use.
```

---

## Campo 4 · Cómo estás usando Kiro — marca una opción

```
Specs (requirements, design, tasks) + steering
```

---

## Steering · extracto — máx. 3.000 · reglas numeradas

```
R1. La salida principal es la transcripción braille del Documento Técnico B8,
con esta forma exacta: Blancas: Re⠂ Dd⠂ Ta⠂ Th⠂ Cc⠒ Cf⠒ Ac⠲ Ag⠒ a⠆ b⠆ c⠆ d⠒
e⠲ f⠆ g⠆ h⠆
R2. Las filas se escriben con los números braille en posición baja
(1 ⠂ 2 ⠆ 3 ⠒ 4 ⠲ 5 ⠢ 6 ⠖ 7 ⠶ 8 ⠦), nunca con dígitos ASCII.
R3. Las piezas usan la inicial española: R rey, D dama, T torre, C caballo,
A alfil, P peón.
R4. En braille el orden dentro de cada color es R, D, T, C, A y peones. Los
peones van sin la P, solo columna y fila.
R5. En audio el orden es Rey, Dama, Torres, Alfiles, Caballos, Peones, con
singular o plural según el número de piezas y la conjunción antes de la última.
R6. Las casillas resaltadas se detectan por color y se escriben aparte al final,
indicando el color.
R7. Nunca se muestra ni se lee un FEN como salida. El FEN es representación
interna.
R8. El modelo clasifica cada una de las 64 casillas en 13 clases. Es una red
entrenada por nosotros, no un modelo de lenguaje mirando la imagen.
R9. El dataset se genera componiendo tableros sintéticos con sprites recortados
de los propios diagramas de la ONCE, y se etiqueta solo.
R10. El dataset cubre los dos estilos visuales de los ejemplos: tablero moderno
en color y escaneo de libro en blanco y negro.
R11. La detección de casilla resaltada es por color medio, no por el modelo.
R12. Después de cada tarea la aplicación tiene que arrancar y la demo tiene que
poder darse.
R13. Todo en Python: Streamlit, Pillow, OpenCV, python-chess y PyTorch en CPU.
R14. Las reglas de ajedrez no se reimplementan: las resuelve python-chess.
R15. Toda llamada a AWS va detrás de DEMO_MODE; sin red la app sigue
funcionando.
R16. El modelo se guarda en disco y la app carga los pesos; nunca entrena al
arrancar.
R17. Un archivo, una responsabilidad; máximo 200 líneas.
R18. No añadir autenticación, base de datos, Docker, CI/CD ni tests unitarios.
```

---

## Steering · justificación — máx. 1.000 · misma numeración

```
R1 Es el formato que la ONCE ya imprime con Ebrai.
R2 Un dígito normal se confundiría con letra de pieza al tacto.
R3 La signografía del B8 está en español y ya se conoce.
R4 y R5 Cada formato tiene su propio orden en la fuente; unificarlos rompería la
costumbre de lectura.
R6 Los resaltados llevan la información didáctica del libro.
R7 Un FEN no aporta nada a quien escucha.
R8 El reto pide entrenar un modelo propio.
R9 Etiquetas perfectas y mismo dominio que la prueba.
R10 Entrenar con un solo estilo falla con la mitad del material.
R11 El color es un dato exacto y barato.
R12 Hay tres controles evaluados; una demo rota cuesta más que una función.
R13 y R14 Menos depuración, que es el recurso escaso.
R15 La demo no puede depender del wifi.
R16 Entrenar al arrancar haría la demo lenta.
R17 Permite revertir un cambio sin arrastrar el resto.
R18 Lo que no se demuestra no suma y consume tiempo.
```

---

## Borrador de specs — 3 bloques de 4.000 cada uno

Pega aquí los tres ficheros que genere Kiro: `requirements.md`, `design.md` y
`tasks.md`. **Extracto literal**, sin reescribir. Si alguno pasa de 4.000
caracteres, corta las partes menos relevantes pero no reformules.
