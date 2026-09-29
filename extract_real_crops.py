"""
Extract real 64 crops from each reference image using ground truth.
CRITICAL: EXCLUDE tablero3.png and diagrama02.png (held-out test set)
"""

import cv2
import numpy as np
import os
import chess
from parse_reference import parse_referencia
from typing import Tuple, List


def simple_board_detection(image_path: str, style: str) -> Tuple[int, int, int, int]:
    """
    Simple board detection based on style.
    
    Args:
        image_path: Path to image
        style: 'modern' or 'scanned'
    
    Returns:
        (x, y, width, height) of board region
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    height, width = img.shape[:2]
    
    if style == 'modern':
        # tablero1-6: coordinates overlaid, board fills most of image
        # Leave margin for coordinates
        margin_x = int(width * 0.08)
        margin_y = int(height * 0.08)
        board_x = margin_x
        board_y = margin_y
        board_w = width - 2 * margin_x
        board_h = height - 2 * margin_y
        
    else:  # scanned
        # diagrama: black border outside, figure number outside
        # Crop to inner content (more aggressive margin)
        margin_x = int(width * 0.12)
        margin_y = int(height * 0.12)
        board_x = margin_x
        board_y = margin_y
        board_w = width - 2 * margin_x
        board_h = height - 2 * margin_y
    
    return board_x, board_y, board_w, board_h


def extract_64_crops(image_path: str, style: str, ground_truth_fen: str) -> Tuple[List[np.ndarray], List[int]]:
    """
    Extract 64 square crops and their labels from a reference image.
    
    Args:
        image_path: Path to image
        style: 'modern' or 'scanned'
        ground_truth_fen: FEN string for this position
    
    Returns:
        - List of 64 crops (32x32 RGB numpy arrays)
        - List of 64 labels (0-12 class indices)
    """
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    # Convert BGR to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Detect board
    board_x, board_y, board_w, board_h = simple_board_detection(image_path, style)
    
    # Calculate square dimensions
    square_w = board_w / 8
    square_h = board_h / 8
    
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
    
    # Extract squares in a1-h8 order
    for square_idx in range(64):
        # Calculate file and rank
        file_idx = square_idx % 8  # 0-7 (a-h)
        rank_idx = square_idx // 8  # 0-7 (1-8)
        
        # In image coordinates: rank 8 is at top (row 0), rank 1 is at bottom (row 7)
        img_row = 7 - rank_idx
        img_col = file_idx
        
        # Calculate crop bounds (use float for precision, round at the end)
        x = int(board_x + img_col * square_w)
        y = int(board_y + img_row * square_h)
        w = int((img_col + 1) * square_w + board_x) - x
        h = int((img_row + 1) * square_h + board_y) - y
        
        # Extract crop
        crop = img[y:y+h, x:x+w]
        
        # Resize to 32x32
        crop_resized = cv2.resize(crop, (32, 32), interpolation=cv2.INTER_AREA)
        
        # Get ground truth label
        piece = board.piece_at(square_idx)
        piece_symbol = piece.symbol() if piece else None
        label = piece_to_class[piece_symbol]
        
        crops.append(crop_resized)
        labels.append(label)
    
    return crops, labels


def extract_training_crops():
    """
    Extract real crops from all TRAINING images (exclude held-out test set).
    
    CRITICAL: EXCLUDE tablero3.png and diagrama02.png
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
    
    print("Extracting real crops from training set...")
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
            crops, labels = extract_64_crops(img_path, data['style'], data['fen'])
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
    np.savez_compressed('dataset/real_crops.npz', X=X, y=y)
    print(f"\nSaved to dataset/real_crops.npz")
    print(f"Shape: X={X.shape}, y={y.shape}")
    
    # Class distribution
    print("\nClass distribution:")
    class_names = ['empty', 'wP', 'wN', 'wB', 'wR', 'wQ', 'wK', 'bP', 'bN', 'bB', 'bR', 'bQ', 'bK']
    for i in range(13):
        count = np.sum(y == i)
        print(f"  {i:2d} {class_names[i]:5s}: {count:3d} samples ({100*count/len(y):5.1f}%)")
    
    return X, y


if __name__ == '__main__':
    extract_training_crops()
