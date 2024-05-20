import numpy as np

def geometric_median(X, eps=1e-5):
    y = np.mean(X, axis=0)
    
    while True:
        D = np.linalg.norm(X - y, axis=1)
        nonzeros = (D != 0)
        
        if not np.any(nonzeros):
            return y
        
        Dinv = 1 / D[nonzeros]
        Dinvs = np.sum(Dinv)
        W = Dinv / Dinvs
        T = np.sum(W[:, None] * X[nonzeros], axis=0)
        
        num_zeros = len(X) - np.sum(nonzeros)
        if num_zeros == 0:
            y1 = T
        elif num_zeros == len(X):
            return y
        else:
            R = (T - y) * Dinvs
            r = np.linalg.norm(R)
            if r < eps:
                return y
            else:
                y1 = T + R * (1 / (r * Dinvs))
        
        if np.linalg.norm(y - y1) < eps:
            return y1
        
        y = y1