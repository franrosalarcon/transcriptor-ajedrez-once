"""
Train model FROM SCRATCH on ONLY real crops with heavy augmentation.
This is simpler and more direct than trying to fine-tune.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import torch.optim as optim
import random


class ChessSquareCNN(nn.Module):
    """CNN model."""
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
    """Heavy augmentation for small dataset."""
    result = crop.copy().astype(np.float32)
    
    # Random brightness (80%)
    if random.random() < 0.8:
        factor = random.uniform(0.7, 1.3)
        result = np.clip(result * factor, 0, 255)
    
    # Random contrast (50%)
    if random.random() < 0.5:
        mean = np.mean(result)
        factor = random.uniform(0.8, 1.2)
        result = np.clip((result - mean) * factor + mean, 0, 255)
    
    # Add noise (70%)
    if random.random() < 0.7:
        noise = np.random.normal(0, 5, result.shape)
        result = np.clip(result + noise, 0, 255)
    
    # Random shift (60%)
    if random.random() < 0.6:
        dx = random.randint(-2, 2)
        dy = random.randint(-2, 2)
        result = np.roll(result, shift=dx, axis=1)
        result = np.roll(result, shift=dy, axis=0)
    
    # Random slight scale (30%)
    if random.random() < 0.3:
        scale = random.uniform(0.95, 1.05)
        h, w = result.shape[:2]
        new_h, new_w = int(h * scale), int(w * scale)
        # Simple numpy resize
        if new_h > 0 and new_w > 0:
            from PIL import Image
            img = Image.fromarray(result.astype(np.uint8))
            img = img.resize((new_w, new_h), Image.BILINEAR)
            # Crop or pad back to 32x32
            img_array = np.array(img, dtype=np.float32)
            if new_h < 32 or new_w < 32:
                padded = np.zeros((32, 32, 3), dtype=np.float32)
                padded[:min(32,new_h), :min(32,new_w)] = img_array[:32, :32]
                result = padded
            else:
                result = img_array[:32, :32]
    
    return result.astype(np.uint8)


class HeavilyAugmentedDataset(Dataset):
    """Dataset with HEAVY on-the-fly augmentation."""
    
    def __init__(self, X, y, augment=True, augmentation_factor=20):
        self.X_original = X
        self.y_original = y
        self.augment = augment
        self.augmentation_factor = augmentation_factor if augment else 1
    
    def __len__(self):
        return len(self.X_original) * self.augmentation_factor
    
    def __getitem__(self, idx):
        original_idx = idx % len(self.X_original)
        crop = self.X_original[original_idx]
        label = self.y_original[original_idx]
        
        # Apply augmentation if enabled and not the first copy
        if self.augment and (idx >= len(self.X_original)):
            crop = augment_crop(crop)
        
        # Convert to tensor and normalize
        crop_tensor = torch.from_numpy(crop).permute(2, 0, 1).float() / 255.0
        
        return crop_tensor, label


def train_from_scratch(output_path='chess_cnn_real_only.pth',
                       epochs=50,
                       batch_size=32,
                       lr=0.001):
    """Train model from scratch on ONLY real crops."""
    print("=" * 60)
    print("TRAINING FROM SCRATCH ON REAL CROPS ONLY")
    print("=" * 60)
    
    # Load real crops
    print("\nLoading real crops...")
    data = np.load('dataset/real_crops.npz')
    X, y = data['X'], data['y']
    print(f"Loaded {len(X)} real crops")
    
    # Split 80/20
    split_idx = int(0.8 * len(X))
    indices = np.random.permutation(len(X))
    train_indices = indices[:split_idx]
    val_indices = indices[split_idx:]
    
    X_train, y_train = X[train_indices], y[train_indices]
    X_val, y_val = X[val_indices], y[val_indices]
    
    print(f"Train: {len(X_train)} samples (with 20x augmentation = {len(X_train)*20})")
    print(f"Val: {len(X_val)} samples (no augmentation)")
    
    # Create datasets
    train_dataset = HeavilyAugmentedDataset(X_train, y_train, augment=True, augmentation_factor=20)
    val_dataset = HeavilyAugmentedDataset(X_val, y_val, augment=False)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Create NEW model
    print(f"\nCreating new model...")
    model = ChessSquareCNN()
    print("Model created (training from scratch)")
    
    # Setup training
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'max', patience=5, factor=0.5)
    
    # Train
    print(f"\nTraining for {epochs} epochs (lr={lr})...")
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
        
        # Update learning rate
        scheduler.step(val_acc)
        
        if (epoch + 1) % 5 == 0 or val_acc > best_val_acc:
            print(f"Epoch {epoch+1}/{epochs}: "
                  f"Train Loss={avg_train_loss:.4f}, Train Acc={train_acc:.2f}%, "
                  f"Val Acc={val_acc:.2f}%")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), output_path)
            if (epoch + 1) % 5 == 0:
                print(f"  -> Saved best model (val_acc={val_acc:.2f}%)")
    
    print("-" * 60)
    print(f"\nTraining complete!")
    print(f"Best validation accuracy: {best_val_acc:.2f}%")
    print(f"Model saved to: {output_path}")
    
    return model


if __name__ == '__main__':
    train_from_scratch(
        output_path='chess_cnn_real_only.pth',
        epochs=50,
        batch_size=32,
        lr=0.001
    )
