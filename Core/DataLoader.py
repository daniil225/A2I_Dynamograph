from DinoStruct import *
import numpy as np
from const import *

def LoadDinoData(filename, Load_unit = 0, PolishRoadMovement_unit = 0) -> DinoData:
    DinDat: DinoData = DinoData()

    file = open(filename, 'r')
    for i in range(0, 5):
        file.readline()

    DinDat.T = float(file.readline().strip().split(";")[0])/100

    Time_i = 0.0
    TimeStep = DinDat.T/(DINO_SIZE-1)

    while True:
        line = file.readline().strip()
        if line == '':
            break
        
        
        line = line.split(";")
        DinDat.RavTimeGrid.append(Time_i)
        DinDat.Load.append(float(line[1]))
        DinDat.PolishRoadMovement.append(float(line[0]))
        
        Time_i += TimeStep

    # Ставим еденицу измерения
    DinDat.Load_unit = Load_unit
    DinDat.PolishRoadMovement_unit = PolishRoadMovement_unit
    
    if Load_unit == 0:
        DinDat.MaxLoad = np.max(DinDat.Load)
        DinDat.MinLoad = np.min(DinDat.Load)
    
    # Нормировка к [кг] 
    if Load_unit == 1:
        DinDat.Load = [L*FT1KG for L in DinDat.Load]
        DinDat.MaxLoad = np.max(DinDat.Load)
        DinDat.MinLoad = np.min(DinDat.Load)

    if PolishRoadMovement_unit == 0:
        DinDat.PolishRoadMovementMax = np.max(DinDat.PolishRoadMovement)

    # Нормировка к [м] 
    if PolishRoadMovement_unit == 1:
        DinDat.PolishRoadMovement = [P*DU2M for P in DinDat.PolishRoadMovement]
        DinDat.PolishRoadMovementMax = np.max(DinDat.PolishRoadMovement)

    # Нормировка к максимальному значению 
    if Load_unit == 2:
        DinDat.MaxLoad = np.max(DinDat.Load)
        DinDat.MinLoad = np.min(DinDat.Load)
        DinDat.Load = [L/DinDat.MaxLoad for L in DinDat.Load]

    # Нормировка к максимальному значению 
    if PolishRoadMovement_unit == 2:
        DinDat.PolishRoadMovementMax = np.max(DinDat.PolishRoadMovement)
        DinDat.PolishRoadMovement = [P/DinDat.PolishRoadMovementMax for P in DinDat.PolishRoadMovement]

    return DinDat


Din =  LoadDinoData("../tmp_data/dino_lufkin3.txt")
print(Din.TablePrint())



# bool prepare = True - Предподготовка данных для обработки 
# Load_unit = 0, PolishRoadMovement_unit = 0 - Нормировка данных 
def LoadOriginalDinoData(filename,prepare = True ,Load_unit = 0) -> OriginalDinoData:
    OrigData: OriginalDinoData = OriginalDinoData()
    file = open(filename, 'r')
    for i in range(0, 3):
        file.readline()

    OrigData.DataSize = int(file.readline().strip().split(';')[0])
    file.readline()

    Time_i = 0.0

    for i in range(0, OrigData.DataSize):
        line = file.readline().strip().split(';')
        Time_i = Time_i + float(line[1])/1000.0 # Перевод в секунды 

        OrigData.Load.append(float(line[0]))

        OrigData.TimeGrid.append(Time_i)
        OrigData.TimeIntervals.append(float(line[1]))
    
    file.close()
    
    OrigData.T = OrigData.TimeGrid[OrigData.DataSize-1]
    
    if prepare:
        OrigData.Load.insert(0, OrigData.Load[OrigData.DataSize-1])
        OrigData.TimeGrid.insert(0,0.0)
        OrigData.TimeIntervals.insert(0,0.0)
        OrigData.DataSize += 1
        OrigData.TimeIntervals = [ti/1000.0 for ti in OrigData.TimeIntervals] # Приводим к секундам 
    
    
    # Ставим еденицу измерения
    OrigData.Load_unit = Load_unit

    # Нормировка к [кг] 
    if Load_unit == 1:
        OrigData.Load = [L*FT1KG for L in OrigData.Load]
        OrigData.MaxLoad = np.max(OrigData.Load)
        OrigData.MinLoad = np.min(OrigData.Load)

    # Нормировка к 1
    if Load_unit == 2:
        OrigData.MaxLoad = np.max(OrigData.Load)
        OrigData.MinLoad = np.min(OrigData.Load)
        OrigData.Load = [L/OrigData.MaxLoad for L in OrigData.Load]


    return OrigData