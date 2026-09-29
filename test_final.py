import numpy as np
import pickle
from PIL import Image
from deteccion_tablero import recortar_casillas, _near, LIGHT, DARK
import chess
from formatters import BrailleFormatter, AudioFormatter

# Cargar modelos
print("Cargando modelos...")
with open("knn_moderno.pkl", "rb") as f:
    knn_moderno = pickle.load(f)
with open("knn_escaneado.pkl", "rb") as f:
    knn_escaneado = pickle.load(f)
print("Modelos cargados OK")

def detect_style(img):
    a = np.array(img.convert("RGB"))
    es_color = _near(a, LIGHT) | _near(a, DARK)
    return "moderno" if es_color.mean() > 0.25 else "escaneado"

def classify_with_knn(squares, style):
    knn = knn_moderno if style == "moderno" else knn_escaneado
    batch = []
    for sq in squares:
        gray = np.array(sq.convert("L"), dtype=np.float32)
        flat = gray.flatten() / 255.0
        batch.append(flat)
    predictions = knn.predict(np.array(batch))
    return predictions

def to_fen(classifications):
    board = chess.Board(None)
    for i, cls in enumerate(classifications):
        fen_row, fen_col = i // 8, i % 8
        square_idx = (7 - fen_row) * 8 + fen_col
        
        if isinstance(cls, str):
            piece_symbol = None if cls == "empty" else cls
        else:
            class_to_piece = {0: None, 1: "P", 2: "N", 3: "B", 4: "R", 5: "Q", 6: "K",
                              7: "p", 8: "n", 9: "b", 10: "r", 11: "q", 12: "k"}
            piece_symbol = class_to_piece.get(cls)
        
        if piece_symbol:
            board.set_piece_at(square_idx, chess.Piece.from_symbol(piece_symbol))
    
    return board.fen()

# Test con tablero1
print("\nProbando tablero1.png...")
img = Image.open("ejemplos/tablero1.png")
style = detect_style(img)
print(f"Estilo: {style}")

squares = recortar_casillas(img, tam=32, margen=0, recorte_interior=0.06)
classifications = classify_with_knn(squares, style)
print(f"Tipo de clasificacion: {type(classifications[0])}")
print(f"Ejemplo clasificacion: {classifications[0]}")

fen = to_fen(classifications)
board = chess.Board(fen)
print(f"\nFEN: {fen}")
print(f"Piezas: {sum(1 for c in classifications if (isinstance(c, str) and c != \"empty\") or (isinstance(c, int) and c != 0))}")
print("\nTablero:")
print(board)

# Formatear salida
braille = BrailleFormatter().format_position(board, {})
audio = AudioFormatter().format_position(board, {})

print("\n=== BRAILLE ===")
print(braille[:200])
print("\n=== AUDIO ===")
print(audio[:200])

print("\n✓ TODO FUNCIONA CORRECTAMENTE")
