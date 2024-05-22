from const import *
import sqlite3
from pathlib import Path
import random, string


class TableData:
    def __init__(self, file_path, create_time, type_RKM, id_RKM) -> None:
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

        self.conn = sqlite3.connect(self.DBName) # Подключение к БД
        self.curr = self.conn.cursor() # Курсор для выполнения запросов 

        # Создаем если нужно таблицы в БД
        self._create_table(self.TableOriginData)
        self._create_table(self.TableUsovData)
        self._create_table(self.TableLufkinData)


    def _create_table(self, tablename):
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
    
    def insert(self, tablename, data:TableData):
        """
        param: tablename - имя таблицы в которую нужно добавить данные. 
        param: data:TableData - формат данных 
        """
        print(data.file_path)
        self.curr.execute('INSERT INTO {table} (file_path, create_time,type_RKM,id_RKM) VALUES (?, ?, ?, ?)'.format(table = tablename), (data.file_path, data.create_time, data.type_RKM, data.id_RKM))
        self.conn.commit()


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
    
    
    def move_data(self, origin_data = None, usov_dino = None, lufkin_dino = None):
        """
        Производит перенос данных из каталога tmp в каталог db. 
        :return - list of TableData 
        """
        res = []

        # origin_data
        if origin_data != None:
            for file in list(glob(os.path.join(TMP_DATA_DIR,origin_data+"*.txt"))):
                # Get file creation time of file in seconds since epoch
                creationTimesinceEpoc = os.path.getctime(file)
                creationTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(creationTimesinceEpoc))
                res.append(self._gen_new_filename("origin_data_", creationTime))
        
        # usov_dino
        if usov_dino != None:
            pass

        # lufkin_dino
        if lufkin_dino != None:
            pass

        
        return res


import shutil
from glob import glob
import os
import time


fl = FileManager()

print(fl.move_data("data"))


#DB = DBManager()
#DB.insert(DB.TableOriginData, TableData("test.txt", "2024-05-19 17:00:00", "СК8-3,5-4000", "16427"))
#DB.close()