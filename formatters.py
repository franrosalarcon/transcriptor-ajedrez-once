"""
Braille and Audio formatters for ONCE standard transcription formats.
"""

import chess
from typing import Dict, List


class BrailleFormatter:
    """
    Format chess positions in Documento Técnico B8 braille notation.
    
    Rules:
    - Piece order: R, D, T, C, A, then pawns
    - Row encoding: 1⠂ 2⠆ 3⠒ 4⠲ 5⠢ 6⠖ 7⠶ 8⠦
    - Pawns show only column+row (no P prefix)
    - Format: "Blancas: Re⠂ Dd⠂ Ta⠂ ..."
    """
    
    # Braille row encoding
    BRAILLE_ROWS = {
        '1': '⠂', '2': '⠆', '3': '⠒', '4': '⠲',
        '5': '⠢', '6': '⠖', '7': '⠶', '8': '⠦'
    }
    
    # Piece codes (Spanish)
    PIECE_CODES = {
        chess.KING: 'R',    # Rey
        chess.QUEEN: 'D',   # Dama
        chess.ROOK: 'T',    # Torre
        chess.KNIGHT: 'C',  # Caballo
        chess.BISHOP: 'A',  # Alfil
        chess.PAWN: 'P'     # Peón (omitted in output)
    }
    
    # Piece order for braille
    PIECE_ORDER = [chess.KING, chess.QUEEN, chess.ROOK, chess.KNIGHT, chess.BISHOP, chess.PAWN]
    
    def format_square(self, square: int) -> str:
        """
        Format a square in braille notation.
        Returns e.g., "e⠂" for e1.
        """
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        
        file_letter = chr(ord('a') + file)
        rank_number = str(rank + 1)
        braille_rank = self.BRAILLE_ROWS[rank_number]
        
        return f"{file_letter}{braille_rank}"
    
    def format_piece_group(self, board: chess.Board, piece_type: int, color: chess.Color) -> List[str]:
        """
        Format all pieces of a given type and color.
        Returns list of piece notations, e.g., ["Re⠂", "Dd⠂"] or ["a⠆", "b⠆"] for pawns.
        """
        squares = []
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type == piece_type and piece.color == color:
                squares.append(square)
        
        if not squares:
            return []
        
        # Sort by file, then rank
        squares.sort(key=lambda sq: (chess.square_file(sq), chess.square_rank(sq)))
        
        # Format each square
        formatted = []
        for square in squares:
            if piece_type == chess.PAWN:
                # Pawns: just column + row, no P prefix
                formatted.append(self.format_square(square))
            else:
                # Other pieces: piece code + square
                piece_code = self.PIECE_CODES[piece_type]
                formatted.append(f"{piece_code}{self.format_square(square)}")
        
        return formatted
    
    def format_color_pieces(self, board: chess.Board, color: chess.Color) -> str:
        """
        Format all pieces for one color.
        Returns string like "Re⠂ Dd⠂ Ta⠂ Th⠂ ..."
        """
        all_pieces = []
        
        for piece_type in self.PIECE_ORDER:
            pieces = self.format_piece_group(board, piece_type, color)
            all_pieces.extend(pieces)
        
        return ' '.join(all_pieces)
    
    def format_position(self, board: chess.Board, highlights: Dict[str, List[str]] = None) -> str:
        """
        Format complete position in B8 braille notation.
        
        Args:
            board: chess.Board object
            highlights: dict with 'yellow' and/or 'red' keys containing lists of squares
        
        Returns:
            Formatted braille transcription
        """
        lines = []
        
        # White pieces
        white_pieces = self.format_color_pieces(board, chess.WHITE)
        lines.append(f"Blancas: {white_pieces}")
        
        # Black pieces
        black_pieces = self.format_color_pieces(board, chess.BLACK)
        lines.append(f"Negras: {black_pieces}")
        
        # Highlights (if any)
        if highlights:
            if 'yellow' in highlights and highlights['yellow']:
                yellow_squares = ' '.join([self.format_square(sq) for sq in highlights['yellow']])
                lines.append(f")Resaltadas en amarillo las casillas {yellow_squares}(")
            
            if 'red' in highlights and highlights['red']:
                red_squares = ' '.join([self.format_square(sq) for sq in highlights['red']])
                lines.append(f")Resaltadas en rojo las casillas {red_squares}(")
        
        return '\n'.join(lines)


class AudioFormatter:
    """
    Format chess positions in ONCE adapted book audio format.
    
    Rules:
    - Piece order: Rey, Dama, Torres, Alfiles, Caballos, Peones (DIFFERENT from braille)
    - Singular/plural based on piece count
    - Conjunction "y" before last square in each group
    - Format: "Blancas: Rey en E2, Dama en A4, Torres en C1 y H1, ..."
    - Sentence ends with period
    """
    
    # Piece names (Spanish)
    PIECE_NAMES = {
        chess.KING: ('Rey', 'Rey'),            # Singular, Plural (same)
        chess.QUEEN: ('Dama', 'Dama'),         # Singular, Plural (same)
        chess.ROOK: ('Torre', 'Torres'),       # Singular, Plural
        chess.BISHOP: ('Alfil', 'Alfiles'),    # Singular, Plural
        chess.KNIGHT: ('Caballo', 'Caballos'), # Singular, Plural
        chess.PAWN: ('Peón', 'Peones')         # Singular, Plural
    }
    
    # Piece order for audio (DIFFERENT from braille!)
    PIECE_ORDER = [chess.KING, chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]
    
    def format_square(self, square: int) -> str:
        """
        Format square in audio notation (uppercase).
        Returns e.g., "E1" for e1.
        """
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        
        file_letter = chr(ord('A') + file)
        rank_number = str(rank + 1)
        
        return f"{file_letter}{rank_number}"
    
    def format_square_list(self, squares: List[int]) -> str:
        """
        Format list of squares with conjunction "y" before last.
        e.g., "C1 y H1" or "A2, B2, C2 y D2"
        """
        if not squares:
            return ""
        
        formatted_squares = [self.format_square(sq) for sq in squares]
        
        if len(formatted_squares) == 1:
            return formatted_squares[0]
        elif len(formatted_squares) == 2:
            return f"{formatted_squares[0]} y {formatted_squares[1]}"
        else:
            # Multiple squares: comma-separated with "y" before last
            return ', '.join(formatted_squares[:-1]) + f" y {formatted_squares[-1]}"
    
    def format_piece_group(self, board: chess.Board, piece_type: int, color: chess.Color) -> str:
        """
        Format one piece type.
        Returns string like "Torres en C1 y H1" or empty string if no pieces.
        """
        squares = []
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type == piece_type and piece.color == color:
                squares.append(square)
        
        if not squares:
            return ""
        
        # Sort by file, then rank
        squares.sort(key=lambda sq: (chess.square_file(sq), chess.square_rank(sq)))
        
        # Choose singular or plural name
        singular, plural = self.PIECE_NAMES[piece_type]
        name = singular if len(squares) == 1 else plural
        
        # Format square list
        square_list = self.format_square_list(squares)
        
        return f"{name} en {square_list}"
    
    def format_color_pieces(self, board: chess.Board, color: chess.Color) -> str:
        """
        Format all pieces for one color.
        Returns string like "Rey en E2, Dama en A4, Torres en C1 y H1, ..."
        """
        groups = []
        
        for piece_type in self.PIECE_ORDER:
            group = self.format_piece_group(board, piece_type, color)
            if group:
                groups.append(group)
        
        return ', '.join(groups) + '.'
    
    def format_position(self, board: chess.Board, highlights=None) -> str:
        """
        Format complete position in audio format.
        
        Returns:
            Formatted audio transcription
        """
        lines = []
        
        # White pieces
        white_pieces = self.format_color_pieces(board, chess.WHITE)
        lines.append(f"Blancas: {white_pieces}")
        
        # Black pieces
        black_pieces = self.format_color_pieces(board, chess.BLACK)
        lines.append(f"Negras: {black_pieces}")
        
        return '\n'.join(lines)


def main():
    """Test formatters with a simple position."""
    # Create a simple position
    board = chess.Board("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
    
    print("=== Braille Format ===")
    braille_formatter = BrailleFormatter()
    print(braille_formatter.format_position(board))
    
    print("\n=== Audio Format ===")
    audio_formatter = AudioFormatter()
    print(audio_formatter.format_position(board))


if __name__ == '__main__':
    main()
