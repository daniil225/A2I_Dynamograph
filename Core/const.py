import os

# Core const

# Расчетные константы 
FT1KG = 0.453592 # Коэффициент перевода фунтов в килограммы
KG2FT = 2.204623 # Коэффициент перевода килограмм в футы
DU2M = 0.000254  # Коэффициент перевода дюймов в метры 
EPS = 1e-7       # Требуемая точность вычислений 
DINO_SIZE = 200  # Размер динамограммы 200 точек 

#Настройка корректных путей до файлов 

def get_root_dir():
    tmp = os.getcwd().split("\\")
    path = ""
    for e in range(0, len(tmp)):
        path += tmp[e] + "/"
    
    return path


root_dir = get_root_dir()
# Настройки БД
DB_NAME = os.path.join(root_dir, "DB_data", "Dino.db")
TABLE_ORIGIN_DATA = "Origin_Data"
TABLE_USOV_DATA = "Usov_dino"
TABLE_LUFKIN_DATA = "Lufkin_dino"

# Настройки путей/шаблонов данных
TMP_DATA_DIR =   os.path.join(root_dir,"tmp_data")
DB_DATA_DIR =  os.path.join(root_dir,"DB_data")