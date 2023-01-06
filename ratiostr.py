# Версия 2022-12-17
# Лицензия CC0 https://creativecommons.org/publicdomain/zero/1.0/deed.ru

from rationals import Rational as Frac

"""Convert Rational numbers (fractions) from/to string"""

class RatioString:

    """Base convertation format is \"-I.N/D\""""

    __negasign = '-'
    __sprInt   = '.'
    __sprFrac  = '/'

    @staticmethod
    def __is_separators_correct(negasign, sprInt, sprFrac):
        return(
                #must not match (i.e. with negasign)
                len({negasign,sprInt,sprFrac}) == 3
                #must be strings
                and isinstance(sprInt,  str)
                and isinstance(sprFrac, str)
                #must have 1-symbol length
                and len(sprInt)  == 1
                and len(sprFrac) == 1
                and sprInt.strip()  != ''
                and sprFrac.strip() != ''
                )

    @classmethod
    def set_separators(cls, sprInt, sprFrac):
        if cls.__is_separators_correct(cls.__negasign, sprInt, sprFrac):
            cls.__sprInt  = sprInt.strip()
            cls.__sprFrac = sprFrac.strip()
            return True
        return False

    @classmethod
    def to_string(cls, frac) -> str:
        #a = f'{self.__negasign + " " if self.isNegative else ""}{str(self.intPart)}{self.__sprInt}{str(self.numerator)}{self.__sprFrac}{str(self.denominator)}'
        return (
                 (cls.__negasign + ' ' if frac.isNegative else '')
                + str(frac.intPart)   + cls.__sprInt
                + str(frac.numerator) + cls.__sprFrac + str(frac.denominator)
                )

    # parse fraction from string like '-I.N/D', where ALL LAST parts of string (including seperstors) can be empty
    # returns tuple fraction, tail-of-string
    @classmethod
    def from_string(cls, instr):
        instr = instr.strip()

        #in the simplest case returns "zero", empty
        if instr == '' or instr == cls.__negasign:
            return (Frac(), '')

        isNegative = False
        # first input symbol can be negative sign or none
        if instr[0] == cls.__negasign:
            isNegative = True
            instr = instr[1:].strip()

        # string parts for constructing fraction from input
        parts = {'intPart':'', 'numerator':'', 'denominator':''}

        currKey  = 'intPart' #constructing intPart at first (think so)
        switches = cls.__sprInt + cls.__sprFrac #if meet switch, change constructing part
        lenstr = len(instr)
        for i in range(lenstr):
            symb = instr[i]
            if symb.isdigit():
                parts[currKey] = parts[currKey] + symb
                continue

            # non-numeral symbol
            if not symb in switches:
                break

            # it's a switch
            if symb == cls.__sprInt:
                currKey  = 'numerator'
                switches = cls.__sprFrac
            else:
                # it's sprFrac
                if cls.__sprInt in switches:
                    # meet sprFrac before meet sprInt
                    # so, in fact we construct numerator, not the intPart
                    parts['numerator'] = parts['intPart']
                    parts['intPart']   = ''
                
                currKey  = 'denominator'
                switches = ''

        if switches == cls.__sprFrac:
            # previously not find sprFrac, so it is decimal fraction
            parts['denominator'] = '1' + '0'*len(parts['numerator'])

        outFrac = Frac().dict()
        outFrac['isNegative'] = isNegative
        for key in parts:
            if parts[key] != '':
                outFrac[key] = int(parts[key])
        try:
            mFrac = Frac(**outFrac)
        except ValueError as err:
            raise ValueError('error while parsing string to rational: ' + str(err))

        return(mFrac,  instr[i:] if i < (lenstr - 1) else '')
        
