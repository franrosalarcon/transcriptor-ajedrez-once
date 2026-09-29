"""
Extract real 64 crops from each reference image using VERIFIED board detection.
This replaces the simple margin-based detection with the verified detect_board()
from deteccion_tablero.py that properly aligns the grid.

CRITICAL: EXCLUDE tablero3.png and diagrama02.png (held-out test set)
"""

import numpy as np
import os
import chess
from PIL import Image
from parse_reference import parse_referencia
from deteccion_tablero import recortar_casillas
from typing import List


def extract_64_crops_verified(image_path: str, ground_truth_fen: str) -> tuple:
    """
    Extract 64 square crops using VERIFIED detection and their labels.
    
    Args:
        image_path: Path to image
        ground_truth_fen: FEN string for this position
    
    Returns:
        - List of 64 crops (32x32 RGB numpy arrays)
        - List of 64 labels (0-12 class indices)
    """
    # Load image with PIL
    img = Image.open(image_path)
    
    # Use VERIFIED detection from deteccion_tablero.py
    # This properly aligns the grid on both modern and scanned boards
    casillas = recortar_casillas(img, tam=32, margen=0, recorte_interior=0.06)
    
    # Load ground truth position
    board = chess.Board(ground_truth_fen)
    
    # Class mapping: piece to class index
    piece_to_class = {
        None: 0,  # empty
        'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6,  # white
        'p': 7, 'n': 8, 'b': 9, 'r': 10, 'q': 11, 'k': 12  # black
    }
    
    crops = []
    labels = []
    
    # casillas is in FEN order: a8, b8, ..., h8, a7, b7, ..., h1
    # chess.Board.piece_at() expects: a1=0, b1=1, ..., h1=7, a2=8, ..., h8=63
    # So we need to convert: casillas[i] -> chess square index
    for i, pil_crop in enumerate(casillas):
        # i=0 is a8 (square 56), i=1 is b8 (square 57), ..., i=63 is h1 (square 7)
        # FEN index to chess square: fila 0->rank 8, fila 7->rank 1
        fen_row = i // 8  # 0-7 (0=rank 8, 7=rank 1)
        fen_col = i % 8   # 0-7 (0=file a, 7=file h)
        chess_rank = 7 - fen_row  # Convert FEN row to chess rank (0-7)
        chess_file = fen_col
        square_idx = chess_rank * 8 + chess_file
        
        # Convert to numpy array (RGB)
        crop_array = np.array(pil_crop, dtype=np.uint8)
        
        # Get ground truth label
        piece = board.piece_at(square_idx)
        piece_symbol = piece.symbol() if piece else None
        label = piece_to_class[piece_symbol]
        
        crops.append(crop_array)
        labels.append(label)
    
    return crops, labels


def extract_training_crops_verified():
    """
    Extract real crops from all TRAINING images using VERIFIED detection.
    
    CRITICAL: EXCLUDE tablero3.png and diagrama02.png (held-out test set)
    """
    # Parse ground truth
    ground_truth = parse_referencia()
    
    # Define TRAINING SET (8 images) - EXCLUDE TEST SET
    training_images = [
        'tablero1.png',
        'tablero2.png',
        # 'tablero3.png',  # HELD OUT FOR TESTING
        'tablero4.png',
        'tablero5.png',
        'tablero6.png',
        'diagrama01.png',
        # 'diagrama02.png',  # HELD OUT FOR TESTING
        'diagrama05.png',
        'diagrama23.png'
    ]
    
    all_crops = []
    all_labels = []
    
    print("Extracting real crops with VERIFIED board detection...")
    print(f"Training on {len(training_images)} images (held out: tablero3.png, diagrama02.png)")
    print()
    
    for img_name in training_images:
        if img_name not in ground_truth:
            print(f"WARNING: {img_name} not in ground truth, skipping")
            continue
        
        img_path = os.path.join('ejemplos', img_name)
        data = ground_truth[img_name]
        
        print(f"Processing {img_name} ({data['style']})...")
        
        try:
            crops, labels = extract_64_crops_verified(img_path, data['fen'])
            all_crops.extend(crops)
            all_labels.extend(labels)
            
            # Count pieces
            label_counts = {}
            for label in labels:
                label_counts[label] = label_counts.get(label, 0) + 1
            
            print(f"  Extracted 64 squares: {label_counts}")
            
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print()
    print(f"Total crops extracted: {len(all_crops)}")
    print(f"Total labels: {len(all_labels)}")
    
    # Convert to numpy arrays
    X = np.array(all_crops, dtype=np.uint8)
    y = np.array(all_labels, dtype=np.int64)
    
    # Save
    os.makedirs('dataset', exist_ok=True)
    np.savez_compressed('dataset/real_crops_verified.npz', X=X, y=y)
    print(f"\nSaved to dataset/real_crops_verified.npz")
    print(f"Shape: X={X.shape}, y={y.shape}")
    
    # Class distribution
    print("\nClass distribution:")
    class_names = ['empty', 'wP', 'wN', 'wB', 'wR', 'wQ', 'wK', 'bP', 'bN', 'bB', 'bR', 'bQ', 'bK']
    for i in range(13):
        count = np.sum(y == i)
        print(f"  {i:2d} {class_names[i]:5s}: {count:3d} samples ({100*count/len(y):5.1f}%)")
    
    return X, y


if __name__ == '__main__':
    extract_training_crops_verified()
