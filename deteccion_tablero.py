"""
Detección de tablero para el reto ONCE.
Verificado sobre los diez diagramas de ejemplos/: la rejilla queda alineada en
los dos estilos (tablero moderno en color y escaneo de libro en blanco y negro).

Sustituye a la detección anterior, que se desviaba media casilla y hacía que
cada recorte contuviera trozos de dos casillas.
"""

from PIL import Image
import numpy as np

# Colores del tablero moderno (medidos en los ejemplos)
LIGHT = (234, 235, 208)
DARK = (115, 147, 86)
HIGHLIGHT_YELLOW = (184, 200, 81)


def _near(arr, color, tol=18):
    return np.abs(arr.astype(int) - np.array(color)).max(2) <= tol


def detect_board(img, margen=0):
    """
    Devuelve (x0, y0, x1, y1): la caja del tablero dentro de la imagen.

    margen: desplazamiento en píxeles aplicado a los cuatro lados. Positivo
            encoge la caja, negativo la agranda. Es lo que conectamos a los
            deslizadores de ajuste manual de la interfaz.
    """
    a = np.array(img.convert("RGB"))

    # ¿Es un tablero moderno en color? Se reconoce por sus dos colores de casilla.
    es_color = _near(a, LIGHT) | _near(a, DARK) | _near(a, HIGHLIGHT_YELLOW)

    if es_color.mean() > 0.25:
        ys, xs = np.where(es_color)
        box = [xs.min(), ys.min(), xs.max() + 1, ys.max() + 1]
    else:
        # Diagrama escaneado: el tablero va dentro de un marco negro. Buscamos
        # las filas y columnas que son casi enteramente oscuras: son el marco.
        oscuro = a.astype(int).sum(2) < 300
        h, w = oscuro.shape
        filas = np.where(oscuro.sum(1) > 0.5 * w)[0]
        cols = np.where(oscuro.sum(0) > 0.5 * h)[0]
        if len(filas) >= 2 and len(cols) >= 2:
            box = [cols.min(), filas.min(), cols.max() + 1, filas.max() + 1]
        else:
            ys, xs = np.where(oscuro)
            box = [xs.min(), ys.min(), xs.max() + 1, ys.max() + 1]

    x0, y0, x1, y1 = box
    return (x0 + margen, y0 + margen, x1 - margen, y1 - margen)


def recortar_casillas(img, tam=32, margen=0, recorte_interior=0.06):
    """
    Devuelve una lista de 64 imágenes de casilla, en orden a8..h8, a7..h7, ... a1..h1
    (el mismo orden de lectura de un FEN).

    recorte_interior: fracción del lado que se descarta en cada borde de la
        casilla. Un 6% quita las líneas de separación y las etiquetas de
        coordenadas sin llegar a cortar las piezas.
    """
    x0, y0, x1, y1 = detect_board(img, margen)
    tablero = img.convert("RGB").crop((x0, y0, x1, y1))
    W, H = tablero.size
    sx, sy = W / 8.0, H / 8.0
    dx, dy = sx * recorte_interior, sy * recorte_interior

    casillas = []
    for fila in range(8):          # fila 0 = rank 8
        for col in range(8):       # col 0 = columna a
            cx0 = col * sx + dx
            cy0 = fila * sy + dy
            cx1 = (col + 1) * sx - dx
            cy1 = (fila + 1) * sy - dy
            c = tablero.crop((int(cx0), int(cy0), int(cx1), int(cy1)))
            casillas.append(c.resize((tam, tam), Image.LANCZOS))
    return casillas


def color_de_casilla(img, idx, margen=0):
    """
    Color de fondo de una casilla: 'clara', 'oscura', 'amarilla' o 'roja'.
    Sirve para transcribir los resaltados sin pasarlos por el modelo.
    """
    x0, y0, x1, y1 = detect_board(img, margen)
    a = np.array(img.convert("RGB").crop((x0, y0, x1, y1)))
    H, W, _ = a.shape
    fila, col = divmod(idx, 8)
    # Muestra una esquina de la casilla, lejos de donde se dibuja la pieza
    py = int(fila * H / 8 + H / 8 * 0.10)
    px = int(col * W / 8 + W / 8 * 0.10)
    p = a[py, px].astype(int)
    r, g, b = p
    if r > 150 and g > 150 and b < 130:
        return "amarilla"
    if r > 140 and g < 110 and b < 110:
        return "roja"
    return "oscura" if p.sum() < 520 else "clara"


if __name__ == "__main__":
    import sys, os
    from PIL import ImageDraw

    carpeta = sys.argv[1] if len(sys.argv) > 1 else "ejemplos"
    for f in sorted(os.listdir(carpeta)):
        if not f.lower().endswith(".png"):
            continue
        im = Image.open(os.path.join(carpeta, f))
        x0, y0, x1, y1 = detect_board(im)
        print(f"{f:18s} caja=({x0},{y0},{x1},{y1})  "
              f"lado={x1-x0}x{y1-y0}  casilla={(x1-x0)/8:.1f}x{(y1-y0)/8:.1f}")

        # Deja una imagen de comprobación con la rejilla dibujada
        vis = im.convert("RGB")
        d = ImageDraw.Draw(vis)
        W, H = x1 - x0, y1 - y0
        d.rectangle([x0, y0, x1 - 1, y1 - 1], outline=(255, 0, 0), width=3)
        for i in range(1, 8):
            d.line([x0 + W * i / 8, y0, x0 + W * i / 8, y1], fill=(255, 0, 255), width=2)
            d.line([x0, y0 + H * i / 8, x1, y0 + H * i / 8], fill=(255, 0, 255), width=2)
        vis.save(f"rejilla_{f}")
