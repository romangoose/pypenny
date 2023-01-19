# Версия 2023-01-03
# Лицензия CC0 https://creativecommons.org/publicdomain/zero/1.0/deed.ru

from sys import argv as sysArgv

from simpleini import SimpleIni as Ini
from simpletab import SimpleTab as Tab
import mixednum as MNum
from rationals import Rational as Frac
from mixedstr import MixedString as MStr

class main:

    __batch = None

    __msgStart = '''Mixed number calculator demo started. Type "help" for help. Type "exit" for Exit'''

    __msgHelp = '''A simple demo mixed number calculator. Contains one calculating register.
    '''

    def show_help(self, pars = None):
        """HELP HELP MESSAGE"""
        print(self.__msgHelp)

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


    def do_invert(self, pars = None):
        pass
    '''
        try:
            self.__register = self.__register.reciprocal()
        except ZeroDivisionError as err:
            print(str(err))
            return False
        self.show_output('inv')
    '''

    def do_reduce(self, pars = None):
        '''
        self.__register = self.__register.reduce()
        self.show_output('reduce')
        '''

    __methods = {
        'HELP'    : show_help
        ,'FORMAT' : read_IO_settings
        ,'RATES'  : read_rates

        ##,'INV'    : do_invert
        ##,'REDUCE' : do_reduce
    }
    
    __parHelp = '?'

    __mthSynonyms = {
        'HELP'    : 'HELP'
        ,'ПОМОЩЬ' : 'HELP'
        ,'EXIT'   : 'EXIT'
        ,'ВЫХОД'  : 'EXIT'
        ,'FORM'   : 'FORMAT'
        ,'ФОРМ'   : 'FORMAT'
        ,'КУРС'   : 'RATES'
        ,'RATE'   : 'RATES'
        ##,'REDUCE' : 'REDUCE'
        ##,'СОКР'   : 'REDUCE'
    }
    __mthBreak = 'EXIT'

    def evaluate(self, instr):
    
        op = instr[0] if len(instr) > 0 else ' '
        if not op in '+-*/=':
            print('"' + instr + '" is incorrect')
            return False

        sInp = instr[1:]
        mInp = MStr.from_string(sInp.strip())

        if op == '=':
            self.__register = mInp
        
        elif op == '+':
            self.__register = self.__register.compose(mInp)
        elif op == '-':
            self.__register = self.__register.compose(mInp.with_rationals(Frac.opposite))
        '''
        elif op == '*':
            self.__register = self.__register.mul(fInp)
        elif op == '/':
            try:
                self.__register = self.__register.div(fInp)
            except ZeroDivisionError as err:
                print(str(err))
                return False
        '''

        #self.__register = self.__register.mixed()
        self.show_output(op,mInp)
        return True

    def show_output(self, op = '=>', opnd = None):
        print(MStr.to_string(self.__register))

    def init(self):
        if len(sysArgv) > 1:
            self.__batch = sysArgv[1]

        self.__register  = MNum.MixedNum() #put Zero in current register
        self.__archReg   = MNum.MixedNum() #put Zero in 'archive' register
        self.__converter = MNum.Converter()

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
