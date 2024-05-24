# Мат. Модель построения динамограммы 
import numpy as np
from const import *
from PRPos import *
from DinoStruct import *
from DataLoader import *
from Interpolation import *

class MakeDino:
    def __init__(self, filename, param: SKParam, PRPos_v = 2,  LoadErrorCoef = 0.03, PolishRoadMovementErrorCoef = 0.0001,prepare = True ,Load_unit = 1) -> None:
        self.DinoData:MyDinoData = MyDinoData(LoadOriginalDinoData(filename, prepare, Load_unit),  LoadErrorCoef, PolishRoadMovementErrorCoef)
        self.DinoData.Load_unit = Load_unit
        self.DinoData.PolishRoadMovement_unit = 1 # Расчет ведется в метрах 
        
        PRpos:PRPos = PRPos(param) # Модель перемещения ПШ 
        # Генерация угловой сетки  
        self.DinoData.T = self.DinoData.OrigData.T
        self.DinoData.PhiGrid = [(i*360.0)/(self.DinoData.OrigData.DataSize-1) for i in range(0, self.DinoData.OrigData.DataSize)]

        # Генерация равномерной сетки по времени 
        self.DinoData.RavTimeGrid = [(i*self.DinoData.T)/(DINO_SIZE-1) for i in range(0, DINO_SIZE)]
        # Генерация массива перемещений по не равномерной сетке
        if PRPos_v == 1:
            self.DinoData.PRData = [PRpos.PRPos_v1(phi_i) for phi_i in self.DinoData.PhiGrid]
        elif PRPos_v == 2:
            self.DinoData.PRData = [PRpos.PRPos_v2(phi_i) for phi_i in self.DinoData.PhiGrid]
            #self.DinoData.PRData = [1.75*(1-np.cos(2*np.pi*ti/self.DinoData.T)) for ti in self.DinoData.OrigData.TimeGrid]
        elif PRPos_v == 3:
            self.DinoData.PRData = [PRpos.PRPos_v3(phi_i) for phi_i in self.DinoData.PhiGrid]
        
        # Построение массива ошибок 
        self.DinoData.LoadErrorLvl = [L*self.DinoData.LoadErrorCoef for L in self.DinoData.OrigData.Load]
        
        x0 = np.min(self.DinoData.PRData)
        self.DinoData.PolishRoadMovementErrorLvl = [(P- x0)*self.DinoData.PolishRoadMovementErrorCoef for P in self.DinoData.PRData]

        self._GenDino() # Построение динамограммы 

    def _CalcIdxInterval(self, idx):
        
        # Для алгоритма нужно 6 точек. По сетке. 
        # Если idx = 0 то 0,1,2,3,4,5
        # Если idx = 1 то 0, 1, 2, 3, 4, 5
        # Если idx = 2 то 0, 1,2,3,4,5
        # Если idx = 3...size - 3 то idx-3,idx-2, idx-1, idx, idx+1, idx+2
        # Если idx = size - 2 ... size -1 

        # DataIdx = [-1,-1,-1,-1,-1,-1] # Массив индексов в массиве выборки 
        # if idx >= 0 and idx <= 2: DataIdx = [0,1,2,3,4,5]
        # elif (idx >= 3 and idx <= len(self.DinoData.OrigData.TimeGrid) - 3): DataIdx = [idx-3, idx-2, idx-1, idx, idx+1, idx+2]
        # elif(idx == len(self.DinoData.OrigData.TimeGrid)-2): DataIdx = [idx-4, idx-3, idx-2, idx-1, idx, idx+1]
        # else: DataIdx = [idx-5, idx-4, idx-3, idx-2, idx-1, idx]
        
        DataIdx = [-1,-1,-1,-1] # Массив индексов в массиве выборки 
        if idx >= 0 and idx <= 2: DataIdx = [0,1,2,3]
        elif (idx >= 3 and idx <= len(self.DinoData.OrigData.TimeGrid) - 3): DataIdx = [ idx-1, idx, idx+1, idx+2]
        elif(idx == len(self.DinoData.OrigData.TimeGrid)-2): DataIdx = [ idx-2, idx-1, idx, idx+1]
        else: DataIdx = [ idx-3, idx-2, idx-1, idx]

        return DataIdx

    # Расчет перемезщения 
    def _CalcX(self, point):      
        # Для рачета 
        res = -1.0 # Результат вычисления функции в точке 
        epsiloninterp = 0.0
        # Получаем индекс отрезка которому точка принадлежит 
        idx = 0
        for i in range(0, len(self.DinoData.PRData)-1):
            if ((point - self.DinoData.OrigData.TimeGrid[i])>= EPS and (point - self.DinoData.OrigData.TimeGrid[i+1]) <= EPS):
                idx = i
                break

        DataIdx = self._CalcIdxInterval(idx)
        x = np.array([self.DinoData.OrigData.TimeGrid[i] for i in DataIdx])
        y = np.array([self.DinoData.PRData[i] for i in DataIdx])

        if (point <= EPS):
            res = self.DinoData.PRData[0]
        elif ((abs(point-self.DinoData.OrigData.TimeGrid[len(self.DinoData.OrigData.TimeGrid)-1])) <= EPS):
            res = self.DinoData.PRData[len(self.DinoData.PRData)-1]
        else:
            #res, epsiloninterp = Aiteiken(x, y, point)
            res = LagrangePoly(x,y).interpolate(point)
        return res, epsiloninterp
    
    # Расчет усилия 
    def _CalcF(self, point):
        # Для рачета 
        res = -1.0 # Результат вычисления функции в точке 
        epsiloninterp = 0.0
        # Получаем индекс отрезка которому точка принадлежит 
        idx = 0
        for i in range(0, len(self.DinoData.PRData)-1):
            if (self.DinoData.OrigData.TimeGrid[i] <= point and point <= self.DinoData.OrigData.TimeGrid[i+1]):
                idx = i
                break
            

         # Для алгоритма нужно 6 точек. По сетке. 
        # Если idx = 0 то 0,1,2,3,4,5
        # Если idx = 1 то 0, 1, 2, 3, 4, 5
        # Если idx = 2 то 0, 1,2,3,4,5
        # Если idx = 3...size - 3 то idx-3,idx-2, idx-1, idx, idx+1, idx+2
        # Если idx = size - 2 ... size -1  
    
        DataIdx = self._CalcIdxInterval(idx)

        x = np.array([self.DinoData.OrigData.TimeGrid[i] for i in DataIdx])
        y = np.array([self.DinoData.OrigData.Load[i] for i in DataIdx])

        if (point <= EPS):
            res = self.DinoData.OrigData.Load[0]
        elif ((abs(point-self.DinoData.OrigData.TimeGrid[len(self.DinoData.OrigData.TimeGrid)-1])) <= EPS):
            res = self.DinoData.OrigData.Load[len(self.DinoData.OrigData.Load)-1]
        else:
            #res, epsiloninterp = Aiteiken(x, y, point)
            res = LagrangePoly(x,y).interpolate(point)
        
        return res, epsiloninterp        
    
    # Расчет динамошграммы
    def _GenDino(self):
        
        for x in self.DinoData.RavTimeGrid:
            f = self._CalcF(x)
            pr_pos = self._CalcX(x)
            self.DinoData.Load.append(f[0])
            
            self.DinoData.PolishRoadMovement.append(pr_pos[0])
            
            

        
        self.DinoData.MaxLoad = np.max(self.DinoData.OrigData.Load)
        self.DinoData.MinLoad = np.min(self.DinoData.OrigData.Load) 

        # Приводим к нужной размерности
        x0 = np.min(self.DinoData.PolishRoadMovement)
        self.DinoData.PolishRoadMovement = [xi - x0 for xi in self.DinoData.PolishRoadMovement]

        if self.DinoData.Load_unit == 2:
            max_p = np.max(self.DinoData.PolishRoadMovement)
            self.DinoData.PolishRoadMovement = [P/max_p for P in self.DinoData.PolishRoadMovement]

        #self.DinoData.PolishRoadMovement.reverse()
        # for i in range(0, 100):
        #     self.DinoData.PolishRoadMovement[199-i] = self.DinoData.PolishRoadMovement[i]
