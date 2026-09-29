"""
Generate synthetic training dataset from extracted sprites.
Creates random valid chess positions and composites boards.
"""

import numpy as np
import cv2
import os
import random
import chess
from typing import List, Tuple, Dict
import pickle


def load_sprites(sprites_dir: str = 'sprites') -> Dict[str, Dict[str, List[np.ndarray]]]:
    """
    Load all extracted sprites organized by style and piece.
    
    Returns: {style: {piece_symbol: [crop1, crop2, ...]}}
    """
    sprites = {'modern': {}, 'scanned': {}}
    
    for style in ['modern', 'scanned']:
        style_dir = os.path.join(sprites_dir, style)
        if not os.path.exists(style_dir):
            continue
        
        for piece_symbol in os.listdir(style_dir):
            piece_dir = os.path.join(style_dir, piece_symbol)
            if not os.path.isdir(piece_dir):
                continue
            
            sprites[style][piece_symbol] = []
            
            for filename in os.listdir(piece_dir):
                if filename.endswith('.png'):
                    img_path = os.path.join(piece_dir, filename)
                    img = cv2.imread(img_path)
                    if img is not None:
                        sprites[style][piece_symbol].append(img)
    
    return sprites


def generate_random_position() -> chess.Board:
    """
    Generate a random valid chess position.
    Uses a simple approach: start from empty board and place pieces randomly.
    """
    board = chess.Board(None)  # Empty board
    
    # Place kings (required)
    white_king_square = random.randint(0, 63)
    board.set_piece_at(white_king_square, chess.Piece(chess.KING, chess.WHITE))
    
    # Black king must not be adjacent
    available_squares = [s for s in range(64) if s != white_king_square 
                        and chess.square_distance(s, white_king_square) > 1]
    black_king_square = random.choice(available_squares)
    board.set_piece_at(black_king_square, chess.Piece(chess.KING, chess.BLACK))
    
    # Randomly place other pieces
    occupied = {white_king_square, black_king_square}
    
    # Define piece pool (fewer pieces for more empty squares)
    piece_types = [
        (chess.QUEEN, 0.3), (chess.ROOK, 0.4), (chess.BISHOP, 0.4),
        (chess.KNIGHT, 0.4), (chess.PAWN, 0.6)
    ]
    
    for piece_type, probability in piece_types:
        for color in [chess.WHITE, chess.BLACK]:
            # Decide how many of this piece to place
            if piece_type == chess.PAWN:
                max_count = 8
            elif piece_type == chess.QUEEN:
                max_count = 1
            else:
                max_count = 2
            
            for _ in range(max_count):
                if random.random() > probability:
                    continue
                
                # Find available square
                available = [s for s in range(64) if s not in occupied]
                if not available:
                    break
                
                # No pawns on first or last rank
                if piece_type == chess.PAWN:
                    available = [s for s in available 
                               if chess.square_rank(s) not in [0, 7]]
                    if not available:
                        continue
                
                square = random.choice(available)
                board.set_piece_at(square, chess.Piece(piece_type, color))
                occupied.add(square)
    
    return board


def composite_board(board: chess.Board, sprites: Dict[str, List[np.ndarray]], 
                   style: str) -> np.ndarray:
    """
    Create a synthetic board image by compositing sprites.
    
    Returns 256x256 RGB image (32x32 per square).
    """
    board_img = np.zeros((256, 256, 3), dtype=np.uint8)
    
    for rank in range(8):
        for file in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            
            # Get sprite
            if piece:
                piece_symbol = piece.symbol()
            else:
                piece_symbol = 'empty'
            
            if piece_symbol not in sprites:
                # Use random empty if piece not available
                piece_symbol = 'empty'
            
            sprite_list = sprites[piece_symbol]
            if not sprite_list:
                # Fallback: create solid color
                sprite = np.full((32, 32, 3), 128, dtype=np.uint8)
            else:
                sprite = random.choice(sprite_list)
            
            # Place sprite in board image
            # Row 0 = rank 0 (bottom), but in image coordinates top is row 0
            img_row = 7 - rank
            img_col = file
            
            y = img_row * 32
            x = img_col * 32
            
            board_img[y:y+32, x:x+32] = sprite
    
    return board_img


def create_dataset(sprites: Dict[str, Dict[str, List[np.ndarray]]], 
                  n_samples: int = 2000, style: str = 'modern') -> Tuple[np.ndarray, np.ndarray]:
    """
    Create training dataset with synthetic boards.
    
    Returns:
        X: (n_samples * 64, 32, 32, 3) array of square images
        y: (n_samples * 64,) array of class labels
    """
    # Class mapping
    class_map = {
        'empty': 0,
        'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6,
        'p': 7, 'n': 8, 'b': 9, 'r': 10, 'q': 11, 'k': 12
    }
    
    X_list = []
    y_list = []
    
    style_sprites = sprites[style]
    
    print(f"Generating {n_samples} synthetic {style} boards...")
    
    for i in range(n_samples):
        if (i + 1) % 100 == 0:
            print(f"  Generated {i+1}/{n_samples} boards")
        
        # Generate random position
        board = generate_random_position()
        
        # Composite board image
        board_img = composite_board(board, style_sprites, style)
        
        # Extract 64 squares with labels
        for square in range(64):
            piece = board.piece_at(square)
            piece_symbol = piece.symbol() if piece else 'empty'
            
            rank = chess.square_rank(square)
            file = chess.square_file(square)
            
            # Extract square crop
            img_row = 7 - rank
            img_col = file
            y_px = img_row * 32
            x_px = img_col * 32
            
            square_img = board_img[y_px:y_px+32, x_px:x_px+32]
            
            X_list.append(square_img)
            y_list.append(class_map[piece_symbol])
    
    X = np.array(X_list, dtype=np.uint8)
    y = np.array(y_list, dtype=np.int64)
    
    print(f"Dataset created: X shape {X.shape}, y shape {y.shape}")
    
    return X, y


def save_dataset(X: np.ndarray, y: np.ndarray, style: str, output_dir: str = 'dataset'):
    """Save dataset to disk."""
    os.makedirs(output_dir, exist_ok=True)
    
    filename = os.path.join(output_dir, f'{style}_dataset.npz')
    np.savez_compressed(filename, X=X, y=y)
    
    print(f"Dataset saved to {filename}")


def main():
    """Generate synthetic datasets for both styles."""
    print("Loading sprites...")
    sprites = load_sprites()
    
    # Generate datasets for both styles
    for style in ['modern', 'scanned']:
        # Use more samples for modern (we have more sprite variety)
        n_samples = 1000 if style == 'modern' else 500
        
        X, y = create_dataset(sprites, n_samples=n_samples, style=style)
        save_dataset(X, y, style)
        
        # Print class distribution
        print(f"\n{style.capitalize()} dataset class distribution:")
        unique, counts = np.unique(y, return_counts=True)
        class_names = ['empty', 'P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']
        for cls, count in zip(unique, counts):
            print(f"  {class_names[cls]}: {count}")
        print()


if __name__ == '__main__':
    main()
