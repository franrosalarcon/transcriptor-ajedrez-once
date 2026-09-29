import numpy as np
import os
import chess
from PIL import Image
from parse_reference import parse_referencia
from deteccion_tablero import recortar_casillas
from sklearn.neighbors import KNeighborsClassifier
import pickle


def extract_crops_for_image(image_path, ground_truth_fen):
    img = Image.open(image_path)
    casillas = recortar_casillas(img, tam=32, margen=0, recorte_interior=0.06)
    board = chess.Board(ground_truth_fen)
    
    piece_to_class = {
        None: 0,
        'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6,
        'p': 7, 'n': 8, 'b': 9, 'r': 10, 'q': 11, 'k': 12
    }
    
    crops = []
    labels = []
    
    for i, pil_crop in enumerate(casillas):
        fen_row = i // 8
        fen_col = i % 8
        chess_rank = 7 - fen_row
        chess_file = fen_col
        square_idx = chess_rank * 8 + chess_file
        
        crop_array = np.array(pil_crop, dtype=np.uint8)
        piece = board.piece_at(square_idx)
        piece_symbol = piece.symbol() if piece else None
        label = piece_to_class[piece_symbol]
        
        crops.append(crop_array)
        labels.append(label)
    
    return crops, labels


def train_dual_knn():
    ground_truth = parse_referencia()
    
    modern_images = ['tablero1.png', 'tablero2.png', 'tablero4.png', 'tablero5.png', 'tablero6.png']
    scanned_images = ['diagrama01.png', 'diagrama05.png', 'diagrama23.png']
    
    print("=" * 60)
    print("TRAINING DUAL k-NN CLASSIFIERS")
    print("=" * 60)
    print()
    
    print("Extracting MODERN board crops...")
    modern_crops = []
    modern_labels = []
    
    for img_name in modern_images:
        img_path = os.path.join('ejemplos', img_name)
        data = ground_truth[img_name]
        print(f"  {img_name}")
        crops, labels = extract_crops_for_image(img_path, data['fen'])
        modern_crops.extend(crops)
        modern_labels.extend(labels)
    
    X_modern = np.array(modern_crops, dtype=np.uint8).reshape(len(modern_crops), -1)
    y_modern = np.array(modern_labels, dtype=np.int64)
    print(f"  Total: {len(X_modern)} crops")
    print()
    
    print("Extracting SCANNED diagram crops...")
    scanned_crops = []
    scanned_labels = []
    
    for img_name in scanned_images:
        img_path = os.path.join('ejemplos', img_name)
        data = ground_truth[img_name]
        print(f"  {img_name}")
        crops, labels = extract_crops_for_image(img_path, data['fen'])
        scanned_crops.extend(crops)
        scanned_labels.extend(labels)
    
    X_scanned = np.array(scanned_crops, dtype=np.uint8).reshape(len(scanned_crops), -1)
    y_scanned = np.array(scanned_labels, dtype=np.int64)
    print(f"  Total: {len(X_scanned)} crops")
    print()
    
    print("Training MODERN k-NN (k=3)...")
    knn_modern = KNeighborsClassifier(n_neighbors=3)
    knn_modern.fit(X_modern, y_modern)
    train_acc_modern = knn_modern.score(X_modern, y_modern) * 100
    print(f"  Training accuracy: {train_acc_modern:.1f}%")
    
    with open('knn_modern.pkl', 'wb') as f:
        pickle.dump(knn_modern, f)
    print("  Saved to knn_modern.pkl")
    print()
    
    print("Training SCANNED k-NN (k=3)...")
    knn_scanned = KNeighborsClassifier(n_neighbors=3)
    knn_scanned.fit(X_scanned, y_scanned)
    train_acc_scanned = knn_scanned.score(X_scanned, y_scanned) * 100
    print(f"  Training accuracy: {train_acc_scanned:.1f}%")
    
    with open('knn_scanned.pkl', 'wb') as f:
        pickle.dump(knn_scanned, f)
    print("  Saved to knn_scanned.pkl")
    print()
    
    print("=" * 60)
    print("DUAL CLASSIFIER TRAINING COMPLETE")
    print("=" * 60)
    print(f"Modern classifier: {len(X_modern)} samples, {train_acc_modern:.1f}% training accuracy")
    print(f"Scanned classifier: {len(X_scanned)} samples, {train_acc_scanned:.1f}% training accuracy")


if __name__ == '__main__':
    train_dual_knn()
