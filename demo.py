# Any copyright is dedicated to the Public Domain.
# https://creativecommons.org/publicdomain/zero/1.0/

# Версия 2023-01-25

from sys import argv as sysArgv

from simpleini import SimpleIni as Ini
from simpletab import SimpleTab as Tab
import mixednum as MNum
from rationals import Rational as Frac
from mixedstr import MixedString as MStr

class main:

# ==========METHODS[

    def show_help(self, inStr = ''):
        """Справка."""
        """При вызове с параметром (методом) выведет справку по этому методу.
Справка о самом себе вызовет общий метод справки.

        """
        __msgHelp = """
Демострационный калькулятор операций со смешанными числами.
При запуске параметром можно передать файл со списком команд, которые будут выполнены.
(В таком файле можно указать команды настройки и инициализации данных
либо команды ввода и вычисления, в этом случае можно использовать перенаправление вывода 
в файл, чтобы получить результаты вычислений).

Вычисления:
Поддерживается последовательный ввод четырех арифметических операций, единственный регистр вычислений; 
Ввод ""=число"" помещает число в этот регистр.
Ввод одной из операций ""[+-*/%]число"" выполняет действие над текущим регистром и введенным числом.

Доступны дополнительные команды. Справку по команде можно получить, выполнив команду ""ПОМОЩЬ"", указав команду параметром
        """

        strTopic = inStr.strip().upper()
        if not strTopic:
            print(__msgHelp)
            outList = []
            for el in self.__mthSynonyms.keys():
                outList.append(el)
            print (outList)
            return True

        syn = self.__mthSynonyms.get(strTopic)
        if syn == self.__mthHelp:
            self._mthHelp()
            return True

        mth = self.__methods.get(self.__mthSynonyms.get(strTopic))
        if mth == self.__mthHelp:
            self.__mthHelp()
            return True

        if mth and mth.__doc__:
            print(mth.__doc__)
            return True
        
        print('Отсутствует справка по методу ', inStr)
        
        return True            

    def show_decimal(self, pars = None):
        """Показывает в десятичном виде числовые значения элементов смешанного числа в регистре
Само значение регистра не изменяется.

"""
        outList = []
        for elem in self.__register.list:
            outList.append('{dec}{name}'.format(
                dec  = Frac.decimal(elem.rational)
                ,name = (' ' + elem.name if elem.name else '')
                )
            )
        print ((self.__sprFld + ' ').join(outList))

    def clear_registers(self, pars = None):
        """Очищает регистры и таблицу курсов"""

        self.__register  = MNum.MixedNum() #put Zero in current register
        self.__archReg   = MNum.MixedNum() #put Zero in 'archive' register
        self.__converter = MNum.Converter()

    def show_convert(self, strMeasures):
        """Конвертирует число из текущего регистра в уазанные единицы и помещает результат в регистр.
Настройка конвертации задается параметром в виде списка единиц, разделенных аналогично частям смешанного числа (см. ФОРМ).
Если в конвертируемом числе присутствуют части с единицами, которые не могут быть приведены к указанным настройкам, эти части выводятся в конце как есть.
Для конвертации необходима установка курсов (см. КУРС).

"""
        measures = []
        for el in strMeasures.split(self.__sprFld):
            measures.append(el.strip())
        mNum = self.normalize(self.__converter.convert(self.__register, measures))
        self.__register = self.normalize(mNum)
        self.show_output(' => ', MNum.MixedNum())

    def show_compare(self, strNum):
        """Сравнивает текущее число в регистре с указанным числом."""

        mNum = MStr.from_string(strNum)
        intResult = self.__register.intComp(mNum, self.__converter)
        print (MStr.to_string(mNum))

        if intResult == 0:
            print ('Числа равны')
        elif intResult == 1:
            print ('Введенное число меньше')
        elif intResult == -1:
            print ('Введенное число больше')
        else:
            print('Сравнение неопределено')


    def show_rates(self, pars = None):
        """Выводит таблицу курсов."""
        print(str(self.__converter.rates))

    def show_measures(self, pars = None):
        """Выводит списки единиц из таблицы курсов, изолированные по ""сетам""."""
        print(self.__converter.measures)

    def show_ranged(self, pars = None):
        """Выводит общую ранжированную таблицу единиц."""
        for el in self.__converter.ranged:
            print(el)

# ==========]METHODS

# ==========EVALUATE[

    def evaluate(self, instr):
        """арифметические вычисления"""
        def isRegular(inMNum):
            measures = inMNum.names()
            return(len(measures) == 1 and not measures[0].strip())

        op = instr[0] if len(instr) > 0 else ' '

        sInp = instr[1:]
        mInp = MStr.from_string(sInp.strip())

        if op == '=':
            self.__register = mInp
        
        elif op == '+':
            #СЛОЖЕНИЕ
            self.__register = self.__register.compose(mInp)
        elif op == '-':
            #ВЫЧИТАНИЕ
            self.__register = self.__register.compose(mInp.with_rationals(Frac.opposite))
        elif op == '*':
            #УМНОЖЕНИЕ (только на обычное число, "увеличение в N раз")
            if isRegular(mInp):
                multiplicand = self.__register
                multiplier   = mInp
            elif isRegular(self.__register):
                multiplicand = mInp
                multiplier   = self.__register
            else:
                print('Перемножение двух смешанных чисел не определено')
                return False
            self.__register = multiplicand.with_rationals(Frac.mul, multiplier.list[0].rational)
        elif op == '/' or op == '%':
            #ДЕЛЕНИЕ (с остатком)
            try:
                if isRegular(mInp):
                    # на обычное число, "уменьшение в N раз"
                    quotient  = self.__register.with_rationals(Frac.mul, mInp.list[0].rational.reciprocal())
                    remainder = MNum.MixedNum((MNum.Elem(Frac()),)) # остаток всегда ноль
                else:
                    # на смешанное число, "исчерпывание" (в том числе и обычного числа)
                    result = self.__register.times(mInp, self.__converter)
                    quotient  = MNum.MixedNum((MNum.Elem(result[0]),))
                    remainder = result[1]

                if op == '/':
                    # результат - частное
                    print ('Остаток: ', MStr.to_string(self.normalize(remainder)))
                    self.__register = quotient
                else:
                    # результат - остаток
                    print ('Результат: ', MStr.to_string(self.normalize(quotient)))
                    self.__register = remainder
            except ZeroDivisionError as err:
                print(str(err))
                return False
        else:
            print('"' + instr + '" is incorrect')
            return False

        self.__register = self.normalize(self.__register)
        self.show_output(op,mInp)
        return True

    def normalize(self, mNum):
        """приводит число в более удобный вид"""
        return(mNum.with_rationals(Frac.mixed).with_rationals(Frac.reduce).pack())

    def show_output(self, op = '=>', opnd = None):
        """общий формат вывода после вычисления"""
        # пока не выводим ничего кроме собственно нового состояния регистра
        # (смешанное число и так громоздко на вид)
        print(MStr.to_string(self.__register))
    
# ==========]EVALUATE

# ==========INIT[

    def read_IO_settings(self, fileName):
        """Читает настройки ввода-вывода из файла.
Имя файла необходимо передать параметром команды.
Образец файла настроек:

sprFld  = ,  # Разделяет части смешанного числа
# относится к дроби внутри одной части смешанного числа:
sprInt  = .  # Отделяет целую часть от дробной
sprFrac = /  # Разделяет числитель и знаменатель

Значения настроек разделителей не должны совпадать.        
        
        """

        __sprComm = '#'
        __sprVal  = "="
        
        mIni = Ini({'sprFld' : None, 'sprInt' : None, 'sprFrac' : None})
        fileName = fileName.strip()
        try:
            mIni.read_from_file(fileName, __sprComm, __sprVal)
        except FileNotFoundError as err:
            print('Settings file not foud: ', fileName, ', format was not changed')
            return False
        
        if not MStr.set_separators(mIni['sprFld'], mIni['sprInt'] ,mIni['sprFrac']):
            print('Incorrect separators, format was not changed')
            return False

        self.__sprFld = mIni['sprFld']

        return True

    def read_rates(self, fileName):
        """Читает курсы единиц из файла. Имя файла необходимо передать параметром команды.
Прочитанные курсы добавляются к текущим настройкам.
Файл курсов - таблица в формате DSV, с разделителем "";"".
В первой строке обязательны имена полей (порядок не важен)
Образец:

# Это знак комментария
Multiplicity;   Source;             Rate;           Target;
#Кратность;     ПриводимаяЕдиница;  Курс;           ПриведеннаяЕдиница
1;  			Километр;			1000;	        Метр
В качестве значений кратности и курса можно указывать дробные значения в установленном формате (см.ФОРМ).
        """

        __sprComm = '#'
        __sprFld  = ";"

        tab = Tab()
        try:
            tab.read_from_file(fileName, __sprComm, __sprFld)
        except FileNotFoundError as err:
            print('Rates file not foud: ', fileName)
            return False

        for rowIdx in range(tab.rows):
            row = tab.get_row(rowIdx)
            if not self.__converter.add_rate(
                    row['Source']
                    ,row['Target']
                    ,MStr.from_string(row['Multiplicity']).rationals()[0]
                    ,MStr.from_string(row['Rate']).rationals()[0]
                ):
                print('WARNING ', row['Source'],', ', row['Target'])
        return True

# ==========]INIT

# ==========MAIN[

    def __init__(self):
        self.__sprFld = ', '

        self.__batch = None

        self.__msgStart = '''Mixed number calculator demo started. Type "help" for help. Type "exit" for Exit'''

        self.__methods = {
            'HELP'     : self.show_help
            ,'FORMAT'  : self.read_IO_settings
            ,'RATES'   : self.read_rates
            ,'CLEAR'   : self.clear_registers
            ,'CONVERT' : self.show_convert
            ,'COMPARE' : self.show_compare

            ,'RATETAB':self.show_rates
            ,'MEASURES':self.show_measures
            ,'RANGED':self.show_ranged

            ,'DECIMAL' : self.show_decimal
        }

        self.__synBreak = 'EXIT'
        self.__mthHelp  = self.show_help

        self.__mthSynonyms = {
            'HELP'    : 'HELP'
            ,'ПОМОЩЬ' : 'HELP'
            ,'EXIT'   : 'EXIT'
            ,'ВЫХОД'  : 'EXIT'
            ,'FORM'   : 'FORMAT'
            ,'ФОРМ'   : 'FORMAT'
            ,'RATE'   : 'RATES'
            ,'КУРС'   : 'RATES'
            ,'CLR'    : 'CLEAR'
            ,'ЧИСТ'   : 'CLEAR'
            ,'CONV'   : 'CONVERT'
            ,'КОНВ'   : 'CONVERT'
            ,'COMP'   : 'COMPARE'
            ,'СРАВ'   : 'COMPARE'


            ,'TAB':'RATETAB'
            ,'ТАБ':'RATETAB'
            ,'MSR':'MEASURES'
            ,'ЕД':'MEASURES'
            ,'RANG':'RANGED'
            ,'РАНГ':'RANGED'

            ,'DEC'    : 'DECIMAL'
            ,'ДЕС'    : 'DECIMAL'
        }

    def init(self):
        if len(sysArgv) > 1:
            self.__batch = sysArgv[1]
        self.clear_registers()
        print(self.__msgStart)
        return True

    def read_batch(self):
        """read commands from batch file"""

        __sprComm = '#'

        if isinstance(self.__batch, str):
            try:
                with open(self.__batch,'r',encoding='utf-8-sig') as mFile:
                    while True:
                        line = mFile.readline()
                        if line == '':
                            break
                        
                        # очищаем строку от комментария
                        line = line.split(__sprComm)[0].strip()
                        if line == '':
                            continue
                        
                        if not self.process(line):
                            #exit in batch
                            return False

            except FileNotFoundError as err:
                print(str(err))
            
            return True

    def work(self):
        """main operating cycle"""
        while True:
            self.__archReg = self.__register #put current register to archive
            instr = input('>>').strip()
            if not self.process(instr):
                break

    def process(self, inCommand):
        """executes one command, returns False if Exit was called"""

        # предполагаем, что первое слово - метод, остальное - параметр
        posSpace = inCommand.find(' ')
        if posSpace > 0:
            command = inCommand[0:posSpace]
            par     = inCommand[posSpace + 1:]
        else:
            command = inCommand
            par     = ''

        upper = command.upper()
        syn = self.__mthSynonyms.get(upper)
        if syn:
            if syn == self.__synBreak:
                return False

            self.__methods[syn](par)
            return True

        # все, что не метод - пробуем вычислить
        self.evaluate(inCommand)
        return True

# ==========]MAIN

main_ = main()
if main_.init():
    if main_.read_batch():
        main_.work()