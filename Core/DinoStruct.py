# Структуры данных представления динамограмм
import pandas as pd
from Core.const import *

# Данные для построения динамограммы. Небыло никаких преобразований данных. 
# Они прям из контроллера 

class OriginalDinoData:
    def __init__(self) -> None:
        self.Load_units = ["ft", "kg", "norm"] # Еденица измерения параметра Нагрузки
        self.Load_unit = 0 # По умолчанию еденица измерения футы 

        self.Load = [] # Нагрузка Фунты
        self.TimeIntervals = [] # Временные интервалы в секундах 

        # Вычесленные характеристики 
        self.TimeGrid = [] # Построенная сетка по времнеи в секундах 
        self.T = -1 # Общий период качания 
        self.DataSize = -1 # Общий размер входных данных 
    
    # Представление в табличной форме 
    def TablePrint(self):
        DF = []
        for i in range(0, self.DataSize):
            row = [self.Load[i], self.TimeGrid[i], self.TimeIntervals[i]]
            DF.append(row)
        col = ["Нагрузка [{0}]".format(self.Load_units[self.Load_unit]), "Сетка по времени [s]", "Временные интервалы [s]"]        
        return pd.DataFrame(DF, columns=col)
    

# Готовая динамограмма от Лафкина/Усова, Моя так же может быть конвертированна в данный формат 
class DinoData:
    def __init__(self) -> None:
        self.Load = [] # Нагрузка в фунтах 
        self.PolishRoadMovement = [] # Перемещение ПШ в  
        self.PolishRoadMovementMax = -1 # Максимальное смещение ПШ

        self.MinLoad = -1 # Минимальная нагрузка
        self.MaxLoad = -1 # Максимальная нагрузка 
        self.T = -1 # Период качания 

        self.Load_units = ["ft", "kg", "norm"] # Еденица измерения параметра Нагрузки
        self.Load_unit = 0 # По умолчанию еденица измерения футы 
        self.Load_prev_unit = 0 # Предыдущая еденица измерения до конвертации

        self.PolishRoadMovement_units = ["inch", "m", "norm"]
        self.PolishRoadMovement_unit = 0 # еденица измерения для перемещения
        self.PolishRoadMovement_prev_unit = 0 # Предыдущая еденица измерения до конвертации

        # Вспомогательные данные вычисляются 
        self.RavTimeGrid = [] # Равномерная сетка по времени 
    
    def TablePrint(self):
        DF = []
        for i in range(0, DINO_SIZE):
            row = [self.Load[i], self.PolishRoadMovement[i], self.RavTimeGrid[i]]
            DF.append(row)
        col = ["Нагрузка [{0}]".format(self.Load_units[self.Load_unit]), "Перемещение [{0}]".format(self.PolishRoadMovement_units[self.PolishRoadMovement_unit]), "Время [c]"]
        pd.set_option('display.float_format', '{:.2f}'.format)
        DF = pd.DataFrame(DF, columns=col)    
        return DF

class MyDinoData:
    def __init__(self, Data:OriginalDinoData, LoadErrorCoef = 0.03, PolishRoadMovementErrorCoef = 0.0001,Load_unit = 0 ,PolishRoadMovement_unit = 0 ) -> None:

        self.OrigData = Data # Входные данные для построение динамограммы 
        
        self.Load_units = ["ft", "kg", "norm"] # Еденица измерения параметра Нагрузки
        self.Load_unit = Load_unit # По умолчанию еденица измерения футы 
        self.Load_prev_unit = 0 # Предыдущая еденица измерения до конвертации

        self.PolishRoadMovement_units = ["inch", "m", "norm"]
        self.PolishRoadMovement_unit = PolishRoadMovement_unit # еденица измерения для перемещения
        self.PolishRoadMovement_prev_unit = 0 # Предыдущая еденица измерения до конвертации

        # Полученная динамограмма 
        self.Load = [] # Нагрузка в фунтах 200 точек  
        self.PolishRoadMovement = [] # Перемещение ПШ в 200 точек 
        self.MinLoad = -1 # Минимальная нагрузка
        self.MaxLoad = -1 # Максимальная нагрузка 
        self.T = -1 # Период качания 
        self.LoadErrorCoef = LoadErrorCoef # Ошибка для нагрузки 3%
        self.PolishRoadMovementErrorCoef = PolishRoadMovementErrorCoef # Ошибка для перемещения 0.01%

        # Вспомогательные данные 
        self.PRData = [] # Массив перемещений построенный на неравномерной сетке 
        self.RavTimeGrid = [] # Равномерная сетка по времени  
        self.PhiGrid = [] # Угловая сетка  
    
    def MyDinoData2DinoData(self) -> DinoData:
        DinData: DinoData = DinoData()
        DinData.Load = self.Load
        DinData.PolishRoadMovement = self.PolishRoadMovement
        DinData.MinLoad = self.MinLoad
        DinData.MaxLoad = self.MaxLoad
        DinData.RavTimeGrid = self.RavTimeGrid
        DinData.T = self.T

        DinData.Load_unit = self.Load_unit
        DinData.PolishRoadMovement_unit = self.PolishRoadMovement_unit

        return DinData
    
    def TablePrint(self):
        return self.MyDinoData2DinoData().TablePrint()