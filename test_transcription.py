"""
Test transcription on training set and report accuracy.
Focus on getting tablero1.png exact first, then test on others.
"""

import os
import sys
import cv2
import numpy as np
import torch
import chess
from board_processor import ChessSquareCNN
from formatters import BrailleFormatter
from parse_reference import parse_referencia


def simple_board_detection(image_path: str, style: str):
    """Simple board detection (same as extract_real_crops.py)."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    height, width = img.shape[:2]
    
    if style == 'modern':
        # tablero1-6: coordinates overlaid
        margin_x = int(width * 0.08)
        margin_y = int(height * 0.08)
    else:  # scanned
        # diagrama: black border outside
        margin_x = int(width * 0.12)
        margin_y = int(height * 0.12)
    
    board_x = margin_x
    board_y = margin_y
    board_w = width - 2 * margin_x
    board_h = height - 2 * margin_y
    
    return board_x, board_y, board_w, board_h


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


def classify_squares(model, squares):
    """Classify 64 squares."""
    # Prepare batch
    batch = np.array(squares, dtype=np.float32) / 255.0
    batch_tensor = torch.from_numpy(batch).permute(0, 3, 1, 2)
    
    # Inference
    with torch.no_grad():
        outputs = model(batch_tensor)
        _, predicted = torch.max(outputs.data, 1)
    
    return predicted.numpy().tolist()


def predictions_to_fen(classifications):
    """Convert predictions to FEN."""
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
    
    return board.fen()


def transcribe_diagram(image_path, style, model):
    """Full pipeline: image -> FEN -> braille."""
    # Load image
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Detect board
    board_x, board_y, board_w, board_h = simple_board_detection(image_path, style)
    
    # Crop squares
    squares = crop_64_squares(img, board_x, board_y, board_w, board_h)
    
    # Classify
    classifications = classify_squares(model, squares)
    
    # Convert to FEN
    fen = predictions_to_fen(classifications)
    board = chess.Board(fen)
    
    # Format as braille
    formatter = BrailleFormatter()
    braille_output = formatter.format_position(board)
    
    return board, fen, braille_output


def compare_positions(predicted_board, expected_board):
    """Compare two boards square by square."""
    correct = 0
    errors = []
    
    for square_idx in range(64):
        pred_piece = predicted_board.piece_at(square_idx)
        exp_piece = expected_board.piece_at(square_idx)
        
        if pred_piece == exp_piece:
            correct += 1
        else:
            square_name = chess.square_name(square_idx)
            pred_str = pred_piece.symbol() if pred_piece else '.'
            exp_str = exp_piece.symbol() if exp_piece else '.'
            errors.append(f"{square_name}: predicted {pred_str}, expected {exp_str}")
    
    return correct, errors


def test_on_training_set(model_path='chess_cnn_finetuned.pth'):
    """Test on training set images."""
    # Load model
    print("Loading model...")
    model = ChessSquareCNN()
    model.load_state_dict(torch.load(model_path))
    model.eval()
    print(f"Loaded {model_path}")
    print()
    
    # Load ground truth
    ground_truth = parse_referencia()
    
    # Training images (excluding held-out test set)
    training_images = [
        'tablero1.png',
        'tablero2.png',
        'tablero4.png',
        'tablero5.png',
        'tablero6.png',
        'diagrama01.png',
        'diagrama05.png',
        'diagrama23.png'
    ]
    
    total_correct = 0
    total_squares = 0
    perfect_matches = 0
    
    print("=" * 70)
    print("TESTING ON TRAINING SET")
    print("=" * 70)
    print()
    
    for img_name in training_images:
        if img_name not in ground_truth:
            print(f"WARNING: {img_name} not in ground truth, skipping")
            continue
        
        img_path = os.path.join('ejemplos', img_name)
        data = ground_truth[img_name]
        
        print(f"Testing {img_name}...")
        
        try:
            # Transcribe
            pred_board, pred_fen, braille_output = transcribe_diagram(img_path, data['style'], model)
            
            # Compare with expected
            exp_board = chess.Board(data['fen'])
            correct, errors = compare_positions(pred_board, exp_board)
            
            total_correct += correct
            total_squares += 64
            
            accuracy = 100 * correct / 64
            print(f"  Square accuracy: {correct}/64 ({accuracy:.1f}%)")
            
            if correct == 64:
                perfect_matches += 1
                print(f"  ✓ PERFECT MATCH!")
                
                # Show braille output
                if 'braille' in data:
                    print(f"\n  Expected braille:")
                    for line in data['braille'].split('\n'):
                        print(f"    {line}")
                    print(f"\n  Generated braille:")
                    for line in braille_output.split('\n'):
                        print(f"    {line}")
                    
                    # Character comparison
                    if braille_output.strip() == data['braille'].strip():
                        print(f"  ✓✓ CHARACTER-BY-CHARACTER EXACT MATCH!")
                    else:
                        print(f"  ⚠ Braille differs slightly")
            else:
                print(f"  Errors ({len(errors)}):")
                for error in errors[:10]:  # Show first 10
                    print(f"    {error}")
                if len(errors) > 10:
                    print(f"    ... and {len(errors)-10} more")
            
            print()
        
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total square accuracy: {total_correct}/{total_squares} ({100*total_correct/total_squares:.1f}%)")
    print(f"Perfect diagrams: {perfect_matches}/{len(training_images)}")
    print()


if __name__ == '__main__':
    # Test with fine-tuned model
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    else:
        model_path = 'chess_cnn_finetuned.pth'
    
    test_on_training_set(model_path)
