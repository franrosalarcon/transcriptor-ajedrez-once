import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import pickle
import torch
import torch.nn as nn

# Load real crops
data = np.load('dataset/real_crops_verified.npz')
X, y = data['X'], data['y']
X_flat = X.reshape(len(X), -1)

print(f'Training k-NN on {len(X)} real crops...')

# Train k-NN (k=3 for robustness)
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_flat, y)

# Save model
with open('knn_model.pkl', 'wb') as f:
    pickle.dump(knn, f)

print('k-NN model saved to knn_model.pkl')

# Create simple wrapper class that matches CNN interface
class KNNClassifier:
    def __init__(self, model_path):
        with open(model_path, 'rb') as f:
            self.knn = pickle.load(f)
    
    def eval(self):
        pass
    
    def __call__(self, X):
        # X is torch tensor (N, C, H, W)
        X_np = X.permute(0, 2, 3, 1).numpy()
        X_flat = X_np.reshape(len(X_np), -1)
        predictions = self.knn.predict(X_flat)
        
        # Return as torch tensor mimicking CNN output
        class FakeOutput:
            def __init__(self, preds):
                self.data = torch.zeros(len(preds), 13)
                for i, p in enumerate(preds):
                    self.data[i, p] = 1
        
        return FakeOutput(predictions)

print('Testing k-NN classifier...')
print('Use it by loading: processor = BoardProcessor(\"knn_model.pkl\")')
