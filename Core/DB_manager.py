# Пользовотельские
from Core.const import *


import sqlite3, os, time, shutil,random, string
from glob import glob



class TableData:
    def __init__(self, file_path:str, create_time:str, type_RKM:str, id_RKM:str) -> None:
        self.file_path = file_path  # Путь 
        self.create_time = create_time # Время создания
        self.type_RKM = type_RKM # Тип станка качалки
        self. id_RKM = id_RKM # Id станка качалки с которого тянутся данные



class DBManager:
    """
    Управление БД динамограмм. 
    1. Позволяет вносить данные в БД \\
    2. Получать данные из нее с параметром сортировки по времени 
    """
    
    def __init__(self) -> None:

        self.DBName = DB_NAME
        self.TableOriginData = TABLE_ORIGIN_DATA
        self.TableUsovData = TABLE_USOV_DATA
        self.TableLufkinData = TABLE_LUFKIN_DATA

        #print(self.DBName)
        self.conn = sqlite3.connect(self.DBName) # Подключение к БД
        
        self.curr = self.conn.cursor() # Курсор для выполнения запросов 

        # Создаем если нужно таблицы в БД
        self._create_table(self.TableOriginData)
        self._create_table(self.TableUsovData)
        self._create_table(self.TableLufkinData)


    def _create_table(self, tablename:str):
        self.curr.execute('''
            CREATE TABLE IF NOT EXISTS {table} (
            id INTEGER PRIMARY KEY,
            file_path TEXT NOT NULL,
            create_time TEXT NOT NULL,
            type_RKM TEXT NOT NULL,
            id_RKM TEXT NOT NULL            
            )
            '''.format(table=tablename)
        )
    
    def insert(self, tablename:str, data:TableData):
        """
        param: tablename - имя таблицы в которую нужно добавить данные. 
        param: data:TableData - формат данных 
        """
        self.curr.execute('INSERT INTO {table} (file_path, create_time,type_RKM,id_RKM) VALUES (?, ?, ?, ?)'.format(table = tablename), (data.file_path, data.create_time, data.type_RKM, data.id_RKM))
        self.conn.commit()

    def get_data_by_time(self, tablename:str, time_from:str, time_to:str):
        res = []
        self.curr.execute(''' SELECT *
                          FROM {0}
                          WHERE create_time BETWEEN '{1}' AND '{2}'

                        '''.format(tablename, time_from, time_to))

        data = self.curr.fetchall() # Получить результат из БД
        for d in data:
            td:TableData = TableData(d[1], d[2], d[3], d[4])
            res.append(td)

        return res

    def close(self):
        self.conn.close()


class FileManager:
    """
    Переносим файлы определенного шаблона из папки tmp_data в папку DB_data для управления данными.Нужно для того что бы добавить их \\
    в таблицу контроля в БД 

    временные файлы хранения информации о динамограммах переносятся в каталог и переименовываются в соответсвующий формат: \\
    Например origin_datanum.txt -> origin_data_YYYY_MM_DD_HH:MM:SS.txt \\
    с остальными типами файлов аналогично. 
    """
    def __init__(self) -> None:
        
        self.src_dir = TMP_DATA_DIR # Исходный каталог. Из него тянем данные 
        self.dst_dir = DB_DATA_DIR # Каталог куда будем складывать все данные 


    def _randomword(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))


    def _gen_new_filename(self, base, time_creation):
        tm = time_creation.split()
        return base + tm[0] + "_" + tm[1] + "_" + self._randomword(10) + ".txt"
    
    
    def move_data(self, data = None, base_name = None):
        """
        Производит перенос данных из каталога tmp в каталог db. 
        :return - list of TableData 
        """
        res = []

        # origin_data
        if data != None:
            for file in list(glob(os.path.join(self.src_dir, data+"*.txt"))):
                # Get file creation time of file in seconds since epoch
                creationTimesinceEpoc = os.path.getctime(file)
                creationTime = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(creationTimesinceEpoc))
                if base_name != None:
                    new_filename = self._gen_new_filename(base_name+"_", creationTime)
                    new_dst = self.dst_dir + "/" +  new_filename
                    res.append(new_dst)
                    shutil.move(file, new_dst)

        
        return res


# Служебные объекты
DataBaseManager = DBManager() # Установили соединение с бд


# Функция добавления файлов в БД и перенос в индексируемую дирректорию нужной информации 
def file_indexing(data:str, base_name:str, type_RKM = "СК8-3,5-4000", id_RKM = "16427"):
    fl = FileManager()
    files = fl.move_data(data=data, base_name=base_name)
    
    for file in files:
        filename = file.split("/")
        filename = filename[len(filename)-1]
        d = filename.split("_")[2]
        t_ = filename.split("_")[3].split("-")
        t = t_[0] + ":" + t_[1] + ":" + t_[2]
        res_t = d + " " + t
        td:TableData = TableData(filename, res_t, type_RKM, id_RKM)

        if base_name == "origin_data":
            DataBaseManager.insert(DataBaseManager.TableOriginData, td)
        elif base_name == "usov_dino":
            DataBaseManager.insert(DataBaseManager.TableUsovData, td)
        elif base_name == "lufkin_dino":
            DataBaseManager.insert(DataBaseManager.TableLufkinData, td)

# Закрытия соединения с БД
def DB_close():
    DataBaseManager.close()



