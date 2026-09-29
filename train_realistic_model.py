"""
Train CNN model on realistic synthetic dataset.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from model import ChessSquareCNN
import sys


def load_dataset(filename: str = 'dataset/combined_realistic.npz'):
    """Load dataset from npz file."""
    data = np.load(filename)
    X = data['X']
    y = data['y']
    
    print(f"Loaded dataset: {len(X)} samples")
    print(f"Class distribution:")
    unique, counts = np.unique(y, return_counts=True)
    class_names = ['empty', 'P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']
    for cls, count in zip(unique, counts):
        print(f"  {class_names[cls]}: {count} ({100*count/len(y):.1f}%)")
    
    return X, y


def train_model(X, y, epochs=20, batch_size=128, model_output='chess_cnn_realistic.pth'):
    """Train PyTorch CNN model."""
    
    # Split into train/val
    split_idx = int(0.85 * len(X))
    
    # Shuffle
    indices = np.random.permutation(len(X))
    X = X[indices]
    y = y[indices]
    
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]
    
    print(f"\nTrain: {len(X_train)} samples, Val: {len(X_val)} samples")
    
    # Normalize to [0, 1]
    X_train = X_train.astype(np.float32) / 255.0
    X_val = X_val.astype(np.float32) / 255.0
    
    # Convert to PyTorch tensors (NCHW format)
    X_train_t = torch.from_numpy(X_train).permute(0, 3, 1, 2)
    y_train_t = torch.from_numpy(y_train).long()
    X_val_t = torch.from_numpy(X_val).permute(0, 3, 1, 2)
    y_val_t = torch.from_numpy(y_val).long()
    
    # Create data loaders
    train_dataset = TensorDataset(X_train_t, y_train_t)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    
    # Initialize model
    model = ChessSquareCNN()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    print(f"\nTraining PyTorch CNN for {epochs} epochs...")
    
    best_val_acc = 0.0
    
    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            train_total += y_batch.size(0)
            train_correct += (predicted == y_batch).sum().item()
        
        train_acc = 100 * train_correct / train_total
        
        # Validation
        model.eval()
        with torch.no_grad():
            val_outputs = model(X_val_t)
            _, val_predicted = torch.max(val_outputs.data, 1)
            val_correct = (val_predicted == y_val_t).sum().item()
            val_acc = 100 * val_correct / len(y_val)
        
        print(f"Epoch {epoch+1}/{epochs}: Train Acc={train_acc:.2f}%, Val Acc={val_acc:.2f}%")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), model_output)
            print(f"  → Saved best model to {model_output}")
    
    print(f"\nBest validation accuracy: {best_val_acc:.2f}%")
    print(f"Model saved to {model_output}")
    
    # Load best model
    model.load_state_dict(torch.load(model_output))
    
    return model


def main():
    """Main training script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train CNN on realistic dataset')
    parser.add_argument('--dataset', type=str, default='dataset/combined_realistic.npz',
                       help='Path to dataset npz file')
    parser.add_argument('--epochs', type=int, default=20,
                       help='Number of training epochs')
    parser.add_argument('--output', type=str, default='chess_cnn_realistic.pth',
                       help='Output model path')
    
    args = parser.parse_args()
    
    print("="*60)
    print("TRAIN CNN ON REALISTIC DATASET")
    print("="*60)
    
    # Load dataset
    X, y = load_dataset(args.dataset)
    
    # Train
    model = train_model(X, y, epochs=args.epochs, model_output=args.output)
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE!")
    print("="*60)


if __name__ == '__main__':
    main()
