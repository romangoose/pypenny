# Any copyright is dedicated to the Public Domain.
# https://creativecommons.org/publicdomain/zero/1.0/
# ===================== OR =========================
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Версия 2023-01-27

"""Convert Mixed Numbers from/to string"""

from ratiostr import RatioString as FStr
from mixednum import MixedNum, Elem

class MixedString(FStr):
    __sprFld = ';'

    @classmethod
    def __is_separators_correct(cls, sprFld, sprInt, sprFrac):
        return(
                #must not match with FStr separators
                len({cls._RatioString__negasign, sprFld,sprInt, sprFrac}) == 4
                #must be string
                and isinstance(sprFld,  str)
                #must have 1-symbol length
                and len(sprFld)  == 1
                and sprFld.strip()  != ''
                )

    @classmethod
    def set_separators(cls, sprFld, sprInt, sprFrac):
        if (
            cls.__is_separators_correct(sprFld, sprInt, sprFrac)
            and super().set_separators(sprInt, sprFrac)
            ):
            cls.__sprFld = sprFld
            return True
        return False

    @classmethod
    def to_string(cls, mixNum) -> str:
        outList = []
        for elem in mixNum.list:
            outList.append('{frac}{name}'.format(
                frac  = super().to_string(elem.rational)
                ,name = (' ' + elem.name if elem.name else '')
                )
            )
        if not len(outList):
            # empty value
            outList.append(super().to_string(super().from_string("")[0]))
        return (cls.__sprFld + ' ').join(outList)

    @classmethod
    def from_string(cls, instr):
        outList = []
        for strNum in instr.split(cls.__sprFld):
            outList.append(Elem(*super().from_string(strNum)))
        return MixedNum(outList)
