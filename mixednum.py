# Any copyright is dedicated to the Public Domain.
# https://creativecommons.org/publicdomain/zero/1.0/
# ===================== OR =========================
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Версия 2023-02-05

"""Mixed Number arithmetic"""

"""
here put the theory of a mixed numbers

"""

from rationals import Rational as Frac

class MsrPart:
    """the elementary part of combined measure: name and exponent"""
    def __init__(self, name = '', exponent = 1):
        def is_correct(name, exponent):
            return(
                isinstance(name, str)
                and type(exponent) is int
                and exponent != 0
            )
        if not is_correct(name, exponent):
            raise ValueError("incorrect part(s) of measure")
            
        self.__name = name.strip()
        self.__exponent = exponent
        

    def __str__(self):
        return(str({'name':str(self.__name), 'exponent':str(self.__exponent)}))

    def __eq__(self, other):
        if not isinstance(other, MsrPart):
            return False
        return(
            self.name == other.name
            and self.exponent == other.exponent
        )

    @property
    def name(self):
        return(self.__name)

    @property
    def exponent(self):
        return(self.__exponent)

class Measure:
    """combined measure: list of elementary parts (MsrPart)"""
    def __init__(self, inList = []):
        self.__list = []
        for el in inList:
            if not isinstance(el, MsrPart):
                raise ValueError("incorrect measure's part")
            if el.name == '':
                continue
            idx = self.get_part_index_by_name(el.name)
            if idx == None:
                self.__list.append(MsrPart(el.name, el.exponent))
            else:
                newExpo = el.exponent + self.__list[idx].exponent
                if newExpo:
                    self.__list[idx] = MsrPart(self.__list[idx].name, newExpo)
                else:
                    del self.__list[idx]

    def __str__(self):
        return(','.join([str(i) for i in self.__list]))

    def __eq__(self, other):
        if not isinstance(other, Measure):
            return False
        sN = self.get_parts_names()
        oN = other.get_parts_names()
        allN = {*sN,*oN}
        if len(allN) == len(sN) == len(oN):
            for name in allN:
                if self.get_part_by_name(name) != other.get_part_by_name(name):
                    return False
            return True
        return False

    def __neg__(self):
        outList = []
        for el in self.__list:
            outList.append(MsrPart(el.name, -el.exponent))
        return(Measure(outList))

    @property
    def list(self):
        return(self.__list)

    def get_parts_names(self):
        """all part's names of the measure"""
        outList = []
        for el in self.__list:
            outList.append(el.name)
        return outList

    def get_part_index_by_name(self, inName):
        for idx in range(len(self.__list)):
            if self.__list[idx].name == inName:
                return idx
        return None

    def get_part_by_name(self, inName):
        idx = self.get_part_index_by_name(inName)
        if idx == None:
            return None
        return(self.__list[idx])

    def combine(self, *others):
        """union (multiplication with the summation  of the same-name exponents) lists of entering parts of measure"""
        outList = []
        outList.extend(self.__list)
        for el in others:
            outList.extend(el.list)
        return(Measure(outList))



class Elem:
    """the elementary part of a mixed number: a fraction having a measure"""
    def __init__(self, rational, measure = Measure()):
        def is_correct(rational, measure):
            return(
                isinstance(rational, Frac)
                and isinstance(measure, Measure)
            )
        if measure == None:
            measure = Measure()
        if not is_correct(rational, measure):
            raise ValueError("incorrect part(s) of mixed number element")
        
        self.__rational = rational
        self.__measure = measure.combine()

    def __str__(self):
        return(str({'rational':str(self.__rational), 'measure':str(self.__measure)}))

    @property
    def measure(self):
        return(self.__measure)

    @property
    def rational(self):
        return(self.__rational)

    def reduce_measure(self, converter):
        
        unitSet = set(self.measure.get_parts_names())

        # сортируем ranged, если еще не сортирован
        converter.sort_ranged()

        msrList = []
        elOperative = Frac(**self.rational.dict())

        for part in self.measure.list:
            found = False
            for base in converter.ranged:
                baseName = base['name']

                if not baseName in unitSet:
                    # нет в именах запрошенных единиц
                    continue

                if part.name == baseName:
                    # та же самая единица - elOperative не меняется
                    break

                rate = (part.name, baseName)
                if rate in converter.rates.keys():
                    
                    # иначе если существует курс перевода
                    found = True
    
                    # домножаем числовую часть временного элемента:
                    # формируем множитель пересчета
                    mutiplier = Frac.shorter(
                                    numerator = converter.rates[rate]['rate']
                                    ,denominator = converter.rates[rate]['multiplicity']
                                )
                    # возводим в необходимую степень
                    if part.exponent < 0:
                        mutiplier = mutiplier.reciprocal()
                    for i in range(abs(part.exponent) - 1):
                        mutiplier = mutiplier.mul(mutiplier)

                    # новое промежуточное стостояние elOperative
                    elOperative = elOperative.mul(mutiplier).reduce()
                    msrList.append(MsrPart(baseName, part.exponent))
                    break
            if not found:
                msrList.append(part)
        return(Elem(elOperative, Measure(msrList)))

        

class MixedNum:
    """list of named fractions"""
    def __init__(self, inList = []):
        self.__list = []
        # for lst in inLists:
        for el in inList:
            if not isinstance(el, Elem):
                raise ValueError("incorrect element of mixed number")
            idx = self.get_measure_index(el.measure)
            if idx == None:
                self.__list.append(Elem(el.rational, el.measure))
            else:
                self.__list[idx] = Elem(self.__list[idx].rational.add(el.rational), el.measure)

    def __str__(self):
        return(','.join([str(i) for i in self.__list]))

    @property
    def list(self):
        return(self.__list)

    def rationals(self):
        """all fractions of the number"""
        outList = []
        for el in self.__list:
            outList.append(el.rational)
        return outList

    def get_measures(self):
        outList = []
        for el in self.__list:
            outList.append(el.measure)
        return outList

    def get_measure_index(self, inMeasure):
        for idx in range(len(self.__list)):
            if self.__list[idx].measure == inMeasure:
                return idx
        return None

    def get_elem_by_measure(self, inMeasure):
        idx = self.get_measure_index(inMeasure)
        if idx == None:
            return None
        return(self.__list[idx])

    def compose(self, *others):
        """union (with the summation  of the same-name parts) lists of entering MixedNumbers"""

        # по факту, и конструирование числа из элементов
        # и суммирование двух чисел - 
        # сводятся к операции компоновки,
        # то есть, объединению списков суммированию одноименных элементов.
        # compose фактически явлется алиасом для конструктора класса:
        # в конструктор передаются списки,
        # сюда - непосредственно MixedNum

        outList = []
        outList.extend(self.__list)
        for mxNum in others:
            outList.extend(mxNum.list)
        return(MixedNum(outList))

    def reciprocal(self):
        """for division as multiplication"""
        outList = []
        for el in self.__list:
            outList.append(
                Elem(
                    el.rational.reciprocal()
                    ,-el.measure
                )
            )
        return(MixedNum(outList))

    def mul(self, other):
        """Mx/Mx multiplication with convertions of measures"""
        outList = []
        for oEl in other.__list:
            for sEl in self.__list:
                outList.append(
                    Elem(
                        oEl.rational.mul(sEl.rational)
                        ,oEl.measure.combine(sEl.measure)
                    )
                )
        return(MixedNum(outList))

    def div(self, other, converter):
        """Mx/Mx division: shortcut for multiplication with preliminary conversion and check"""

        # check if a mixed number contains only one element (one measure)
        measures = []
        for el in other.list:
            if el.measure not in measures:
                measures.append(el.measure)
        divisor = converter.convert_to_lowest(other, measures)
        if len(divisor.list) > 1:
            raise ValueError('divisor contains more than one measure')

        # flip the elements' numbers
        # may causes divizion by zero
        divisor = divisor.with_rationals(Frac.reciprocal)

        # finally flip the units of measure
        outList = []
        for el in divisor.list:
            partList = []
            for part in el.measure.list:
                partList.append(MsrPart(part.name, -part.exponent))
            outList.append(Elem(el.rational, Measure(partList)))
        
        return(self.mul(MixedNum(outList)))


    def pack(self):
        """remove zero-elements"""
        outList = []
        for el in self.__list:
            if not el.rational.isZero():
                outList.append(Elem(el.rational, el.measure))
        return(MixedNum(outList))

    def with_rationals(self, func, pars=None):
        """apply a function to the rational part of the MixedNumber elements"""

        """in this way it is possible, for example, to multiply (by a measureless number), reduce, etc."""
        outList = []
        for el in self.list:
            if pars == None:
                outList.append(Elem(func(el.rational), el.measure))
            else:
                outList.append(Elem(func(el.rational,pars), el.measure))
        return(MixedNum(outList))

    def reduce_measures(self, converter):
        outList = []
        for el in self.list:
            outList.append(el.reduce_measure(converter))
        return(MixedNum(outList))

    def times(self, other, converter):

        """Mx/Mx division: calculate how many times the divisor occurs in the dividend; remainder is possible"""

        # вычисляем, сколько раз (м.б. дробью) встречается делитель в делимом,
        # неровный излишек помещается в остаток
        # фактически - деление понимается, как множественное "исчерпывание" делимого делителем
        # Определим исчерпывание как такое вычитание,
        # при котором абсолютная величина уменьшаемого (делимого) - уменьшается, "исчерпывается"
        # к остатку, который более невозможно исчерпать.
        # В случае одноименных знаков делимого и делителя именно так и происходи:
        # при этом результат всегда будет положительным числом по правилу одноименных знаков.
        # Проще говоря, в случае одноименных знаков мы оперируем только абсолютными величинами операндов.
        # В случае противоположных знаков, на первый взгляд,
        # абсолютная величина делителя будет возрастать к бесконечности,
        # поэтому доопределим "обратное" исчерпывание для такого случая:
        # по-прежнему, будем исчерпывать асболютную величину делимого асболютной величиной делителя,
        # но результат будет иметь отрицательный знак (по правилу противоположных знаков)
        # Последнее допущение: позволим исчерпывать делитель не только исходным делителем, 
        # но и произвольной его долей, что позволит получать дробный результат деления.

        # Как итог, исчерпывания каждой части делимого 
        # для получения однозначно определенного результата
        # должны происходить в одинаковых направлениях 
        # (либо только одноименные знаки операндов,
        # либо только противоположные)


        # подготавливаем общий список всех единиц 
        measures = []
        for el in *self.list, *other.list:
            if el.measure not in measures:
                measures.append(el.measure)

        # преобразуем делимое и делитель к наименьшим единицам в существующих сетах единиц
        lwSelf  = converter.convert_to_lowest(self, measures).pack()
        lwOther = converter.convert_to_lowest(other, measures).pack()
        if len(lwOther.__list) == 0:
            raise ZeroDivisionError('division by zero')

        msrOther = lwOther.get_measures()
        msrSelf  = lwSelf.get_measures()

        # вычисляем минимальное (по модулю) частное среди пар операндов с совпадающими единицами
        minQuotient = None
        exsDirection = None
        for msr in msrOther:
            if msr in msrSelf:
                elSelf  = lwSelf.get_elem_by_measure(msr)
                elOther = lwOther.get_elem_by_measure(msr)
                quotient = elSelf.rational.div(elOther.rational).reduce()
                if exsDirection == None: 
                    exsDirection = quotient.intSign() # архивируем знак (направление исчерпывания)
                else:
                    if exsDirection != quotient.intSign():
                        # нарушен принцип одинакового направления исчерпывания
                        # то есть, делитель в делимом содержится ноль раз
                        minQuotient = Frac()
                        break

                if (minQuotient == None) or (quotient.abs().intComp(minQuotient.abs()) < 0):
                    minQuotient = Frac(**quotient.dict())
            else:
                # если в делителе есть единица, не входящая в состав делимого
                # то делимое невозможно исчерпать делителем, седовательно делитель содержится в делимом ноль раз
                minQuotient = Frac()
                break
        # вычитаем из делимого делитель, умноженный на найденное минимальное частное
        remainder = self.compose(other.with_rationals(Frac.mul, minQuotient).with_rationals(Frac.opposite))

        # конвертируем остаток в исходные единицы делимого
        # (иначе может быть неудобное представление просто из-за того,
        # что в делимом и делителе присутствуют разные единицы даже из одного и того же сета)
        remainder = converter.convert(remainder, self.get_measures())

        return(minQuotient, remainder)

    def intComp(self, other, converter):

        """compare. return -1,0,1 for self is lesser than, equal to or bigger than other; or None if undefined"""

        # сравнение определим только для случаев, 
        # в которых все элементы числа self
        # (приведенные к минимальной единице для каждого сета)
        # находятся по "одну сторону" от соответствующих элементов числа other
        # (некоторые элементы при этом могут быть равны между собой)
        # если равны все элементы - то равны и числа
        # если одноименные элементы находятся по разные стороны друг от друга
        # то сравнение неопределено

        # подготавливаем общий список всех единиц 
        measures = []
        for el in *self.list, *other.list:
            if el.measure not in measures:
                measures.append(el.measure)

        # преобразуем делимое и делитель к наименьшим единицам в существующих сетах единиц
        lwSelf  = converter.convert_to_lowest(self, measures).pack()
        lwOther = converter.convert_to_lowest(other, measures).pack()

        msrOther = lwOther.get_measures()
        msrSelf  = lwSelf.get_measures()

        result = 0 # по умолчанию числа равны
        # перебираем "левое соединение" единиц other с с единицами self
        for msr in msrOther:
            if msr in msrSelf:
                elSelf  = lwSelf.get_elem_by_measure(msr)
                elOther = lwOther.get_elem_by_measure(msr)
                side = elSelf.rational.intComp(elOther.rational)
            else:
                # сравнение элемента с ничем полностью определяется знаком элемента
                # (нулевые элементы, которые имеют неотрицательный знак, - исключены благодаря pack())
                elOther =   lwOther.get_elem_by_measure(msr)
                side    = - elOther.rational.intSign() # здесь минус: знак инвертирован, 
                                                       # потому что элементы сравниваются в обратном порядке)

            if side == 0:
                continue
            if result != 0 and result != side:
                # разошлись стороны относительно нуля
                return None
            result = side

        # соединяем единицы наборот, 
        # в поисках единиц, присутствующих только в self 
        # проверяем знак на совпадение
        for msr in msrSelf:
            if msr not in msrOther:
                elSelf  = lwSelf.get_elem_by_measure(msr)
                side = elSelf.rational.intSign()
                if side == 0:
                    continue
                if result != 0 and result != side:
                    # разошлись стороны относительно нуля
                    return None
                result = side

        # если ранее не был возвращен None - возвращаем одинаковую "сторону" или ноль
        return result 


class Converter:
    """converts one measure to another if a corresponding exchange rate exists"""

    # именно и только converter знает о соотношениях единиц между собой
    # rates - главный объект конвертера, таблица (словарь) курсов
    # (используеся терминология курсов валют: исходная единица, целевая, кратность, курс)
    # вспомогательные объекты:
    # units - список множеств, отдельное множество - это перечень базовых единиц, относящихся к одному контексту
    # (то есть таких, которые могут быть взаимно выражены друг через друга)
    # ranged - список всех единиц, общий (не разделенный по сетам), 
    # который перед конвертацией должен быть отсортирован в восходящем порядке
    # (в итоге для каждого сета будет известен упорядоченный список единиц)
    # isRanged - соответственно, признак отсортированности, 
    # который сбрасывается при любом изменении курсов 
    
    def __init__(self) -> None:
        self.__rates    = {}    # list of dictionaries, contains rates to convert one measure to another
        self.__units = []       # ??UNNECESSARY?? list of sets, every set contains "line" (unordered) of units of one context
        self.__ranged   = []    # ranged (sorted from "minimal" to "maximal") list of units' names (all-in-one)
        self.__isRanged = False # True, if ranged was really sorted. When rate are modifyed, sets to False

    @property
    def rates(self):
        return(self.__rates)

    @property
    def units(self):
        return(self.__units)

    def sort_ranged(self):

        """sort ranged if not yet"""

        if not self.__isRanged:
            # bubble sort (ascending)
            done = False
            while not done:
                done = True
                for idx in range(1,len(self.__ranged)):
                    if (self.__ranged[idx]['rational'].intComp(self.__ranged[idx-1]['rational']) < 0):
                        self.__ranged[idx], self.__ranged[idx-1] = self.__ranged[idx-1], self.__ranged[idx]
                        done = False
            self.__isRanged = True

    @property
    def ranged(self):
        self.sort_ranged()
        return(self.__ranged)

    def get_unitSet(self, inName):
        # unused

        """return set where the inName is"""

        for el in self.__units:
            if inName in el:
                return el
        return None

    def get_unitList(self, inName):
        # unused

        """return (ordered) list of inName's set"""

        mSet = self.get_unitSet(inName)
        if mSet == None:
            return None

        self.sort_ranged()
        outList = []
        for el in self.ranged:
            if el['name'] in mSet:
                outList.append(el['name'])
        return (outList)

    def add_rate(self, source, target, multiplicity, rate):
        """add main and dependent (cross and reverse) rates"""

        #inner auxiliary functions
        def update_units(*inNames):
            """add a measure to the corresponding set"""

            outList = []
            crSet = {*inNames}
            for mSt in self.__units:
                found = False
                for name in inNames:
                    if name in mSt:
                        found = True
                        crSet = crSet.union(mSt)
                        break
                if not found:
                    outList.append(mSt)
            outList.append(crSet)
            self.__units = outList
            return self.__units[-1]

        def update_ranged(inName, rate, multiplicity):
            frac = Frac.shorter(rate, multiplicity)
            for idx in range(len(self.__ranged)):
                if self.__ranged[idx]['name'] == inName:
                    # if found
                    if (self.__ranged[idx]['rational'].intComp(frac) > 0):
                        # replace by lesser
                        self.__ranged[idx]['rational'] = frac
                    return None
            # not found - append
            self.__ranged.append({'name' : inName, 'rational' : frac})
            return None

        def add_cross_rate(base, cross, unitSet, depth = False):
            """cross-rates"""
            
            for msreFound in unitSet:
                if msreFound == cross:
                    continue

                if (msreFound,cross) in self.__rates:
                    continue

                rateBase  = self.__rates[(base, cross)]
                rateFound = self.__rates[(base, msreFound)]

                multiplicity = rateFound['rate']         * rateBase['multiplicity']
                rate         = rateFound['multiplicity'] * rateBase['rate']
                gcd_ = Frac.gcd(multiplicity, rate)
                add_record(
                    msreFound, cross, unitSet
                        ,multiplicity // gcd_
                        ,rate         // gcd_
                    )
                if not depth:
                    # для случаев, когда два разных сета объединяются достаточно поздно
                    # (например, соответствие двух линеек устанавливается после того,
                    # как обе линейки уже заполнены)
                    # потребуется рекурсивный вызов, 
                    # но глубина рекурсии заведомо ограничена двумя уровнями 
                    # (одно соответствие по определению связывет только две единицы)
                    add_cross_rate(cross, msreFound, unitSet, True)
                

        def add_record(source, target, unitSet, multiplicity, rate):
            """elementary entry of rate table"""

            # таблица устроена как словарь, 
            # где ключом является кортеж (исходная + целевая единица),
            # данными - словарь {кратность, курс}

            self.__rates[(source, target)] = {
                                                'multiplicity': multiplicity
                                                ,'rate':        rate
                                            }
            update_ranged(source, rate, multiplicity)
 
            # reverse record
            if not (target, source) in self.__rates:
                add_record(target, source, unitSet, rate, multiplicity)
            
            return True

        # main function body
        if source == target:
            return False

        if multiplicity.isZero() or rate.isZero():
            return False

        if (source,target) in self.__rates:
            return False

        # multiplicity and rate may be fractional, 
        # must convert them to integers
        commonMult = Frac(multiplicity.denominator * rate.denominator)
        
        multiplicity = multiplicity.mul(commonMult).simple()
        multiplicity = (multiplicity.numerator // multiplicity.denominator)*multiplicity.intSign()
        
        rate = rate.mul(commonMult).simple()
        rate = (rate.numerator // rate.denominator)*rate.intSign()

        unitSet = update_units(source, target)

        self.__isRanged = False # сбрасываем признак сортировки 
        add_record(source, target, unitSet, multiplicity, rate)
        add_cross_rate(source, target, unitSet)
        add_cross_rate(target, source, unitSet)

        return True



    def convert_to_lowest(self, mixedNum, inMeasures):
        """
        preliminary calculation for Convert and for methods that require casting to a single (minimal) value
        """

        unitSet = set()
        for inMsr in inMeasures:
            unitSet = unitSet.union(inMsr.get_parts_names())

        allParts = []
        for inMsr in inMeasures:
            for part in inMsr.list:
                if part not in allParts:
                    allParts.append(part) 

        # приводим элементы MixedNum к наименьшей единице внутри каждого сета

        # сортируем ranged, если еще не сортирован
        self.sort_ranged()

        lowest      = []
        unConverted = []

        for el in mixedNum.list:
            elReduce = el.reduce_measure(self)
            # признак того, полностью ли конвертировались все части единицы у элемента
            # по умолчанию равен истине, при неудаче в одном жлементе сбрасывается в ложь
            convertComplete = True
            # временный элемент, в котором будут заменяться и пересчитываться единицы
            elOperative = Elem(elReduce.rational, elReduce.measure)

            for msrPart in elReduce.reduce_measure(self).measure.list:
                # признак того, сконвертировалась ли каждая отдельная часть единицы
                # признак полного конвертирования есть полное логическое И
                # всех таких признаков
                partFound = False
                # перебираем упорядоченный набор единиц
                # (начиная с наименьшей)

                for base in self.__ranged:
                    baseName = base['name']

                    if not baseName in unitSet:
                        # нет в именах запрошенных единиц
                        continue

                    if not MsrPart(baseName, msrPart.exponent) in allParts:
                        # нужной степени нет в частях запрошенных единиц
                        continue

                    if msrPart.name == baseName:
                        # та же самая единица - elOperative не меняется
                        partFound = True
                        break

                    rate = (msrPart.name, baseName)
                    if rate in self.__rates.keys():
                        # иначе если существует курс перевода
                        partFound = True
                        # текущий elOperative будет домножен на найденный курс
                        # а его единица будет модифицирована с учетом найденной части:
                        
                        # формируем новую единицу измерения, удалив исходную часть
                        # и добавив взамен найденную:
                        tmpParts = elOperative.measure.list[:]
                        del tmpParts[elOperative.measure.get_part_index_by_name(msrPart.name)]
                        tmpParts.append(MsrPart(baseName, msrPart.exponent))
                        
                        # домножаем числовую часть временного элемента:
                        # формируем множитель пересчета
                        mutiplier = Frac.shorter(
                                        numerator = self.__rates[rate]['rate']
                                        ,denominator = self.__rates[rate]['multiplicity']
                                    )
                        # возводим в необходимую степень
                        if msrPart.exponent < 0:
                            mutiplier = mutiplier.reciprocal()
                        for i in range(abs(msrPart.exponent) - 1):
                            mutiplier = mutiplier.mul(mutiplier)

                        # новое промежуточное стостояние elOperative
                        elOperative = Elem(
                                elOperative.rational.mul(mutiplier).reduce()
                                ,Measure(tmpParts)
                            )
                        break
                convertComplete = convertComplete and partFound
            if convertComplete:
                # полностью преобразованный элемент помещаем в основной список
                lowest.append(elOperative)
            else:
                # игнорируем частичную конвертацию
                unConverted.append(el)

        # кондиционные элементы просто идут первыми
        lowest.extend(unConverted)

        return(MixedNum(lowest))

    def get_conversion_divisor(self, inElem, inMeasure):
        # сортируем ranged, если еще не сортирован
        self.sort_ranged()

        inParts = []
        for part in inMeasure.list:
            expo = 1
            if part.exponent < 0:
                expo = -1
            for i in range(abs(part.exponent)):
                inParts.append(MsrPart(part.name, expo))

        divisor = Frac(1)
        for elPart in inElem.measure.list:
            expo = 1
            if elPart.exponent < 0:
                expo = -1
            for i in range(abs(elPart.exponent)):
                found = False
                for idx in range(len(inParts)):
                    if inParts[idx].exponent == expo:
                        if elPart.name == inParts[idx].name:
                            found = True
                            break
                        rate = (elPart.name, inParts[idx].name)
                        if rate in self.__rates:
                            divisor = divisor.mul(
                                Frac.shorter(
                                            numerator = self.__rates[rate]['multiplicity']
                                            ,denominator = self.__rates[rate]['rate']
                                )
                            )
                            found = True
                            break
                if found:
                    del inParts[idx]
                else:
                    return None
        if len(inParts) == 0:
            return divisor
        
        return None

    def convert(self, mixedNum, inMeasures):
        """heart of whole class"""
        
        # приводим к наименьшим единицам (среди запрошенных)
        lowest = self.convert_to_lowest(mixedNum, inMeasures)

        outList = []    # сюда будем накапливать результат
        # вспомогательные списки
        remainders = [] # остатки
        quotients  = [] # частные
        for el in lowest.list:
            # изначально равны исходным числам
            # и будут последовательно уменьшаться
            remainders.append(el)
            # изначально равны исходным числам,
            # но будут целиком перезаписаны
            # каждый раз, когда найдется соответствующий курс
            # или останутся в предыдущем состоянии
            quotients.append(el)  

        for inMsr in inMeasures:
            # для каждой запрошенной единицы
            
            for idx in range(len(remainders)):
                
                divisor = self.get_conversion_divisor(remainders[idx], inMsr)
                if divisor:
                
                    # получаем очередное частное
                    quotient = remainders[idx].rational.div(divisor)
                    # выделяем целую часть (на случай, если далее встретятся более мелкие единицы)
                    intQuotient = Frac(quotient.mixed().intPart)
                    # целая часть помещается в результат
                    outList.append(Elem(intQuotient, inMsr))
                    # остаток уменьшается
                    remainders[idx] = Elem(remainders[idx].rational.sub(intQuotient.mul(divisor)), remainders[idx].measure)
                    # в сырое частное помещается остаток от целой части, номинированный в текущей единице
                    # (или целиком текущая единица, если для нее не был сформирован делитель)
                    # в конце вычислений, если после очередной единицы
                    # не встретится более мелкая - такие необработанные ошметки сырых частных скомпонуются с результатом
                    quotients[idx]  = Elem(quotient.sub(intQuotient), inMsr)

        outList.extend(quotients)
        return(MixedNum(outList).pack())
        """

                # определяем делитель (по умолчанию = 1, таким и остается,
                # если единицы равны или не удастся получить колный делитель
                divisor = Frac(1)
                # признак того, что делитель сформирован на основании
                # всех частей единицы
                divisorComplete = True
                if inMsr != remainders[idx].measure:
                    # если входящая единица не равна единице элемента
                    # вычисляем делитель по частям
                    for numPart in remainders[idx].measure.list:
                        # для каждой части единицы очередного остатка
                        # partFound = False
                        
                        for inPart in inMsr.list:
                            partFound = False
                            # для каждой части очередной входной единицы
                            if numPart == inPart:
                                partFound = True
                                continue
                       
                            if abs(numPart.exponent) != abs(inPart.exponent):
                                # incomparable
                                continue

                            rate = (numPart.name, inPart.name)
                            if not rate in self.__rates.keys():
                                continue
                            # если существует курс перевода
                            partFound = True

                            # формируем множитель, на который будет домножен делитель
                            mutiplier = Frac.shorter(
                                            numerator = self.__rates[rate]['multiplicity']
                                            ,denominator = self.__rates[rate]['rate']
                                        )
                            # возводим в необходимую степень
                            if numPart.exponent < 0:
                                mutiplier = mutiplier.reciprocal()
                            for i in range(abs(numPart.exponent) - 1):
                                mutiplier = mutiplier.mul(mutiplier)

                            # новое промежуточное стостояние делителя
                            divisor = divisor.mul(mutiplier)

                        divisorComplete = divisorComplete and partFound

                if divisorComplete:
                    # делитель для очередного элемента числа полностью пересчитан
                    # относительно очредной входящей единицы:
                    # обсчитываем вспомогательные данные 
                    # и формируем очередную часть результата
                    # иначе их текущие состояния полностью сохраняются для следующей итерации

                    # получаем очередное частное
                    quotient = remainders[idx].rational.div(divisor)
                    # выделяем целую часть (на случай, если далее встретятся более мелкие единицы)
                    intQuotient = Frac(quotient.mixed().intPart)
                    # целая часть помещается в результат
                    outList.append(Elem(intQuotient, inMsr))
                    # остаток уменьшается
                    remainders[idx] = Elem(remainders[idx].rational.sub(intQuotient.mul(divisor)), remainders[idx].measure)
                    # в сырое частное помещается остаток от целой части, номинированный в текущей единице
                    # (или целиком текущая единица, если для нее не был сформирован делитель)
                    # в конце вычислений, если после очередной единицы
                    # не встретится более мелкая - такие необработанные ошметки сырых частных скомпонуются с результатом
                    quotients[idx]  = Elem(quotient.sub(intQuotient), inMsr)

        outList.extend(quotients)
        return(MixedNum(outList).pack())
        """