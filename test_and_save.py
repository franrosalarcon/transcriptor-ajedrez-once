"""
Test the EXISTING model and SAVE results to a file.
"""

import sys
import numpy as np
import torch
import os
from board_processor import BoardProcessor
from parse_reference import parse_referencia

# Redirect output to file
output_file = open('test_results.txt', 'w')
original_stdout = sys.stdout
sys.stdout = output_file

try:
    def test_on_training_set():
        """Test the existing model on the 8 training images with verified detection."""
        # Initialize processor with existing model
        processor = BoardProcessor('chess_cnn_best.pth')
        
        # Parse ground truth
        ground_truth = parse_referencia()
        
        # Training images
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
        perfect_diagrams = 0
        
        print("Testing EXISTING model (chess_cnn_best.pth) with VERIFIED crops")
        print("=" * 70)
        print()
        
        tablero1_accuracy = None
        
        for img_name in training_images:
            if img_name not in ground_truth:
                print(f"WARNING: {img_name} not in ground truth, skipping")
                continue
            
            img_path = os.path.join('ejemplos', img_name)
            data = ground_truth[img_name]
            
            # Process image with verified detection
            try:
                board, fen = processor.process_image(img_path)
                
                # Compare with ground truth
                gt_fen = data['fen']
                
                # Extract just the position part
                predicted_pos = fen.split()[0]
                gt_pos = gt_fen.split()[0]
                
                # Count correct squares
                pred_squares = predicted_pos.replace('/', '')
                gt_squares = gt_pos.replace('/', '')
                
                # Expand digits to actual squares
                def expand_fen_row(s):
                    result = []
                    for c in s:
                        if c.isdigit():
                            result.extend(['1'] * int(c))
                        else:
                            result.append(c)
                    return result
                
                pred_expanded = expand_fen_row(pred_squares)
                gt_expanded = expand_fen_row(gt_squares)
                
                correct = sum(1 for p, g in zip(pred_expanded, gt_expanded) if p == g)
                
                total_correct += correct
                total_squares += 64
                
                is_perfect = (predicted_pos == gt_pos)
                if is_perfect:
                    perfect_diagrams += 1
                
                print(f"{img_name:18s} ({data['style']:7s}): {correct}/64 correct ({100*correct/64:5.1f}%) {'✓ PERFECT' if is_perfect else ''}")
                
                if img_name == 'tablero1.png':
                    tablero1_accuracy = (correct, 64)
                
                if not is_perfect:
                    print(f"  Predicted: {predicted_pos}")
                    print(f"  Expected:  {gt_pos}")
                    
                    mismatches = []
                    for i, (p, g) in enumerate(zip(pred_expanded, gt_expanded)):
                        if p != g:
                            file = chr(ord('a') + (i % 8))
                            rank = 8 - (i // 8)
                            mismatches.append(f"{file}{rank}:{g}→{p}")
                    
                    if len(mismatches) <= 10:
                        print(f"  Errors: {', '.join(mismatches)}")
                    else:
                        print(f"  Errors: {', '.join(mismatches[:10])} ... ({len(mismatches)} total)")
                
                print()
                
            except Exception as e:
                print(f"{img_name}: ERROR - {e}")
                import traceback
                traceback.print_exc()
                print()
        
        # Summary
        print("=" * 70)
        print(f"OVERALL RESULTS:")
        print(f"  Square-level accuracy: {total_correct}/{total_squares} ({100*total_correct/total_squares:.1f}%)")
        print(f"  Perfect diagrams: {perfect_diagrams}/8")
        
        if tablero1_accuracy:
            correct, total = tablero1_accuracy
            print(f"  tablero1.png accuracy: {correct}/{total} ({100*correct/total:.1f}%)")
        
        print()
        print("Previous performance (misaligned crops): 69.5% square accuracy")
        print("Current performance (verified crops): {:.1f}% square accuracy".format(100*total_correct/total_squares))
        
        improvement = 100*total_correct/total_squares - 69.5
        if improvement > 0:
            print(f"Improvement: +{improvement:.1f}%")
        else:
            print(f"Change: {improvement:.1f}%")

    test_on_training_set()
    
finally:
    sys.stdout = original_stdout
    output_file.close()
    print("Results saved to test_results.txt")
