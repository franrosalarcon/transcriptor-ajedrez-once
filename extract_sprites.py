"""
Extract piece sprites from reference images.
Handles both modern color boards and scanned B&W diagrams.
"""

import cv2
import numpy as np
from PIL import Image
import os
import chess
from parse_reference import parse_referencia
from typing import Dict, List, Tuple


def detect_board_grid(image_path: str, ground_truth_fen: str) -> Tuple[np.ndarray, List[Tuple[int, int, int, int]]]:
    """
    Detect board boundaries and extract 64 square crops.
    
    Returns:
        - image as numpy array
        - list of 64 (x, y, w, h) tuples for each square (a1 to h8)
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    height, width = img.shape[:2]
    
    # Simple grid-based approach: assume board fills most of image
    # Leave margin for coordinates
    margin_percent = 0.1
    margin_x = int(width * margin_percent)
    margin_y = int(height * margin_percent)
    
    board_width = width - 2 * margin_x
    board_height = height - 2 * margin_y
    
    square_w = board_width // 8
    square_h = board_height // 8
    
    squares = []
    # Generate squares from a1 (bottom-left) to h8 (top-right)
    # But in image coordinates, row 0 is top, so we need to flip
    for rank in range(8):  # 0=rank 1, 7=rank 8
        for file in range(8):  # 0=a, 7=h
            # In image: top row is rank 8, bottom row is rank 1
            img_row = 7 - rank  # Flip: rank 0 (row 1) -> img row 7
            img_col = file
            
            x = margin_x + img_col * square_w
            y = margin_y + img_row * square_h
            
            squares.append((x, y, square_w, square_h))
    
    return img, squares


def extract_piece_sprite(img: np.ndarray, x: int, y: int, w: int, h: int, 
                         piece: chess.Piece) -> np.ndarray:
    """
    Extract and resize a piece sprite from a square.
    Returns 32x32 RGB crop.
    """
    crop = img[y:y+h, x:x+w]
    
    # Resize to 32x32
    crop_resized = cv2.resize(crop, (32, 32), interpolation=cv2.INTER_AREA)
    
    return crop_resized


def extract_all_sprites(image_path: str, ground_truth_fen: str, style: str) -> Dict[str, List[np.ndarray]]:
    """
    Extract all piece sprites from a reference image.
    
    Returns dict: piece_symbol -> list of 32x32 crops
    """
    img, squares = detect_board_grid(image_path, ground_truth_fen)
    board = chess.Board(ground_truth_fen)
    
    sprites = {}
    
    # For each square, extract the piece sprite if present
    for square_idx in range(64):
        piece = board.piece_at(square_idx)
        x, y, w, h = squares[square_idx]
        
        piece_key = piece.symbol() if piece else 'empty'
        
        if piece_key not in sprites:
            sprites[piece_key] = []
        
        crop = extract_piece_sprite(img, x, y, w, h, piece)
        sprites[piece_key].append(crop)
    
    return sprites


def save_sprites(all_sprites: Dict[str, Dict[str, List[np.ndarray]]], output_dir: str = 'sprites'):
    """
    Save extracted sprites organized by style and piece type.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for style, style_sprites in all_sprites.items():
        style_dir = os.path.join(output_dir, style)
        os.makedirs(style_dir, exist_ok=True)
        
        for piece_symbol, crops in style_sprites.items():
            piece_dir = os.path.join(style_dir, piece_symbol)
            os.makedirs(piece_dir, exist_ok=True)
            
            for idx, crop in enumerate(crops):
                filename = os.path.join(piece_dir, f'{piece_symbol}_{idx:03d}.png')
                cv2.imwrite(filename, crop)
    
    print(f"Sprites saved to {output_dir}/")


def main():
    """Extract sprites from all reference images."""
    ground_truth = parse_referencia()
    
    # Organize by style
    all_sprites = {
        'modern': {},
        'scanned': {}
    }
    
    for img_name, data in ground_truth.items():
        img_path = os.path.join('ejemplos', img_name)
        style = data['style']
        fen = data['fen']
        
        print(f"Extracting sprites from {img_name} ({style})...")
        
        try:
            sprites = extract_all_sprites(img_path, fen, style)
            
            # Merge into all_sprites
            for piece_symbol, crops in sprites.items():
                if piece_symbol not in all_sprites[style]:
                    all_sprites[style][piece_symbol] = []
                all_sprites[style][piece_symbol].extend(crops)
            
            print(f"  Extracted {sum(len(crops) for crops in sprites.values())} squares")
        
        except Exception as e:
            print(f"  Error: {e}")
    
    # Summary
    print("\nSprite extraction summary:")
    for style in ['modern', 'scanned']:
        print(f"\n{style.capitalize()} style:")
        for piece_symbol in sorted(all_sprites[style].keys()):
            count = len(all_sprites[style][piece_symbol])
            print(f"  {piece_symbol}: {count} samples")
    
    # Save sprites
    save_sprites(all_sprites)
    
    return all_sprites


if __name__ == '__main__':
    main()
