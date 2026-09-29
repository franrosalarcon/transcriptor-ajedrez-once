import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score

data = np.load('dataset/real_crops_verified.npz')
X, y = data['X'], data['y']

X_flat = X.reshape(len(X), -1)

print('Testing k-NN (k=1) on', len(X), 'real crops with cross-validation...')

knn = KNeighborsClassifier(n_neighbors=1)
scores = cross_val_score(knn, X_flat, y, cv=5, scoring='accuracy')

print()
print('Cross-validation accuracy: {:.1f}% (+/- {:.1f}%)'.format(scores.mean()*100, scores.std()*100))
print('Individual folds:', ['{:.1f}%'.format(s*100) for s in scores])

if scores.mean() > 0.95:
    print()
    print('OK: Crops are GOOD (>95%). Problem is CNN training.')
    print('Paso 4 will work: train on realistic synthetics.')
else:
    print()
    print('BAD: Crops still have issues ({:.1f}% < 95%).'.format(scores.mean()*100))
