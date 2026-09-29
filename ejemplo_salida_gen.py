from PIL import Image
from board_processor import recortar_casillas
import numpy as np
import pickle
import chess
from formatters import BrailleFormatter, AudioFormatter

with open("knn_model.pkl", "rb") as f:
    knn = pickle.load(f)

class_to_piece = {0: None, 1: "P", 2: "N", 3: "B", 4: "R", 5: "Q", 6: "K", 7: "p", 8: "n", 9: "b", 10: "r", 11: "q", 12: "k"}

def classify_with_knn(squares):
    batch = [np.array(sq, dtype=np.float32).flatten() for sq in squares]
    return knn.predict(np.array(batch)).tolist()

def to_fen(classifications):
    board = chess.Board(None)
    for i, cls in enumerate(classifications):
        square_idx = (7 - i // 8) * 8 + i % 8
        piece_symbol = class_to_piece[cls]
        if piece_symbol:
            board.set_piece_at(square_idx, chess.Piece.from_symbol(piece_symbol))
    return board.fen()

img = Image.open("ejemplos/tablero1.png")
squares = recortar_casillas(img, tam=32, margen=0, recorte_interior=0.06)
classifications = classify_with_knn(squares)
fen = to_fen(classifications)
board = chess.Board(fen)

braille_text = BrailleFormatter().format_position(board, {})
audio_text = AudioFormatter().format_position(board, {})

total_pieces = sum(1 for c in classifications if c != 0)

with open("ejemplo_salida.txt", "w", encoding="utf-8") as f:
    f.write("EJEMPLO DE SALIDA: tablero1.png\n")
    f.write("="*70 + "\n\n")
    f.write("Tipo de diagrama: Tablero moderno en color (verde y crema)\n")
    f.write("Total de piezas: {} piezas\n\n".format(total_pieces))
    f.write("TRANSCRIPCION BRAILLE (Documento Tecnico B8):\n")
    f.write(braille_text + "\n\n")
    f.write("TRANSCRIPCION AUDIO (Libro Adaptado ONCE):\n")
    f.write(audio_text + "\n")

print("Ejemplo guardado en ejemplo_salida.txt")