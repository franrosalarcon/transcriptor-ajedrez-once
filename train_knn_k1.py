import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import pickle

data = np.load('dataset/real_crops_verified.npz')
X, y = data['X'], data['y']
X_flat = X.reshape(len(X), -1)

print(f'Training k-NN with k=1 on {len(X)} real crops...')

knn = KNeighborsClassifier(n_neighbors=1)
knn.fit(X_flat, y)

with open('knn_model.pkl', 'wb') as f:
    pickle.dump(knn, f)

print('k-NN (k=1) model saved')
