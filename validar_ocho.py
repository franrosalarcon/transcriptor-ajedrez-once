import numpy as np
import pickle
from PIL import Image
from board_processor import recortar_casillas
import chess

with open("knn_model.pkl", "rb") as f:
    knn = pickle.load(f)

class_to_piece = {0: None, 1: "P", 2: "N", 3: "B", 4: "R", 5: "Q", 6: "K", 7: "p", 8: "n", 9: "b", 10: "r", 11: "q", 12: "k"}

def classify_with_knn(squares):
    batch = [np.array(sq, dtype=np.float32).flatten() for sq in squares]
    return knn.predict(np.array(batch)).tolist()

def to_fen(classifications):
    board = chess.Board(None)
    for i, cls in enumerate(classifications):
        square_idx = (7 - i // 8) * 8 + i % 8
        piece_symbol = class_to_piece[cls]
        if piece_symbol:
            board.set_piece_at(square_idx, chess.Piece.from_symbol(piece_symbol))
    return board.fen()

training_images = [("tablero1.png", "r1bqk2r/ppp2p2/2n2n1p/2b1p1p1/2B1P3/2NP1NB1/PPP2PPP/R2QK2R"),
                   ("tablero2.png", "r1bqkb1r/pp3ppp/3p4/4p3/4PBn1/2N5/PPP2PPP/R2QKB1R"),
                   ("tablero4.png", "k7/p7/1p6/6p1/P4pPp/1P3P1P/2P5/7K"),
                   ("tablero5.png", "1q4k1/3b1p2/1r1b1p1p/2pPp2N/2P1P3/2BQ3P/r2N2P1/2R3K1"),
                   ("tablero6.png", "1rb2rk1/1nq1bppp/3p1n2/1ppPp3/1P2P3/2P2N1P/2BN1PP1/R1BQR1K1"),
                   ("diagrama01.png", "r3kb1r/pppppppp/2n5/8/Q5b1/2N2N2/PPPP1PPP/R1B1K2R"),
                   ("diagrama05.png", "r2q1rk1/pppp1ppp/n4n2/1b2p3/1b2P3/1B3N2/PPPP1PPP/RNBQR1K1"),
                   ("diagrama23.png", "8/p3r2k/P5pq/2P2p2/6P1/6NK/4N3/5R2")]

print("VALIDACION CONTRA REFERENCIA.md")
print("="*70)
print()

results = []
total_correct = 0
total_squares = 0
perfect_count = 0

for img_name, expected_fen in training_images:
    img = Image.open("ejemplos/" + img_name)
    squares = recortar_casillas(img, tam=32, margen=0, recorte_interior=0.06)
    classifications = classify_with_knn(squares)
    predicted_fen = to_fen(classifications)
    
    pred_pos = predicted_fen.split()[0]
    exp_pos = expected_fen.split()[0]
    
    correct = sum(1 for p, e in zip(pred_pos, exp_pos) if p == e)
    is_perfect = (pred_pos == exp_pos)
    
    total_correct += correct
    total_squares += 64
    if is_perfect:
        perfect_count += 1
    
    results.append({"name": img_name, "correct": correct, "perfect": is_perfect})
    
    status = "EXACTO" if is_perfect else "PARCIAL"
    print("{:18s} {}/64 casillas  [{}]".format(img_name, correct, status))

print()
print("="*70)
print("TOTAL: {}/{} casillas correctas ({:.1f}%)".format(total_correct, total_squares, 100*total_correct/total_squares))
print("EXACTOS: {}/8 diagramas".format(perfect_count))

with open("resultados_validacion.txt", "w", encoding="utf-8") as f:
    f.write("VALIDACION CONTRA REFERENCIA.md\n")
    f.write("="*70 + "\n\n")
    for r in results:
        status = "EXACTO" if r["perfect"] else "PARCIAL"
        f.write("{:18s} {}/64 casillas  [{}]\n".format(r["name"], r["correct"], status))
    f.write("\n" + "="*70 + "\n")
    f.write("TOTAL: {}/{} casillas correctas ({:.1f}%)\n".format(total_correct, total_squares, 100*total_correct/total_squares))
    f.write("EXACTOS: {}/8 diagramas\n".format(perfect_count))

print()
print("Resultados guardados en resultados_validacion.txt")