# Requirements Document

## Introduction

La feature `pdf-multi-board-transcription` amplía la aplicación Streamlit bilingüe para aceptar un documento PDF, localizar todos los diagramas de ajedrez detectables, extraerlos en orden visual y procesarlos secuencialmente mediante el pipeline de imagen existente. Los documentos, imágenes y resultados permanecen únicamente en memoria de sesión, con revisión accesible por tablero y descarga local opcional. El flujo actual de imágenes PNG y JPG conserva su comportamiento.

## Glossary

- **Aplicación**: aplicación web Streamlit bilingüe de transcripción accesible de diagramas de ajedrez.
- **Fuente_de_Entrada**: opción seleccionable para aportar una imagen PNG/JPG, un ejemplo existente o un Documento_PDF.
- **Flujo_de_Imagen**: comportamiento existente que procesa una imagen PNG o JPG individual.
- **Documento_PDF**: secuencia de bytes seleccionada por la persona usuaria como archivo PDF.
- **Validador_PDF**: componente que comprueba el contenido, la estructura, la accesibilidad, el tamaño y la enumeración de páginas de un Documento_PDF.
- **PDF_Protegido**: Documento_PDF cifrado o que requiere contraseña para acceder al contenido de las páginas.
- **PDF_Válido**: Documento_PDF cuya estructura puede verificarse a partir del contenido, cuyas páginas pueden enumerarse, que contiene al menos una página, que no es un PDF_Protegido y que cumple los Límites_Configurables de archivo y páginas.
- **Límites_Configurables**: valores de protección de recursos; los valores predeterminados son 50 MiB por Documento_PDF, 100 páginas, 40 megapíxeles por Página_Rasterizada y 1 GiB de Memoria_de_Feature por sesión.
- **Límite_Configurable**: umbral individual vigente perteneciente a los Límites_Configurables.
- **DPI**: cantidad de píxeles por pulgada usada para medir la resolución de rasterización.
- **MiB**: unidad de memoria equivalente a 1.048.576 bytes.
- **GiB**: unidad de memoria equivalente a 1.073.741.824 bytes.
- **Megapíxel**: unidad equivalente a un millón de píxeles.
- **Braille B8**: notación oficial de salida braille usada por la Aplicación.
- **SVG**: formato vectorial usado para la vista táctil.
- **OCR**: reconocimiento óptico de caracteres aplicado a texto general.
- **Página**: página de un Documento_PDF identificada mediante un índice consecutivo basado en uno.
- **Dimensiones_Físicas**: anchura y altura de una Página expresadas en pulgadas a partir de las dimensiones declaradas por el PDF.
- **Rasterizador**: componente local que convierte una Página en una Página_Rasterizada sin interpretar ni ejecutar Contenido_Activo.
- **Página_Rasterizada**: representación en píxeles de una Página con anchura y altura calculadas a partir de las Dimensiones_Físicas y una resolución efectiva mínima de 200 DPI en ambos ejes.
- **Resultado_de_Página**: registro único de una Página con índice y estado completado o fallido, incluidos los Tableros_Extraídos detectados y un Error_Descriptivo cuando corresponde.
- **Cuadrícula_Detectable**: región que permite identificar ocho filas, ocho columnas y los cuatro límites exteriores completos de un tablero de ajedrez.
- **Detector_de_Tableros**: componente que localiza cero, una o varias Cuadrículas_Detectables dentro de una Página_Rasterizada.
- **Candidato_de_Tablero**: región rectangular propuesta por el Detector_de_Tableros, con índice de Página, coordenadas de los bordes superior, izquierdo, inferior y derecho, y Confianza_de_Detección.
- **Confianza_de_Detección**: valor numérico producido por el Detector_de_Tableros para ordenar candidatos que representan la misma Cuadrícula_Detectable.
- **IoU**: cociente entre el área de intersección y el área de unión de dos Candidatos_de_Tablero de una misma Página.
- **Grupo_Duplicado**: componente transitivo de Candidatos_de_Tablero de una misma Página conectados directa o indirectamente por pares con IoU igual o superior a 0,80 y asociados con la misma Cuadrícula_Detectable.
- **Orden_Visual**: orden ascendente determinista por índice de Página, borde superior, borde izquierdo, borde inferior y borde derecho.
- **Tablero_Extraído**: imagen recortada de una Cuadrícula_Detectable conservada después de la deduplicación, junto con página, coordenadas y ordinal dentro de la Página.
- **Identificador_de_Tablero**: etiqueta estable compuesta exclusivamente por el índice de Página y el ordinal del Tablero_Extraído dentro de la Página.
- **Pipeline_Existente**: flujo aplicado por el Flujo_de_Imagen a un tablero para identificar el tipo visual, clasificar 64 casillas y generar número de piezas, Braille B8, descripción textual para audio, piezas y movimientos, respuestas a consultas textuales y vista táctil SVG.
- **Procesador_de_Lote**: componente que coordina rasterización, detección y ejecución secuencial del Pipeline_Existente sobre los Tableros_Extraídos.
- **Fase_de_Procesamiento**: uno de los estados validando, rasterizando, detectando, procesando tableros, completado, fallido o cancelado.
- **Registro_de_Tablero**: datos de un Tablero_Extraído, incluidos Identificador_de_Tablero, Estado_de_Tablero, tipo visual, imagen, resultados accesibles y Error_Descriptivo cuando corresponde.
- **Estado_de_Tablero**: uno de los valores pendiente, procesando, completado, fallido o cancelado.
- **Error_Descriptivo**: mensaje localizado que identifica el elemento afectado y la causa verificable del fallo.
- **Galería_de_Sesión**: lista en Orden_Visual de Registros_de_Tablero disponible durante la sesión activa.
- **Selector_de_Tablero**: control que permite elegir un Registro_de_Tablero para revisar resultados, consultar la posición y reproducir audio local.
- **Almacén_de_Sesión**: memoria volátil asociada con la sesión activa de Streamlit.
- **Paquete_de_Descarga**: archivo ZIP generado en memoria que contiene imágenes extraídas, transcripciones disponibles y un Manifiesto.
- **Manifiesto**: archivo del Paquete_de_Descarga que relaciona cada Identificador_de_Tablero con página, ordinal, estado, tipo visual, imagen, transcripciones disponibles y Error_Descriptivo cuando corresponde.
- **Interfaz_Accesible**: controles, estados y resultados operables mediante teclado y compatibles con lector de pantalla.
- **Idioma_Activo**: español o inglés seleccionado en la Aplicación.
- **Memoria_de_Feature**: memoria de sesión atribuible al Documento_PDF, Páginas_Rasterizadas, Tableros_Extraídos, resultados y Paquete_de_Descarga.
- **Entorno_de_Referencia**: equipo con CPU de cuatro núcleos, 8 GiB de RAM, almacenamiento local y sin GPU.
- **Contenido_Activo**: scripts, acciones, formularios, adjuntos, contenido multimedia, referencias externas o ejecutables incorporados en un Documento_PDF.
- **Alcance_Inicial**: capacidades incluidas en la primera versión de la feature.

## Requirements

### Requirement 1: Fuente PDF y compatibilidad de entradas

**User Story:** Como persona usuaria, quiero seleccionar un PDF además de las fuentes actuales, para transcribir varios tableros sin perder el flujo de imágenes existente.

#### Acceptance Criteria

1. THE Aplicación SHALL presentar Documento_PDF como una Fuente_de_Entrada adicional y diferenciada.
2. WHEN la persona usuaria selecciona la Fuente_de_Entrada Documento_PDF, THE Aplicación SHALL aceptar una única selección cuyo nombre termine en `.pdf` sin distinción entre mayúsculas y minúsculas.
3. IF una selección contiene más de un archivo o una extensión distinta de `.pdf`, THEN THE Aplicación SHALL rechazar la selección y mostrar un Error_Descriptivo.
4. WHEN la persona usuaria cambia la Fuente_de_Entrada, THE Aplicación SHALL mostrar los controles correspondientes a la Fuente_de_Entrada seleccionada.
5. THE Flujo_de_Imagen SHALL conservar el comportamiento y los resultados disponibles antes de incorporar la Fuente_de_Entrada Documento_PDF.

### Requirement 2: Validación del documento y de las páginas

**User Story:** Como persona usuaria, quiero conocer los problemas del PDF antes de procesarlo, para corregir la entrada sin perder el control de la sesión.

#### Acceptance Criteria

1. WHEN la persona usuaria proporciona un Documento_PDF, THE Validador_PDF SHALL verificar el contenido, la estructura y la enumeración completa de páginas antes de iniciar la rasterización.
2. IF el contenido o la estructura del Documento_PDF no puede verificarse como PDF, THEN THE Validador_PDF SHALL rechazar el Documento_PDF antes de la rasterización y mostrar un Error_Descriptivo.
3. IF el Documento_PDF es un PDF_Protegido, THEN THE Validador_PDF SHALL rechazar el Documento_PDF antes de la rasterización e informar que los PDFs protegidos están fuera del Alcance_Inicial.
4. IF la enumeración del Documento_PDF produce cero páginas, THEN THE Validador_PDF SHALL rechazar el Documento_PDF e informar que el documento está vacío.
5. IF el tamaño del Documento_PDF supera el Límite_Configurable vigente, THEN THE Validador_PDF SHALL rechazar el Documento_PDF e informar el tamaño recibido y el límite vigente.
6. IF el número enumerado de páginas supera el Límite_Configurable vigente, THEN THE Validador_PDF SHALL rechazar el Documento_PDF e informar el número recibido y el límite vigente.
7. WHEN el Documento_PDF satisface todas las condiciones definidas para PDF_Válido, THE Validador_PDF SHALL clasificar el Documento_PDF como PDF_Válido.
8. IF una Página de un PDF_Válido no puede rasterizarse, THEN THE Procesador_de_Lote SHALL crear un Resultado_de_Página fallido con el índice de Página y continuar con la Página siguiente.
9. THE Aplicación SHALL mostrar los Límites_Configurables vigentes de tamaño y páginas antes de iniciar el procesamiento.

### Requirement 3: Rasterización, progreso y cancelación

**User Story:** Como persona usuaria, quiero seguir y cancelar el procesamiento de las páginas, para mantener el control sobre documentos extensos.

#### Acceptance Criteria

1. WHEN comienza el procesamiento de un PDF_Válido, THE Rasterizador SHALL calcular las dimensiones en píxeles de cada Página a partir de las Dimensiones_Físicas y una resolución mínima de 200 DPI en ambos ejes.
2. WHEN finaliza la rasterización de una Página, THE Procesador_de_Lote SHALL asociar el resultado con el índice basado en uno de la Página.
3. WHILE el Procesador_de_Lote está activo, THE Aplicación SHALL mostrar la Fase_de_Procesamiento, el índice de Página actual, el total de páginas y los totales de tableros detectados, completados y fallidos.
4. WHILE el Procesador_de_Lote está activo, THE Aplicación SHALL actualizar el progreso con un intervalo máximo de un segundo y después de cada cambio de estado de una Página.
5. WHEN el Procesador_de_Lote registra una solicitud de cancelación, THE Procesador_de_Lote SHALL dejar de iniciar nuevas rasterizaciones, detecciones y ejecuciones del Pipeline_Existente.
6. WHEN el Procesador_de_Lote confirma la cancelación, THE Procesador_de_Lote SHALL conservar los Registros_de_Tablero completados y marcar como cancelados los Registros_de_Tablero pendientes.
7. IF una Página_Rasterizada supera el límite vigente de megapíxeles, THEN THE Rasterizador SHALL omitir la Página, crear un Resultado_de_Página fallido e informar el límite excedido.
8. WHEN el Procesador_de_Lote finaliza sin cancelación, THE Procesador_de_Lote SHALL producir exactamente un Resultado_de_Página completado o fallido por cada Página enumerada del PDF_Válido.

### Requirement 4: Detección, deduplicación, orden y recorte

**User Story:** Como persona usuaria, quiero que la aplicación encuentre cada tablero una sola vez y en el orden del documento, para revisar el lote completo.

#### Acceptance Criteria

1. WHEN una Página_Rasterizada contiene K Cuadrículas_Detectables, THE Detector_de_Tableros SHALL producir exactamente K Tableros_Extraídos para la Página.
2. WHEN una Página_Rasterizada contiene cero Cuadrículas_Detectables, THE Detector_de_Tableros SHALL registrar cero Tableros_Extraídos sin marcar la Página como fallida.
3. WHEN una cadena de Candidatos_de_Tablero contiene pares consecutivos con IoU igual o superior a 0,80 para la misma Cuadrícula_Detectable, THE Detector_de_Tableros SHALL asignar todos los candidatos de la cadena al mismo Grupo_Duplicado.
4. WHEN varios Candidatos_de_Tablero forman un Grupo_Duplicado, THE Detector_de_Tableros SHALL conservar exactamente un Candidato_de_Tablero del Grupo_Duplicado.
5. WHEN el Detector_de_Tableros selecciona un Candidato_de_Tablero de un Grupo_Duplicado, THE Detector_de_Tableros SHALL elegir la mayor Confianza_de_Detección y resolver empates mediante el Orden_Visual.
6. WHEN finaliza la deduplicación, THE Detector_de_Tableros SHALL ordenar los Tableros_Extraídos mediante el Orden_Visual.
7. WHEN el Detector_de_Tableros crea un Tablero_Extraído, THE Detector_de_Tableros SHALL recortar la imagen por los cuatro límites exteriores de la Cuadrícula_Detectable completa.
8. WHEN se crea un Tablero_Extraído, THE Aplicación SHALL mostrar una vista previa con el índice de Página, el ordinal y las coordenadas detectadas.
9. WHEN se asigna un Identificador_de_Tablero, THE Aplicación SHALL derivar el Identificador_de_Tablero exclusivamente del índice de Página y del ordinal determinado por el Orden_Visual.

### Requirement 5: Procesamiento secuencial mediante el pipeline existente

**User Story:** Como persona usuaria, quiero procesar cada tablero igual que una imagen individual, para obtener resultados equivalentes aunque otro tablero falle.

#### Acceptance Criteria

1. WHEN un Tablero_Extraído alcanza el estado procesando, THE Procesador_de_Lote SHALL entregar al Pipeline_Existente una imagen con dimensiones y valores de píxel idénticos a los del Tablero_Extraído.
2. WHILE el Procesador_de_Lote procesa Tableros_Extraídos, THE Procesador_de_Lote SHALL mantener como máximo una ejecución activa del Pipeline_Existente.
3. WHEN el Pipeline_Existente procesa un Tablero_Extraído, THE Pipeline_Existente SHALL usar los mismos modelos, configuración, clasificación de 64 casillas y formateadores que el Flujo_de_Imagen.
4. WHEN el Pipeline_Existente identifica el tipo visual, THE Registro_de_Tablero SHALL registrar moderno, escaneado o no clasificado.
5. WHEN el Pipeline_Existente completa un Tablero_Extraído, THE Procesador_de_Lote SHALL marcar el Registro_de_Tablero como completado y continuar con el siguiente Identificador_de_Tablero en Orden_Visual.
6. IF el Pipeline_Existente falla para un Tablero_Extraído, THEN THE Procesador_de_Lote SHALL limitar el fallo al Registro_de_Tablero afectado y conservar un Error_Descriptivo.
7. WHEN un Registro_de_Tablero queda fallido, THE Procesador_de_Lote SHALL continuar con el siguiente Identificador_de_Tablero en Orden_Visual.
8. WHILE el Procesador_de_Lote está activo, THE Aplicación SHALL usar modelos previamente entrenados y omitir operaciones de entrenamiento o ajuste.
9. WHEN una misma imagen se procesa con igual configuración mediante Documento_PDF y Flujo_de_Imagen, THE Pipeline_Existente SHALL producir clasificaciones de casillas, número de piezas y tipo visual iguales, y Braille B8, descripción, piezas, movimientos, respuesta a la misma consulta y SVG táctil iguales carácter por carácter.

### Requirement 6: Galería y revisión de resultados

**User Story:** Como persona usuaria, quiero revisar cada tablero y todos sus resultados, para navegar por el documento sin repetir el análisis.

#### Acceptance Criteria

1. WHEN se crea un Tablero_Extraído, THE Galería_de_Sesión SHALL crear exactamente un Registro_de_Tablero en el Orden_Visual.
2. THE Registro_de_Tablero SHALL mostrar Identificador_de_Tablero, índice de Página, ordinal, Estado_de_Tablero, tipo visual e imagen extraída correspondientes al mismo Tablero_Extraído.
3. WHEN un Registro_de_Tablero está completado, THE Registro_de_Tablero SHALL mostrar número de piezas, Braille B8, descripción textual, piezas y movimientos, consulta textual y vista táctil SVG.
4. IF un Registro_de_Tablero está fallido, THEN THE Registro_de_Tablero SHALL mostrar el Error_Descriptivo y conservar disponibles los demás Registros_de_Tablero.
5. WHEN la persona usuaria elige un Identificador_de_Tablero mediante el Selector_de_Tablero, THE Aplicación SHALL mostrar el detalle del Registro_de_Tablero correspondiente sin reprocesar el Documento_PDF.
6. WHEN la persona usuaria realiza una consulta textual, THE Aplicación SHALL usar la posición reconocida del Registro_de_Tablero seleccionado.
7. WHERE el audio local está disponible, WHEN la persona usuaria solicita reproducción, THE Selector_de_Tablero SHALL reproducir la descripción del Registro_de_Tablero seleccionado.
8. IF la síntesis de audio local falla, THEN THE Aplicación SHALL mantener visible la descripción completa y mostrar un Error_Descriptivo.
9. THE Galería_de_Sesión SHALL mantener visibles el Braille B8 y la descripción completa con independencia de la disponibilidad o del estado del audio.
10. WHEN el lote contiene páginas sin tableros, THE Aplicación SHALL incluir los índices de las páginas con cero Tableros_Extraídos en el resumen del lote.

### Requirement 7: Memoria de sesión, descarga y limpieza

**User Story:** Como persona usuaria, quiero conservar temporalmente los tableros y descargar una copia local opcional, para decidir qué información guardar.

#### Acceptance Criteria

1. THE Almacén_de_Sesión SHALL conservar el Documento_PDF, las Páginas_Rasterizadas, los Tableros_Extraídos, los resultados y el Paquete_de_Descarga únicamente en memoria volátil durante la sesión activa.
2. WHEN finaliza, falla o se cancela el procesamiento, THE Aplicación SHALL dejar sin cambios el almacenamiento persistente del servidor respecto del Documento_PDF y los artefactos derivados.
3. WHEN la persona usuaria solicita explícitamente una descarga, THE Aplicación SHALL generar el Paquete_de_Descarga completamente en memoria.
4. WHEN se genera el Paquete_de_Descarga, THE Paquete_de_Descarga SHALL incluir la imagen de cada Tablero_Extraído, las transcripciones disponibles y el Manifiesto.
5. WHEN el Paquete_de_Descarga contiene un Registro_de_Tablero fallido, THE Manifiesto SHALL registrar el Identificador_de_Tablero, el estado fallido y el Error_Descriptivo sin crear transcripciones para el fallo.
6. WHEN la persona usuaria activa la descarga, THE Aplicación SHALL entregar el Paquete_de_Descarga al navegador sin seleccionar ni escribir una ruta persistente del servidor.
7. WHEN la persona usuaria selecciona un Documento_PDF diferente, THE Almacén_de_Sesión SHALL eliminar el Documento_PDF anterior, los artefactos derivados y el Paquete_de_Descarga anterior antes de procesar el nuevo documento.
8. WHEN termina la sesión, THE Almacén_de_Sesión SHALL liberar el Documento_PDF, las Páginas_Rasterizadas, los Tableros_Extraídos, los resultados y el Paquete_de_Descarga.
9. WHEN la persona usuaria no solicita una descarga, THE Aplicación SHALL completar el lote sin crear archivos persistentes derivados en el cliente ni en el servidor.

### Requirement 8: Idiomas y accesibilidad

**User Story:** Como persona usuaria de tecnología de asistencia, quiero manejar el lote en español o inglés, para revisar los resultados sin depender de visión ni ratón.

#### Acceptance Criteria

1. WHEN cambia el Idioma_Activo, THE Aplicación SHALL mostrar en el Idioma_Activo todas las etiquetas, instrucciones, nombres accesibles, estados, progresos, avisos y errores de la feature.
2. WHEN cambia el Idioma_Activo, THE Aplicación SHALL conservar la notación oficial del Braille B8 carácter por carácter.
3. THE Interfaz_Accesible SHALL permitir seleccionar el PDF, iniciar y cancelar el lote, recorrer la Galería_de_Sesión, elegir un tablero, consultar, reproducir audio y descargar usando solo teclado.
4. WHEN un control recibe foco mediante teclado, THE Interfaz_Accesible SHALL mostrar un indicador de foco visible.
5. THE Interfaz_Accesible SHALL proporcionar un nombre accesible único a cada control de PDF, procesamiento, cancelación, galería, selección, consulta, audio y descarga.
6. WHEN cambia el progreso, el Estado_de_Tablero o el resumen del lote, THE Interfaz_Accesible SHALL anunciar cada cambio una vez mediante una región de estado compatible con lector de pantalla.
7. WHEN la persona usuaria selecciona un Registro_de_Tablero, THE Interfaz_Accesible SHALL asociar el detalle visible con el Identificador_de_Tablero seleccionado.
8. THE Interfaz_Accesible SHALL mantener visibles las transcripciones completas cuando el audio está desactivado, no disponible o en reproducción.
9. IF una acción falla, THEN THE Interfaz_Accesible SHALL asociar el foco con el Error_Descriptivo y conservar los Registros_de_Tablero válidos existentes.

### Requirement 9: Rendimiento y control de memoria

**User Story:** Como persona usuaria, quiero que los documentos se procesen con límites medibles, para evitar bloqueos de la sesión.

#### Acceptance Criteria

1. WHEN el Entorno_de_Referencia rasteriza una Página A4 dentro de los Límites_Configurables, THE Rasterizador SHALL disponer de la Página_Rasterizada en un máximo de cinco segundos desde el inicio de la rasterización.
2. WHEN el Entorno_de_Referencia procesa un Tablero_Extraído, THE Pipeline_Existente SHALL disponer del Registro_de_Tablero completado o fallido en un máximo de cinco segundos desde el inicio del análisis.
3. WHILE el Procesador_de_Lote está activo, THE Procesador_de_Lote SHALL mantener la Memoria_de_Feature en un máximo de 1 GiB por sesión.
4. WHEN el Procesador_de_Lote se dispone a iniciar la siguiente operación, THE Procesador_de_Lote SHALL estimar la Memoria_de_Feature resultante.
5. IF la estimación de la siguiente operación supera el límite vigente de Memoria_de_Feature, THEN THE Procesador_de_Lote SHALL omitir la operación, liberar artefactos intermedios prescindibles y mostrar un Error_Descriptivo.
6. WHEN una Página_Rasterizada deja de ser necesaria para detección, recorte o vista previa, THE Almacén_de_Sesión SHALL liberar la Página_Rasterizada antes de conservar más de una Página_Rasterizada adicional.
7. WHERE los Límites_Configurables se modifican mediante configuración de despliegue, THE Validador_PDF SHALL aplicar y mostrar los valores vigentes.
8. IF un Documento_PDF o una Página incumple un Límite_Configurable, THEN THE Procesador_de_Lote SHALL detener el trabajo afectado antes de asignar recursos a la siguiente fase del trabajo rechazado.

### Requirement 10: Privacidad y tratamiento seguro

**User Story:** Como persona usuaria, quiero que el PDF se trate como datos locales inertes, para evitar filtraciones o ejecución de contenido incorporado.

#### Acceptance Criteria

1. THE Aplicación SHALL realizar validación, rasterización, detección, clasificación, generación de resultados y empaquetado mediante recursos locales sin solicitudes de red.
2. WHEN el Rasterizador abre un Documento_PDF, THE Rasterizador SHALL tratar el Contenido_Activo como datos inertes y leer únicamente el contenido necesario para rasterizar las páginas.
3. IF un Documento_PDF contiene referencias externas, THEN THE Rasterizador SHALL omitir la resolución por red y continuar con el contenido local renderizable.
4. IF un Documento_PDF contiene adjuntos o ejecutables, THEN THE Rasterizador SHALL omitir la apertura y ejecución de los adjuntos o ejecutables.
5. WHEN finaliza, falla o se cancela un lote, THE Aplicación SHALL eliminar de memoria los artefactos intermedios que no pertenezcan a la Galería_de_Sesión o al Paquete_de_Descarga solicitado.
6. WHILE la persona usuaria revisa los resultados, THE Aplicación SHALL informar que el Documento_PDF y los Tableros_Extraídos permanecen en la sesión y que la descarga requiere una acción explícita.

### Requirement 11: Propiedades de corrección del lote

**User Story:** Como responsable de calidad, quiero propiedades verificables del procesamiento por lotes, para detectar pérdidas, duplicados y diferencias respecto del flujo individual.

#### Acceptance Criteria

1. WHEN un PDF_Válido de N páginas finaliza sin cancelación, THE Procesador_de_Lote SHALL producir exactamente N Resultados_de_Página con índices únicos del 1 al N.
2. WHEN el mismo PDF_Válido se procesa dos veces con iguales modelos, configuración y límites, THE Procesador_de_Lote SHALL producir los mismos Resultados_de_Página, Identificadores_de_Tablero, coordenadas, Orden_Visual, estados, tipos visuales, clasificaciones, números de piezas y transcripciones.
3. WHEN el mismo conjunto de Candidatos_de_Tablero se presenta en cualquier orden, THE Detector_de_Tableros SHALL producir el mismo conjunto ordenado de Tableros_Extraídos.
4. WHEN una Página contiene K Cuadrículas_Detectables y cualquier cantidad de candidatos duplicados asociados con esas cuadrículas, THE Detector_de_Tableros SHALL producir exactamente K Tableros_Extraídos.
5. WHILE el Procesador_de_Lote está activo, WHEN falla un Identificador_de_Tablero, THE Procesador_de_Lote SHALL conservar sin cambios los Registros_de_Tablero completados y procesar los Identificadores_de_Tablero posteriores.
6. WHEN una misma imagen se procesa con igual configuración mediante Documento_PDF y Flujo_de_Imagen, THE Pipeline_Existente SHALL producir resultados equivalentes según el criterio de equivalencia definido en Requirement 5.
7. WHEN termina el procesamiento sin una descarga explícita, THE Aplicación SHALL producir cero archivos persistentes derivados del Documento_PDF en el servidor y en el cliente.

### Requirement 12: Alcance inicial

**User Story:** Como responsable del producto, quiero límites explícitos para la primera versión, para concentrar la entrega en la transcripción de tableros.

#### Acceptance Criteria

1. THE Alcance_Inicial SHALL clasificar el reconocimiento OCR del texto general del documento como capacidad fuera de alcance.
2. THE Alcance_Inicial SHALL clasificar la apertura mediante contraseña o el descifrado de PDFs protegidos como capacidad fuera de alcance.
3. THE Alcance_Inicial SHALL clasificar la edición manual avanzada de regiones, casillas o piezas reconocidas como capacidad fuera de alcance.
4. THE Alcance_Inicial SHALL clasificar el entrenamiento, reentrenamiento o ajuste de modelos durante el procesamiento PDF como capacidad fuera de alcance.
