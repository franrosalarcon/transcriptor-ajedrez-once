# PROMPT SPRINT 1 — pégalo en Kiro, modo Spec

```
# Contexto

Hackathon de un día, reto de la ONCE, trabajo solo. Tres controles evaluados:
13:30, 14:45 y 17:15. En el primero se puntúa el PLAN, no el código.

Construimos una herramienta que recibe la imagen de un diagrama de ajedrez y la
transcribe a los dos formatos oficiales que la ONCE ya usa. No inventamos
formato de salida: reproducimos el suyo, carácter a carácter.

Lee `.kiro/steering/hackathon.md` y `REFERENCIA.md`. En REFERENCIA.md están los
diez diagramas de ejemplo con su transcripción exacta: son la verdad de
referencia y el conjunto de validación. En `ejemplos/` están las imágenes.

# Las dos salidas oficiales

BRAILLE (Documento Técnico B8 de la Comisión Braille Española):
Blancas: Re⠂ Dd⠂ Ta⠂ Th⠂ Cc⠒ Cf⠒ Ac⠲ Ag⠒ a⠆ b⠆ c⠆ d⠒ e⠲ f⠆ g⠆ h⠆
Negras: Re⠦ Dd⠦ Ta⠦ Th⠦ Cc⠖ Cf⠖ Ac⠢ Ac⠦ a⠶ b⠶ c⠶ d⠖ e⠢ f⠶ g⠢ h⠖
)Resaltadas en amarillo las casillas g⠒ y h⠲(

AUDIO (el libro adaptado de la ONCE):
Blancas: Rey en E2, Dama en A4, Torres en C1 y H1, Alfil en B5, Caballos en C3
y F3, Peones en A2, B2, D2, F2, G2 y H2.

Fíjate en que el orden de piezas NO es el mismo en los dos formatos: en braille
va R, D, T, C, A, peones; en audio va Rey, Dama, Torres, Alfiles, Caballos,
Peones. Respeta cada uno.

# Decisiones ya tomadas — no las replantees

Pipeline: imagen → recortar en 64 casillas → clasificar cada casilla con una
red entrenada por nosotros (13 clases: vacía + 6 piezas × 2 colores) → posición
interna con python-chess → transcripción braille y transcripción de audio.

Dataset: lo generamos nosotros. Recorta los sprites de las piezas de los
propios diagramas de `ejemplos/` (ya sabemos qué pieza hay en cada casilla
porque tenemos la transcripción) y compón con Pillow miles de tableros
sintéticos con etiquetas perfectas.

CRÍTICO: los ejemplos vienen en DOS estilos visuales muy distintos. Los seis
primeros son tableros modernos en color con coordenadas; los cuatro últimos son
escaneos de libro en blanco y negro con las casillas oscuras rayadas y las
piezas de imprenta antigua. Genera dataset de los DOS estilos. Un modelo
entrenado con uno solo falla con la mitad del material.

Casillas resaltadas: se detectan por el color medio de la casilla, no con el
modelo.

Modelo: CNN pequeña en PyTorch CPU sobre recortes de 32x32. Si PyTorch no
instala en 5 minutos, usa MLPClassifier de scikit-learn y sigue sin
preguntarme.

Interfaz: Streamlit. Voz: Amazon Polly con voz neuronal española, detrás de
DEMO_MODE.

# Qué tiene que estar listo a las 13:30

Este sprint puntúa el plan, no el código. En este orden:

1. Las specs completas: requirements, design y tasks. Son entregables: los
   pego literalmente en un formulario, con un límite de 4.000 caracteres cada
   bloque. Escríbelos para que se entiendan por sí solos.
2. En el design tiene que quedar explícito: qué reconoces del diagrama, qué
   salida das en cada formato, y cómo compruebas que acierta. La comprobación
   es comparar carácter a carácter contra las diez transcripciones de
   REFERENCIA.md.
3. Si sobra tiempo: el generador de dataset y el entrenamiento funcionando.

# Reglas de decisión

- Ante dos opciones, elige la más aburrida y rápida de poner en pie.
- Si algo va a costar más de 30 minutos, dímelo y ofrece una versión recortada.
- Si una librería no instala a la primera, usa la alternativa y avísame.
- Si vas por el tercer intento del mismo error, para y pregúntame.
- Al terminar cada tarea, dime en una línea qué funciona y cómo lo pruebo.

# Empieza así

Modo Spec. Genera requirements, design y tasks solo para este alcance. Divide
las tareas en trozos de menos de 20 minutos y marca cuáles son requeridas y
cuáles opcionales. Los reviso antes de que escribas código.
```

---

# PROMPT SPRINT 2 — después del control de las 13:30

```
Sprint 1 cerrado. Ahora el objetivo es que el flujo completo funcione sobre los
diagramas reales de ejemplos/ y que la salida se entienda al escucharla.

Tengo 75 minutos, hasta las 14:45. En este orden:

1. Ejecuta las tasks hasta que el flujo entero funcione: imagen → 64 casillas →
   modelo → transcripción braille + transcripción de audio.

2. Script de validación que compare la salida contra las diez transcripciones
   de REFERENCIA.md, carácter a carácter, y diga cuántas casillas y cuántos
   diagramas acierta. Necesito ese número para el formulario.

3. Amazon Polly leyendo la transcripción de audio. Detrás de DEMO_MODE: sin red
   o sin credenciales la app muestra el texto y sigue.

4. La app: subir imagen, ver las dos transcripciones, escuchar el audio. El
   texto siempre visible y copiable.

Si repito una acción varias veces, conviértela en un hook o un skill de Kiro y
dímelo: cuenta para la nota.

A las 14:45 tengo que poder coger un diagrama, verlo transcrito en los dos
formatos y escucharlo. Ese es el único objetivo.
```

---

# PROMPT SPRINT 3 — después del control de las 14:45

```
Último sprint, vale el 50%. Termina a las 17:15. Desde las 16:15 no se toca
ninguna funcionalidad: solo pulir, preparar la demo y rellenar el formulario.

# Prioridad 1 — que funcione con diagramas NUEVOS (40 min)

El formulario exige probar con diagramas que no haya usado desarrollando.
Apártame ahora dos de los ejemplos para no tocarlos, y prepara la app para
aceptar cualquier imagen: deslizadores de recorte manual y botón de girar el
tablero por si viene del lado de las negras. Nunca una traza de error en
pantalla.

# Prioridad 2 — la experiencia completa como la viviría una persona ciega (30 min)

Etiquetas en todos los controles, orden de tabulación lógico, nada que dependa
solo del color, modo de texto plano, y la transcripción siempre copiable para
poder llevarla a Ebrai.

# Prioridad 3 — cierre (desde las 16:15)

- Specs finales, que van al formulario como extracto literal.
- README de una página: qué es, por qué, objetivo, innovación.
- Precisión medida contra REFERENCIA.md, con el número exacto.
- Si has creado agentes personalizados, skills o hooks, documenta cuáles y por
  qué: suman bonus.

No añadas nada más después de las 16:15.
```
