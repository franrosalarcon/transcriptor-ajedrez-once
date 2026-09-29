"""Test formatters against reference transcriptions."""

import chess
from formatters import BrailleFormatter, AudioFormatter
from parse_reference import parse_referencia

# Load ground truth
ground_truth = parse_referencia()

braille_formatter = BrailleFormatter()
audio_formatter = AudioFormatter()

# Test tablero1 (braille)
print("=== Testing tablero1.png (Braille) ===")
tablero1_data = ground_truth['tablero1.png']
board = chess.Board(tablero1_data['fen'])

expected_braille = tablero1_data['braille']
actual_braille = braille_formatter.format_position(board)

print(f"Expected:\n{expected_braille}\n")
print(f"Actual:\n{actual_braille}\n")

if expected_braille.split('\n')[0] == actual_braille.split('\n')[0]:
    print("✓ White pieces match!")
else:
    print("✗ White pieces differ")

if expected_braille.split('\n')[1] == actual_braille.split('\n')[1]:
    print("✓ Black pieces match!")
else:
    print("✗ Black pieces differ")

# Test diagrama01 (audio)
print("\n=== Testing diagrama01.png (Audio) ===")
diagrama01_data = ground_truth['diagrama01.png']
board = chess.Board(diagrama01_data['fen'])

expected_audio = diagrama01_data['audio']
actual_audio = audio_formatter.format_position(board)

print(f"Expected:\n{expected_audio}\n")
print(f"Actual:\n{actual_audio}\n")

if expected_audio.split('\n')[0] == actual_audio.split('\n')[0]:
    print("✓ White pieces match!")
else:
    print("✗ White pieces differ")

if expected_audio.split('\n')[1] == actual_audio.split('\n')[1]:
    print("✓ Black pieces match!")
else:
    print("✗ Black pieces differ")
