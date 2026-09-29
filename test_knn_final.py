import numpy as np
import pickle
from PIL import Image
from board_processor import recortar_casillas
import chess
from formatters import BrailleFormatter

with open('knn_model.pkl', 'rb') as f:
    knn = pickle.load(f)

class_to_piece = {0: None, 1: 'P', 2: 'N', 3: 'B', 4: 'R', 5: 'Q', 6: 'K',
                  7: 'p', 8: 'n', 9: 'b', 10: 'r', 11: 'q', 12: 'k'}

def classify_with_knn(squares):
    batch = []
    for sq in squares:
        arr = np.array(sq, dtype=np.float32)
        batch.append(arr.flatten())
    batch = np.array(batch)
    predictions = knn.predict(batch)
    return predictions.tolist()

def to_fen(classifications):
    board = chess.Board(None)
    for i, cls in enumerate(classifications):
        fen_row = i // 8
        fen_col = i % 8
        chess_rank = 7 - fen_row
        chess_file = fen_col
        square_idx = chess_rank * 8 + chess_file
        piece_symbol = class_to_piece[cls]
        if piece_symbol:
            piece = chess.Piece.from_symbol(piece_symbol)
            board.set_piece_at(square_idx, piece)
    return board.fen()

img = Image.open('ejemplos/tablero1.png')
squares = recortar_casillas(img, tam=32, margen=0, recorte_interior=0.06)
classifications = classify_with_knn(squares)
fen = to_fen(classifications)
board = chess.Board(fen)

print('FEN predicted:', fen)
print('FEN expected: r1bqk2r/ppp2p2/2n2n1p/2b1p1p1/2B1P3/2NP1NB1/PPP2PPP/R2QK2R w - - 0 1')

formatter = BrailleFormatter()
result = formatter.format_position(board, {})

# Save to file to avoid encoding issues
with open('tablero1_result.txt', 'w', encoding='utf-8') as f:
    f.write(result)

print('Braille saved to tablero1_result.txt')

# Count correct squares
expected_fen = 'r1bqk2r/ppp2p2/2n2n1p/2b1p1p1/2B1P3/2NP1NB1/PPP2PPP/R2QK2R'
pred_pos = fen.split()[0]
exp_pos = expected_fen.split()[0]

correct = sum(1 for p, e in zip(pred_pos, exp_pos) if p == e)
total = len(exp_pos)
print(f'Square accuracy: {correct}/{total} = {100*correct/total:.1f}%')
