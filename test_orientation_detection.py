"""
Test orientation detection on tablero2.png and other boards.
"""

from board_processor import BoardProcessor
from formatters import BrailleFormatter
import sys


def main():
    """Test orientation detection."""
    
    # Test with existing model first
    try:
        processor = BoardProcessor('chess_cnn_best.pth')
        print("Loaded chess_cnn_best.pth")
    except:
        try:
            processor = BoardProcessor('chess_cnn_realistic.pth')
            print("Loaded chess_cnn_realistic.pth")
        except Exception as e:
            print(f"Error: No trained model found! {e}")
            print("Run train_realistic_model.py first")
            return
    
    formatter = BrailleFormatter()
    
    # Test tablero2 (known to be rotated)
    test_images = [
        ('ejemplos/tablero1.png', 'tablero1 (normal)'),
        ('ejemplos/tablero2.png', 'tablero2 (rotated 180°)'),
        ('ejemplos/tablero3.png', 'tablero3 (normal)'),
    ]
    
    print("\n" + "="*70)
    print("ORIENTATION DETECTION TEST")
    print("="*70)
    
    for img_path, description in test_images:
        print(f"\n{description}:")
        print("-" * 70)
        
        try:
            board, fen, rotated = processor.process_image(img_path, try_both_orientations=True)
            
            print(f"FEN: {fen}")
            print(f"Rotated: {rotated}")
            print(f"\nBoard (first 3 ranks):\n{str(board).split(chr(10))[:3]}")
            
            # Try to format to braille
            try:
                white_pieces = formatter.format_color_pieces(board, True)  # True = WHITE
                print(f"\nWhite pieces (braille): {white_pieces[:80]}...")
            except Exception as e:
                print(f"Could not format to braille: {e}")
        
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
