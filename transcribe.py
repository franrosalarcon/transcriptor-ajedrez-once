"""
End-to-end chess diagram transcription pipeline.
"""

import sys
import chess
from board_processor import BoardProcessor
from formatters import BrailleFormatter, AudioFormatter


def transcribe_diagram(image_path: str) -> dict:
    """
    Transcribe a chess diagram image to ONCE formats.
    
    Args:
        image_path: Path to chess diagram image
    
    Returns:
        dict with keys: 'board', 'fen', 'braille', 'audio'
    """
    print(f"Processing {image_path}...")
    
    # Step 1: Process image and classify squares
    processor = BoardProcessor()
    board, fen = processor.process_image(image_path)
    
    print(f"Position detected: {fen}")
    
    # Step 2: Format as braille
    braille_formatter = BrailleFormatter()
    braille_text = braille_formatter.format_position(board)
    
    # Step 3: Format as audio
    audio_formatter = AudioFormatter()
    audio_text = audio_formatter.format_position(board)
    
    return {
        'board': board,
        'fen': fen,
        'braille': braille_text,
        'audio': audio_text
    }


def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <image_path>")
        print("\nExample:")
        print("  python transcribe.py ejemplos/tablero1.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    result = transcribe_diagram(image_path)
    
    print("\n" + "="*60)
    print("BRAILLE TRANSCRIPTION (Documento Técnico B8)")
    print("="*60)
    print(result['braille'])
    
    print("\n" + "="*60)
    print("AUDIO TRANSCRIPTION (Adapted Book Format)")
    print("="*60)
    print(result['audio'])
    
    print("\n" + "="*60)
    print(f"FEN: {result['fen']}")
    print("="*60)


if __name__ == '__main__':
    main()
