# Implementation Plan: Modo de consulta de posición

## Overview

Implementación incremental del modo bilingüe de consulta de posición.

## Tasks

- [x] 1. Crear base de dominio y normalización
  - [x] 1.1 Implementar modelos tipados para intención, consulta, coincidencia, resultado, ambigüedad y error, sin serialización.
    - _Requisitos: 1.5-1.8, 2.4, 5.3-5.6_
  - [x] 1.2 Implementar `normalize`: recorte, espacios únicos y `casefold`.
    - _Requisitos: 2.1-2.2_

- [x] 2. Implementar intérprete bilingüe
  - [x] 2.1 Parsear ES/EN para casilla, fila, columna, filtros y resumen; devolver ambigüedades y errores localizables.
    - _Requisitos: 1.1-1.8, 2.3-2.5, 5.7_
  - [ ]* 2.2 Añadir pruebas unitarias de sinónimos ES/EN, ambigüedad, entradas vacías e inválidas.
    - _Requisitos: 2.3-2.5, 5.7_

- [x] 3. Implementar motor puro sobre snapshot
  - [x] 3.1 Copiar `chess.Board` al enviar y consultar `piece_at`/`piece_map` sin reanalizar imagen.
    - _Requisitos: 1.1-1.5, 1.9, 5.1_
  - [x] 3.2 Implementar filtros, orden `(fila,columna)`, cero resultados y subtotales de resumen.
    - _Requisitos: 1.5-1.8, 5.5-5.6_
  - [ ]* 3.3 PBT Hypothesis — **Propiedad 1: Normalización canónica y equivalencia ES/EN**.
    - **Valida: 2.1-2.3**
  - [ ]* 3.4 PBT Hypothesis — **Propiedad 2: Exactitud sin duplicados y orden**.
    - **Valida: 1.1-1.6, 1.8, 5.6**
  - [ ]* 3.5 PBT Hypothesis — **Propiedad 3: Resumen consistente**.
    - **Valida: 1.7**
  - [ ]* 3.6 PBT Hypothesis — **Propiedad 4: No mutación de FEN y turno**.
    - **Valida: 1.9, 5.1**
  - [ ]* 3.7 PBT Hypothesis — **Propiedad 5: Determinismo**.
    - **Valida: 5.5**

- [x] 4. Checkpoint — ejecutar `pytest`; asegurar que pase y preguntar si surgen dudas.

- [x] 5. Implementar respuesta y control
  - [x] 5.1 Formatear toda respuesta ES/EN, incluidos alcance vacío, resumen y errores.
    - _Requisitos: 1.1-1.8, 2.5, 3.1, 4.4_
  - [x] 5.2 Controlar snapshot, rechazo previo al motor, falta de tablero y selección de ambigüedad.
    - _Requisitos: 2.4, 2.6, 5.1, 5.7_
  - [ ]* 5.3 PBT Hypothesis — **Propiedad 7: Rechazo sin ejecutar el motor**.
    - **Valida: 5.7**
  - [ ]* 5.4 Añadir unitarias para cero resultados, falta de tablero y mensajes localizados.
    - _Requisitos: 1.8, 2.5-2.6_

- [x] 6. Integrar Streamlit accesible y TTS local
  - [x] 6.1 Añadir a `app.py` campo, envío, repetición, audio, estado mínimo, foco, etiquetas y anuncio único por teclado.
    - _Requisitos: 3.3, 4.1-4.4, 5.4_
  - [x] 6.2 Conectar `analysis_result["board"]` y `synthesize_audio` sin red; conservar texto ante fallo y no llamar TTS si audio está apagado.
    - _Requisitos: 3.1-3.4, 5.1-5.2_
  - [ ]* 6.3 PBT Hypothesis — **Propiedad 6: texto visible igual al enviado a TTS**.
    - **Valida: 3.1-3.2, 4.4**

- [ ] 7. Completar pruebas de integración y privacidad
  - [ ]* 7.1 Probar con mocks que no hay visión, red, escritura ni TTS desactivado; cubrir fallo TTS.
    - _Requisitos: 3.3-3.4, 5.1-5.4_
  - [ ]* 7.2 Probar flujo Streamlit: teclado, nombres accesibles, anuncio único, repetición y texto persistente.
    - _Requisitos: 4.1-4.4_

- [x] 8. Checkpoint final — ejecutar `pytest`; asegurar que pase y preguntar si surgen dudas.

## Notes
- `*` indica prueba opcional; usar `pytest`/`hypothesis` (mínimo 100 casos PBT).
- Sin micrófono, despliegue, entrenamiento ni reanálisis de imágenes.

## Task Dependency Graph

```json
{"waves":[{"id":0,"tasks":["1.1"]},{"id":1,"tasks":["1.2"]},{"id":2,"tasks":["2.1"]},{"id":3,"tasks":["2.2","3.1"]},{"id":4,"tasks":["3.2"]},{"id":5,"tasks":["3.3","3.4","3.5","3.6","3.7"]},{"id":6,"tasks":["5.1"]},{"id":7,"tasks":["5.2"]},{"id":8,"tasks":["5.3","5.4"]},{"id":9,"tasks":["6.1"]},{"id":10,"tasks":["6.2"]},{"id":11,"tasks":["6.3"]},{"id":12,"tasks":["7.1","7.2"]}]}
```