import chess
from formatters import BrailleFormatter, AudioFormatter

b = chess.Board(None)
b.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
b.set_piece_at(chess.A2, chess.Piece(chess.PAWN, chess.WHITE))
b.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))

braille_text = BrailleFormatter().format_position(b, {})
audio_text = AudioFormatter().format_position(b)

with open("test_desfase_result.txt", "w", encoding="utf-8") as f:
    f.write("BRAILLE:\n")
    f.write(braille_text + "\n\n")
    f.write("AUDIO:\n")
    f.write(audio_text + "\n\n")
    f.write("ESPERADO:\n")
    f.write("Braille: Blancas: Re\u2802 a\u2806   Negras: Re\u2826\n")
    f.write("Audio: Blancas: Rey en E1, Peon en A2.  Negras: Rey en E8.\n")

print("Guardado en test_desfase_result.txt")