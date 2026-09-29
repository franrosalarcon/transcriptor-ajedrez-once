"""
Board detection, cropping, and square classification.
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple
import chess
from PIL import Image


class ChessSquareCNN(nn.Module):
    """CNN model for square classification (same as in model.py)."""
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.pool1 = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool2 = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 8 * 8, 128)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(128, 13)
    
    def forward(self, x):
        x = self.pool1(F.relu(self.conv1(x)))
        x = self.pool2(F.relu(self.conv2(x)))
        x = x.reshape(-1, 64 * 8 * 8)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x


# Verified board detection from deteccion_tablero.py
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


class BoardProcessor:
    """Detect board, crop squares, and classify positions."""
    
    def __init__(self, model_path: str = 'chess_cnn_best.pth'):
        """Load trained CNN model."""
        self.model = ChessSquareCNN()
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
        
        # Class mapping
        self.class_to_piece = {
            0: None,  # empty
            1: 'P', 2: 'N', 3: 'B', 4: 'R', 5: 'Q', 6: 'K',
            7: 'p', 8: 'n', 9: 'b', 10: 'r', 11: 'q', 12: 'k'
        }
    
    def score_orientation_plausibility(self, classifications: List[int]) -> float:
        """
        Score how plausible a board orientation is.
        
        A valid chess position should have:
        - Exactly 2 kings (one white, one black)
        - No pawns on rank 1 or rank 8
        - Reasonable piece distribution
        
        Returns a score where higher = more plausible
        """
        score = 0.0
        
        # Count pieces
        white_king_count = 0
        black_king_count = 0
        pawns_on_invalid_ranks = 0
        
        for i, cls in enumerate(classifications):
            # Calculate rank (0-7, where 0=rank 1, 7=rank 8 in FEN order)
            fen_row = i // 8  # 0-7 (0=rank 8, 7=rank 1 in FEN)
            chess_rank = 7 - fen_row  # Convert to chess rank (0-7, 0=rank 1)
            
            piece = self.class_to_piece[cls]
            
            if piece == 'K':
                white_king_count += 1
            elif piece == 'k':
                black_king_count += 1
            elif piece == 'P' and chess_rank in [0, 7]:  # Pawn on rank 1 or 8
                pawns_on_invalid_ranks += 1
            elif piece == 'p' and chess_rank in [0, 7]:
                pawns_on_invalid_ranks += 1
        
        # Exactly 2 kings is essential
        if white_king_count == 1 and black_king_count == 1:
            score += 100
        else:
            score -= 50 * abs(white_king_count - 1)
            score -= 50 * abs(black_king_count - 1)
        
        # Penalize pawns on first/last rank (impossible)
        score -= 20 * pawns_on_invalid_ranks
        
        return score
    
    def classify_squares(self, squares: List[Image.Image]) -> List[int]:
        """
        Classify all 64 squares.
        Returns list of class labels.
        """
        # Convert PIL Images to numpy arrays
        batch = []
        for sq in squares:
            arr = np.array(sq, dtype=np.float32) / 255.0
            batch.append(arr)
        
        batch = np.array(batch)
        batch_tensor = torch.from_numpy(batch).permute(0, 3, 1, 2)
        
        # Inference
        with torch.no_grad():
            outputs = self.model(batch_tensor)
            _, predicted = torch.max(outputs.data, 1)
        
        return predicted.numpy().tolist()
    
    def to_fen(self, classifications: List[int]) -> str:
        """
        Convert 64 classifications to FEN string.
        
        classifications: List of 64 class labels in FEN order (a8, b8, ..., h1)
        """
        board = chess.Board(None)  # Empty board
        
        # classifications is in FEN order: a8, b8, ..., h8, a7, ..., h1
        # chess.Board.piece_at() expects: a1=0, b1=1, ..., h8=63
        for i, cls in enumerate(classifications):
            # Convert FEN index to chess square index
            fen_row = i // 8  # 0-7 (0=rank 8, 7=rank 1)
            fen_col = i % 8   # 0-7 (0=file a, 7=file h)
            chess_rank = 7 - fen_row  # Convert to chess rank (0-7)
            chess_file = fen_col
            square_idx = chess_rank * 8 + chess_file
            
            piece_symbol = self.class_to_piece[cls]
            if piece_symbol:
                piece = chess.Piece.from_symbol(piece_symbol)
                board.set_piece_at(square_idx, piece)
        
        return board.fen()
    
    def process_image(self, image_path: str, try_both_orientations: bool = True, 
                     force_rotation: bool = False) -> Tuple[chess.Board, str, bool]:
        """
        Full pipeline: load image -> detect board -> classify -> return Board.
        
        Args:
            image_path: Path to chess diagram image
            try_both_orientations: If True, try both normal and 180° rotation and pick best
            force_rotation: If True, force 180° rotation without scoring
        
        Returns:
            - chess.Board object
            - FEN string
            - bool: True if board was rotated 180°
        """
        # Load image with PIL
        img = Image.open(image_path)
        
        rotated = False
        
        if force_rotation:
            # Force rotation
            img = img.rotate(180)
            rotated = True
            squares = recortar_casillas(img, tam=32, margen=0, recorte_interior=0.06)
            classifications = self.classify_squares(squares)
        
        elif try_both_orientations:
            # Try both orientations and pick the more plausible one
            
            # Normal orientation
            squares_normal = recortar_casillas(img, tam=32, margen=0, recorte_interior=0.06)
            classifications_normal = self.classify_squares(squares_normal)
            score_normal = self.score_orientation_plausibility(classifications_normal)
            
            # Rotated 180°
            img_rotated = img.rotate(180)
            squares_rotated = recortar_casillas(img_rotated, tam=32, margen=0, recorte_interior=0.06)
            classifications_rotated = self.classify_squares(squares_rotated)
            score_rotated = self.score_orientation_plausibility(classifications_rotated)
            
            print(f"Orientation scores: Normal={score_normal:.1f}, Rotated={score_rotated:.1f}")
            
            # Pick best orientation
            if score_rotated > score_normal:
                print("→ Using ROTATED orientation (board is from black's perspective)")
                classifications = classifications_rotated
                rotated = True
            else:
                print("→ Using NORMAL orientation")
                classifications = classifications_normal
                rotated = False
        
        else:
            # Just use normal orientation
            squares = recortar_casillas(img, tam=32, margen=0, recorte_interior=0.06)
            classifications = self.classify_squares(squares)
        
        # Convert to FEN
        fen = self.to_fen(classifications)
        
        # Create Board object
        board = chess.Board(fen)
        
        return board, fen, rotated


def main():
    """Test board processing on a reference image."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python board_processor.py <image_path> [--force-rotate]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    force_rotation = '--force-rotate' in sys.argv
    
    print(f"Processing {image_path}...")
    
    processor = BoardProcessor()
    board, fen, rotated = processor.process_image(image_path, force_rotation=force_rotation)
    
    print(f"\nFEN: {fen}")
    print(f"Rotated: {rotated}")
    print(f"\nBoard:\n{board}")


if __name__ == '__main__':
    main()
