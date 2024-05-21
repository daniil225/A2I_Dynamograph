# Функции интерполяции

import numpy as np
from const import *


def Aiteiken(x, y, xp):
    """
    Интерполяция лагранжа 
    :bug Схема работает не корректно. Не проходит тест узлы интерполяции. При этом наблюдается сильная осциляция при интерполировании 
    """
    idx = 0
    for i in range(0, len(x)-1):
        if ( xp >= x[i] and  x[i+1] >= xp ):
            idx = i
            break
    p = np.zeros((len(x), len(x)))
    # Выставляем стартовое значение
    step = 0
    for i in range(len(x)):
        p[i,i] = y[i]
    step += 1
    eps = np.ones((len(x), len(x)))
    
    # Расчет матрицы 
    for step in range(1, len(x)):
        for i in range(0, len(x)-step):
            j = i + step
            p[i,j] = (1.0/(x[j] - x[i]))*((xp - x[i])*p[i+1, j] - (xp - x[j])*p[i, j-1] )


    for i in range(0, len(x)):
        for j in range(i+1, len(x)):
            eps[i, j] = np.abs(p[i, j] - p[i, j-1])
            if eps[i, j] < EPS:
                break

    idx = 0
    min_eps = 1.0
    for i in range(0, len(x)):
        for j in range(i+1, len(x)):
            if min_eps > eps[i][j] and (x[i] <= xp and x[j] >= xp):
                idx = i*len(x) + j
                min_eps = eps[i][j]
    
    i = int(idx / len(x))
    j = idx % len(x)
    return p[i,j], eps[i,j]

class LagrangePoly:
        """
            Класс интерполирующий полиномами лагранжа. Степень полинома определается количеством входных точек.
        """

        def __init__(self, X, Y):
            self.n = len(X)
            self.X = np.array(X)
            self.Y = np.array(Y)

        def basis(self, x, j):
            b = [(x - self.X[m]) / (self.X[j] - self.X[m])
                 for m in range(self.n) if m != j]
            return np.prod(b, axis=0) * self.Y[j]

        def interpolate(self, x):
            b = [self.basis(x, j) for j in range(self.n)]
            return np.sum(b, axis=0)