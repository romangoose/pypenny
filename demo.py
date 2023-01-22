# Версия 2023-01-03
# Лицензия CC0 https://creativecommons.org/publicdomain/zero/1.0/deed.ru

from sys import argv as sysArgv

from simpleini import SimpleIni as Ini
from simpletab import SimpleTab as Tab
import mixednum as MNum
from rationals import Rational as Frac
from mixedstr import MixedString as MStr

class main:

    __sprFld = ', '

    __batch = None

    __msgStart = '''Mixed number calculator demo started. Type "help" for help. Type "exit" for Exit'''

    __msgHelp = '''A simple demo mixed number calculator. Contains one calculating register.
    '''

    def show_help(self, pars = None):
        """HELP HELP MESSAGE"""
        print(self.__msgHelp)
        print(self.__mthSynonyms)

    def read_IO_settings(self, fileName):
        """FORMAT HELP MESSAGE"""

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
        """RATES HELP MESSAGE"""

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
                print('err with ', row['Source'],', ', row['Target'])
        return True

    def show_decimal(self, pars = None):
        """показывает текущее число в десятичном виде (само число не изменяется)"""
        outList = []
        for elem in self.__register.list:
            outList.append('{dec}{name}'.format(
                dec  = Frac.decimal(elem.rational)
                ,name = (elem.name + ': ' if elem.name else '')
                )
            )
        print ((' ' + self.__sprFld).join(outList))

    def clear_registers(self, pars = None):
        """очищает регистры и таблицу курсов"""

        self.__register  = MNum.MixedNum() #put Zero in current register
        self.__archReg   = MNum.MixedNum() #put Zero in 'archive' register
        self.__converter = MNum.Converter()

    def show_convert(self, strMeasures):
        """конвертирует текущее число в заданные единицы (число не изменяется)"""
        measures = strMeasures.split(self.__sprFld)
        for el in measures:
            el = el.strip()
        mNum = self.normalize(self.__converter.convert(self.__register, measures))
        print(MStr.to_string(mNum))

    def show_rates(self, pars = None):
        print(self.__converter.rates)
        '''
        print('Multiplicity;		Source;						Rate;			Target;')
        for key in self.__converter.rates:
            print('{mul} {source} = {rate} {target}'.format(
                mul     = self.__converter.rates[key]['multiplicity']
                ,source = key[0]
                ,rate   = self.__converter.rates[key]['rate']
                ,target = key[1]
                )
            )
        '''

    def show_measures(self, pars = None):
        print(self.__converter.measures)

    def show_ranged(self, pars = None):
        print(self.__converter.ranged)
    
    __methods = {
        'HELP'     : show_help
        ,'FORMAT'  : read_IO_settings
        ,'RATES'   : read_rates
        ,'CLEAR'   : clear_registers
        ,'CONVERT' : show_convert

        ,'RATETAB':show_rates
        ,'MEASURES':show_measures
        ,'RANGED':show_ranged

        ,'DECIMAL' : show_decimal
    }
    
    __parHelp = '?'

    __mthSynonyms = {
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

        ,'TAB':'RATETAB'
        ,'ТАБ':'RATETAB'
        ,'MSR':'MEASURES'
        ,'ЕД':'MEASURES'
        ,'RANG':'RANGED'
        ,'РАНГ':'RANGED'

        ,'DEC'    : 'DECIMAL'
        ,'ДЕС'    : 'DECIMAL'
    }
    __mthBreak = 'EXIT'

    @staticmethod
    def isRegular(inMNum):
        measures = inMNum.names()
        return(len(measures) == 1 and not measures[0].strip())

    def evaluate(self, instr):
    
        op = instr[0] if len(instr) > 0 else ' '

        sInp = instr[1:]
        mInp = MStr.from_string(sInp.strip())

        if op == '=':
            self.__register = mInp
        
        elif op == '+':
            self.__register = self.__register.compose(mInp)
        elif op == '-':
            self.__register = self.__register.compose(mInp.with_rationals(Frac.opposite))
        elif op == '*':
            if self.isRegular(mInp):
                multiplicand = self.__register
                multiplier   = mInp
            elif self.isRegular(self.__register):
                multiplicand = mInp
                multiplier   = self.__register
            else:
                print('Перемножение двух смешанных чисел не определено')
                return False
            #factor[0].Rational
            self.__register = multiplicand.with_rationals(Frac.mul, multiplier.list[0].rational)
        elif op == '/' or op == '%':
            try:
                if self.isRegular(mInp):
                    numPart  = self.__register.with_rationals(Frac.mul, mInp.list[0].rational.reciprocal())
                    remainder = MNum.MixedNum((MNum.Elem(Frac()),))
                else:
                    result = self.__register.times(mInp, self.__converter)
                    numPart  = MNum.MixedNum((MNum.Elem(result[0]),))
                    remainder = result[1]

                if op == '/':
                    print ('Остаток: ', MStr.to_string(self.normalize(remainder)))
                    self.__register = numPart
                else:    
                    print ('Результат: ', MStr.to_string(self.normalize(numPart)))
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
        return(mNum.with_rationals(Frac.mixed).with_rationals(Frac.reduce).pack())

    def show_output(self, op = '=>', opnd = None):
        print(MStr.to_string(self.__register))

    def init(self):
        if len(sysArgv) > 1:
            self.__batch = sysArgv[1]
        self.clear_registers()
        print(self.__msgStart)
        return True

    def read_batch(self):
        """reads commands from batch file"""

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
        mth = self.__mthSynonyms.get(upper)
        if mth:
            if par == self.__parHelp:
                topic = self.__methods[mth].__doc__
                if topic:
                    print(topic)
                else:
                    print('No help topic about ', command)
                return True

            if mth == self.__mthBreak:
                return False

            self.__methods[mth](self, par)
            return True

        # все, что не метод - пробуем вычислить
        self.evaluate(inCommand)
        return True


main_ = main()
if main_.init():
    if main_.read_batch():
        main_.work()
