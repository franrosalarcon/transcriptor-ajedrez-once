# Lector de diagramas de ajedrez para personas ciegas

Reto ONCE · Hackathon Kiro 2026 · Autor: Francisco Ros Alarcón

Recibe la imagen de un diagrama de ajedrez (PNG/JPG) y la transcribe a los dos
formatos oficiales que usa la ONCE: la notación braille del Documento Técnico B8
de la Comisión Braille Española y la descripción en audio del libro adaptado.
Todo el procesamiento es local, sin red.

## Requisitos

Python 3.9 o superior. Desarrollado y probado con Python 3.13 en Windows.

Dependencias en `requirements.txt`: streamlit, python-chess, pillow, numpy,
scikit-learn, opencv-python-headless, gTTS y pyttsx3. La síntesis de voz se hace
en local con `pyttsx3`, así que no hace falta ninguna credencial ni conexión a
internet.

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS
pip install -r requirements.txt
```

## Ejecución

```bash
python -m streamlit run app.py
```

Abre http://localhost:8501

Variante sin abrir el navegador:

```bash
python -m streamlit run app.py --server.headless true --server.port 8501 --browser.gatherUsageStats false
```

Para parar: `Ctrl+C`.

La app no entrena al arrancar: carga los pesos ya guardados en `knn_moderno.pkl`
y `knn_escaneado.pkl`.

## Cómo se usa

En la barra lateral: elegir idioma (Español/English), elegir fuente (subir
imagen o galería de ejemplos), ajustar el recorte con el deslizador si hace
falta y resolver la orientación del tablero.

Para la orientación hay dos controles. La casilla «Orientación automática
(experimental)» intenta deducir por qué lado se mira el tablero, pero no siempre
acierta. La casilla «Girar tablero 180°» fuerza el giro a mano, y es la opción
recomendada cuando se quiere un resultado reproducible o cuando el diagrama
viene del lado de las negras.

En el área principal: estilo detectado, número de piezas y cuatro pestañas:

- transcripción braille B8
- descripción en audio con reproducción local
- tabla de piezas y movimientos con narración
- vista táctil en SVG descargable

Abajo hay un modo de consulta de posición en texto, en español o inglés (por
ejemplo «¿qué hay en e4?»).

## Estructura

Estos archivos son la solución entregada:

| Archivo | Responsabilidad |
| --- | --- |
| `app.py` | interfaz Streamlit completa, bilingüe |
| `deteccion_tablero.py` | localiza el tablero y lo parte en 64 casillas |
| `formatters.py` | `BrailleFormatter` (B8) y `AudioFormatter` (libro adaptado) |
| `entrenar_dual.py` | entrena los dos clasificadores y hace validación leave-one-image-out |
| `validar_modelos.py` | mide los modelos guardados contra los diez diagramas de referencia |
| `position_query_*.py` | modo de consulta de posición (modelos, parser, motor, formateador, controlador, audio) |
| `knn_moderno.pkl`, `knn_escaneado.pkl` | clasificadores entrenados |
| `REFERENCIA.md` | verdad de referencia oficial de la ONCE, diez diagramas |
| `ejemplos/` | las diez imágenes de diagrama |
| `casos_finales.txt` | transcripciones de los casos finales de prueba |
| `test_position_query_*.py` | 49 pruebas unitarias del modo de consulta |

El repositorio conserva además scripts de experimentación del hackathon
(extracción de sprites, pruebas de CNN, generadores de dataset, volcados de
salida). No forman parte de la solución entregada y se mantienen como registro
del proceso.

## Reproducir la validación

```bash
python validar_modelos.py    # no entrena; evalúa los .pkl guardados y escribe resultados_validacion.txt
python entrenar_dual.py      # reentrena los dos modelos y muestra la validación leave-one-image-out
python -m unittest discover -s . -p "test_position_query*.py" -v    # 49 pruebas, pasan todas
```

Aviso: `entrenar_dual.py` sobrescribe `knn_moderno.pkl` y `knn_escaneado.pkl`.
Para comprobar la precisión sin tocar los modelos, usar `validar_modelos.py`.

## Resultados

Medido contra `REFERENCIA.md`, comparando casilla a casilla.

- Validación leave-one-image-out, 1-NN, 8 diagramas de entrenamiento: 442/512
  casillas (86,3%), 2/8 diagramas exactos.
- Diagramas reservados, nunca usados para entrenar: 118/128 casillas (92,2%),
  1 de 2 exactos. En detalle, `tablero3.png` 64/64 y `diagrama02.png` 54/64.
- Con los modelos finales y la orientación correcta: 9 de los 10 diagramas de
  referencia salen exactos (64/64). Esta cifra no mide generalización: con un
  clasificador 1-NN, los ocho diagramas usados para entrenar aciertan por
  construcción, porque el vecino más cercano de cada casilla es ella misma. Las
  cifras informativas son las dos anteriores.
- Sin corregir la orientación, esos 8 diagramas bajan a 476/512 casillas
  (93,0%). Las 36 casillas perdidas son todas de `tablero2.png`: el
  reconocimiento de pieza acierta, lo que falla es decidir el lado del tablero.

## Limitaciones conocidas

- La detección automática de orientación no es fiable: en `tablero2.png` empata
  y hay que marcar el giro manual, que lleva ese diagrama de 28/64 a 64/64. Por
  eso la casilla «Orientación automática» está marcada como experimental.
- `diagrama02.png`, el escaneado reservado, se queda en 54/64: no reproduce la
  transcripción oficial.
- Resaltados en amarillo y rojo: `deteccion_tablero.color_de_casilla` los
  reconoce y `BrailleFormatter` sabe escribirlos, pero la app todavía no los
  pasa a la transcripción. Las flechas del documento B8 no se transcriben.
- No hay aviso de incertidumbre: el sistema no indica nunca que dude de una
  casilla. Con `n_neighbors=1`, `predict_proba` no sirve para esto; habría que
  usar la distancia al vecino más cercano que devuelve `kneighbors()`.
- El entrenamiento parte de solo diez diagramas, así que el modelo no está
  probado con estilos visuales distintos de esos dos. Los generadores de dataset
  sintético están en el repositorio, pero los modelos entregados no los usan.
- No hay soporte de PDF: la entrada es una imagen por vez.
- La salida no indica a quién le toca jugar: el diagrama no informa de turno,
  enroques ni captura al paso.

## Privacidad

La imagen se procesa en memoria, en el equipo local. No hay llamadas de red, ni
telemetría, ni almacenamiento de los diagramas subidos.
