import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import pickle

data = np.load('dataset/real_crops_verified.npz')
X, y = data['X'], data['y']
X_flat = X.reshape(len(X), -1)

knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_flat, y)

with open('knn_model.pkl', 'wb') as f:
    pickle.dump(knn, f)

print('k-NN (k=3) restored')
