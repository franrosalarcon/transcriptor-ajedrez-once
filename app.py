import html
import os
import pickle
import tempfile

import chess
import numpy as np
import streamlit as st
from PIL import Image

from deteccion_tablero import DARK, LIGHT, _near, recortar_casillas
from formatters import AudioFormatter, BrailleFormatter


# ========== CONFIGURACIÓN E IDIOMAS ==========
st.set_page_config(
    page_title="ONCE Chess",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="expanded",
)

LANGUAGE_OPTIONS = {"Español": "es", "English": "en"}
language_option = st.sidebar.selectbox(
    "Idioma / Language",
    options=list(LANGUAGE_OPTIONS),
    key="global_language",
    help="Selecciona el idioma de toda la interfaz / Choose the interface language.",
)
LANG = LANGUAGE_OPTIONS[language_option]

TEXT = {
    "es": {
        "eyebrow": "♟ Tecnología accesible · Hackathon 2026",
        "hero_title": "El tablero se ve.<br>La posición se escucha.",
        "hero_subtitle": "Transforma diagramas de ajedrez en transcripciones Braille B8, descripciones de audio y vistas táctiles desde una experiencia clara y accesible.",
        "made_by": "Realizado por Francisco Ros Alarcón",
        "impact_kicker": "Impacto social",
        "impact_title": "Ajedrez más accesible, estudio más autónomo",
        "impact_copy": "Una ayuda para convertir información visual del tablero en formatos que facilitan el acceso, la revisión y el aprendizaje de posiciones de ajedrez.",
        "flow_label": "Flujo de uso en tres pasos",
        "upload_short": "Sube",
        "upload_flow": "Selecciona un diagrama PNG o JPG, o utiliza un ejemplo.",
        "analyze_short": "Analiza",
        "analyze_flow": "El sistema detecta el estilo y reconoce las 64 casillas.",
        "explore_short": "Explora",
        "explore_flow": "Consulta Braille B8, audio, movimientos y vista táctil.",
        "start_here": "Comienza aquí",
        "step_1": "Paso 1 de 3 · Selecciona el origen del diagrama",
        "image_source": "Origen de la imagen",
        "upload_source": "📤 Subir archivo",
        "gallery_source": "📚 Galería de ejemplos",
        "source_help": "Puedes cargar un archivo local o probar la experiencia con un ejemplo.",
        "upload_diagram": "Sube un diagrama de ajedrez",
        "upload_help": "Formatos admitidos: PNG, JPG y JPEG.",
        "image_ready": "Imagen válida y lista para analizar.",
        "invalid_image": "No se pudo leer la imagen. Comprueba que sea un PNG o JPG válido.",
        "select_example": "Selecciona un ejemplo",
        "example_help": "Los ejemplos permiten probar el flujo sin subir un archivo.",
        "example_ready": "{name} listo para analizar.",
        "example_missing": "El ejemplo seleccionado no está disponible en este momento.",
        "board_settings": "Ajustes del tablero",
        "crop_adjustment": "Ajuste de recorte (píxeles)",
        "crop_help": "Corrige el margen si la cuadrícula no queda bien delimitada.",
        "rotate": "Girar tablero 180°",
        "rotate_help": "Giro manual. Solo se aplica cuando la orientación automática está desactivada.",
        "auto_orientation": "Orientación automática (experimental)",
        "auto_orientation_help": "Prueba 0° y 180° con el mismo pipeline. Está desactivada por defecto; al activarla, el giro manual se ignora para evitar dobles rotaciones.",
        "orientation_selected": "Orientación elegida: {orientation}",
        "orientation_normal": "normal (0°)",
        "orientation_rotated": "girada 180°",
        "prototype_info": "Información del prototipo",
        "prototype_caption": "Clasificación dual k-NN · Casillas en escala de grises de 32 × 32 px · Detección automática de estilo",
        "privacy_sidebar": "Privacidad: la imagen se procesa localmente durante esta sesión y no se envía a servicios externos.",
        "model_error": "No se pudieron cargar los modelos locales. Comprueba que los archivos del modelo estén disponibles.",
        "step_2": "Paso 2 · Analiza",
        "reading_title": "Lectura del diagrama",
        "reading_copy": "Revisa la imagen seleccionada y el resumen de la posición reconocida.",
        "selected_diagram": "Diagrama seleccionado",
        "image_preview": "Vista previa de la imagen que se analizará",
        "analysis_summary": "Resumen del análisis",
        "analyzing": "Analizando las 64 casillas del tablero…",
        "style_detected": "Estilo detectado: {style}",
        "modern_style": "moderno en color",
        "scanned_style": "escaneado en blanco y negro",
        "pieces_metric": "PIEZAS",
        "white_metric": "BLANCAS",
        "black_metric": "NEGRAS",
        "analysis_done": "Análisis completado. Los resultados accesibles están listos.",
        "processing_error": "No se pudo completar el análisis. Revisa el recorte o prueba con otra imagen válida.",
        "step_3": "Paso 3 · Consulta, escucha e imprime",
        "results_title": "Resultados accesibles",
        "results_copy": "El texto permanece disponible aunque la reproducción de audio no esté activa.",
        "braille_tab": "⠃ Braille B8",
        "audio_tab": "🔊 Audio en español",
        "moves_tab": "♞ Piezas y movimientos",
        "tactile_tab": "◫ Vista para impresión en relieve",
        "braille_title": "Transcripción Braille B8",
        "braille_caption": "Formato oficial B8 en Unicode, preparado para lectura, revisión y copia. Su notación oficial se conserva y no se traduce.",
        "braille_label": "Texto de la transcripción Braille B8",
        "show_braille": "Mostrar texto Braille para copiar",
        "braille_copy_ready": "Texto Braille visible y listo para seleccionar y copiar.",
        "audio_title": "Descripción adaptada para audio",
        "audio_caption": "Texto en español siempre disponible, con reproducción local opcional.",
        "audio_label": "Texto de la descripción de audio",
        "play_audio": "🔊 Reproducir descripción",
        "preparing_audio": "Preparando el audio en español…",
        "audio_ready": "Audio preparado. Usa el control para reproducirlo.",
        "audio_unavailable": "El audio no está disponible; la descripción de texto permanece visible.",
        "audio_error": "No se pudo sintetizar el audio local en este dispositivo.",
        "show_copy": "Mostrar para copiar",
        "moves_title": "Piezas y movimientos",
        "moves_intro": "Cada fila identifica una pieza detectada y los destinos que puede alcanzar en la posición reconocida.",
        "conditional_mode": "Destinos legales condicionados",
        "conditional_note": "La posición contiene ambos reyes y supera la validación de python-chess. Los destinos se calculan suponiendo que el color de cada pieza tiene el turno. El diagrama no informa de turno, enroques ni captura al paso, por lo que esas condiciones especiales no se pueden confirmar.",
        "pseudo_mode": "Destinos geométricos o pseudolegales",
        "pseudo_note": "La posición reconocida no permite calcular jugadas legales fiables (puede ser incompleta o inválida). Los destinos mostrados describen el movimiento de la pieza y la ocupación actual; no deben interpretarse como jugadas legales.",
        "moves_mode": "Modo: {mode}",
        "color_column": "Color",
        "piece_column": "Pieza",
        "square_column": "Casilla",
        "destinations_column": "Destinos alcanzables",
        "white": "Blancas",
        "black": "Negras",
        "king": "Rey",
        "queen": "Dama",
        "rook": "Torre",
        "bishop": "Alfil",
        "knight": "Caballo",
        "pawn": "Peón",
        "no_destinations": "Ninguno",
        "no_pieces": "No se detectaron piezas en el tablero.",
        "moves_error": "No se pudieron calcular algunos destinos; el resto de resultados sigue disponible.",
        "moves_audio_title": "Escuchar piezas y destinos",
        "moves_audio_intro": "Elige si quieres escuchar toda la tabla o únicamente los destinos de una pieza.",
        "moves_read_option": "Contenido que se va a narrar",
        "read_full_table": "Leer toda la tabla",
        "read_one_piece": "Leer destinos de una pieza",
        "full_narration_label": "Texto exacto de la narración de toda la tabla",
        "piece_selector": "Selecciona una pieza por color, tipo y casilla",
        "piece_narration_label": "Texto exacto de la narración de la pieza seleccionada",
        "narration_mode": "Modo de destinos: {mode}.",
        "full_table_one_piece": "La tabla contiene una pieza. Se leerá en el orden mostrado.",
        "full_table_many_pieces": "La tabla contiene {count} piezas. Se leerán en el orden mostrado.",
        "piece_with_destinations": "{color}, {piece} en {square}. Destinos alcanzables: {destinations}.",
        "piece_without_destinations": "{color}, {piece} en {square}. No tiene destinos alcanzables.",
        "play_full_table": "🔊 Reproducir tabla completa",
        "play_one_piece": "🔊 Reproducir destinos de esta pieza",
        "preparing_moves_audio": "Preparando la narración de piezas y destinos…",
        "moves_audio_ready": "Audio preparado. Usa el control para reproducirlo.",
        "moves_audio_error": "No se pudo sintetizar esta narración. El texto exacto permanece disponible.",
        "moves_audio_empty": "No hay una tabla de piezas que se pueda narrar.",
        "tactile_title": "Vista para impresión en relieve",
        "tactile_intro": "Previsualización monocroma de alto contraste con cuadrícula, coordenadas, formas y patrones diferenciados.",
        "tactile_warning": "Es una plantilla o previsualización. El relieve físico requiere papel microcápsula, termoformado o una impresora/embosadora táctil; una impresora convencional no produce relieve.",
        "download_svg": "Descargar SVG para impresión",
        "download_help": "Descarga un SVG generado localmente, sin enviar datos a la red.",
        "svg_title": "Plantilla táctil de posición de ajedrez",
        "svg_desc": "Tablero monocromo con coordenadas. Las piezas blancas usan círculos y las negras rombos; cada tipo tiene letra y patrón propios.",
        "svg_legend": "Leyenda: círculo = blancas · rombo = negras · K rey · Q dama · R torre · B alfil · N caballo · P peón",
        "svg_disclaimer": "Plantilla: el relieve requiere tecnología de impresión táctil especializada.",
        "ready_kicker": "Listo para comenzar",
        "ready_title": "Selecciona un diagrama en el panel lateral",
        "ready_copy": "Sube una imagen propia o abre un ejemplo. Cuando sea válida, el análisis y todos los formatos accesibles aparecerán en esta zona.",
        "output_1": "Salida 01",
        "braille_card": "Notación oficial Unicode legible y preparada para copiar.",
        "output_2": "Salida 02",
        "audio_card_title": "🔊 Audio en español",
        "audio_card": "Descripción textual adaptada con reproducción local.",
        "more_formats": "Más formatos",
        "more_card_title": "♞ Movimiento y tacto",
        "more_card": "Destinos de las piezas y plantilla SVG monocroma para impresión táctil.",
        "tech_kicker": "Tecnología y privacidad",
        "tech_title": "Procesamiento local, experiencia transparente",
        "tech_copy": "La aplicación combina detección de tablero, clasificación dual k-NN y lógica de <strong>python-chess</strong>. Las imágenes se procesan localmente; este flujo no realiza solicitudes de red ni almacena las imágenes de forma permanente.",
        "sponsors": "Patrocinadores",
        "footer_title": "Transcriptor accesible de diagramas de ajedrez",
        "footer_by": "Realizado por <span class=\"footer-highlight\">Francisco Ros Alarcón</span>",
        "footer_meta": "Hackathon 2026 · Construido con Streamlit · Procesamiento local",
    },
    "en": {
        "eyebrow": "♟ Accessible technology · Hackathon 2026",
        "hero_title": "See the board.<br>Hear the position.",
        "hero_subtitle": "Turn chess diagrams into B8 Braille transcriptions, audio descriptions, and tactile views through a clear and accessible experience.",
        "made_by": "Created by Francisco Ros Alarcón",
        "impact_kicker": "Social impact",
        "impact_title": "More accessible chess, more independent study",
        "impact_copy": "A tool that converts visual board information into formats that support access, review, and independent learning of chess positions.",
        "flow_label": "Three-step workflow",
        "upload_short": "Upload",
        "upload_flow": "Choose a PNG or JPG diagram, or use an example.",
        "analyze_short": "Analyze",
        "analyze_flow": "The system detects the style and recognizes all 64 squares.",
        "explore_short": "Explore",
        "explore_flow": "Read B8 Braille, listen to audio, inspect moves, and open the tactile view.",
        "start_here": "Start here",
        "step_1": "Step 1 of 3 · Choose the diagram source",
        "image_source": "Image source",
        "upload_source": "📤 Upload file",
        "gallery_source": "📚 Example gallery",
        "source_help": "Upload a local file or try the experience with an example.",
        "upload_diagram": "Upload a chess diagram",
        "upload_help": "Supported formats: PNG, JPG, and JPEG.",
        "image_ready": "Valid image, ready to analyze.",
        "invalid_image": "The image could not be read. Make sure it is a valid PNG or JPG file.",
        "select_example": "Choose an example",
        "example_help": "Examples let you try the workflow without uploading a file.",
        "example_ready": "{name} is ready to analyze.",
        "example_missing": "The selected example is not currently available.",
        "board_settings": "Board settings",
        "crop_adjustment": "Crop adjustment (pixels)",
        "crop_help": "Adjust the margin if the grid is not correctly bounded.",
        "rotate": "Rotate board 180°",
        "rotate_help": "Manual rotation. It is applied only when automatic orientation is off.",
        "auto_orientation": "Automatic orientation (experimental)",
        "auto_orientation_help": "Tests 0° and 180° with the same pipeline. It is off by default; when enabled, manual rotation is ignored to prevent double rotation.",
        "orientation_selected": "Selected orientation: {orientation}",
        "orientation_normal": "normal (0°)",
        "orientation_rotated": "rotated 180°",
        "prototype_info": "Prototype information",
        "prototype_caption": "Dual k-NN classification · 32 × 32 px grayscale squares · Automatic style detection",
        "privacy_sidebar": "Privacy: the image is processed locally during this session and is not sent to external services.",
        "model_error": "The local models could not be loaded. Make sure the model files are available.",
        "step_2": "Step 2 · Analyze",
        "reading_title": "Diagram reading",
        "reading_copy": "Review the selected image and the summary of the recognized position.",
        "selected_diagram": "Selected diagram",
        "image_preview": "Preview of the image to be analyzed",
        "analysis_summary": "Analysis summary",
        "analyzing": "Analyzing all 64 board squares…",
        "style_detected": "Detected style: {style}",
        "modern_style": "modern color board",
        "scanned_style": "scanned black-and-white board",
        "pieces_metric": "PIECES",
        "white_metric": "WHITE",
        "black_metric": "BLACK",
        "analysis_done": "Analysis complete. The accessible results are ready.",
        "processing_error": "The analysis could not be completed. Check the crop or try another valid image.",
        "step_3": "Step 3 · Read, listen, and print",
        "results_title": "Accessible results",
        "results_copy": "The text remains available even when audio playback is unavailable.",
        "braille_tab": "⠃ B8 Braille",
        "audio_tab": "🔊 English audio",
        "moves_tab": "♞ Pieces and moves",
        "tactile_tab": "◫ Tactile print view",
        "braille_title": "B8 Braille transcription",
        "braille_caption": "Official B8 Unicode format, ready to read, review, and copy. Its official notation is preserved and is not translated.",
        "braille_label": "B8 Braille transcription text",
        "show_braille": "Show Braille text for copying",
        "braille_copy_ready": "Braille text is visible and ready to select and copy.",
        "audio_title": "Adapted audio description",
        "audio_caption": "English text is always available, with optional local playback.",
        "audio_label": "Audio description text",
        "play_audio": "🔊 Play description",
        "preparing_audio": "Preparing English audio…",
        "audio_ready": "Audio is ready. Use the control to play it.",
        "audio_unavailable": "Audio is unavailable; the text description remains visible.",
        "audio_error": "Local audio could not be synthesized on this device.",
        "show_copy": "Show for copying",
        "moves_title": "Pieces and moves",
        "moves_intro": "Each row identifies a detected piece and the destinations it can reach in the recognized position.",
        "conditional_mode": "Conditional legal destinations",
        "conditional_note": "The position contains both kings and passes python-chess validation. Destinations are calculated by assuming that each piece's color is to move. The diagram does not provide turn, castling, or en-passant state, so those special conditions cannot be confirmed.",
        "pseudo_mode": "Geometric or pseudo-legal destinations",
        "pseudo_note": "The recognized position does not support reliable legal-move calculation (it may be incomplete or invalid). These destinations describe piece movement and current occupancy; they must not be interpreted as legal moves.",
        "moves_mode": "Mode: {mode}",
        "color_column": "Color",
        "piece_column": "Piece",
        "square_column": "Square",
        "destinations_column": "Reachable destinations",
        "white": "White",
        "black": "Black",
        "king": "King",
        "queen": "Queen",
        "rook": "Rook",
        "bishop": "Bishop",
        "knight": "Knight",
        "pawn": "Pawn",
        "no_destinations": "None",
        "no_pieces": "No pieces were detected on the board.",
        "moves_error": "Some destinations could not be calculated; the remaining results are still available.",
        "moves_audio_title": "Listen to pieces and destinations",
        "moves_audio_intro": "Choose whether to hear the full table or only one piece and its destinations.",
        "moves_read_option": "Content to narrate",
        "read_full_table": "Read full table",
        "read_one_piece": "Read one piece's destinations",
        "full_narration_label": "Exact text for the full-table narration",
        "piece_selector": "Select a piece by color, type, and square",
        "piece_narration_label": "Exact text for the selected-piece narration",
        "narration_mode": "Destination mode: {mode}.",
        "full_table_one_piece": "The table contains one piece. It will be read in the displayed order.",
        "full_table_many_pieces": "The table contains {count} pieces. They will be read in the displayed order.",
        "piece_with_destinations": "{color} {piece} on {square}. Reachable destinations: {destinations}.",
        "piece_without_destinations": "{color} {piece} on {square}. It has no reachable destinations.",
        "play_full_table": "🔊 Play full table",
        "play_one_piece": "🔊 Play this piece's destinations",
        "preparing_moves_audio": "Preparing the pieces and destinations narration…",
        "moves_audio_ready": "Audio is ready. Use the control to play it.",
        "moves_audio_error": "This narration could not be synthesized. The exact text remains available.",
        "moves_audio_empty": "There is no piece table to narrate.",
        "tactile_title": "Tactile print view",
        "tactile_intro": "High-contrast monochrome preview with a grid, coordinates, shapes, and distinct piece patterns.",
        "tactile_warning": "This is a template or preview. Physical relief requires swell paper, thermoforming, or a tactile printer/embosser; a standard printer does not produce relief.",
        "download_svg": "Download print SVG",
        "download_help": "Download an SVG generated locally without sending data over the network.",
        "svg_title": "Tactile chess-position template",
        "svg_desc": "Monochrome board with coordinates. White pieces use circles and black pieces use diamonds; every type has its own letter and pattern.",
        "svg_legend": "Legend: circle = White · diamond = Black · K king · Q queen · R rook · B bishop · N knight · P pawn",
        "svg_disclaimer": "Template: physical relief requires specialized tactile-printing technology.",
        "ready_kicker": "Ready to begin",
        "ready_title": "Choose a diagram in the sidebar",
        "ready_copy": "Upload your own image or open an example. Once it is valid, the analysis and every accessible format will appear here.",
        "output_1": "Output 01",
        "braille_card": "Readable official Unicode notation, ready to copy.",
        "output_2": "Output 02",
        "audio_card_title": "🔊 English audio",
        "audio_card": "Adapted text description with local playback.",
        "more_formats": "More formats",
        "more_card_title": "♞ Movement and touch",
        "more_card": "Piece destinations and a monochrome SVG template for tactile printing.",
        "tech_kicker": "Technology and privacy",
        "tech_title": "Local processing, transparent experience",
        "tech_copy": "The app combines board detection, dual k-NN classification, and <strong>python-chess</strong> logic. Images are processed locally; this workflow makes no network requests and does not store images permanently.",
        "sponsors": "Sponsors",
        "footer_title": "Accessible chess diagram transcriber",
        "footer_by": "Created by <span class=\"footer-highlight\">Francisco Ros Alarcón</span>",
        "footer_meta": "Hackathon 2026 · Built with Streamlit · Local processing",
    },
}


def tr(key, **kwargs):
    """Return a localized interface string."""
    return TEXT[LANG][key].format(**kwargs)


# ========== ESTILOS CSS PERSONALIZADOS ==========
st.markdown(
    """
<style>
    :root {
        --once-blue: #003b70;
        --once-blue-bright: #0068b5;
        --once-yellow: #ffd24a;
        --ink: #17212b;
        --muted: #52606d;
        --surface: #ffffff;
        --surface-soft: #f4f7fa;
        --border: #d9e2ec;
        --success: #087f5b;
    }
    .stApp { background: #f7f9fc; color: var(--ink); }
    .block-container { max-width: 1180px; padding-top: 1.5rem; padding-bottom: 1rem; }
    .main-header {
        position: relative; overflow: hidden;
        background: linear-gradient(120deg, #002f5d 0%, #005a9c 100%);
        color: #fff; padding: clamp(2rem, 5vw, 3.75rem); border-radius: 24px;
        margin-bottom: 1.25rem; box-shadow: 0 18px 45px rgba(0, 59, 112, 0.16);
    }
    .main-header::after {
        content: "⠿"; position: absolute; right: 2rem; bottom: -3rem;
        color: rgba(255,255,255,.08); font-size: 12rem; line-height: 1; pointer-events: none;
    }
    .eyebrow, .section-kicker {
        color: var(--once-blue-bright); font-size: .78rem; font-weight: 800;
        letter-spacing: .1em; text-transform: uppercase;
    }
    .eyebrow { display: inline-flex; margin: 0 0 1rem; color: var(--once-yellow); }
    .main-title { max-width: 780px; color: #fff; font-size: clamp(2.1rem,5vw,3.7rem); font-weight: 800; letter-spacing: -.035em; line-height: 1.05; margin: 0; }
    .main-subtitle { max-width: 760px; color: #e7f2fb; font-size: clamp(1rem,2vw,1.2rem); line-height: 1.65; margin: 1.25rem 0 0; }
    .hero-credit { display: inline-block; margin-top: 1.35rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,.25); color: #fff; font-size: .92rem; font-weight: 650; }
    .section-intro { margin: 1.5rem 0 .8rem; }
    .section-title { color: var(--ink); font-size: clamp(1.45rem,3vw,2rem); line-height: 1.2; margin: .3rem 0 .35rem; }
    .section-copy { max-width: 800px; color: var(--muted); line-height: 1.65; margin: 0; }
    .flow-grid { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: .85rem; margin: 1rem 0 1.75rem; }
    .flow-step, .content-box, .trust-card {
        background: var(--surface); border: 1px solid var(--border); border-radius: 16px;
        padding: 1.25rem; box-shadow: 0 8px 24px rgba(31,45,61,.05);
    }
    .flow-number { display: inline-grid; place-items: center; width: 2rem; height: 2rem; margin-bottom: .75rem; border-radius: 50%; background: #e8f3fb; color: var(--once-blue); font-weight: 800; }
    .flow-step strong { display: block; color: var(--ink); font-size: 1.05rem; margin-bottom: .25rem; }
    .flow-step p, .content-box p, .trust-card p { color: var(--muted); line-height: 1.55; margin: 0; }
    .status-banner { display: flex; align-items: center; gap: .65rem; background: #eaf7f1; color: #075c43; border: 1px solid #a9dfca; border-radius: 12px; padding: .8rem 1rem; margin: .25rem 0 1rem; font-weight: 700; }
    .style-badge { display: inline-flex; align-items: center; gap: .4rem; padding: .45rem .8rem; border: 1px solid transparent; border-radius: 999px; font-size: .82rem; font-weight: 750; }
    .style-moderno { background: #eaf7f1; border-color: #a9dfca; color: #075c43; }
    .style-escaneado { background: #fff4dc; border-color: #f0cc7d; color: #704b00; }
    .metric-card { min-height: 112px; display: grid; place-content: center; background: var(--surface); border: 1px solid var(--border); border-top: 4px solid var(--once-blue-bright); border-radius: 14px; padding: 1rem; text-align: center; box-shadow: 0 8px 20px rgba(31,45,61,.05); }
    .metric-value { color: var(--once-blue); font-size: 2rem; font-weight: 800; line-height: 1; }
    .metric-label { color: var(--muted); font-size: .78rem; font-weight: 750; letter-spacing: .04em; margin-top: .55rem; }
    .stButton > button, .stDownloadButton > button { min-height: 2.8rem; background: var(--once-blue); color: #fff; border: 1px solid var(--once-blue); border-radius: 10px; font-weight: 700; box-shadow: none; transition: background-color 160ms ease,border-color 160ms ease,transform 160ms ease; }
    .stButton > button:hover, .stDownloadButton > button:hover { background: #002c55; border-color: #002c55; color: #fff; transform: translateY(-1px); }
    .stButton > button:focus-visible, .stDownloadButton > button:focus-visible, input:focus-visible, textarea:focus-visible, [role="tab"]:focus-visible, [role="combobox"]:focus-visible { outline: 3px solid #005a9c !important; outline-offset: 2px; box-shadow: 0 0 0 2px var(--once-yellow) !important; }
    .stTextArea textarea { background: #fff; color: var(--ink); border: 1px solid #8ba1b3; border-radius: 10px; font-family: Consolas,"Courier New",monospace; font-size: 1rem; line-height: 1.55; }
    [data-testid="stFileUploader"] { background: #fff; border: 1px dashed #6d879d; border-radius: 12px; padding: .4rem; }
    [data-testid="stImage"] img { border-radius: 14px; border: 1px solid var(--border); }
    .tactile-preview { background: #fff; color: #000; border: 3px solid #000; border-radius: 10px; padding: 1rem; margin: .75rem 0 1rem; box-shadow: 7px 7px 0 #c6c6c6; }
    .tactile-preview h3 { color: #000; margin-top: 0; }
    .tactile-preview p { color: #111; line-height: 1.5; }
    .tactile-preview svg { display: block; width: min(100%,760px); height: auto; margin: 1rem auto 0; background: #fff; }
    .trust-card { margin: 1.5rem 0; border-left: 5px solid var(--once-blue-bright); }
    .sponsor-section { text-align: center; background: #edf3f8; border: 1px solid var(--border); border-radius: 18px; padding: 1.5rem; margin-top: 2rem; }
    .sponsor-label { color: var(--muted); font-size: .76rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; margin-bottom: .8rem; }
    .sponsor-list { display: flex; flex-wrap: wrap; justify-content: center; gap: .55rem; }
    .sponsor-badge { background: #fff; color: var(--once-blue); border: 1px solid #9fb5c7; border-radius: 999px; padding: .5rem .95rem; font-weight: 750; }
    .footer { text-align: center; color: var(--muted); border-top: 1px solid var(--border); padding: 1.6rem 1rem .5rem; margin-top: 1.5rem; }
    .footer-title { color: var(--ink); font-weight: 800; margin: 0 0 .3rem; }
    .footer-text { font-size: .9rem; line-height: 1.55; margin: .2rem 0; }
    .footer-highlight { color: var(--once-blue); font-weight: 750; }
    @media (max-width:760px) { .block-container { padding-top:.75rem; } .main-header { border-radius:16px; } .main-header::after { display:none; } .flow-grid { grid-template-columns:1fr; } }
    @media (prefers-reduced-motion:reduce) { *,*::before,*::after { scroll-behavior:auto !important; transition-duration:.01ms !important; animation-duration:.01ms !important; animation-iteration-count:1 !important; } }
    @media print {
        @page { size: landscape; margin: 10mm; }
        body * { visibility: hidden !important; }
        .tactile-preview, .tactile-preview * { visibility: visible !important; }
        .tactile-preview { position: absolute; inset: 0 auto auto 0; width: 100%; border: 0; box-shadow: none; padding: 0; }
        .tactile-preview svg { width: 185mm; max-height: 175mm; filter: grayscale(1) contrast(2); }
    }
</style>
""",
    unsafe_allow_html=True,
)


# ========== CABECERA ==========
st.markdown(
    f"""
<header class="main-header" role="banner">
    <p class="eyebrow">{tr('eyebrow')}</p>
    <h1 class="main-title">{tr('hero_title')}</h1>
    <p class="main-subtitle">{tr('hero_subtitle')}</p>
    <p class="hero-credit">{tr('made_by')}</p>
</header>
<section aria-labelledby="impact-title" class="section-intro">
    <span class="section-kicker">{tr('impact_kicker')}</span>
    <h2 class="section-title" id="impact-title">{tr('impact_title')}</h2>
    <p class="section-copy">{tr('impact_copy')}</p>
</section>
<div class="flow-grid" aria-label="{tr('flow_label')}">
    <div class="flow-step"><span class="flow-number" aria-hidden="true">1</span><strong>{tr('upload_short')}</strong><p>{tr('upload_flow')}</p></div>
    <div class="flow-step"><span class="flow-number" aria-hidden="true">2</span><strong>{tr('analyze_short')}</strong><p>{tr('analyze_flow')}</p></div>
    <div class="flow-step"><span class="flow-number" aria-hidden="true">3</span><strong>{tr('explore_short')}</strong><p>{tr('explore_flow')}</p></div>
</div>
""",
    unsafe_allow_html=True,
)


# ========== CARGA DE MODELOS Y FUNCIONES CORE ==========
@st.cache_resource
def load_models():
    """Load the existing local classifiers without training or network access."""
    with open("knn_moderno.pkl", "rb") as modern_file:
        modern_model = pickle.load(modern_file)
    with open("knn_escaneado.pkl", "rb") as scanned_file:
        scanned_model = pickle.load(scanned_file)
    return modern_model, scanned_model


try:
    knn_moderno, knn_escaneado = load_models()
    model_load_error = False
except (OSError, pickle.PickleError, EOFError, AttributeError, ValueError):
    knn_moderno, knn_escaneado = None, None
    model_load_error = True


def detect_style(img):
    array = np.array(img.convert("RGB"))
    color_matches = _near(array, LIGHT) | _near(array, DARK)
    return "moderno" if color_matches.mean() > 0.25 else "escaneado"


def classify_with_knn(squares, style):
    """Preserve the existing 32x32 grayscale /255 k-NN input pipeline."""
    if len(squares) != 64:
        raise ValueError("Expected 64 square crops")
    knn = knn_moderno if style == "moderno" else knn_escaneado
    if knn is None:
        raise RuntimeError("Local classifier unavailable")
    batch = []
    for square_image in squares:
        gray = np.array(square_image.convert("L"), dtype=np.float32)
        batch.append(gray.flatten() / 255.0)
    return knn.predict(np.array(batch))


def orientation_score(classifications, rotation_degrees):
    """Rank orientation candidates, preserving 0° as the final stable tie-break."""
    extreme_pawns = sum(
        str(classification) in {"wP", "bP"} and index // 8 in {0, 7}
        for index, classification in enumerate(classifications)
    )
    piece_count = sum(str(classification) != "empty" for classification in classifications)
    return (
        extreme_pawns == 0,
        -extreme_pawns,
        piece_count,
        rotation_degrees == 0,
    )


def analyze_board_orientation(img, margen=0, automatic=False):
    """Run the existing detector and classifier at 0° and, optionally, 180°."""
    candidates = []
    for rotation_degrees in ((0, 180) if automatic else (0,)):
        oriented_image = img if rotation_degrees == 0 else img.rotate(180)
        style = detect_style(oriented_image)
        squares = recortar_casillas(
            oriented_image, tam=32, margen=margen, recorte_interior=0.06
        )
        classifications = classify_with_knn(squares, style)
        candidates.append(
            {
                "rotation": rotation_degrees,
                "image": oriented_image,
                "style": style,
                "classifications": classifications,
                "score": orientation_score(classifications, rotation_degrees),
            }
        )
    return max(candidates, key=lambda candidate: candidate["score"])


def to_fen(classifications):
    """Convert recognized labels to a python-chess board FEN safely."""
    board = chess.Board(None)
    valid_symbols = set("pnbrqk")
    for index, classification in enumerate(classifications):
        class_name = str(classification)
        if class_name == "empty" or len(class_name) != 2:
            continue
        color_code, symbol = class_name[0], class_name[1]
        if color_code not in {"w", "b"} or symbol.lower() not in valid_symbols:
            continue
        fen_row, fen_column = divmod(index, 8)
        square_index = (7 - fen_row) * 8 + fen_column
        piece_symbol = symbol.upper() if color_code == "w" else symbol.lower()
        board.set_piece_at(square_index, chess.Piece.from_symbol(piece_symbol))
    return board.fen()


def format_english_audio(board):
    """Create a localized English counterpart while preserving AudioFormatter for Spanish."""
    names = {
        chess.KING: ("King", "Kings"),
        chess.QUEEN: ("Queen", "Queens"),
        chess.ROOK: ("Rook", "Rooks"),
        chess.BISHOP: ("Bishop", "Bishops"),
        chess.KNIGHT: ("Knight", "Knights"),
        chess.PAWN: ("Pawn", "Pawns"),
    }
    order = [chess.KING, chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]

    def square_list(squares):
        labels = [chess.square_name(square).upper() for square in squares]
        if len(labels) == 1:
            return labels[0]
        if len(labels) == 2:
            return f"{labels[0]} and {labels[1]}"
        return ", ".join(labels[:-1]) + f", and {labels[-1]}"

    lines = []
    for color, color_name in ((chess.WHITE, "White"), (chess.BLACK, "Black")):
        groups = []
        for piece_type in order:
            squares = sorted(
                board.pieces(piece_type, color),
                key=lambda square: (chess.square_file(square), chess.square_rank(square)),
            )
            if squares:
                singular, plural = names[piece_type]
                piece_name = singular if len(squares) == 1 else plural
                groups.append(f"{piece_name} on {square_list(squares)}")
        description = ", ".join(groups) + "." if groups else "No pieces."
        lines.append(f"{color_name}: {description}")
    return "\n".join(lines)


def synthesize_audio(text, language):
    """Synthesize speech locally and prefer a voice matching the selected language."""
    temp_path = None
    engine = None
    try:
        import pyttsx3

        engine = pyttsx3.init()
        voice_markers = {
            "es": ("spanish", "español", "es-es", "es_mx", "helena", "sabina", "pablo"),
            "en": ("english", "en-us", "en-gb", "zira", "david", "hazel", "mark"),
        }
        for voice in engine.getProperty("voices"):
            language_values = getattr(voice, "languages", []) or []
            searchable = " ".join(
                [str(getattr(voice, "name", "")), str(getattr(voice, "id", ""))]
                + [str(value) for value in language_values]
            ).lower()
            if any(marker in searchable for marker in voice_markers[language]):
                engine.setProperty("voice", voice.id)
                break
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 1.0)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_path = temp_file.name
        engine.save_to_file(text, temp_path)
        engine.runAndWait()
        with open(temp_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        if not audio_bytes:
            raise OSError("Empty local audio output")
        return audio_bytes, "wav"
    except Exception:
        return None, None
    finally:
        if engine is not None:
            try:
                engine.stop()
            except Exception:
                pass
        if temp_path:
            try:
                os.unlink(temp_path)
            except OSError:
                pass


PIECE_KEYS = {
    chess.KING: "king",
    chess.QUEEN: "queen",
    chess.ROOK: "rook",
    chess.BISHOP: "bishop",
    chess.KNIGHT: "knight",
    chess.PAWN: "pawn",
}


def has_reliable_piece_placement(board):
    """Check whether python-chess can safely apply king-safety legality rules."""
    try:
        return (
            board.is_valid()
            and len(board.pieces(chess.KING, chess.WHITE)) == 1
            and len(board.pieces(chess.KING, chess.BLACK)) == 1
        )
    except Exception:
        return False


def destinations_for_piece(board, square, reliable):
    """Return conditional legal or pseudo-legal destinations without propagating board errors."""
    piece = board.piece_at(square)
    if piece is None:
        return []
    working_board = board.copy(stack=False)
    working_board.turn = piece.color
    try:
        generator = (
            working_board.generate_legal_moves(from_mask=chess.BB_SQUARES[square])
            if reliable
            else working_board.generate_pseudo_legal_moves(from_mask=chess.BB_SQUARES[square])
        )
        return sorted({move.to_square for move in generator}, key=chess.square_name)
    except Exception:
        try:
            return sorted(
                {
                    target
                    for target in chess.scan_forward(working_board.attacks_mask(square))
                    if not (working_board.piece_at(target) and working_board.color_at(target) == piece.color)
                },
                key=chess.square_name,
            )
        except Exception:
            return []


def build_piece_rows(board, language):
    """Build localized rows for every detected piece and its reachable destinations."""
    reliable = has_reliable_piece_placement(board)
    rows = []
    for color in (chess.WHITE, chess.BLACK):
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None or piece.color != color:
                continue
            destinations = destinations_for_piece(board, square, reliable)
            destination_text = ", ".join(chess.square_name(item) for item in destinations)
            rows.append(
                {
                    TEXT[language]["color_column"]: TEXT[language]["white" if color else "black"],
                    TEXT[language]["piece_column"]: TEXT[language][PIECE_KEYS[piece.piece_type]],
                    TEXT[language]["square_column"]: chess.square_name(square),
                    TEXT[language]["destinations_column"]: destination_text or TEXT[language]["no_destinations"],
                }
            )
    return rows, reliable


def format_spoken_list(values, language):
    """Join destination squares naturally for the selected narration language."""
    if len(values) < 2:
        return values[0] if values else ""
    conjunction = "y" if language == "es" else "and"
    if len(values) == 2:
        return f"{values[0]} {conjunction} {values[1]}"
    return f"{', '.join(values[:-1])}, {conjunction} {values[-1]}"


def build_moves_narration(rows, reliable, language, row_index=None):
    """Build the exact localized narration for all rows or one selected piece."""
    localized = TEXT[language]
    mode = localized["conditional_mode" if reliable else "pseudo_mode"]
    sentences = [localized["narration_mode"].format(mode=mode)]

    if row_index is None:
        count = len(rows)
        count_key = "full_table_one_piece" if count == 1 else "full_table_many_pieces"
        sentences.append(localized[count_key].format(count=count))
        narrated_rows = rows
    else:
        narrated_rows = [rows[row_index]]

    for row in narrated_rows:
        destinations = row[localized["destinations_column"]]
        narration_values = {
            "color": row[localized["color_column"]],
            "piece": row[localized["piece_column"]],
            "square": row[localized["square_column"]],
        }
        if destinations == localized["no_destinations"]:
            sentences.append(localized["piece_without_destinations"].format(**narration_values))
        else:
            narration_values["destinations"] = format_spoken_list(
                [value.strip() for value in destinations.split(",")], language
            )
            sentences.append(localized["piece_with_destinations"].format(**narration_values))

    return " ".join(sentences)


def build_tactile_svg(board, language):
    """Generate a local, monochrome SVG suitable as a tactile-printing template."""
    localized = TEXT[language]
    cell = 75
    board_x, board_y = 80, 55
    board_size = cell * 8
    pattern_ids = {
        chess.KING: "kingPattern",
        chess.QUEEN: "queenPattern",
        chess.ROOK: "rookPattern",
        chess.BISHOP: "bishopPattern",
        chess.KNIGHT: "knightPattern",
        chess.PAWN: "pawnPattern",
    }
    piece_letters = {
        chess.KING: "K", chess.QUEEN: "Q", chess.ROOK: "R",
        chess.BISHOP: "B", chess.KNIGHT: "N", chess.PAWN: "P",
    }
    title = html.escape(localized["svg_title"])
    description = html.escape(localized["svg_desc"])
    legend = html.escape(localized["svg_legend"])
    disclaimer = html.escape(localized["svg_disclaimer"])
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 800" role="img" aria-labelledby="svgTitle svgDesc">',
        f'<title id="svgTitle">{title}</title><desc id="svgDesc">{description}</desc>',
        """<defs>
        <pattern id="kingPattern" width="14" height="14" patternUnits="userSpaceOnUse"><path d="M7 0v14M0 7h14" stroke="#000" stroke-width="2"/></pattern>
        <pattern id="queenPattern" width="12" height="12" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.8" fill="#000"/><circle cx="9" cy="9" r="1.8" fill="#000"/></pattern>
        <pattern id="rookPattern" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M2 0v10M7 0v10" stroke="#000" stroke-width="2"/></pattern>
        <pattern id="bishopPattern" width="12" height="12" patternUnits="userSpaceOnUse"><path d="M-3 12L12-3M3 15L15 3" stroke="#000" stroke-width="2"/></pattern>
        <pattern id="knightPattern" width="12" height="12" patternUnits="userSpaceOnUse"><path d="M0 0l12 12M12 0L0 12" stroke="#000" stroke-width="1.5"/></pattern>
        <pattern id="pawnPattern" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M0 3h10M0 8h10" stroke="#000" stroke-width="2"/></pattern>
        </defs>""",
        '<rect x="0" y="0" width="760" height="800" fill="#fff"/>',
    ]
    for rank_from_top in range(8):
        for file_index in range(8):
            x = board_x + file_index * cell
            y = board_y + rank_from_top * cell
            fill = "#fff" if (rank_from_top + file_index) % 2 == 0 else "#d8d8d8"
            svg.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{fill}" stroke="#000" stroke-width="2"/>')
    for index in range(8):
        file_label = chr(ord("a") + index)
        rank_label = str(8 - index)
        center_x = board_x + index * cell + cell / 2
        center_y = board_y + index * cell + cell / 2 + 7
        svg.extend(
            [
                f'<text x="{center_x}" y="35" text-anchor="middle" font-family="Arial,sans-serif" font-size="20" font-weight="700">{file_label}</text>',
                f'<text x="{center_x}" y="685" text-anchor="middle" font-family="Arial,sans-serif" font-size="20" font-weight="700">{file_label}</text>',
                f'<text x="55" y="{center_y}" text-anchor="middle" font-family="Arial,sans-serif" font-size="20" font-weight="700">{rank_label}</text>',
                f'<text x="705" y="{center_y}" text-anchor="middle" font-family="Arial,sans-serif" font-size="20" font-weight="700">{rank_label}</text>',
            ]
        )
    for square, piece in board.piece_map().items():
        file_index = chess.square_file(square)
        rank_index = chess.square_rank(square)
        cx = board_x + file_index * cell + cell / 2
        cy = board_y + (7 - rank_index) * cell + cell / 2
        pattern = pattern_ids[piece.piece_type]
        letter = piece_letters[piece.piece_type]
        if piece.color == chess.WHITE:
            svg.append(f'<circle cx="{cx}" cy="{cy}" r="27" fill="url(#{pattern})" stroke="#000" stroke-width="4"/>')
        else:
            points = f"{cx},{cy-31} {cx+31},{cy} {cx},{cy+31} {cx-31},{cy}"
            svg.append(f'<polygon points="{points}" fill="url(#{pattern})" stroke="#000" stroke-width="5"/>')
        svg.append(f'<rect x="{cx-13}" y="{cy-17}" width="26" height="25" rx="3" fill="#fff" stroke="#000" stroke-width="1"/>')
        svg.append(f'<text x="{cx}" y="{cy+4}" text-anchor="middle" font-family="Arial,sans-serif" font-size="23" font-weight="900" fill="#000">{letter}</text>')
    svg.extend(
        [
            f'<text x="380" y="725" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700">{legend}</text>',
            f'<text x="380" y="755" text-anchor="middle" font-family="Arial,sans-serif" font-size="13">{disclaimer}</text>',
            '<rect x="77" y="52" width="606" height="606" fill="none" stroke="#000" stroke-width="5"/>',
            "</svg>",
        ]
    )
    return "".join(svg)


# ========== PANEL DE ENTRADA ==========
with st.sidebar:
    st.markdown(f"## {tr('start_here')}")
    st.caption(tr("step_1"))
    source_options = [tr("upload_source"), tr("gallery_source")]
    source = st.radio(tr("image_source"), source_options, help=tr("source_help"))
    img = None
    if source == source_options[0]:
        uploaded_file = st.file_uploader(
            tr("upload_diagram"), type=["png", "jpg", "jpeg"], help=tr("upload_help")
        )
        if uploaded_file:
            try:
                candidate = Image.open(uploaded_file)
                candidate.verify()
                uploaded_file.seek(0)
                img = Image.open(uploaded_file).copy()
                st.success(tr("image_ready"))
            except (OSError, ValueError):
                st.error(tr("invalid_image"))
    else:
        selected = st.selectbox(
            tr("select_example"),
            [
                "tablero1.png", "tablero2.png", "tablero4.png", "tablero5.png",
                "tablero6.png", "diagrama01.png", "diagrama05.png", "diagrama23.png",
            ],
            help=tr("example_help"),
        )
        if selected:
            try:
                img = Image.open(os.path.join("ejemplos", selected)).copy()
                st.success(tr("example_ready", name=selected))
            except OSError:
                st.error(tr("example_missing"))
    st.divider()
    st.markdown(f"### {tr('board_settings')}")
    margen = st.slider(tr("crop_adjustment"), -20, 20, 0, help=tr("crop_help"))
    auto_orientation = st.checkbox(
        tr("auto_orientation"), value=False, help=tr("auto_orientation_help")
    )
    rotate_board = st.checkbox(
        tr("rotate"), help=tr("rotate_help"), disabled=auto_orientation
    )
    manual_rotation = rotate_board and not auto_orientation
    processing_img = img.rotate(180) if img is not None and manual_rotation else img
    st.divider()
    st.markdown(f"### {tr('prototype_info')}")
    st.caption(tr("prototype_caption"))
    st.info(tr("privacy_sidebar"))
    if model_load_error:
        st.error(tr("model_error"))


# ========== CONTENIDO PRINCIPAL ==========
if img is not None:
    st.markdown(
        f"""
<section class="section-intro" aria-labelledby="analysis-title">
    <span class="section-kicker">{tr('step_2')}</span>
    <h2 class="section-title" id="analysis-title">{tr('reading_title')}</h2>
    <p class="section-copy">{tr('reading_copy')}</p>
</section>
""",
        unsafe_allow_html=True,
    )
    image_column, results_column = st.columns([1, 1.5], gap="large")
    analysis_result = None
    with image_column:
        st.markdown(f"### {tr('selected_diagram')}")
        st.image(processing_img, use_container_width=True, caption=tr("image_preview"))
    with results_column:
        st.markdown(f"### {tr('analysis_summary')}")
        if model_load_error:
            st.error(tr("model_error"))
        else:
            try:
                with st.spinner(tr("analyzing")):
                    orientation = analyze_board_orientation(
                        processing_img, margen=margen, automatic=auto_orientation
                    )
                    style = orientation["style"]
                    classifications = orientation["classifications"]
                    orientation_degrees = (
                        orientation["rotation"] if auto_orientation
                        else (180 if manual_rotation else 0)
                    )
                    fen = to_fen(classifications)
                    board = chess.Board(fen)
                    num_white = chess.popcount(board.occupied_co[chess.WHITE])
                    num_black = chess.popcount(board.occupied_co[chess.BLACK])
                    num_pieces = num_white + num_black
                    braille_text = BrailleFormatter().format_position(board)
                    audio_text = (
                        AudioFormatter().format_position(board)
                        if LANG == "es"
                        else format_english_audio(board)
                    )
                    piece_rows, reliable_moves = build_piece_rows(board, LANG)
                    tactile_svg = build_tactile_svg(board, LANG)
                    analysis_result = {
                        "style": style,
                        "orientation": orientation_degrees,
                        "fen": fen,
                        "board": board,
                        "braille": braille_text,
                        "audio": audio_text,
                        "rows": piece_rows,
                        "reliable_moves": reliable_moves,
                        "svg": tactile_svg,
                    }
                badge_class = "style-moderno" if style == "moderno" else "style-escaneado"
                icon = "◉" if style == "moderno" else "▤"
                style_label = tr("modern_style") if style == "moderno" else tr("scanned_style")
                st.markdown(
                    f'<div style="margin-bottom:1rem"><span class="style-badge {badge_class}">{icon} {tr("style_detected", style=style_label)}</span></div>',
                    unsafe_allow_html=True,
                )
                orientation_label = (
                    tr("orientation_normal") if orientation_degrees == 0
                    else tr("orientation_rotated")
                )
                st.caption(tr("orientation_selected", orientation=orientation_label))
                metric_columns = st.columns(3)
                metric_values = (
                    (num_pieces, "♟️", tr("pieces_metric")),
                    (num_white, "○", tr("white_metric")),
                    (num_black, "◆", tr("black_metric")),
                )
                for column, (value, metric_icon, label) in zip(metric_columns, metric_values):
                    with column:
                        st.markdown(
                            f'<div class="metric-card"><div class="metric-value">{value}</div><div class="metric-label">{metric_icon} {label}</div></div>',
                            unsafe_allow_html=True,
                        )
                st.markdown(
                    f'<div class="status-banner" role="status"><span aria-hidden="true">✓</span>{tr("analysis_done")}</div>',
                    unsafe_allow_html=True,
                )
            except Exception:
                st.error(tr("processing_error"))

    if analysis_result is not None:
        st.divider()
        st.markdown(
            f"""
<section class="section-intro" aria-labelledby="results-title">
    <span class="section-kicker">{tr('step_3')}</span>
    <h2 class="section-title" id="results-title">{tr('results_title')}</h2>
    <p class="section-copy">{tr('results_copy')}</p>
</section>
""",
            unsafe_allow_html=True,
        )
        tab_braille, tab_audio, tab_moves, tab_tactile = st.tabs(
            [tr("braille_tab"), tr("audio_tab"), tr("moves_tab"), tr("tactile_tab")]
        )
        with tab_braille:
            st.markdown(f"### {tr('braille_title')}")
            st.caption(tr("braille_caption"))
            st.text_area(
                tr("braille_label"), analysis_result["braille"], height=150,
                label_visibility="visible", key=f"braille_{LANG}",
            )
            if st.button(tr("show_braille"), use_container_width=True, key=f"copy_braille_{LANG}"):
                st.code(analysis_result["braille"], language=None)
                st.success(tr("braille_copy_ready"))
        with tab_audio:
            st.markdown(f"### {tr('audio_title')}")
            st.caption(tr("audio_caption"))
            st.text_area(
                tr("audio_label"), analysis_result["audio"], height=170,
                label_visibility="visible", key=f"audio_{LANG}",
            )
            st.divider()
            audio_column, copy_column = st.columns([3, 1])
            with audio_column:
                if st.button(tr("play_audio"), use_container_width=True, type="primary", key=f"play_{LANG}"):
                    with st.spinner(tr("preparing_audio")):
                        audio_bytes, audio_format = synthesize_audio(analysis_result["audio"], LANG)
                    if audio_bytes:
                        st.audio(audio_bytes, format=f"audio/{audio_format}")
                        st.success(tr("audio_ready"))
                    else:
                        st.warning(tr("audio_unavailable"))
            with copy_column:
                if st.button(tr("show_copy"), use_container_width=True, key=f"copy_audio_{LANG}"):
                    st.code(analysis_result["audio"], language=None)
        with tab_moves:
            st.markdown(f"### {tr('moves_title')}")
            st.write(tr("moves_intro"))
            if analysis_result["reliable_moves"]:
                st.success(tr("moves_mode", mode=tr("conditional_mode")))
                st.caption(tr("conditional_note"))
            else:
                st.warning(tr("moves_mode", mode=tr("pseudo_mode")))
                st.caption(tr("pseudo_note"))
            if analysis_result["rows"]:
                rows = analysis_result["rows"]
                st.dataframe(rows, use_container_width=True, hide_index=True)
                st.divider()
                st.markdown(f"#### {tr('moves_audio_title')}")
                st.write(tr("moves_audio_intro"))
                narration_choice = st.radio(
                    tr("moves_read_option"),
                    options=[tr("read_full_table"), tr("read_one_piece")],
                    horizontal=True,
                    key=f"moves_audio_choice_{LANG}",
                )

                if narration_choice == tr("read_full_table"):
                    narration_text = build_moves_narration(
                        rows, analysis_result["reliable_moves"], LANG
                    )
                    st.text_area(
                        tr("full_narration_label"),
                        narration_text,
                        height=180,
                        disabled=True,
                        key=f"moves_full_narration_{LANG}",
                    )
                    if st.button(
                        tr("play_full_table"),
                        use_container_width=True,
                        type="primary",
                        key=f"play_moves_full_{LANG}",
                    ):
                        with st.spinner(tr("preparing_moves_audio")):
                            audio_bytes, audio_format = synthesize_audio(narration_text, LANG)
                        if audio_bytes:
                            st.audio(audio_bytes, format=f"audio/{audio_format}")
                            st.success(tr("moves_audio_ready"))
                        else:
                            st.warning(tr("moves_audio_error"))
                else:
                    localized = TEXT[LANG]
                    piece_labels = [
                        " · ".join(
                            (
                                row[localized["color_column"]],
                                row[localized["piece_column"]],
                                row[localized["square_column"]],
                            )
                        )
                        for row in rows
                    ]
                    selected_piece = st.selectbox(
                        tr("piece_selector"),
                        options=piece_labels,
                        key=f"moves_piece_selector_{LANG}",
                    )
                    selected_index = piece_labels.index(selected_piece)
                    narration_text = build_moves_narration(
                        rows,
                        analysis_result["reliable_moves"],
                        LANG,
                        row_index=selected_index,
                    )
                    st.text_area(
                        tr("piece_narration_label"),
                        narration_text,
                        height=140,
                        disabled=True,
                        key=f"moves_piece_narration_{LANG}",
                    )
                    if st.button(
                        tr("play_one_piece"),
                        use_container_width=True,
                        type="primary",
                        key=f"play_moves_piece_{LANG}",
                    ):
                        with st.spinner(tr("preparing_moves_audio")):
                            audio_bytes, audio_format = synthesize_audio(narration_text, LANG)
                        if audio_bytes:
                            st.audio(audio_bytes, format=f"audio/{audio_format}")
                            st.success(tr("moves_audio_ready"))
                        else:
                            st.warning(tr("moves_audio_error"))
            else:
                st.info(tr("no_pieces"))
                st.caption(tr("moves_audio_empty"))
        with tab_tactile:
            tactile_markup = f"""
<div class="tactile-preview" role="region" aria-label="{html.escape(tr('tactile_title'))}">
    <h3>{html.escape(tr('tactile_title'))}</h3>
    <p>{html.escape(tr('tactile_intro'))}</p>
    <p><strong>{html.escape(tr('tactile_warning'))}</strong></p>
    {analysis_result['svg']}
</div>
"""
            st.markdown(tactile_markup, unsafe_allow_html=True)
            st.download_button(
                tr("download_svg"),
                data=analysis_result["svg"].encode("utf-8"),
                file_name="vista_tactil_ajedrez.svg" if LANG == "es" else "tactile_chess_view.svg",
                mime="image/svg+xml",
                use_container_width=True,
                help=tr("download_help"),
            )
else:
    st.markdown(
        f"""
<section class="content-box" aria-labelledby="start-title">
    <span class="section-kicker">{tr('ready_kicker')}</span>
    <h2 class="section-title" id="start-title">{tr('ready_title')}</h2>
    <p>{tr('ready_copy')}</p>
</section>
""",
        unsafe_allow_html=True,
    )
    feature_columns = st.columns(3)
    cards = (
        ("output_1", "⠃ Braille B8", "braille_card"),
        ("output_2", "audio_card_title", "audio_card"),
        ("more_formats", "more_card_title", "more_card"),
    )
    for column, (kicker_key, title_value, copy_key) in zip(feature_columns, cards):
        title = title_value if title_value == "⠃ Braille B8" else tr(title_value)
        with column:
            st.markdown(
                f'<div class="content-box"><span class="section-kicker">{tr(kicker_key)}</span><h3>{title}</h3><p>{tr(copy_key)}</p></div>',
                unsafe_allow_html=True,
            )


# ========== CONSULTA TEXTUAL DE LA POSICIÓN ==========
from position_query_audio import prepare_query_audio
from position_query_controller import select_ambiguity, submit_query
from position_query_models import Ambiguity, ParsedQuery, QueryIntent


QUERY_TEXT = {
    "es": {
        "kicker": "Consulta accesible",
        "title": "Consulta la posición",
        "instructions": (
            "Pregunta por una casilla, fila, columna, pieza, color o por el resumen "
            "de la posición reconocida. La consulta usa el tablero actual y no vuelve "
            "a analizar la imagen."
        ),
        "examples_label": "Ejemplos",
        "examples": (
            "«¿Qué hay en e4?», «torres blancas en la columna d» o "
            "«resumen de la posición»."
        ),
        "field": "Escribe tu consulta sobre la posición",
        "placeholder": "Por ejemplo: ¿Qué piezas hay en la fila 4?",
        "send": "Enviar consulta",
        "repeat": "Repetir última consulta",
        "repeat_ready_help": "Vuelve a ejecutar la última consulta sobre el tablero actual.",
        "repeat_empty_help": "Envía una consulta antes de usar la repetición.",
        "audio": "Activar audio para las respuestas",
        "audio_help": (
            "Guarda la preferencia de audio en esta sesión y usa el sintetizador "
            "local solo al enviar, repetir o confirmar una respuesta."
        ),
        "audio_on": "Audio activado para las próximas respuestas.",
        "audio_off": "Audio desactivado; las consultas siguen funcionando por texto.",
        "audio_preparing": "Preparando el audio de la respuesta…",
        "audio_ready": "Audio de la respuesta preparado. Usa el control para reproducirlo.",
        "audio_error": (
            "No se pudo sintetizar el audio local. La respuesta completa permanece visible."
        ),
        "audio_player": "Reproductor de la respuesta de consulta",
        "response": "Respuesta",
        "response_empty": "La respuesta completa aparecerá aquí después de enviar una consulta.",
        "ambiguity_title": "La consulta necesita una selección",
        "ambiguity_status": "Selecciona una interpretación antes de continuar.",
        "ambiguity_selector": "Interpretaciones disponibles",
        "ambiguity_placeholder": "Elige una interpretación",
        "ambiguity_confirm": "Confirmar interpretación",
        "keyboard_help": (
            "Teclado: escribe en el campo y pulsa Intro para enviar; usa Tab para "
            "recorrer repetición, audio y, si aparece, la selección de interpretación."
        ),
        "no_board": (
            "Analiza primero un diagrama. Cuando haya una posición reconocida, "
            "podrás consultarla aquí por texto."
        ),
        "candidate_summary": "Resumen de la posición",
        "candidate_square": "Casilla {value}",
        "candidate_rank": "Fila {value}",
        "candidate_file": "Columna {value}",
        "candidate_board": "Posición completa",
    },
    "en": {
        "kicker": "Accessible query",
        "title": "Ask about the position",
        "instructions": (
            "Ask about a square, rank, file, piece, color, or a summary of the "
            "recognized position. The query uses the current board and does not "
            "analyze the image again."
        ),
        "examples_label": "Examples",
        "examples": (
            "“What is on e4?”, “white rooks on file d”, or “position summary”."
        ),
        "field": "Enter your question about the position",
        "placeholder": "For example: What pieces are on rank 4?",
        "send": "Submit query",
        "repeat": "Repeat last query",
        "repeat_ready_help": "Run the last query again against the current board.",
        "repeat_empty_help": "Submit a query before using repeat.",
        "audio": "Enable audio for responses",
        "audio_help": (
            "Stores the audio preference for this session and uses the local "
            "synthesizer only when submitting, repeating, or confirming a response."
        ),
        "audio_on": "Audio is enabled for upcoming responses.",
        "audio_off": "Audio is disabled; text queries remain available.",
        "audio_preparing": "Preparing response audio…",
        "audio_ready": "Response audio is ready. Use the control to play it.",
        "audio_error": (
            "Local audio could not be synthesized. The complete response remains visible."
        ),
        "audio_player": "Query response audio player",
        "response": "Response",
        "response_empty": "The complete response will appear here after you submit a query.",
        "ambiguity_title": "The query needs a selection",
        "ambiguity_status": "Select one interpretation before continuing.",
        "ambiguity_selector": "Available interpretations",
        "ambiguity_placeholder": "Choose an interpretation",
        "ambiguity_confirm": "Confirm interpretation",
        "keyboard_help": (
            "Keyboard: type in the field and press Enter to submit; use Tab to "
            "reach repeat, audio, and the interpretation selector when present."
        ),
        "no_board": (
            "Analyze a diagram first. Once a position has been recognized, you can "
            "ask about it here using text."
        ),
        "candidate_summary": "Position summary",
        "candidate_square": "Square {value}",
        "candidate_rank": "Rank {value}",
        "candidate_file": "File {value}",
        "candidate_board": "Entire position",
    },
}


def query_tr(key, **kwargs):
    """Return localized copy for the position-query section."""

    return QUERY_TEXT[LANG][key].format(**kwargs)


def describe_query_candidate(candidate: ParsedQuery, language: str) -> str:
    """Build a concise localized label for one ambiguity candidate."""

    localized = QUERY_TEXT[language]
    if candidate.intent == QueryIntent.SUMMARY:
        return localized["candidate_summary"]

    parts = []
    if candidate.square is not None:
        parts.append(
            localized["candidate_square"].format(
                value=chess.square_name(candidate.square)
            )
        )
    if candidate.rank is not None:
        parts.append(localized["candidate_rank"].format(value=candidate.rank + 1))
    if candidate.file is not None:
        parts.append(
            localized["candidate_file"].format(
                value=chess.FILE_NAMES[candidate.file]
            )
        )
    if not parts:
        parts.append(localized["candidate_board"])
    if candidate.color is not None:
        color_key = "white" if candidate.color == chess.WHITE else "black"
        parts.append(TEXT[language][color_key])
    if candidate.piece_type is not None:
        parts.append(TEXT[language][PIECE_KEYS[candidate.piece_type]])
    return " · ".join(parts)


def store_position_query_response(response) -> bool:
    """Keep only the current text and pending ambiguity in session memory."""

    previous_text = st.session_state["position_query_response"]
    st.session_state["position_query_response"] = response.text
    if isinstance(response.outcome, Ambiguity):
        st.session_state["position_query_ambiguity"] = response.outcome
        # A repeated/new ambiguous query must require an explicit fresh choice.
        st.session_state.pop("position_query_candidate", None)
    else:
        st.session_state["position_query_ambiguity"] = None
    return response.text != previous_text


def handle_position_query_response(response) -> bool:
    """Store one explicit response and replace its optional local audio."""

    response_changed = store_position_query_response(response)
    audio_enabled = bool(st.session_state["position_query_audio_enabled"])
    if audio_enabled:
        with st.spinner(query_tr("audio_preparing")):
            presentation = prepare_query_audio(
                response.text, LANG, True, synthesize_audio
            )
    else:
        presentation = prepare_query_audio(
            response.text, LANG, False, synthesize_audio
        )

    if presentation.audio_bytes is not None:
        st.session_state["position_query_audio"] = {
            "bytes": presentation.audio_bytes,
            "format": presentation.audio_format,
        }
    else:
        st.session_state["position_query_audio"] = None
    st.session_state["position_query_audio_failed"] = presentation.failed
    return response_changed


st.session_state.setdefault("position_query_last_query", "")
st.session_state.setdefault("position_query_response", "")
st.session_state.setdefault("position_query_ambiguity", None)
st.session_state.setdefault("position_query_audio_enabled", False)
st.session_state.setdefault("position_query_audio", None)
st.session_state.setdefault("position_query_audio_failed", False)

st.markdown(
    """
<style>
    .query-panel {
        background: var(--surface); border: 1px solid var(--border);
        border-left: 5px solid var(--once-blue-bright); border-radius: 16px;
        padding: 1.25rem; margin: 1.5rem 0 .85rem;
        box-shadow: 0 8px 24px rgba(31,45,61,.05);
    }
    .query-panel p { color: var(--muted); line-height: 1.6; margin-bottom: .35rem; }
    .query-response {
        background: #eef6fc; color: var(--ink); border: 2px solid #8bb9da;
        border-radius: 12px; padding: 1rem 1.1rem; margin-top: 1rem;
    }
    .query-response strong { display: block; color: var(--once-blue); margin-bottom: .35rem; }
    .query-response p { white-space: pre-wrap; margin: 0; line-height: 1.6; }
</style>
""",
    unsafe_allow_html=True,
)

current_analysis = locals().get("analysis_result")
query_board = (
    current_analysis.get("board")
    if isinstance(current_analysis, dict)
    and isinstance(current_analysis.get("board"), chess.Board)
    else None
)

st.markdown(
    f"""
<section class="query-panel" aria-labelledby="position-query-title">
    <span class="section-kicker">{html.escape(query_tr('kicker'))}</span>
    <h2 class="section-title" id="position-query-title">{html.escape(query_tr('title'))}</h2>
    <p>{html.escape(query_tr('instructions'))}</p>
    <p><strong>{html.escape(query_tr('examples_label'))}:</strong> {html.escape(query_tr('examples'))}</p>
</section>
""",
    unsafe_allow_html=True,
)

if query_board is None:
    st.session_state["position_query_audio"] = None
    st.session_state["position_query_audio_failed"] = False
    st.info(query_tr("no_board"), icon="ℹ️")
else:
    response_changed = False
    with st.form("position_query_form", clear_on_submit=False):
        query_text = st.text_input(
            query_tr("field"),
            placeholder=query_tr("placeholder"),
            key="position_query_input",
        )
        submitted = st.form_submit_button(
            query_tr("send"), use_container_width=True, type="primary"
        )

    if submitted:
        st.session_state["position_query_last_query"] = query_text
        response = submit_query(query_board, query_text, LANG)
        response_changed = handle_position_query_response(response)

    last_query = st.session_state["position_query_last_query"]
    repeated = st.button(
        query_tr("repeat"),
        use_container_width=True,
        disabled=not bool(last_query.strip()),
        help=query_tr(
            "repeat_ready_help" if last_query.strip() else "repeat_empty_help"
        ),
        key="position_query_repeat",
    )
    if repeated:
        response = submit_query(query_board, last_query, LANG)
        response_changed = handle_position_query_response(response)

    audio_enabled = st.checkbox(
        query_tr("audio"),
        key="position_query_audio_enabled",
        help=query_tr("audio_help"),
    )
    if not audio_enabled:
        st.session_state["position_query_audio"] = None
        st.session_state["position_query_audio_failed"] = False
    st.caption(query_tr("audio_on" if audio_enabled else "audio_off"))
    st.caption(query_tr("keyboard_help"))

    pending_ambiguity = st.session_state["position_query_ambiguity"]
    if isinstance(pending_ambiguity, Ambiguity):
        st.markdown(f"### {query_tr('ambiguity_title')}")
        st.info(query_tr("ambiguity_status"), icon="↔️")
        selected_candidate = st.selectbox(
            query_tr("ambiguity_selector"),
            options=range(len(pending_ambiguity.candidates)),
            index=None,
            placeholder=query_tr("ambiguity_placeholder"),
            format_func=lambda index: describe_query_candidate(
                pending_ambiguity.candidates[index], LANG
            ),
            key="position_query_candidate",
        )
        confirmed = st.button(
            query_tr("ambiguity_confirm"),
            use_container_width=True,
            disabled=selected_candidate is None,
            key="position_query_confirm",
        )
        if confirmed and selected_candidate is not None:
            response = select_ambiguity(
                query_board,
                pending_ambiguity,
                selected_candidate + 1,
                LANG,
            )
            response_changed = handle_position_query_response(response)

    visible_response = (
        st.session_state["position_query_response"] or query_tr("response_empty")
    )
    response_role = "status" if response_changed else "region"
    live_attribute = ' aria-live="polite" aria-atomic="true"' if response_changed else ""
    st.markdown(
        f"""
<div class="query-response" role="{response_role}" aria-label="{html.escape(query_tr('response'))}"{live_attribute}>
    <strong>{html.escape(query_tr('response'))}</strong>
    <p>{html.escape(visible_response)}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.session_state["position_query_audio_failed"]:
        st.warning(query_tr("audio_error"), icon="⚠️")
    else:
        query_audio = st.session_state["position_query_audio"]
        if query_audio is not None:
            st.success(query_tr("audio_ready"))
            st.caption(query_tr("audio_player"))
            st.audio(
                query_audio["bytes"],
                format=f"audio/{query_audio['format']}",
            )


# ========== TECNOLOGÍA, PRIVACIDAD Y CRÉDITOS ==========
st.markdown(
    f"""
<section class="trust-card" aria-labelledby="technology-title">
    <span class="section-kicker">{tr('tech_kicker')}</span>
    <h2 class="section-title" id="technology-title">{tr('tech_title')}</h2>
    <p>{tr('tech_copy')}</p>
</section>
<section class="sponsor-section" aria-labelledby="sponsors-title">
    <div class="sponsor-label" id="sponsors-title">{tr('sponsors')}</div>
    <div class="sponsor-list">
        <span class="sponsor-badge">AWS</span><span class="sponsor-badge">UCJC</span>
        <span class="sponsor-badge">Kiro</span><span class="sponsor-badge">Capgemini</span>
        <span class="sponsor-badge">ONCE</span>
    </div>
</section>
<footer class="footer">
    <p class="footer-title">{tr('footer_title')}</p>
    <p class="footer-text">{tr('footer_by')}</p>
    <p class="footer-text">{tr('footer_meta')}</p>
</footer>
""",
    unsafe_allow_html=True,
)
