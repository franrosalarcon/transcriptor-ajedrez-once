"""
CNN model for chess square classification.
Supports both PyTorch (preferred) and sklearn (fallback).
"""

import numpy as np
import os
import time


# Try PyTorch first
try:
    import_start = time.time()
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    import torch.optim as optim
    from torch.utils.data import TensorDataset, DataLoader
    import_time = time.time() - import_start
    
    USING_PYTORCH = True
    print(f"PyTorch loaded successfully in {import_time:.2f}s")
    
    class ChessSquareCNN(nn.Module):
        """
        Small CNN for 13-class square classification.
        Input: 32x32x3 RGB images
        Output: 13-class logits
        """
        def __init__(self):
            super().__init__()
            # Conv layer 1: 3 -> 32 channels
            self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)  # 32x32
            self.pool1 = nn.MaxPool2d(2, 2)  # -> 16x16
            
            # Conv layer 2: 32 -> 64 channels
            self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)  # 16x16
            self.pool2 = nn.MaxPool2d(2, 2)  # -> 8x8
            
            # Fully connected layers
            self.fc1 = nn.Linear(64 * 8 * 8, 128)
            self.dropout = nn.Dropout(0.5)
            self.fc2 = nn.Linear(128, 13)
        
        def forward(self, x):
            # Conv blocks
            x = self.pool1(F.relu(self.conv1(x)))
            x = self.pool2(F.relu(self.conv2(x)))
            
            # Flatten
            x = x.reshape(-1, 64 * 8 * 8)
            
            # FC layers
            x = F.relu(self.fc1(x))
            x = self.dropout(x)
            x = self.fc2(x)
            
            return x

except (ImportError, Exception) as e:
    USING_PYTORCH = False
    print(f"PyTorch not available: {e}")
    print("Falling back to sklearn MLPClassifier")
    
    from sklearn.neural_network import MLPClassifier
    from sklearn.preprocessing import StandardScaler


def load_datasets(data_dir: str = 'dataset'):
    """Load both modern and scanned datasets."""
    modern_data = np.load(os.path.join(data_dir, 'modern_dataset.npz'))
    scanned_data = np.load(os.path.join(data_dir, 'scanned_dataset.npz'))
    
    # Combine datasets
    X = np.concatenate([modern_data['X'], scanned_data['X']], axis=0)
    y = np.concatenate([modern_data['y'], scanned_data['y']], axis=0)
    
    print(f"Combined dataset: {X.shape[0]} samples")
    print(f"Modern: {len(modern_data['X'])}, Scanned: {len(scanned_data['X'])}")
    
    return X, y


def train_pytorch_model(X_train, y_train, X_val, y_val, epochs=20, batch_size=128):
    """Train PyTorch CNN model."""
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
            torch.save(model.state_dict(), 'chess_cnn_best.pth')
    
    print(f"\nBest validation accuracy: {best_val_acc:.2f}%")
    
    # Load best model
    model.load_state_dict(torch.load('chess_cnn_best.pth'))
    
    return model


def train_sklearn_model(X_train, y_train, X_val, y_val):
    """Train sklearn MLP model (fallback)."""
    # Flatten images
    X_train_flat = X_train.reshape(X_train.shape[0], -1).astype(np.float32)
    X_val_flat = X_val.reshape(X_val.shape[0], -1).astype(np.float32)
    
    # Normalize
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_flat)
    X_val_scaled = scaler.transform(X_val_flat)
    
    print("\nTraining sklearn MLPClassifier...")
    
    model = MLPClassifier(
        hidden_layer_sizes=(256, 128),
        activation='relu',
        solver='adam',
        batch_size=128,
        learning_rate_init=0.001,
        max_iter=20,
        verbose=True,
        early_stopping=True,
        validation_fraction=0.1
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    train_acc = model.score(X_train_scaled, y_train) * 100
    val_acc = model.score(X_val_scaled, y_val) * 100
    
    print(f"\nTrain Acc={train_acc:.2f}%, Val Acc={val_acc:.2f}%")
    
    # Save model
    import pickle
    with open('chess_mlp.pkl', 'wb') as f:
        pickle.dump({'model': model, 'scaler': scaler}, f)
    
    return model, scaler


def train_model():
    """Main training function."""
    print("Loading datasets...")
    X, y = load_datasets()
    
    # Train/val split
    split_idx = int(0.8 * len(X))
    
    # Shuffle
    indices = np.random.permutation(len(X))
    X = X[indices]
    y = y[indices]
    
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]
    
    print(f"Train: {len(X_train)} samples, Val: {len(X_val)} samples")
    
    if USING_PYTORCH:
        model = train_pytorch_model(X_train, y_train, X_val, y_val)
        print("\nModel saved to chess_cnn_best.pth")
        return model
    else:
        model, scaler = train_sklearn_model(X_train, y_train, X_val, y_val)
        print("\nModel saved to chess_mlp.pkl")
        return model


if __name__ == '__main__':
    train_model()
