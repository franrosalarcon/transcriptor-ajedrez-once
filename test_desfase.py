import chess
from formatters import BrailleFormatter, AudioFormatter

b = chess.Board(None)
b.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
b.set_piece_at(chess.A2, chess.Piece(chess.PAWN, chess.WHITE))
b.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))

braille_formatter = BrailleFormatter()
audio_formatter = AudioFormatter()

braille_text = braille_formatter.format_position(b, {})
audio_text = audio_formatter.format_position(b, {})

print("BRAILLE:")
print(braille_text)
print()
print("AUDIO:")
print(audio_text)
print()
print("ESPERADO:")
print("Braille: Blancas: Re\u2802 a\u2806   Negras: Re\u2826")
print("Audio: Blancas: Rey en E1, Peon en A2.  Negras: Rey en E8.")