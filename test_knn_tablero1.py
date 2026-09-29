import numpy as np
import pickle
from PIL import Image
from board_processor import recortar_casillas, detect_board
import chess
from formatters import BrailleFormatter

# Load k-NN model
with open('knn_model.pkl', 'rb') as f:
    knn = pickle.load(f)

print('Loaded k-NN model')

# Class mapping
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

print('Testing on tablero1.png...')
img = Image.open('ejemplos/tablero1.png')
squares = recortar_casillas(img, tam=32, margen=0, recorte_interior=0.06)
classifications = classify_with_knn(squares)
fen = to_fen(classifications)
board = chess.Board(fen)

print(f'\nFEN: {fen}')
print(f'\nBoard:\n{board}')

formatter = BrailleFormatter()
result = formatter.format_position(board, {})
print(f'\nBraille transcription:\n{result}')

# Compare with expected
expected_white = 'Re\u2802 Dd\u2802 Ta\u2802 Th\u2802 Cc\u2812 Cf\u2812 Ac\u2832 Ag\u2812 a\u2806 b\u2806 c\u2806 d\u2812 e\u2832 f\u2806 g\u2806 h\u2806'
print(f'\nExpected white pieces:\nBlancas: {expected_white}')

actual_white = result.split('\n')[0].replace('Blancas: ', '')
print(f'\nActual white pieces:\n{actual_white}')

if actual_white == expected_white:
    print('\n SUCCESS: EXACT MATCH!')
else:
    print('\n PARTIAL MATCH - checking differences...')
