# Requirements Document

## Introduction
Modo local bilingüe para consultar por texto una posición de ajedrez reconocida, con respuesta visible y voz opcional; el micrófono queda fuera del alcance.

## Glossary
- **Modo**: interfaz en español o inglés.
- **Normalizador**: componente que uniforma entradas.
- **Motor**: componente que consulta una Instantánea.
- **Posición**: último `chess.Board` reconocido.
- **Instantánea**: copia inmutable de la Posición al enviar.
- **Respuesta**: resultado textual visible y anunciable.
- **Idioma**: idioma seleccionado.
- **TTS**: voz generada en el dispositivo.
- **Lector**: software que anuncia contenido accesible.

## Requirements

### 1. Alcance y corrección
1. WHEN la casilla consultada está ocupada, THE Motor SHALL informar casilla, tipo y color de pieza.
2. WHEN la casilla consultada está vacía, THE Motor SHALL informar casilla y estado vacío.
3. WHEN se consulta una columna de `a` a `h`, THE Motor SHALL enumerar solo ocupadas por fila de 1 a 8.
4. WHEN se consulta una fila de `1` a `8`, THE Motor SHALL enumerar solo ocupadas desde `a` hasta `h`.
5. WHEN una consulta contiene filtros, THE Motor SHALL aplicar conjuntamente color, tipo y alcance indicados.
6. WHEN el Motor enumera coincidencias, THE Motor SHALL ordenarlas por fila ascendente y después por columna.
7. WHEN se solicita un resumen, THE Motor SHALL informar total y subtotales por color y tipo, con cada grupo de subtotales sumando el total.
8. WHEN una consulta válida obtiene cero coincidencias, THE Motor SHALL identificar el alcance sin resultados.
9. WHEN finaliza una consulta, THE Motor SHALL conservar la posición y el turno de la Posición.

### 2. Normalización y errores
1. WHEN recibe texto, THE Normalizador SHALL recortar extremos, reducir espacios múltiples a uno e ignorar mayúsculas.
2. THE Normalizador SHALL producir igual resultado tras una o varias aplicaciones a una entrada.
3. WHEN dos consultas usan equivalencias españolas e inglesas, THE Motor SHALL devolver iguales datos y orden salvo el Idioma.
4. IF existen varias interpretaciones válidas, THEN THE Modo SHALL presentarlas y esperar una selección.
5. IF el texto no corresponde a un tipo admitido, THEN THE Modo SHALL mostrar tipos disponibles y un ejemplo en el Idioma.
6. IF no existe Posición, THEN THE Modo SHALL omitir la interpretación y pedir analizar un diagrama.

### 3. Idioma y voz
1. WHEN finaliza una consulta, THE Modo SHALL mostrar toda la Respuesta en el Idioma.
2. WHERE el audio está activado, THE TTS SHALL narrar la Respuesta sin añadir ni omitir información.
3. WHERE el audio está desactivado, THE Modo SHALL completar la consulta sin iniciar el TTS.
4. IF el TTS falla, THEN THE Modo SHALL conservar el texto visible y avisar en el Idioma.

### 4. Accesibilidad
1. THE Modo SHALL permitir manejar campo, envío, repetición y audio usando solo teclado.
2. THE Modo SHALL asignar nombres accesibles al campo, envío, repetición, audio y respuesta.
3. WHEN cambia la Respuesta, THE Modo SHALL anunciar el cambio una vez al Lector.
4. THE Modo SHALL mantener visible el texto completo con independencia del audio.

### 5. Integración, privacidad y determinismo
1. WHEN se envía una consulta, THE Motor SHALL consultar una Instantánea sin reanalizar la imagen.
2. THE Modo SHALL consultar y sintetizar voz con recursos locales sin usar red.
3. THE Modo SHALL evitar persistir consultas y respuestas en disco.
4. WHILE una respuesta se muestra o reproduce, THE Modo SHALL conservar en memoria de sesión solo los datos necesarios.
5. WHEN la Instantánea y la entrada normalizada son iguales, THE Motor SHALL devolver iguales datos y orden.
6. WHEN el Motor enumera resultados, THE Motor SHALL incluir exactamente las piezas coincidentes de la Instantánea sin duplicados.
7. IF la entrada está vacía o no es admitida, THEN THE Modo SHALL rechazarla.