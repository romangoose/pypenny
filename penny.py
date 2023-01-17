# Версия 2023-01-03
# Лицензия CC0 https://creativecommons.org/publicdomain/zero/1.0/deed.ru

from sys import argv as sysArgv

#from simpleini import SimpleIni as Ini
#from simpletab import SimpleTab as Tab
import mixednum as MNum
#from ratiostr import RatioString as FStr

class main:

    __batch = None

    __sprComm = '#'

    __msgStart = '''Mixed number calculator demo started. Type "help" for help. Type "exit" for Exit'''

    __msgHelp = '''A simple demo mixed number calculator. Contains one calculating register.
    '''

    def show_help(self):
        print(self.__msgHelp)

    def do_invert(self):
        pass
    '''
        try:
            self.__register = self.__register.reciprocal()
        except ZeroDivisionError as err:
            print(str(err))
            return False
        self.show_output('inv')
    '''

    def do_reduce(self):
        '''
        self.__register = self.__register.reduce()
        self.show_output('reduce')
        '''

    __methods = {
                'HELP'    : show_help
                ,'INV'    : do_invert
                ,'REDUCE' : do_reduce
                }
    __synMethods = {
                'HELP'    : 'HELP'
                ,'ПОМОЩЬ' : 'HELP'
                ,'EXIT'   : 'EXIT'
                ,'ВЫХОД'  : 'EXIT'
                ##,'INV'    : 'INV'
                ##,'ИНВ'    : 'INV'
                ##,'REDUCE' : 'REDUCE'
                ##,'СОКР'   : 'REDUCE'
               }
    __methodBreak = 'EXIT'

    def evaluate(self, instr):
        pass
    '''
        op = instr[0] if len(instr) > 0 else ' '
        if not op in '+-*/=':
            print('"' + instr + '" is incorrect')
            return False

        sInp = instr[1:]
        fInp = FStr.from_string(sInp.strip())[0]

        if op == '=':
            self.__register = fInp
        elif op == '+':
            self.__register = self.__register.add(fInp)
        elif op == '-':
            self.__register = self.__register.sub(fInp)
        elif op == '*':
            self.__register = self.__register.mul(fInp)
        elif op == '/':
            try:
                self.__register = self.__register.div(fInp)
            except ZeroDivisionError as err:
                print(str(err))
                return False


        self.__register = self.__register.mixed()
        self.show_output(op,fInp)
        return True
    '''

    def show_output(self, op = '=>',curr = None):
        pass
    '''
        print(
            FStr.to_string(self.__archReg)
            + ' '  + op
            + ('' if curr == None else ' '  + FStr.to_string(curr))
            + ' = ' + FStr.to_string(self.__register)
            + ' => ' + str(self.__register.decimal())
        )
    '''

    def init(self):
        if len(sysArgv) > 1:
            self.__batch = sysArgv[1]

        self.__register = MNum.MixedNum() #put Zero in current register
        self.__archReg  = MNum.MixedNum() #put Zero in 'archive' register

        print(self.__msgStart)

        return True

    def read_batch(self):
        """reads commands from batch file"""
        if isinstance(self.__batch, str):
            try:
                with open(self.__batch,'r',encoding='utf-8-sig') as mFile:
                    while True:
                        line = mFile.readline()
                        if line == '':
                            break
                        
                        # очищаем строку от комментария
                        line = line.split(self.__sprComm)[0].strip()
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
            instr = input('>>').strip()
            if not self.process(instr):
                break

    def process(self, inCommand):
        """executes one command"""
        upper = inCommand.upper()
        if upper in self.__synMethods:
            method_ = self.__synMethods[upper]
            if method_ == self.__methodBreak:
                return False

            self.__methods[method_](self)
            return True

        self.evaluate(inCommand)
        return True
        

main_ = main()
if main_.init():
    if main_.read_batch():
        main_.work()
