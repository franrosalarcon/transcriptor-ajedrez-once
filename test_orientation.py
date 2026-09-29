import chess
from board_processor import recortar_casillas, ChessSquareCNN
import torch
import numpy as np
from PIL import Image

def detect_orientation(img, model):
    '''
    Detecta si el tablero esta normal o girado 180 grados.
    Prueba ambas orientaciones y queda con la posicion mas plausible.
    '''
    squares_normal = recortar_casillas(img, tam=32, margen=0, recorte_interior=0.06)
    squares_flipped = recortar_casillas(img.rotate(180), tam=32, margen=0, recorte_interior=0.06)
    
    # Clasificar ambas
    def classify_batch(squares):
        batch = []
        for sq in squares:
            arr = np.array(sq, dtype=np.float32) / 255.0
            batch.append(arr)
        batch = np.array(batch)
        batch_tensor = torch.from_numpy(batch).permute(0, 3, 1, 2)
        with torch.no_grad():
            outputs = model(batch_tensor)
            _, predicted = torch.max(outputs.data, 1)
        return predicted.numpy().tolist()
    
    cls_normal = classify_batch(squares_normal)
    cls_flipped = classify_batch(squares_flipped)
    
    # Convertir a FEN y validar plausibilidad
    class_to_piece = {0: None, 1: 'P', 2: 'N', 3: 'B', 4: 'R', 5: 'Q', 6: 'K',
                      7: 'p', 8: 'n', 9: 'b', 10: 'r', 11: 'q', 12: 'k'}
    
    def score_plausibility(classifications):
        score = 0
        # Contar reyes
        kings = sum(1 for c in classifications if c in [6, 12])
        if kings == 2: score += 10
        # Peones no en fila 1 ni 8
        for i, c in enumerate(classifications):
            rank = 8 - (i // 8)
            if c in [1, 7]:  # pawn
                if rank == 1 or rank == 8:
                    score -= 5
                else:
                    score += 1
        return score
    
    score_normal = score_plausibility(cls_normal)
    score_flipped = score_plausibility(cls_flipped)
    
    return 0 if score_normal >= score_flipped else 180

print('Testing orientation detection...')
print('tablero2.png should be detected as 180 degrees')
