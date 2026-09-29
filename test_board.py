"""Quick test of board processing."""

from board_processor import BoardProcessor

print("Loading model...")
processor = BoardProcessor()

print("Processing tablero1.png...")
board, fen = processor.process_image('ejemplos/tablero1.png')

print(f"\nFEN: {fen}")
print(f"\nBoard:\n{board}")
