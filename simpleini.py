# Any copyright is dedicated to the Public Domain.
# https://creativecommons.org/publicdomain/zero/1.0/

# Версия 2023-01-21

class SimpleIni(dict):
    """Читает простейший ini-подобный файл в словарь.

    Ini-файл содержит строки вида ключ-значение, разделенные символом(символами) sprVal (по умолчанию \"=\").
    Каждая строка может включать комментарий, отделенный символом (символами) sprComm (по умолчанию \"#\")
    Ключи могут дублироваться, ключу присваивается последнее встретившееся значение.
    При последовательном чтении нескольких файлов ключи в словаре объединяются.

    """

    def read_from_file(self, filename: str, sprComm: str, sprVal: str) -> None:
        """Читает значения из файла.

        Исключения при чтении файла не обрабатываются.

        """

        with open(filename,'r',encoding='utf-8-sig') as mFile:
            while True:
                line = mFile.readline()
                if line == '':
                    break
                
                # очищаем строку от комментария
                line = line.split(sprComm)[0]
                
                fields = line.split(sprVal)
                # если прочитали не менее двух полей, вставляем в ключ-значение
                if len(fields) > 1:
                    self[fields[0].strip()] = fields[1].strip()
