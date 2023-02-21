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

            self.__list.append(MsrPart(el.name, el.exponent))

    def __str__(self):
        return(','.join([str(i) for i in self.__list]))

    def __eq__(self, other):
        def sgn(expo):
            return(expo > 0)
        
        if not isinstance(other, Measure):
            return False

        sParts = {}
        for part in self.__list:
            expo = sParts.get((part.name, sgn(part.exponent)))

            if expo:
                sParts[(part.name, sgn(expo))] = expo + part.exponent
            else:
                sParts[(part.name, sgn(part.exponent))] = part.exponent
        
        for part in other.__list:
            if not (part.name,sgn(part.exponent)) in sParts:
                return False
            sParts[(part.name, sgn(part.exponent))] = sParts[(part.name, sgn(part.exponent))] - part.exponent

        for part in sParts:
            if sParts[part] != 0:
                return False

        return True

    def __neg__(self):
        outList = []
        for el in self.__list:
            outList.append(MsrPart(el.name, -el.exponent))
        return(Measure(outList))

    @property
    def list(self):
        return(self.__list)

    def combine(self, *others):
        """union lists of entering parts of measure"""
        outList = []
        outList.extend(self.__list)
        for el in others:
            outList.extend(el.list)
        return(Measure(outList))

    def fold(self):
        """
        summation of the same-name exponents, removing zeroes
        """

        def get_index(inList, inName):
            for idx in range(len(inList)):
                if inList[idx].name == inName:
                    return idx
            return None

        outList = []
        for el in self.__list:
            idx = get_index(outList, el.name)
            if idx == None:
                outList.append(MsrPart(el.name, el.exponent))
            else:
                newExpo = el.exponent + outList[idx].exponent
                if newExpo:
                    outList[idx] = MsrPart(outList[idx].name, newExpo)
                else:
                    del outList[idx]
        return(Measure(outList))

    def isTrivial(self):
        """if the measure is trivial: it has only one part and the exponent 1"""
        return(
            len(self.__list) == 1
            and self.__list[0].exponent == 1
        )

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

class MixedNum:
    """list of named fractions"""
    def __init__(self, inList = []):
        self.__list = []
        for el in inList:
            if not isinstance(el, Elem):
                raise ValueError("incorrect element of mixed number")
            idx = self.get_measure_index(el.measure)
            if idx == None:
                self.__list.append(Elem(el.rational, el.measure))
            else:
                self.__list[idx] = Elem(self.__list[idx].rational.add(el.rational), self.__list[idx].measure)

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
        divisor = converter.convert_to_lowest_join(other, measures)
        if len(divisor.list) > 1:
            raise ValueError('divisor contains more than one measure')

        return(self.mul(divisor.reciprocal()))

    def pack(self):
        """remove zero-elements"""
        outList = []
        for el in self.__list:
            if not el.rational.isZero():
                outList.append(Elem(el.rational, el.measure))
        return(MixedNum(outList))

    def fold_measures(self):
        outList = []
        for el in self.__list:
            outList.append(
                Elem(
                    el.rational
                    ,el.measure.fold()
                )
            )
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
        for el in (*self.list, *other.list):
            if el.measure not in measures:
                measures.append(el.measure)

        # преобразуем делимое и делитель к наименьшим единицам в существующих сетах единиц
        lwSelf  = converter.convert_to_lowest_join(self, measures).pack()
        lwOther = converter.convert_to_lowest_join(other, measures).pack()
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
        for el in (*self.list, *other.list):
            if el.measure not in measures:
                measures.append(el.measure)

        # преобразуем делимое и делитель к наименьшим единицам в существующих сетах единиц
        lwSelf  = converter.convert_to_lowest_join(self, measures).pack()
        lwOther = converter.convert_to_lowest_join(other, measures).pack()

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
    
    def __init__(self) -> None:
        self.__rates    = {}    # list of dictionaries, contains rates to convert one measure to another
        self.__units = []       # ??UNNECESSARY?? list of sets, every set contains "line" (unordered) of units of one context
        # units используется теперь фактически только при расчете кросс-курсов (оптимизирует поиск,
        # но тратится время на само заполнение units
        # кроме того, это единственный объект, который различает отдельные "линейки", полезен для пользователя
        # надо ли? теоретически изолированные сеты можно получить рассчетным методом по таблице курсов)
        self.__aliases = {} # словарь имен производных единиц (1 литр = 0.001 м^3) {имя: элемент}

    @property
    def rates(self):
        return(self.__rates)

    @property
    def units(self):
        return(self.__units)

    @property
    def aliases(self):
        return(self.__aliases)

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

            #alias
            al = self.__aliases.get(target)
            if al:
                self.add_alias_record(source, Elem(al.rational.mul(Frac.shorter(rate,multiplicity)).reduce(),al.measure))

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

        add_record(source, target, unitSet, multiplicity, rate)
        add_cross_rate(source, target, unitSet)
        add_cross_rate(target, source, unitSet)

        return True

    def get_unit_rate(self, source, target):
        """multiplier that converts the source unit to the target OR None"""
        if source == target:
            return(Frac(1))
        rate = self.__rates.get((source,target))
        if rate:
            return(
                Frac.shorter(
                    numerator    = rate['multiplicity']
                    ,denominator = rate['rate']
                )
            )
        return None

    def get_measure_rate(self, source, target):
        """multiplier that converts the source measure to the target OR None"""
        def uncover(msr):
            # по максимуму унифицируем единицы перед расчетом курса
            disclosed = self.disclose_measure(msr) 
            mult = Frac(**disclosed.rational.dict()) # результирующий множитель
            # объединяем
            unified = self.unify_measure(disclosed.measure)
            mult = mult.mul(unified.rational)
            # сворачиваем
            folded = unified.measure.fold()
            return(mult, folded)

        # входная:
        # раскрываем псевдонимы
        # disclosed = self.disclose_measure(target) 
        # mult = Frac(**disclosed.rational.dict()) # результирующий множитель
        # объединяем
        # unified = self.unify_measure(disclosed.measure)
        # mult = mult.mul(unified.rational)
        # сворачиваем
        # folded = unified.measure.fold()

        tgtMult, folded = uncover(target)


        # все части входящей единицы, разбитые "по одной" степени
        tgtParts = []
        for part in folded.list:
            expo = 1
            if part.exponent < 0:
                expo = -1
            for i in range(abs(part.exponent)):
                tgtParts.append(MsrPart(part.name, expo))


        # исходная
        # disclosed = self.disclose_measure(source)
        # mult = mult.div(disclosed.rational)
        # unified = self.unify_measure(disclosed.measure)
        # mult = mult.div(unified.rational)
        # folded = unified.measure.fold()

        srcMult, folded = uncover(source)
        mult = tgtMult.div(srcMult)

        # для каждой части исходной единицы
        for srcPart in folded.list:
            expo = 1
            if srcPart.exponent < 0:
                expo = -1
            # каждую единицу степени перебираем отдельно
            for i in range(abs(srcPart.exponent)):
                found = False
                for idx in range(len(tgtParts)):
                    if tgtParts[idx].exponent == expo:

                        if srcPart.name == tgtParts[idx].name:
                            found = True
                            break

                        opMult = self.get_unit_rate(srcPart.name, tgtParts[idx].name)
                        if opMult:
                            if expo < 0:
                                opMult = opMult.reciprocal()
                            mult = mult.mul(opMult)
                            found = True
                            break
                if found:
                    # удаляем "использованную" часть входной единицы
                    del tgtParts[idx]
                else:
                    # однозначно сигнализирует о несовместимости единиц
                    return None
        if len(tgtParts) == 0:
            # если в конечном счете использованы все части - ОК
            return mult
        
        return None

    def get_unitSet(self, unit):
        """return set where the inMeasure is"""
        for el in self.__units:
            if unit in el:
                return el
        return None

    def add_alias_record(self, alias, elem):
        if alias in self.__aliases:
            return False
        self.__aliases[alias] = elem
        return True

    def add_alias(self, alias, elem):
        if self.add_alias_record(alias, elem):
            unitSet = self.get_unitSet(alias)
            if unitSet:
                for uni in unitSet:
                    if uni == alias:
                        continue
                    rate = self.get_unit_rate(uni, alias)
                    if rate:
                        self.add_alias_record(uni, Elem(elem.rational.div(rate).reduce(),elem.measure))
            return True

        return False
    
    def disclose_alias(self, alias):
        elem = self.__aliases.get(alias)
        if elem:
            outList = []
            mult = Frac(**elem.rational.dict())
            for msr in elem.measure.list:
                elem = self.disclose_alias(msr.name)
                if elem:
                    iSgn = 1 if msr.exponent > 0 else -1
                    if iSgn > 0:
                        mult = mult.mul(elem.rational)
                    else:
                        mult = mult.div(elem.rational)
                    for fndPart in elem.measure.list:
                        outList.append(MsrPart(fndPart.name, fndPart.exponent * iSgn))
                else:
                    outList.append(msr)
            return(Elem(mult, Measure(outList)))

        return elem

    def disclose_measure(self, inMeasure):
        outList = []
        mult = Frac(1)
        for inPart in inMeasure.list:

            elem = self.disclose_alias(inPart.name)
            if elem:
                iSgn = 1 if inPart.exponent > 0 else -1
                if iSgn > 0:
                    mult = mult.mul(elem.rational)
                else:
                    mult = mult.div(elem.rational)
                for fndPart in elem.measure.list:
                    outList.append(MsrPart(fndPart.name, fndPart.exponent * iSgn))
            else:
                outList.append(inPart)
        return(Elem(mult, Measure(outList)))

    def unify_measure(self, inMeasure):
        """replace all parts of measure to the lowest"""
        outList = []   # результирующий список юниотов
        mult = Frac(1) # результирующий множитель
        for inPart in inMeasure.list:
            # очередной юнит сверяем с юнитами результирующего списка
            # (в начале он пуст)
            chosenMsr = MsrPart(inPart.name, inPart.exponent)
            for idx in range(len(outList)):
                if outList[idx].name == chosenMsr.name:
                    continue
                # текущий множитель, преобразующий юнит списка к очередному
                opMult = self.get_unit_rate(outList[idx].name, chosenMsr.name)
                if opMult:
                    if Frac(1).intComp(opMult) > 0:
                        # текущий множитель меньше единицы:
                        # в результирующем списке юнит с бОльшей единицей
                        # подменяем в нем имя единицы на имя очередного юнита
                        outList[idx] = MsrPart(chosenMsr.name, outList[idx].exponent)
                        # переворачиваем множитель -
                        # он должен быть больше единицы, 
                        opMult = opMult.reciprocal()
                        # запоминаем экспоненту большего юнита
                        # (того, который является причиной изменения множителя на данной итерации)
                        expo = outList[idx].exponent
                    else:
                        # текущий множитель меньше единицы
                        # меньший юнит уже лежит в результирующем списке
                        # подменяем его именем имя в очередном юните
                        chosenMsr = MsrPart(outList[idx].name, chosenMsr.exponent)
                        # причиной изменений стал очередной юнит - запоминаем его экспоненту
                        expo = chosenMsr.exponent

                    # увеличиваем множитель, если менялся элемент с положительной экспонентой
                    # иначе уменьшаем
                    for i in range(abs(expo)):
                        if expo > 0:
                            mult = mult.mul(opMult)
                        else:
                            mult = mult.div(opMult)

            outList.append(chosenMsr)

        return(Elem(mult, Measure(outList)))

    def convert_to_lowest_join(self, inMNum, inMeasures):
        lowest = self.convert_to_lowest(inMNum, inMeasures)
        return(lowest[0].compose(lowest[1]))

    def convert_to_lowest(self, inMNum, inMeasures):
        """convert to the smallest requested measure if possible"""
 
        # приводим элементы inMNum к наименьшей возможной из запрошенных
        # (если возможно)
        # это гарантирует конвертацию в запрошенные единицы
        # (с последовательным выделением целых от наибольшей к меньшей)
        # а также это необходимо для деления и сравнения
        # (т.к. приводит к единой единице, неважно, что к наименьшей)

        lowest      = []
        unConverted = []

        for el in inMNum.list:
            divisor = None
            chosenMsr = None

            for inMsr in inMeasures:

                opDiv = self.get_measure_rate(el.measure, inMsr) # дробь или не существует
                if (
                    opDiv # если существует
                    and (
                            not divisor # делитель еще не инициализирован
                            # или:
                            # если текущий делитель меньше сохраненного
                            # значит, он приведет число к большему значению 
                            # (что соответствует меньшей единице)
                            or opDiv.intComp(divisor) < 0
                    )
                ):
                    # перезаписываем делитель и запоминаем текущую единицу
                    divisor = Frac(**opDiv.dict())
                    chosenMsr = inMsr.combine()
            if divisor:
                lowest.append(Elem(el.rational.div(divisor),chosenMsr))
            else:
                unConverted.append(el)
        
        return(MixedNum(lowest), MixedNum(unConverted))

    def convert_join(self, inMNum, inMeasures):
        """alias for convert with composing result"""
        res = self.convert(inMNum, inMeasures)
        return(res[0].compose(res[1]))

    def convert(self, inMNum, inMeasures):
        """convert to requested measures if possible"""
        
        # приводим к наименьшим единицам (среди запрошенных)
        lowest = self.convert_to_lowest(inMNum, inMeasures)

        # конвертировать будем только первый элемент кортежа
        # т.к. только он гарантированно соответствует запрошенным единицам
        # несконвертированную часть - добавим отдельно, аналогично convert_to_lowest
        unConverted = lowest[1]
        lowest = lowest[0]

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
                # для каждого остатка (изначально - элемента)
                # получаем делитель к запрошенной единице
                divisor = self.get_measure_rate(remainders[idx].measure, inMsr)
                if divisor:
                    # если делитель существует
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
        return(MixedNum(outList).pack(), unConverted)
