# Any copyright is dedicated to the Public Domain.
# https://creativecommons.org/publicdomain/zero/1.0/
# ===================== OR =========================
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Версия 2023-01-23

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
        return(
            '{neg}{int}{sprI}{num}{sprF}{den}'.format(
                int = str(frac.intPart), num = str(frac.numerator), den = str(frac.denominator)
                ,neg = (cls.__negasign if frac.isNegative else '')
                ,sprI = cls.__sprInt, sprF = cls.__sprFrac
            )
        )


    @classmethod
    def from_string(cls, instr):
        """parse fraction from string like '-I.N/D', where ALL LAST parts of string (including seperstors) can be empty.
returns tuple (fraction, tail-of-string)

        """

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

        currKey  = 'intPart' #first suppose that you start to collect the integer part
        switches = cls.__sprInt + cls.__sprFrac #separators toggles input part
        wasTail = False
        for i in range(len(instr)):
            symb = instr[i]
            if symb.isdigit():
                # digits are collected in the selected part
                parts[currKey] = parts[currKey] + symb
                continue

            # undefined symbol (not digit, not switch): finishes construction
            if not symb in switches:
                wasTail = True
                break

            # it's a switch
            if symb == cls.__sprInt:
                currKey  = 'numerator'
                switches = cls.__sprFrac
            else:
                # it's sprFrac
                if cls.__sprInt in switches:
                    # separator sprFrac occurs before separator sprInt
                    # so previously the numerator was actually constructed, not the intPart
                    parts['numerator'] = parts['intPart']
                    parts['intPart']   = ''
                
                currKey  = 'denominator'
                switches = ''

        if switches == cls.__sprFrac:
            # sprFrac was not previously found, so it's a decimal fraction
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

        return(mFrac,  instr[i:] if wasTail else '')
        
