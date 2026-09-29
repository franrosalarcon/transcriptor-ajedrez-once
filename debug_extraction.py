"""
Debug: Save crops from tablero1.png to verify extraction is correct.
"""

from PIL import Image
import os
from deteccion_tablero import recortar_casillas
from parse_reference import parse_referencia
import chess

# Parse ground truth
ground_truth = parse_referencia()
data = ground_truth['tablero1.png']

# Load image
img = Image.open('ejemplos/tablero1.png')

# Get crops using verified detection
casillas = recortar_casillas(img, tam=32, margen=0, recorte_interior=0.06)

# Load expected board
board = chess.Board(data['fen'])

# Save crops with labels
os.makedirs('debug_crops_tablero1_corrected', exist_ok=True)

piece_to_class = {
    None: 0,  'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6,
    'p': 7, 'n': 8, 'b': 9, 'r': 10, 'q': 11, 'k': 12
}

print("Saving debug crops with corrected indexing...")
print("FEN idx -> Chess Square -> Piece")
print("=" * 50)

for i, pil_crop in enumerate(casillas):
    # Convert FEN index to chess square index
    fen_row = i // 8  # 0-7 (0=rank 8, 7=rank 1)
    fen_col = i % 8   # 0-7 (0=file a, 7=file h)
    chess_rank = 7 - fen_row
    chess_file = fen_col
    square_idx = chess_rank * 8 + chess_file
    
    # Get piece at this square
    piece = board.piece_at(square_idx)
    piece_symbol = piece.symbol() if piece else 'empty'
    
    # Square name
    file_name = chr(ord('a') + chess_file)
    rank_name = chess_rank + 1
    square_name = f"{file_name}{rank_name}"
    
    # Save crop
    filename = f"{square_name}_{piece_symbol}.png"
    pil_crop.save(os.path.join('debug_crops_tablero1_corrected', filename))
    
    if i < 16 or piece_symbol != 'empty':  # Print first 2 rows and all pieces
        print(f"FEN[{i:2d}] -> {square_name} = {piece_symbol:5s}")

print(f"\nSaved 64 crops to debug_crops_tablero1_corrected/")
print("Check that piece names match what you see in the images!")
