class SimpleTab:
    __columns = {}
    __header  = {}
    __index   = {}
    __rows    = 0

    @property
    def columns(self):
        return(self.__columns)

    @property
    def header(self):
        return(self.__header)

    @property
    def index(self):
        return(self.__index)

    @property
    def rows(self):
        return(self.__rows)

    def get_row(self, idx):
        outTuple = {}
        for key in self.__header:
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
                        self.__header[field]  = idx
                        self.__index[idx]     = field
                    continue
                
                for idx in range(min(len(fields),len(self.__index))):
                    self.__columns[self.__index[idx]].append(fields[idx].strip())
                self.__rows = self.__rows + 1