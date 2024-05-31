import numpy as np

class ContollErrorCalc:

  def __init__(self, func,N,T) -> None:
    """
    func - Функция которую хотим считать при помощи интерполяции \\
    N    - Количество точек в интервале \\
    T    - Период функции \\
    """
    self.func = func # Просчитываемая функция
    self.N = N # Точек в интерполяции
    self.T = T # Период функции

    ##### Переменные для расчета
    self.h = T/N
    self.X = [np.round(i*self.h, 15) for i in range(0, N+1)]
    self.Y = [np.round(func(xi), 15) for xi in self.X]

  def ReInit(self, func, N, T):
    """
    func - табулируемая функция \\
    N - число отсчетов функции \\
    T - период функции \\
    @return: void \\
    """
    self.func = func # Просчитываемая функция
    self.N = N # Точек в интерполяции
    self.T = T # Период функции
    
    ##### Переменные для расчета
    self.h = T/N
    self.X = [np.round(i*self.h, 15) for i in range(0, N+1)]
    self.Y = [np.round(func(xi), 15) for xi in self.X]

  def _Bring2Interval(self, x):
    """
    Приведение аргумента функции к интервалу интерполяции
    """
    N = np.abs(int(x/self.T))
    
    if x >= self.T:
      x = x - N*self.T
    elif x <= 0:
      x = x + (N+1)*self.T
    
    return x

  def Calc(self, x):
    """
    x - Аргумент функции для расчета
    @return: (f(x); eps) - значение и точность расчета
    """
    x = self._Bring2Interval(x)
    n0 = int(x/self.h)
    n1 = n0 + 1
    if n0 == self.N:
      n0 = self.N-1
      n1 = self.N
    x0 = n0*self.h
    x1 = n1*self.h
    y0 = self.Y[n0]
    y1 = self.Y[n1]

    res = y0 + ((y1-y0)/(x1-x0))*(x-x0)
    return res, np.abs(self.func(x) - res)

# Пример использования
# FastF:ContollErrorCalc = ContollErrorCalc(func=np.sin, N = 512, T = 2*np.pi)

  

# x = np.linspace(0, 400*np.pi, 1000000)
# eps = [FastF.Calc(xi)[1] for xi in x]
# print(np.max(eps))


# FastF.ReInit(func=np.sin, N = 1024, T = 2*np.pi)
# eps = [FastF.Calc(xi)[1] for xi in x]
# print(np.max(eps))