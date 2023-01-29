# Any copyright is dedicated to the Public Domain.
# https://creativecommons.org/publicdomain/zero/1.0/

# Версия 2023-01-21

from sys import argv as sysArgv

from simpleini import SimpleIni as Ini
import rationals as Frac
from ratiostr import RatioString as FStr

class main:

    __msgSettingsError = '''The calculator must be started with a parameter that specifies the name of the I/O settings file.
Sample settings file:
    sprInt  = . # separator of the integer and fractional part
    sprFrac = / # separator of the numerator and denominator
Values must have 1-symbol length and must not match.'''
    
    __msgStart = '''Fraction calculator demo started. Type "help" for help. Type "exit" for exit'''

    __msgHelp = '''Simple fraction calculator. Contains one calculating register, sequential input of operations [+-*/].
Typing "=fraction" sets a fraction to a register.
Also use "reduce" and "inv" (1/x) command.
Fraction input format is "-I.N/D"
(specify the fileт with I/O settings (separators) as the first parameter at startup).

Поддерживается последовательный ввод четырех арифметических операций, единственный регистр вычислений; 
Ввод "=дробь" помещает дробь в этот регистр.
Ввод одной из операций "[+-*/]дробь" выполняет действие над текущим регистром и введенным числом.
Команда "сокр" или "reduce" - сокращает текущую дробь.
Команда "инв" или "inv" "переворачивает" дробь (1/х).
Формат ввода (и вывода) дроби: "-Ц.Ч/З". Конкретные разделители устанавливаются в файле настроек,
который необходимо указать первым параметром при запуске файла демо.

    '''

    def show_help(self):
        print(self.__msgHelp)

    def do_invert(self):
        try:
            self.__register = self.__register.reciprocal()
        except ZeroDivisionError as err:
            print(str(err))
            return False
        self.show_output('inv')

    def do_reduce(self):
        self.__register = self.__register.reduce()
        self.show_output('reduce')

    __methods = {
                'HELP'    : show_help
                ,'INV'    : do_invert
                ,'REDUCE' : do_reduce
                }
    __synonims = {
                'HELP'    : 'HELP'
                ,'ПОМОЩЬ' : 'HELP'
                ,'EXIT'   : 'EXIT'
                ,'ВЫХОД'  : 'EXIT'
                ,'INV'    : 'INV'
                ,'ИНВ'    : 'INV'
                ,'REDUCE' : 'REDUCE'
                ,'СОКР'   : 'REDUCE'
               }
    __methodBreak = 'EXIT'

    def init(self):
        try:
            if len(sysArgv) < 2:
               raise Exception ('missing file with i/o settings')
            mIni = Ini({'sprInt':None,'sprFrac':None})
            mIni.read_from_file(sysArgv[1],'#','=')
            
            FStr.set_separators(mIni['sprInt'],mIni['sprFrac'])

        except Exception as exc:
            print(exc)
            print(main.__msgSettingsError)
            return False

        self.__register = Frac.Rational() #put Zero in current register
        self.__archReg  = Frac.Rational() #put Zero in 'archive' register
        print(self.__msgStart)

        return True

    def evaluate(self, instr):
        op = instr[0] if len(instr) > 0 else ' '
        if not op in '+-*/=':
            print('"{0}" is incorrect'.format(instr))
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

    def show_output(self, op = '=>',operand = None):
        print(
            '{arch} {op}{opnd} = {result} => {dec}'.format(
                arch    = FStr.to_string(self.__archReg)
                ,op     = op
                ,opnd   = ('' if operand == None else ' '  + FStr.to_string(operand))
                ,result = FStr.to_string(self.__register)
                ,dec    = str(self.__register.decimal())
            )
        )

    def work(self):
        while True:
            self.__archReg = self.__register #put current register to archive
            instr = input('>>').strip()
            upper = instr.upper()
            if upper in self.__synonims:
                method_ = self.__synonims[upper]
                if method_ == self.__methodBreak:
                    break

                self.__methods[method_](self)
                continue

            self.evaluate(instr)

main_ = main()
if main_.init():
    main_.work()
