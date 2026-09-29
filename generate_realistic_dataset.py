"""
Generate REALISTIC synthetic training dataset from extracted sprites.

Key improvements:
- Use REAL sprite sizes and backgrounds from actual board images
- Position and scale augmentation
- Brightness/contrast variation
- Small amount of noise
- Combine synthetic data with real crops from crops_corrected/
"""

import numpy as np
import cv2
import os
import random
import chess
from typing import List, Tuple, Dict
from PIL import Image, ImageEnhance


# Board style parameters (measured from actual boards)
MODERN_STYLE = {
    'light_bg': (234, 235, 208),
    'dark_bg': (115, 147, 86),
    'highlight_yellow': (184, 200, 81),
    'square_size': 74,  # Original size before crop
}

SCANNED_STYLE = {
    'light_bg': (255, 255, 255),  # White background
    'dark_bg': (0, 0, 0),  # Will use hatching pattern
    'square_size': 36,
}


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
                    # Load with PIL to preserve transparency if any
                    img = Image.open(img_path).convert('RGB')
                    sprites[style][piece_symbol].append(np.array(img))
    
    print(f"Loaded sprites:")
    for style in sprites:
        for piece in sprites[style]:
            count = len(sprites[style][piece])
            if count > 0:
                print(f"  {style}/{piece}: {count} sprites")
    
    return sprites


def create_hatched_square(size: int = 32) -> np.ndarray:
    """Create a dark square with diagonal hatching pattern (for scanned diagrams)."""
    square = np.ones((size, size, 3), dtype=np.uint8) * 255
    
    # Add diagonal hatching
    for i in range(0, size, 2):
        cv2.line(square, (i, 0), (0, i), (0, 0, 0), 1)
        cv2.line(square, (size-1, i), (i, size-1), (0, 0, 0), 1)
    
    return square


def generate_random_position() -> chess.Board:
    """
    Generate a random valid chess position.
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
    
    # Define piece pool (adjusted probabilities for realistic positions)
    piece_types = [
        (chess.QUEEN, 0.4), (chess.ROOK, 0.5), (chess.BISHOP, 0.5),
        (chess.KNIGHT, 0.6), (chess.PAWN, 0.7)
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


def augment_sprite(sprite: np.ndarray, max_shift: int = 2, max_scale: float = 0.05) -> np.ndarray:
    """
    Apply realistic augmentation to a sprite.
    
    - Position shift: ±max_shift pixels
    - Scale: ±max_scale (e.g., 0.05 = ±5%)
    - Brightness: ±15%
    - Small Gaussian noise
    """
    img = sprite.copy()
    h, w = img.shape[:2]
    
    # Random scale
    if max_scale > 0 and random.random() < 0.5:
        scale_factor = 1.0 + random.uniform(-max_scale, max_scale)
        new_size = int(w * scale_factor), int(h * scale_factor)
        img = cv2.resize(img, new_size, interpolation=cv2.INTER_LINEAR)
        
        # Crop or pad to original size
        if img.shape[0] > h or img.shape[1] > w:
            # Crop
            y_start = (img.shape[0] - h) // 2
            x_start = (img.shape[1] - w) // 2
            img = img[y_start:y_start+h, x_start:x_start+w]
        elif img.shape[0] < h or img.shape[1] < w:
            # Pad
            pad_h = (h - img.shape[0]) // 2
            pad_w = (w - img.shape[1]) // 2
            img = cv2.copyMakeBorder(img, pad_h, h - img.shape[0] - pad_h,
                                    pad_w, w - img.shape[1] - pad_w,
                                    cv2.BORDER_CONSTANT, value=[128, 128, 128])
    
    # Random position shift
    if max_shift > 0 and random.random() < 0.7:
        shift_x = random.randint(-max_shift, max_shift)
        shift_y = random.randint(-max_shift, max_shift)
        M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
        img = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_CONSTANT, 
                            borderValue=(128, 128, 128))
    
    # Random brightness/contrast
    if random.random() < 0.5:
        pil_img = Image.fromarray(img)
        
        # Brightness
        enhancer = ImageEnhance.Brightness(pil_img)
        pil_img = enhancer.enhance(random.uniform(0.85, 1.15))
        
        # Contrast
        if random.random() < 0.3:
            enhancer = ImageEnhance.Contrast(pil_img)
            pil_img = enhancer.enhance(random.uniform(0.9, 1.1))
        
        img = np.array(pil_img)
    
    # Small Gaussian noise
    if random.random() < 0.3:
        noise = np.random.normal(0, 3, img.shape)
        img = np.clip(img + noise, 0, 255).astype(np.uint8)
    
    return img


def create_background_square(style: str, is_dark: bool, size: int = 32) -> np.ndarray:
    """Create a background square (empty square)."""
    if style == 'modern':
        color = MODERN_STYLE['dark_bg'] if is_dark else MODERN_STYLE['light_bg']
        square = np.ones((size, size, 3), dtype=np.uint8) * np.array(color, dtype=np.uint8)
    else:  # scanned
        if is_dark:
            square = create_hatched_square(size)
        else:
            square = np.ones((size, size, 3), dtype=np.uint8) * 255
    
    return square


def composite_square(piece_symbol: str, style: str, is_dark_square: bool, 
                    sprites: Dict[str, List[np.ndarray]], size: int = 32) -> np.ndarray:
    """
    Create a single square image by compositing piece over background.
    
    Note: sprites/modern contains white pieces (P,N,B,R,Q,K)
          sprites/scanned contains black pieces (p,n,b,r,q,k)
          We use both for both colors by mapping appropriately
    """
    # Create background
    bg = create_background_square(style, is_dark_square, size)
    
    # If empty, just return background
    if piece_symbol == 'empty':
        return bg
    
    # Get sprite - try exact match first, then try opposite color from opposite style
    style_sprites = sprites.get(style, {})
    sprite_list = style_sprites.get(piece_symbol, [])
    
    if not sprite_list:
        # Try to find the piece in opposite style
        # If looking for lowercase in modern, check scanned
        # If looking for uppercase in scanned, check modern
        opposite_style = 'scanned' if style == 'modern' else 'modern'
        opposite_sprites = sprites.get(opposite_style, {})
        
        # Try to find matching piece (handle case mismatch)
        for key in opposite_sprites:
            if key.upper() == piece_symbol.upper():
                sprite_list = opposite_sprites[key]
                break
    
    if not sprite_list:
        # Still no sprite found - return background with debug marker
        # In production this shouldn't happen often
        return bg
    
    # Pick random sprite and augment
    sprite = random.choice(sprite_list).copy()
    sprite = augment_sprite(sprite, max_shift=2, max_scale=0.05)
    
    # Composite (simple overlay - sprites are already on correct backgrounds)
    return sprite


def create_synthetic_sample(board: chess.Board, style: str, 
                           sprites: Dict[str, Dict[str, List[np.ndarray]]]) -> Tuple[List[np.ndarray], List[int]]:
    """
    Create 64 square crops and labels from a chess position.
    
    Returns:
        squares: List of 64 np.ndarray images (32x32x3)
        labels: List of 64 class labels
    """
    # Class mapping
    class_map = {
        'empty': 0,
        'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6,
        'p': 7, 'n': 8, 'b': 9, 'r': 10, 'q': 11, 'k': 12
    }
    
    squares = []
    labels = []
    
    # Generate in FEN order (a8, b8, ..., h8, a7, ..., h1)
    for rank in range(7, -1, -1):  # 7 down to 0
        for file in range(8):  # 0 to 7
            square_idx = chess.square(file, rank)
            piece = board.piece_at(square_idx)
            
            # Determine piece symbol
            piece_symbol = piece.symbol() if piece else 'empty'
            
            # Determine if dark square (checkerboard pattern)
            is_dark_square = (rank + file) % 2 == 1
            
            # Create square image
            square_img = composite_square(piece_symbol, style, is_dark_square, sprites)
            
            squares.append(square_img)
            labels.append(class_map[piece_symbol])
    
    return squares, labels


def load_real_crops(crops_dir: str = 'crops_corrected') -> Tuple[np.ndarray, np.ndarray]:
    """
    Load real crops from crops_corrected/ directory.
    
    Filename format: diagrama01_a1_empty.png or tablero1_a2_P.png
    """
    class_map = {
        'empty': 0,
        'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6,
        'p': 7, 'n': 8, 'b': 9, 'r': 10, 'q': 11, 'k': 12
    }
    
    X_list = []
    y_list = []
    
    if not os.path.exists(crops_dir):
        print(f"Warning: {crops_dir} not found, skipping real crops")
        return np.array([]), np.array([])
    
    print(f"Loading real crops from {crops_dir}...")
    
    for filename in os.listdir(crops_dir):
        if not filename.endswith('.png'):
            continue
        
        # Parse filename: diagrama01_a1_empty.png
        parts = filename.replace('.png', '').split('_')
        if len(parts) < 3:
            continue
        
        label_str = parts[2]
        
        # Map label
        if label_str not in class_map:
            continue
        
        label = class_map[label_str]
        
        # Load image
        img_path = os.path.join(crops_dir, filename)
        img = cv2.imread(img_path)
        
        if img is None:
            continue
        
        # Resize to 32x32 if needed
        if img.shape[0] != 32 or img.shape[1] != 32:
            img = cv2.resize(img, (32, 32), interpolation=cv2.INTER_LINEAR)
        
        X_list.append(img)
        y_list.append(label)
    
    X = np.array(X_list, dtype=np.uint8)
    y = np.array(y_list, dtype=np.int64)
    
    print(f"Loaded {len(X)} real crops")
    
    return X, y


def create_dataset(sprites: Dict[str, Dict[str, List[np.ndarray]]], 
                  n_synthetic_per_style: int = 5000,
                  include_real_crops: bool = True) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create combined training dataset.
    
    Returns:
        X: (n_samples, 32, 32, 3) array of square images
        y: (n_samples,) array of class labels
    """
    X_list = []
    y_list = []
    
    # Generate synthetic samples for each style
    for style in ['modern', 'scanned']:
        if style not in sprites or not sprites[style]:
            print(f"Warning: No sprites for {style} style, skipping")
            continue
        
        print(f"\nGenerating {n_synthetic_per_style} synthetic {style} positions...")
        
        for i in range(n_synthetic_per_style):
            if (i + 1) % 500 == 0:
                print(f"  {i+1}/{n_synthetic_per_style}...")
            
            # Generate random position
            board = generate_random_position()
            
            # Create 64 squares
            squares, labels = create_synthetic_sample(board, style, sprites)
            
            X_list.extend(squares)
            y_list.extend(labels)
    
    # Add real crops
    if include_real_crops:
        print("\nAdding real crops...")
        X_real, y_real = load_real_crops()
        
        if len(X_real) > 0:
            X_list.extend(X_real)
            y_list.extend(y_real)
    
    # Convert to arrays
    X = np.array(X_list, dtype=np.uint8)
    y = np.array(y_list, dtype=np.int64)
    
    print(f"\nTotal dataset: {len(X)} samples")
    
    # Print class distribution
    print("\nClass distribution:")
    unique, counts = np.unique(y, return_counts=True)
    class_names = ['empty', 'P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']
    for cls, count in zip(unique, counts):
        print(f"  {class_names[cls]}: {count} ({100*count/len(y):.1f}%)")
    
    return X, y


def save_dataset(X: np.ndarray, y: np.ndarray, filename: str):
    """Save dataset to disk."""
    os.makedirs('dataset', exist_ok=True)
    filepath = os.path.join('dataset', filename)
    np.savez_compressed(filepath, X=X, y=y)
    print(f"\nDataset saved to {filepath}")


def main():
    """Generate realistic synthetic dataset."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate realistic synthetic dataset')
    parser.add_argument('--n-synthetic', type=int, default=5000, 
                       help='Number of synthetic positions per style')
    parser.add_argument('--no-real', action='store_true',
                       help='Exclude real crops from dataset')
    parser.add_argument('--output', type=str, default='combined_realistic.npz',
                       help='Output filename')
    
    args = parser.parse_args()
    
    print("="*60)
    print("REALISTIC SYNTHETIC DATASET GENERATOR")
    print("="*60)
    
    # Load sprites
    print("\nLoading sprites...")
    sprites = load_sprites()
    
    # Generate dataset
    X, y = create_dataset(
        sprites, 
        n_synthetic_per_style=args.n_synthetic,
        include_real_crops=not args.no_real
    )
    
    # Save
    save_dataset(X, y, args.output)
    
    print("\n" + "="*60)
    print("DONE!")
    print("="*60)


if __name__ == '__main__':
    main()
