# Any copyright is dedicated to the Public Domain.
# https://creativecommons.org/publicdomain/zero/1.0/
# ===================== OR =========================
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Версия 2023-01-27

"""Convert Mixed Numbers from/to string"""

from ratiostr import RatioString as FStr
from mixednum import MixedNum, Elem, MsrPart, Measure

class MixedString(FStr):
    __sprFld = ';'

    # separators of measure
    __sprDiv = '/'
    __sprMul = '*'
    __sprPow = ':' #'^'

    @classmethod
    def __is_separators_correct(cls, sprFld, sprInt, sprFrac, sprDiv, sprMul, sprPow):
        return(
                # numper parts must not match with FStr separators
                len({cls._RatioString__negasign, sprFld,sprInt, sprFrac}) == 4
                # measure parts must not match
                and len({sprDiv, sprMul, sprPow}) == 3
                # must be string
                and isinstance(sprFld, str)
                and isinstance(sprDiv, str)
                and isinstance(sprMul, str)
                and isinstance(sprPow, str)
                # must have 1-symbol length
                and len(sprFld)  == 1
                and len(sprDiv)  == 1
                and len(sprMul)  == 1
                and len(sprPow)  == 1
                # mast be not empty
                and sprFld.strip()  != ''
                and sprDiv.strip()  != ''
                and sprMul.strip()  != ''
                and sprPow.strip()  != ''
                )

    @classmethod
    def set_separators(cls, sprFld, sprInt, sprFrac, sprDiv, sprMul, sprPow):
        if (
            cls.__is_separators_correct(sprFld, sprInt, sprFrac, sprDiv, sprMul, sprPow)
            and super().set_separators(sprInt, sprFrac)
            ):
            cls.__sprFld = sprFld
            cls.__sprDiv = sprDiv
            cls.__sprMul = sprMul
            cls.__sprPow = sprPow
            return True
        return False

    @classmethod
    def to_string(cls, mixNum) -> str:
        outList = []
        for elem in mixNum.list:
            outList.append('{frac} {msr}'.format(
                frac  = super().to_string(elem.rational)
                ,msr = cls.measure_to_string(elem.measure)
                )
            )
        if not len(outList):
            # empty value
            outList.append(super().to_string(super().from_string("")[0]))
        return (cls.__sprFld + ' ').join(outList)

    @classmethod
    def from_string(cls, instr = ''):
        outList = []
        for strNum in instr.split(cls.__sprFld):
            parts = super().from_string(strNum)
            outList.append(Elem(parts[0], cls.measure_from_string(parts[1])))
        return MixedNum(outList)

    @classmethod
    def measure_from_string(cls, inStr = ''):
        outList = []
        sign = 1 # first part of measure is positive
        for div in inStr.split(cls.__sprDiv):
            # parts with positive and negative exponents
            for mul in div.split(cls.__sprMul):
                nameAndExpo = mul.split(cls.__sprPow)
                if len(nameAndExpo) < 2:
                    nameAndExpo.append('1')
                if not nameAndExpo[1]:
                    nameAndExpo[1] = '1'
                outList.append(MsrPart(nameAndExpo[0].strip(), int(nameAndExpo[1])*sign))
            if sign == 1:
                # next part of measure is negative
                sign = -1
            else:
                # only two-or-less iterations is correct
                break
        return(Measure(outList))

    @classmethod
    def measure_to_string(cls, measure):
        # parts with positive and negative exponents
        positive = []
        negative = []
        for el in measure.list:
            absExpo = abs(el.exponent)
            strPart = '{name}{pow}{expo}'.format(
                name  = el.name
                ,pow  = cls.__sprPow if absExpo != 1 else ''
                ,expo = str(absExpo) if absExpo != 1 else ''
                )
            if el.exponent > 0:
                positive.append(strPart)
            else:
                negative.append(strPart)
        if (
            len(positive) == 0
            and len(negative) == 0
        ):
            return('')

        return(
                '{pos}{div}{neg}'.format(
                    pos  = cls.__sprMul.join(positive) if len(positive) != 0 else '1'
                    ,div = cls.__sprDiv if len(negative) != 0 else ''
                    ,neg = cls.__sprMul.join(negative) if len(negative) != 0 else ''
            )
        )