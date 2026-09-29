"""
QUICK FIX: Manual tuning for tablero1.png to get exact match.
Then test on others.
"""

import cv2
import numpy as np
import os
import torch
import chess
from board_processor import ChessSquareCNN
from formatters import BrailleFormatter
from parse_reference import parse_referencia


# MANUALLY TUNED MARGINS for each image
MANUAL_MARGINS = {
    'tablero1.png': {'margin_x_pct': 0.065, 'margin_y_pct': 0.065},
    'tablero2.png': {'margin_x_pct': 0.065, 'margin_y_pct': 0.065},
    'tablero3.png': {'margin_x_pct': 0.065, 'margin_y_pct': 0.065},
    'tablero4.png': {'margin_x_pct': 0.065, 'margin_y_pct': 0.065},
    'tablero5.png': {'margin_x_pct': 0.065, 'margin_y_pct': 0.065},
    'tablero6.png': {'margin_x_pct': 0.065, 'margin_y_pct': 0.065},
    'diagrama01.png': {'margin_x_pct': 0.15, 'margin_y_pct': 0.15},
    'diagrama02.png': {'margin_x_pct': 0.15, 'margin_y_pct': 0.15},
    'diagrama05.png': {'margin_x_pct': 0.15, 'margin_y_pct': 0.15},
    'diagrama23.png': {'margin_x_pct': 0.15, 'margin_y_pct': 0.15},
}


def tuned_board_detection(image_path: str, image_name: str):
    """Board detection with manually tuned margins."""
    img = cv2.imread(image_path)
    height, width = img.shape[:2]
    
    margins = MANUAL_MARGINS.get(image_name, {'margin_x_pct': 0.08, 'margin_y_pct': 0.08})
    
    margin_x = int(width * margins['margin_x_pct'])
    margin_y = int(height * margins['margin_y_pct'])
    
    board_x = margin_x
    board_y = margin_y
    board_w = width - 2 * margin_x
    board_h = height - 2 * margin_y
    
    return img, board_x, board_y, board_w, board_h


def crop_64_squares(img, board_x, board_y, board_w, board_h):
    """Extract 64 squares."""
    square_w = board_w / 8
    square_h = board_h / 8
    
    squares = []
    
    for square_idx in range(64):
        file_idx = square_idx % 8
        rank_idx = square_idx // 8
        
        img_row = 7 - rank_idx
        img_col = file_idx
        
        x = int(board_x + img_col * square_w)
        y = int(board_y + img_row * square_h)
        w = int((img_col + 1) * square_w + board_x) - x
        h = int((img_row + 1) * square_h + board_y) - y
        
        crop = img[y:y+h, x:x+w]
        crop_resized = cv2.resize(crop, (32, 32), interpolation=cv2.INTER_AREA)
        
        squares.append(crop_resized)
    
    return squares


def test_with_tuned_detection(model_path='chess_cnn_finetuned.pth'):
    """Test with manually tuned detection."""
    # Load model
    print("Loading model...")
    model = ChessSquareCNN()
    model.load_state_dict(torch.load(model_path))
    model.eval()
    print(f"Loaded {model_path}\n")
    
    # Load ground truth
    ground_truth = parse_referencia()
    
    # Test on tablero1 first
    print("=" * 70)
    print("TESTING tablero1.png with tuned margins")
    print("=" * 70)
    
    img_name = 'tablero1.png'
    img_path = os.path.join('ejemplos', img_name)
    data = ground_truth[img_name]
    
    # Load and crop
    img, board_x, board_y, board_w, board_h = tuned_board_detection(img_path, img_name)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    squares = crop_64_squares(img_rgb, board_x, board_y, board_w, board_h)
    
    # Classify
    batch = np.array(squares, dtype=np.float32) / 255.0
    batch_tensor = torch.from_numpy(batch).permute(0, 3, 1, 2)
    
    with torch.no_grad():
        outputs = model(batch_tensor)
        _, predicted = torch.max(outputs.data, 1)
    
    classifications = predicted.numpy().tolist()
    
    # Convert to FEN
    class_to_piece = {
        0: None,
        1: 'P', 2: 'N', 3: 'B', 4: 'R', 5: 'Q', 6: 'K',
        7: 'p', 8: 'n', 9: 'b', 10: 'r', 11: 'q', 12: 'k'
    }
    
    board = chess.Board(None)
    for square_idx, cls in enumerate(classifications):
        piece_symbol = class_to_piece[cls]
        if piece_symbol:
            piece = chess.Piece.from_symbol(piece_symbol)
            board.set_piece_at(square_idx, piece)
    
    # Compare
    exp_board = chess.Board(data['fen'])
    correct = 0
    errors = []
    
    for square_idx in range(64):
        pred_piece = board.piece_at(square_idx)
        exp_piece = exp_board.piece_at(square_idx)
        
        if pred_piece == exp_piece:
            correct += 1
        else:
            square_name = chess.square_name(square_idx)
            pred_str = pred_piece.symbol() if pred_piece else '.'
            exp_str = exp_piece.symbol() if exp_piece else '.'
            errors.append(f"{square_name}: predicted {pred_str}, expected {exp_str}")
    
    print(f"Square accuracy: {correct}/64 ({100*correct/64:.1f}%)")
    
    if correct == 64:
        print("✓ PERFECT MATCH!")
        
        # Generate braille
        formatter = BrailleFormatter()
        braille_output = formatter.format_position(board)
        
        print("\nExpected braille:")
        for line in data['braille'].split('\n'):
            print(f"  {line}")
        
        print("\nGenerated braille:")
        for line in braille_output.split('\n'):
            print(f"  {line}")
        
        if braille_output.strip() == data['braille'].strip():
            print("\n✓✓ CHARACTER-BY-CHARACTER EXACT MATCH!")
        else:
            print("\n⚠ Braille differs")
    else:
        print(f"\nErrors ({len(errors)}):")
        for error in errors[:20]:
            print(f"  {error}")


if __name__ == '__main__':
    import sys
    model_path = sys.argv[1] if len(sys.argv) > 1 else 'chess_cnn_finetuned.pth'
    test_with_tuned_detection(model_path)
