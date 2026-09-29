# Implementation Plan: pdf-multi-board-transcription

## Overview

Plan incremental en Python para incorporar procesamiento local de PDFs con varios tableros, reutilizar el pipeline de imagen existente y mantener todos los artefactos en memoria. Cada paso deja código integrado y verificable; la integración Streamlit comienza solo cuando el dominio, PDF, detección, pipeline común, orquestación y exportación están disponibles.

## Tasks

- [ ] 1. Checkpoint bloqueante de licencia del motor PDF
  - Confirmar explícitamente que la distribución puede cumplir la licencia AGPL o comercial de PyMuPDF antes de iniciar tareas de código.
  - Si no se aprueba, seleccionar y registrar un motor local compatible con el protocolo `PdfRasterizer`, su licencia y versión fijada antes de continuar con 2.1.

- [ ] 2. Configurar el backend PDF aprobado
  - [ ] 2.1 Fijar la dependencia y la frontera del adaptador PDF
    - Si el checkpoint aprueba PyMuPDF, añadir exactamente `PyMuPDF==1.26.4` a `requirements.txt`; en caso contrario, fijar la versión del motor aprobado sin acoplar el dominio a su API.
    - Crear el protocolo de validación/rasterización por bytes y aislar la importación del motor para permitir sustitución sin cambios de dominio.
    - Mantener el backend sin rutas temporales, ejecución de contenido activo ni acceso de red.
    - _Requirements: 2.1, 3.1, 10.1, 10.2, 10.3, 10.4_

- [ ] 3. Implementar modelos de dominio, límites y errores
  - [ ] 3.1 Crear los modelos e invariantes del lote
    - Crear `pdf_batch_models.py` con enums y dataclasses para fases, estados, estilos, límites, geometrías, PDF validado, cajas, candidatos, tableros, análisis, páginas, progreso, lote y manifiesto.
    - Validar índices basados en uno, cajas exclusivas dentro de página, scores finitos, estados coherentes y valores positivos de límites configurables.
    - _Requirements: 2.7, 2.8, 3.2, 3.8, 4.9, 5.4, 6.1, 6.2, 7.1, 9.7_

  - [ ] 3.2 Implementar errores tipados y catálogos ES/EN
    - Crear códigos de `FeatureError`, argumentos seguros y localización completa para documento, página, tablero, audio, exportación, memoria y cancelación.
    - Implementar carga y validación de límites de despliegue con los valores predeterminados del diseño.
    - _Requirements: 1.3, 2.2, 2.3, 2.4, 2.5, 2.6, 3.7, 5.6, 6.4, 8.1, 8.9, 9.5_

  - [ ]* 3.3 Escribir pruebas unitarias de modelos, límites y errores
    - Probar invariantes, transiciones válidas/inválidas, fronteras `límite-1`, `límite`, `límite+1` y paridad de claves ES/EN.
    - _Requirements: 2.5, 2.6, 3.7, 8.1, 9.7_

- [ ] 4. Implementar validación y rasterización PDF local
  - [ ] 4.1 Implementar `PdfValidator` sobre bytes
    - Validar selección única, extensión sin distinción de mayúsculas, tamaño, magic PDF, estructura, tipo, protección, cero páginas, límite de páginas y enumeración completa de geometrías antes de rasterizar.
    - Calcular SHA-256 en memoria y cerrar de forma segura cualquier documento parcial.
    - _Requirements: 1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 9.8, 12.2_

  - [ ] 4.2 Implementar el rasterizador incremental RGB
    - Calcular dimensiones con `ceil(points / 72 × dpi)`, aplicar al menos 200 DPI en ambos ejes y rechazar páginas que superen el límite de píxeles antes de renderizar.
    - Rasterizar una página por índice desde bytes, copiar a PIL RGB sin alfa y liberar pixmap/documento mediante context managers y `finally`.
    - Ignorar enlaces, scripts, formularios, adjuntos, ejecutables y recursos externos sin resolverlos por red.
    - _Requirements: 2.8, 3.1, 3.2, 3.7, 9.1, 9.8, 10.1, 10.2, 10.3, 10.4_

  - [ ]* 4.3 Crear fixtures PDF sintéticos locales
    - Crear generadores deterministas en memoria para PDFs de cero páginas cuando el motor lo permita, una y varias páginas, páginas con cero/uno/varios tableros, estilos moderno y escaneado, dimensiones/rotaciones variadas, estructura corrupta y documento protegido cuando pueda simularse localmente.
    - No descargar fixtures ni usar OCR, red o archivos temporales; documentar como `skip` cualquier variante que el backend no pueda construir de forma fiable.
    - _Requirements: 2.2, 2.3, 2.4, 3.1, 4.1, 4.2, 10.1_

  - [ ]* 4.4 Escribir pruebas unitarias y de integración del validador y rasterizador
    - Cubrir extensión, magic, corrupción, protección, enumeración, límites, A4/Letter/rotación, redondeo, RGB a 200 DPI, error aislado de página y ausencia de resolución externa.
    - _Requirements: 1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.8, 3.1, 3.7, 10.2, 10.3, 10.4_

- [ ] 5. Implementar detección y extracción multi-tablero
  - [ ] 5.1 Implementar generadores moderno/escaneado y evidencia 8×8
    - Crear `multi_board_detector.py` con propuestas por color/componentes y por gris/umbral/líneas morfológicas.
    - Validar cuatro bordes, nueve transiciones por eje, ocho intervalos regulares, soporte mínimo de celdas, geometría y área; calcular el score ponderado y redondeado definido en el diseño.
    - _Requirements: 4.1, 4.2, 4.7, 11.4_

  - [ ] 5.2 Implementar IoU, grupos transitivos, deduplicación, orden, IDs y crop
    - Construir componentes conexas por IoU y compatibilidad de cuadrícula, conservar máxima confianza y resolver empates por Orden Visual.
    - Ordenar ganadores, asignar ordinales e IDs `pNNNN-bNNN`, ajustar cajas a la página y copiar recortes RGB con los cuatro límites completos.
    - _Requirements: 4.3, 4.4, 4.5, 4.6, 4.7, 4.9, 11.3, 11.4_

  - [ ]* 5.3 Escribir pruebas unitarias del detector y extractor
    - Cubrir K=0, K=1, K>1, ambos estilos, tablas no ajedrecísticas, blur/contraste bajo, score, IoU, cadenas transitivas, empates, clamp, coordenadas exclusivas y píxeles exactos del crop.
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

  - [ ]* 5.4 Escribir PBT de la Property 2: deduplicación independiente del orden
    - Generar candidatos, cadenas IoU y permutaciones; comprobar K ganadores estables, máxima confianza, desempate y Orden Visual con al menos 100 ejemplos.
    - Añadir el comentario `Feature: pdf-multi-board-transcription, Property 2` al test.
    - **Property 2: Deduplicación independiente del orden**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 11.3, 11.4**

- [ ] 6. Extraer y reutilizar el pipeline común de tablero
  - [ ] 6.1 Implementar `process_board_image` y conectar el flujo individual
    - Extraer de `app.py` a `board_analysis.py` estilo, orientación, recorte de 64 casillas, k-NN, FEN, conteos, Braille B8, descripción, piezas/movimientos y SVG táctil.
    - Hacer que PNG/JPG/ejemplos llamen a la nueva función con los mismos modelos y opciones, sin entrenar ni alterar preprocesado o salidas.
    - Aceptar copias RGB de tableros PDF sin redimensionar ni recomprimir antes de la llamada.
    - _Requirements: 1.5, 5.1, 5.3, 5.4, 5.8, 5.9, 12.4_

  - [ ]* 6.2 Escribir pruebas de regresión del flujo de imagen individual
    - Comparar corpus/fixtures existentes antes y después de la extracción para estilo, 64 clases, FEN, conteos, Braille, descripción, movimientos, consulta y SVG.
    - _Requirements: 1.5, 5.3, 5.9_

  - [ ]* 6.3 Escribir PBT de la Property 4: equivalencia imagen/PDF
    - Entregar arrays RGB idénticos a ambos adaptadores con modelos fake deterministas y comprobar igualdad de todas las salidas, incluida respuesta a la misma consulta.
    - Añadir el comentario `Feature: pdf-multi-board-transcription, Property 4` al test.
    - **Property 4: Equivalencia entre flujo de imagen y PDF**
    - **Validates: Requirements 5.1, 5.3, 5.9, 11.6**

- [ ] 7. Checkpoint del núcleo de análisis
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implementar memoria, progreso, cancelación y procesamiento secuencial
  - [ ] 8.1 Implementar `MemoryBudget` y liberación incremental
    - Estimar bytes retenidos y reservas antes de abrir, rasterizar, detectar, recortar, analizar y exportar; rechazar antes de asignar si se supera el límite.
    - Liberar páginas, máscaras, pixmaps y artefactos prescindibles para no retener más de una página adicional y mantener el presupuesto de sesión.
    - _Requirements: 3.7, 9.3, 9.4, 9.5, 9.6, 9.8, 10.5_

  - [ ] 8.2 Implementar `BatchProcessor` secuencial y sus eventos
    - Procesar páginas y tableros en Orden Visual con una sola inferencia activa, un `PageResult` por página, aislamiento de fallos y continuidad.
    - Emitir snapshots inmutables por fase/cambio y heartbeat máximo de un segundo; derivar contadores desde registros.
    - Consultar cancelación antes/después de operaciones atómicas, no iniciar trabajo nuevo, conservar completados y cancelar pendientes creados.
    - Cerrar recursos y emitir un único estado terminal incluso ante carreras o errores internos.
    - _Requirements: 2.8, 3.2, 3.3, 3.4, 3.5, 3.6, 3.8, 5.2, 5.5, 5.6, 5.7, 5.8, 9.3, 10.5_

  - [ ]* 8.3 Escribir pruebas unitarias de memoria, progreso, cancelación y aislamiento
    - Usar reloj, rasterizador, detector y pipeline fake para cubrir estimación previa, liberación, contadores, heartbeat, carreras terminales, cancelación en cada checkpoint y fallos de página/tablero.
    - _Requirements: 2.8, 3.3, 3.4, 3.5, 3.6, 3.8, 5.2, 5.6, 5.7, 9.3, 9.4, 9.5, 9.6_

  - [ ]* 8.4 Escribir PBT de la Property 1: cobertura exacta de páginas
    - Generar N páginas y patrones de fallos recuperables; comprobar exactamente `1..N`, índices únicos y estados terminales sin cancelación.
    - Añadir el comentario `Feature: pdf-multi-board-transcription, Property 1` al test.
    - **Property 1: Cobertura exacta de páginas**
    - **Validates: Requirements 3.8, 11.1**

  - [ ]* 8.5 Escribir PBT de la Property 5: aislamiento y continuidad ante fallos
    - Generar secuencias ordenadas con fallos inyectados; comprobar que registros completados no cambian y que se intentan elementos posteriores no cancelados.
    - Añadir el comentario `Feature: pdf-multi-board-transcription, Property 5` al test.
    - **Property 5: Aislamiento y continuidad ante fallos**
    - **Validates: Requirements 2.8, 5.5, 5.6, 5.7, 6.4, 11.5**

  - [ ]* 8.6 Escribir PBT de la Property 6: determinismo del lote
    - Ejecutar dos veces planes/documentos iguales con adaptadores deterministas y comparar la proyección de dominio excluyendo `run_id` y tiempos.
    - Añadir el comentario `Feature: pdf-multi-board-transcription, Property 6` al test.
    - **Property 6: Determinismo del lote**
    - **Validates: Requirements 11.2**

- [ ] 9. Implementar ZIP y manifiesto íntegramente en memoria
  - [ ] 9.1 Implementar `InMemoryZipBuilder`
    - Crear `pdf_batch_export.py` con `BytesIO`/`zipfile`, nombres derivados de IDs, `manifest.json` UTF-8 determinista, imágenes PNG y transcripciones solo disponibles.
    - Registrar fallos sin inventar transcripciones, comprobar memoria antes de cada entrada y descartar el buffer incompleto ante error.
    - _Requirements: 7.3, 7.4, 7.5, 7.6, 7.9, 10.1_

  - [ ]* 9.2 Escribir pruebas unitarias del ZIP y manifiesto
    - Inspeccionar bytes y contenido sin escribir disco; cubrir nombres seguros, orden, Unicode, registros completados/fallidos, presupuesto, cierre y descarte de ZIP parcial.
    - _Requirements: 7.3, 7.4, 7.5, 7.6, 7.9_

- [ ] 10. Integrar la feature en Streamlit ES/EN y hacerla accesible
  - [ ] 10.1 Implementar el controlador de sesión PDF
    - Crear un controlador que acepte upload único, calcule identidad, gestione `run_id`, worker/eventos y descarte eventos obsoletos sin mutar `st.session_state` desde el hilo.
    - Al cambiar de PDF o fuente, cancelar el lote anterior y limpiar bytes, páginas, tableros, audio y ZIP anteriores.
    - _Requirements: 1.1, 1.4, 6.1, 6.5, 7.1, 7.7, 7.8, 10.5_

  - [ ] 10.2 Añadir fuente PDF, límites, inicio, progreso y cancelación a `app.py`
    - Mantener separadas las ramas upload/galería/PDF y conservar el comportamiento PNG/JPG.
    - Mostrar límites vigentes, fase, página/total, detectados/completados/fallidos y cancelación cooperativa con sondeo máximo de un segundo.
    - Mostrar resumen de páginas sin tableros y privacidad de sesión.
    - _Requirements: 1.1, 1.2, 1.4, 1.5, 2.9, 3.3, 3.4, 3.5, 3.6, 6.10, 9.7, 10.6_

  - [ ] 10.3 Integrar galería, selector y todas las salidas por tablero
    - Mostrar preview con página, ordinal, coordenadas, confianza, estado y estilo; seleccionar por ID sin reprocesar.
    - Reutilizar posición reconocida para conteos, Braille, descripción, piezas/movimientos, consulta, audio local bajo demanda y SVG táctil.
    - Conectar descarga ZIP explícita y mantener visibles textos completos aunque audio o exportación fallen.
    - _Requirements: 4.8, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.3, 7.6_

  - [ ] 10.4 Implementar localización y accesibilidad del flujo PDF
    - Añadir todas las etiquetas, estados, ayudas y errores ES/EN sin modificar Braille B8.
    - Proveer nombres accesibles únicos, orden de teclado, foco visible, detalle asociado al ID y una región `aria-live` que anuncie una vez cada secuencia; enfocar errores sin perder registros válidos.
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9_

  - [ ]* 10.5 Escribir PBT de la Property 3: orden, identificadores y galería estables
    - Generar cajas deduplicadas en varias páginas; comprobar ordinales consecutivos, IDs derivados solo de página/ordinal y exactamente un registro por tablero en el mismo orden.
    - Añadir el comentario `Feature: pdf-multi-board-transcription, Property 3` al test.
    - **Property 3: Orden, identificadores y galería estables**
    - **Validates: Requirements 4.6, 4.9, 6.1**

  - [ ]* 10.6 Escribir pruebas automatizadas de integración Streamlit y accesibilidad
    - Usar `AppTest` para fuentes, límites, estados, limpieza, galería, selector, consulta y descarga; usar pruebas de navegador/axe disponibles para teclado, foco, nombres, asociación y anuncios únicos.
    - Verificar que cambiar idioma rerenderiza textos y conserva Braille y resultados sin reprocesar.
    - _Requirements: 1.1, 1.4, 1.5, 6.5, 6.6, 6.7, 6.9, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9_

- [ ] 11. Completar validación automatizada integral
  - [ ]* 11.1 Escribir pruebas de integración del lote con fixtures locales
    - Procesar PDFs sintéticos con cero/uno/varios tableros, ambos estilos, páginas rotadas, corruptas y protegidas cuando sean simulables; comprobar detección, orden, aislamiento, galería y ZIP.
    - Ejecutar sin red y sin entrenamiento; usar corpus local etiquetado para regresiones de falsos positivos/negativos.
    - _Requirements: 2.8, 3.8, 4.1, 4.2, 5.5, 5.7, 5.8, 6.10, 12.1, 12.2, 12.3, 12.4_

  - [ ]* 11.2 Escribir una prueba smoke no interactiva del flujo completo
    - Validar upload PDF → validación → rasterización → detección → análisis secuencial → selección → consulta → exportación en memoria usando fakes/modelos locales pequeños.
    - Comprobar también que el flujo PNG/JPG sigue operativo.
    - _Requirements: 1.5, 2.7, 3.8, 5.9, 6.3, 7.3_

  - [ ]* 11.3 Escribir PBT de la Property 7: cero persistencia y red
    - Espiar APIs de escritura, `tempfile`, sockets y clientes HTTP sobre ejecuciones arbitrarias; exigir traza vacía sin descarga y ZIP entregado como bytes sin ruta cuando se solicita.
    - Añadir el comentario `Feature: pdf-multi-board-transcription, Property 7` al test.
    - **Property 7: Cero persistencia y procesamiento local**
    - **Validates: Requirements 7.2, 7.3, 7.6, 7.9, 10.1, 11.7**

  - [ ]* 11.4 Escribir pruebas de rendimiento y control de recursos
    - Medir rasterización A4 y análisis calentado con límite de cinco segundos en el entorno de referencia; comprobar RSS pico, estimación previa, heartbeat y máximo de páginas coexistentes.
    - Aislar y etiquetar benchmarks para ejecución no interactiva y registrar entorno/versiones sin transmitir datos.
    - _Requirements: 3.4, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

  - [ ]* 11.5 Escribir pruebas de privacidad y tratamiento seguro
    - Denegar red y espiar rutas de escritura, adjuntos, scripts, enlaces y recursos externos; comprobar limpieza al completar, fallar, cancelar, cambiar PDF y cerrar sesión.
    - Verificar cero archivos derivados sin descarga y ausencia de OCR o entrenamiento.
    - _Requirements: 7.1, 7.2, 7.7, 7.8, 7.9, 10.1, 10.2, 10.3, 10.4, 10.5, 11.7, 12.1, 12.4_

- [ ] 12. Checkpoint final
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Las tareas marcadas con `*` son pruebas opcionales y pueden omitirse para un MVP; las tareas de implementación no son opcionales.
- Los siete PBT usan Hypothesis con al menos 100 ejemplos y un test separado por propiedad del diseño.
- Todos los fixtures y procesos son locales: no se permiten descargas, telemetría, OCR, entrenamiento ni solicitudes de red.
- El checkpoint 1 bloquea toda tarea de código. Solo se fija `PyMuPDF==1.26.4` si la licencia se aprueba; de lo contrario se decide primero un adaptador compatible.
- Cada tarea referencia criterios concretos para mantener trazabilidad y el DAG impide integrar Streamlit antes de completar el núcleo.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["2.1", "3.1", "3.2"] },
    { "id": 1, "tasks": ["3.3", "4.1", "4.3", "5.1", "6.1"] },
    { "id": 2, "tasks": ["4.2", "5.2", "6.2", "6.3"] },
    { "id": 3, "tasks": ["4.4", "5.3", "5.4", "8.1"] },
    { "id": 4, "tasks": ["8.2", "9.1"] },
    { "id": 5, "tasks": ["8.3", "8.4", "8.5", "8.6", "9.2", "10.1"] },
    { "id": 6, "tasks": ["10.2", "10.5"] },
    { "id": 7, "tasks": ["10.3"] },
    { "id": 8, "tasks": ["10.4"] },
    { "id": 9, "tasks": ["10.6", "11.1"] },
    { "id": 10, "tasks": ["11.2", "11.3", "11.4", "11.5"] }
  ]
}
```
