# Any copyright is dedicated to the Public Domain.
# https://creativecommons.org/publicdomain/zero/1.0/

# Версия 2023-01-24

class SimpleTab:

    """простая колоночная таблица"""

    def __init__(self):
        self.__columns = {} # словарь списков, где ключ является именем поля, список - значениями колонки этого поля
        self.__header  = {} # имена полей по индексу, для перебора полей по порядку
        self.__rows    = 0  # количество строк в таблице

    @property
    def columns(self):
        return(self.__columns)

    @property
    def header(self):
        return(self.__header)

    @property
    def rows(self):
        return(self.__rows)

    def get_row(self, idx):
        # получаем по индексу кортеж полей, имитирующих строку таблицы
        outTuple = {}
        for key in self.__columns.keys():
            outTuple[key] = self.__columns[key][idx]
        return outTuple

    def read_from_file(self, filename: str, sprComm: str, sprVal: str) -> None:

        with open(filename,'r',encoding='utf-8-sig') as mFile:
            first = True
            while True:
                line = mFile.readline()
                if line == '':
                    break
                
                # очищаем строку от комментария
                line = line.strip().split(sprComm)[0]
                if line == '':
                    continue
                
                fields = line.strip().split(sprVal)

                if first:
                    # обрабатываем заголовки
                    first = False
                    for idx in range(len(fields)):
                        field = fields[idx].strip()
                        if field == '':
                            continue
                        if field in self.__columns.keys():
                            continue
                        self.__columns[field] = []
                        self.__header[idx]     = field
                    continue
                
                for idx in range(min(len(fields),len(self.__header))):
                    self.__columns[self.__header[idx]].append(fields[idx].strip())
                self.__rows = self.__rows + 1