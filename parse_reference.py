"""
Parse REFERENCIA.md to extract ground truth positions.
Maps image paths to their braille and audio transcriptions.
"""

import re
from typing import Dict, Tuple
import chess


def parse_braille_position(braille_text: str) -> chess.Board:
    """
    Convert braille transcription to chess.Board.
    
    Braille format: "Blancas: Re⠂ Dd⠂ Ta⠂ ..."
    Row encoding: 1⠂ 2⠆ 3⠒ 4⠲ 5⠢ 6⠖ 7⠶ 8⠦
    Piece codes: R=King, D=Queen, T=Rook, C=Knight, A=Bishop, P=Pawn (or no prefix)
    """
    # Map braille row symbols to numbers
    braille_rows = {
        '⠂': '1', '⠆': '2', '⠒': '3', '⠲': '4',
        '⠢': '5', '⠖': '6', '⠶': '7', '⠦': '8'
    }
    
    # Map Spanish piece codes to chess piece symbols
    piece_map = {
        'R': 'K',  # Rey -> King
        'D': 'Q',  # Dama -> Queen
        'T': 'R',  # Torre -> Rook
        'C': 'N',  # Caballo -> Knight
        'A': 'B',  # Alfil -> Bishop
        'P': 'P',  # Peón -> Pawn (but usually omitted)
    }
    
    board = chess.Board(None)  # Empty board
    
    # Extract white pieces
    white_match = re.search(r'Blancas:\s*([^\n]+)', braille_text)
    if white_match:
        white_pieces = white_match.group(1)
        parse_pieces(white_pieces, chess.WHITE, board, braille_rows, piece_map)
    
    # Extract black pieces
    black_match = re.search(r'Negras:\s*([^\n]+)', braille_text)
    if black_match:
        black_pieces = black_match.group(1)
        parse_pieces(black_pieces, chess.BLACK, board, braille_rows, piece_map)
    
    return board


def parse_pieces(piece_text: str, color: chess.Color, board: chess.Board, 
                 braille_rows: Dict[str, str], piece_map: Dict[str, str]):
    """Parse piece notation and place on board."""
    # Split by spaces, filter out arrow notation and highlights
    tokens = piece_text.split()
    
    for token in tokens:
        # Skip if contains arrow symbols or parentheses
        if '¬' in token or '(' in token or ')' in token:
            continue
        
        # Parse piece + square notation (e.g., "Re⠂", "a⠆")
        # Pattern: optional piece letter + column letter + braille row
        match = re.match(r'([RDTCAP]?)([a-h])([\u2800-\u28FF])', token)
        if match:
            piece_code, col, braille_row = match.groups()
            
            # Convert braille row to number
            row = braille_rows.get(braille_row)
            if not row:
                continue
            
            # Determine piece type
            if piece_code:
                piece_type_str = piece_map.get(piece_code, 'P')
            else:
                # No piece code means pawn
                piece_type_str = 'P'
            
            # Create piece
            piece = chess.Piece.from_symbol(
                piece_type_str if color == chess.WHITE else piece_type_str.lower()
            )
            
            # Calculate square
            square = chess.square(ord(col) - ord('a'), int(row) - 1)
            
            # Place on board
            board.set_piece_at(square, piece)


def parse_audio_position(audio_text: str) -> chess.Board:
    """
    Convert audio transcription to chess.Board.
    
    Audio format: "Blancas: Rey en E2, Dama en A4, Torres en C1 y H1, ..."
    """
    piece_map = {
        'Rey': 'K',
        'Dama': 'Q',
        'Torre': 'R', 'Torres': 'R',
        'Alfil': 'B', 'Alfiles': 'B',
        'Caballo': 'N', 'Caballos': 'N',
        'Peón': 'P', 'Peones': 'P'
    }
    
    board = chess.Board(None)  # Empty board
    
    # Extract white pieces
    white_match = re.search(r'Blancas:\s*([^\.]+)\.', audio_text)
    if white_match:
        white_pieces = white_match.group(1)
        parse_audio_pieces(white_pieces, chess.WHITE, board, piece_map)
    
    # Extract black pieces
    black_match = re.search(r'Negras:\s*([^\.]+)\.', audio_text)
    if black_match:
        black_pieces = black_match.group(1)
        parse_audio_pieces(black_pieces, chess.BLACK, board, piece_map)
    
    return board


def parse_audio_pieces(piece_text: str, color: chess.Color, board: chess.Board,
                       piece_map: Dict[str, str]):
    """Parse audio piece notation and place on board."""
    # Split by comma
    groups = piece_text.split(',')
    
    for group in groups:
        # Extract piece name and squares
        # Pattern: "Torre en C1" or "Torres en C1 y H1"
        match = re.search(r'(Rey|Dama|Torres?|Alfiles?|Caballos?|Peones?)\s+en\s+([A-H0-9\s,y]+)', group, re.IGNORECASE)
        if match:
            piece_name, squares_text = match.groups()
            
            piece_type_str = piece_map.get(piece_name.capitalize())
            if not piece_type_str:
                continue
            
            # Extract all squares (e.g., "C1 y H1" -> ["C1", "H1"])
            squares = re.findall(r'([A-H][1-8])', squares_text.upper())
            
            for square_name in squares:
                col = ord(square_name[0]) - ord('A')
                row = int(square_name[1]) - 1
                square = chess.square(col, row)
                
                piece = chess.Piece.from_symbol(
                    piece_type_str if color == chess.WHITE else piece_type_str.lower()
                )
                board.set_piece_at(square, piece)


def parse_referencia() -> Dict[str, Dict]:
    """
    Parse entire REFERENCIA.md file.
    Returns dict mapping image filename to ground truth data.
    """
    with open('REFERENCIA.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    ground_truth = {}
    
    # Parse braille boards (tablero1-6)
    braille_boards = [
        'tablero1.png', 'tablero2.png', 'tablero3.png',
        'tablero4.png', 'tablero5.png', 'tablero6.png'
    ]
    
    for board_name in braille_boards:
        # Find section for this board
        pattern = rf'### {re.escape(board_name)}(.*?)(?=###|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            section = match.group(1)
            # Extract code block
            code_match = re.search(r'```\n(.*?)\n```', section, re.DOTALL)
            if code_match:
                braille_text = code_match.group(1)
                board = parse_braille_position(braille_text)
                
                ground_truth[board_name] = {
                    'fen': board.fen(),
                    'braille': braille_text.strip(),
                    'style': 'modern'
                }
    
    # Parse audio boards (diagrama01, 02, 05, 23)
    audio_boards = [
        ('diagrama01.png', 'diagrama01.png — pág. 15 del libro'),
        ('diagrama02.png', 'diagrama02.png — pág. 17'),
        ('diagrama05.png', 'diagrama05.png — pág. 24'),
        ('diagrama23.png', 'diagrama23.png — pág. 44'),
    ]
    
    for board_name, section_title in audio_boards:
        # Find section
        pattern = rf'### {re.escape(section_title)}(.*?)(?=###|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            section = match.group(1)
            # Extract code block
            code_match = re.search(r'```\n(.*?)\n```', section, re.DOTALL)
            if code_match:
                audio_text = code_match.group(1)
                board = parse_audio_position(audio_text)
                
                ground_truth[board_name] = {
                    'fen': board.fen(),
                    'audio': audio_text.strip(),
                    'style': 'scanned'
                }
    
    return ground_truth


if __name__ == '__main__':
    ground_truth = parse_referencia()
    
    print("Ground truth positions parsed:")
    print(f"Total diagrams: {len(ground_truth)}")
    print()
    
    for img_name, data in sorted(ground_truth.items()):
        print(f"{img_name} ({data['style']}):")
        print(f"  FEN: {data['fen']}")
        print()
