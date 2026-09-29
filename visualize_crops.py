"""
Visualize board detection and crops to debug alignment issues.
"""

import cv2
import numpy as np
import os
import chess
from parse_reference import parse_referencia


def simple_board_detection(image_path: str, style: str):
    """Simple board detection."""
    img = cv2.imread(image_path)
    height, width = img.shape[:2]
    
    if style == 'modern':
        margin_x = int(width * 0.08)
        margin_y = int(height * 0.08)
    else:
        margin_x = int(width * 0.12)
        margin_y = int(height * 0.12)
    
    board_x = margin_x
    board_y = margin_y
    board_w = width - 2 * margin_x
    board_h = height - 2 * margin_y
    
    return img, board_x, board_y, board_w, board_h


def visualize_board_detection(image_name):
    """Visualize board detection and grid."""
    ground_truth = parse_referencia()
    
    if image_name not in ground_truth:
        print(f"Error: {image_name} not in ground truth")
        return
    
    data = ground_truth[image_name]
    img_path = os.path.join('ejemplos', image_name)
    
    # Load and detect
    img, board_x, board_y, board_w, board_h = simple_board_detection(img_path, data['style'])
    
    # Draw board boundary
    viz = img.copy()
    cv2.rectangle(viz, (board_x, board_y), (board_x + board_w, board_y + board_h), (0, 255, 0), 2)
    
    # Draw grid
    square_w = board_w / 8
    square_h = board_h / 8
    
    for i in range(9):
        # Vertical lines
        x = int(board_x + i * square_w)
        cv2.line(viz, (x, board_y), (x, board_y + board_h), (255, 0, 0), 1)
        
        # Horizontal lines
        y = int(board_y + i * square_h)
        cv2.line(viz, (board_x, y), (board_x + board_w, y), (255, 0, 0), 1)
    
    # Show expected pieces on grid
    board = chess.Board(data['fen'])
    
    for square_idx in range(64):
        piece = board.piece_at(square_idx)
        if piece:
            file_idx = square_idx % 8
            rank_idx = square_idx // 8
            
            img_row = 7 - rank_idx
            img_col = file_idx
            
            x = int(board_x + (img_col + 0.5) * square_w)
            y = int(board_y + (img_row + 0.5) * square_h)
            
            # Draw piece symbol
            text = piece.symbol()
            cv2.putText(viz, text, (x-5, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    
    # Save visualization
    output_path = f'debug_{image_name}'
    cv2.imwrite(output_path, viz)
    print(f"Saved visualization to {output_path}")
    
    # Also save individual crops for inspection
    crops_dir = f'debug_crops_{image_name[:-4]}'
    os.makedirs(crops_dir, exist_ok=True)
    
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
        
        square_name = chess.square_name(square_idx)
        piece = board.piece_at(square_idx)
        piece_str = piece.symbol() if piece else 'empty'
        
        filename = f'{square_name}_{piece_str}.png'
        cv2.imwrite(os.path.join(crops_dir, filename), crop_resized)
    
    print(f"Saved {64} crops to {crops_dir}/")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python visualize_crops.py <image_name>")
        print("Example: python visualize_crops.py tablero1.png")
        sys.exit(1)
    
    visualize_board_detection(sys.argv[1])
