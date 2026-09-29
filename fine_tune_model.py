"""
Fine-tune existing model with real crops and light augmentation.
Transfer learning approach: start from chess_cnn_best.pth, fine-tune with real data.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import torch.optim as optim
import random


class ChessSquareCNN(nn.Module):
    """CNN model (same architecture as training)."""
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.pool1 = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool2 = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 8 * 8, 128)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(128, 13)
    
    def forward(self, x):
        x = self.pool1(F.relu(self.conv1(x)))
        x = self.pool2(F.relu(self.conv2(x)))
        x = x.reshape(-1, 64 * 8 * 8)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x


def augment_crop(crop: np.ndarray) -> np.ndarray:
    """
    Apply light augmentation to prevent overfitting on small dataset.
    Simple numpy-based augmentations only.
    
    Args:
        crop: 32x32x3 uint8 array
    
    Returns:
        Augmented 32x32x3 uint8 array
    """
    result = crop.copy()
    
    # Random brightness adjustment (50% chance)
    if random.random() < 0.5:
        factor = random.uniform(0.85, 1.15)
        result = np.clip(result.astype(np.float32) * factor, 0, 255).astype(np.uint8)
    
    # Add small random noise (50% chance)
    if random.random() < 0.5:
        noise = np.random.normal(0, 3, result.shape)
        result = np.clip(result.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    
    # Random shift (1-2 pixels)
    if random.random() < 0.5:
        dx = random.randint(-2, 2)
        dy = random.randint(-2, 2)
        result = np.roll(result, shift=dx, axis=1)
        result = np.roll(result, shift=dy, axis=0)
    
    return result


class AugmentedDataset(Dataset):
    """Dataset with on-the-fly augmentation."""
    
    def __init__(self, X, y, augment=True, augmentation_factor=5):
        """
        Args:
            X: (N, 32, 32, 3) uint8 array
            y: (N,) int64 array
            augment: Whether to apply augmentation
            augmentation_factor: How many augmented versions per original
        """
        self.X_original = X
        self.y_original = y
        self.augment = augment
        self.augmentation_factor = augmentation_factor if augment else 1
    
    def __len__(self):
        return len(self.X_original) * self.augmentation_factor
    
    def __getitem__(self, idx):
        # Map to original index
        original_idx = idx % len(self.X_original)
        crop = self.X_original[original_idx]
        label = self.y_original[original_idx]
        
        # Apply augmentation if enabled and not the first copy
        if self.augment and (idx >= len(self.X_original)):
            crop = augment_crop(crop)
        
        # Convert to tensor and normalize
        crop_tensor = torch.from_numpy(crop).permute(2, 0, 1).float() / 255.0
        
        return crop_tensor, label


def load_real_crops():
    """Load real crops dataset."""
    data = np.load('dataset/real_crops.npz')
    return data['X'], data['y']


def fine_tune_model(model_path='chess_cnn_best.pth', 
                    output_path='chess_cnn_finetuned.pth',
                    epochs=10, 
                    batch_size=32,
                    lr=0.0001):
    """
    Fine-tune existing model with real crops.
    
    Args:
        model_path: Path to pre-trained model
        output_path: Where to save fine-tuned model
        epochs: Number of fine-tuning epochs
        batch_size: Batch size
        lr: Learning rate (lower for fine-tuning)
    """
    print("=" * 60)
    print("FINE-TUNING MODEL WITH REAL CROPS")
    print("=" * 60)
    
    # Load real crops
    print("\nLoading real crops...")
    X, y = load_real_crops()
    print(f"Loaded {len(X)} real crops from training set")
    
    # Split into train/val (80/20)
    split_idx = int(0.8 * len(X))
    indices = np.random.permutation(len(X))
    train_indices = indices[:split_idx]
    val_indices = indices[split_idx:]
    
    X_train, y_train = X[train_indices], y[train_indices]
    X_val, y_val = X[val_indices], y[val_indices]
    
    print(f"Train: {len(X_train)} samples (with 5x augmentation = {len(X_train)*5})")
    print(f"Val: {len(X_val)} samples (no augmentation)")
    
    # Create datasets
    train_dataset = AugmentedDataset(X_train, y_train, augment=True, augmentation_factor=5)
    val_dataset = AugmentedDataset(X_val, y_val, augment=False)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Load pre-trained model
    print(f"\nLoading pre-trained model from {model_path}...")
    model = ChessSquareCNN()
    model.load_state_dict(torch.load(model_path))
    print("Pre-trained model loaded successfully")
    
    # Setup training
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    # Fine-tune
    print(f"\nFine-tuning for {epochs} epochs (lr={lr})...")
    print("-" * 60)
    
    best_val_acc = 0.0
    
    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for batch_idx, (inputs, labels) in enumerate(train_loader):
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            train_total += labels.size(0)
            train_correct += (predicted == labels).sum().item()
        
        train_acc = 100 * train_correct / train_total
        avg_train_loss = train_loss / len(train_loader)
        
        # Validation
        model.eval()
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                outputs = model(inputs)
                _, predicted = torch.max(outputs.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        val_acc = 100 * val_correct / val_total
        
        print(f"Epoch {epoch+1}/{epochs}: "
              f"Train Loss={avg_train_loss:.4f}, Train Acc={train_acc:.2f}%, "
              f"Val Acc={val_acc:.2f}%")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), output_path)
            print(f"  -> Saved best model (val_acc={val_acc:.2f}%)")
    
    print("-" * 60)
    print(f"\nFine-tuning complete!")
    print(f"Best validation accuracy: {best_val_acc:.2f}%")
    print(f"Fine-tuned model saved to: {output_path}")
    
    return model


if __name__ == '__main__':
    fine_tune_model(
        model_path='chess_cnn_best.pth',
        output_path='chess_cnn_finetuned.pth',
        epochs=10,
        batch_size=32,
        lr=0.0001
    )
