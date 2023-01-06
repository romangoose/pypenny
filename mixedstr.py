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
            outList.append(super().to_string(elem.rational) + ' ' + elem.name)

        return (cls.__sprFld + ' ').join(outList)

    @classmethod
    def from_string(cls, instr):
        outList = []
        for strNum in instr.split(cls.__sprFld):
            a = super().from_string(strNum)
            #outList.append(Elem(a[1].strip(), a[0]))
            outList.append(Elem(*super().from_string(strNum)))
        return MixedNum(outList)