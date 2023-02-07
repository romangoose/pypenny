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
    def __init__(self, *inLists):
        self.__list = []
        for lst in inLists:
            for el in lst:
                if not isinstance(el, MsrPart):
                    raise ValueError("incorrect measure's part")
                if el.name == '':
                    continue
                idx = self.name_index(el.name)
                if idx == None:
                    self.__list.append(MsrPart(el.name, el.exponent))
                else:
                    newExpo = el.exponent + self.__list[idx].exponent
                    if newExpo:
                        self.__list[idx] = MsrPart(self.__list[idx].name, newExpo)
                    else:
                        del self.__list[idx]
        #if len(self.__list) == 0:
        #    self.__list.append(MsrPart())

    def __str__(self):
        return(','.join([str(i) for i in self.__list]))

    def __eq__(self, other):
        if not isinstance(other, Measure):
            return False
        sN = self.names()
        oN = other.names()
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

    def names(self):
        """all part's names of the measure"""
        outList = []
        for el in self.__list:
            outList.append(el.name)
        return outList

    def name_index(self, inName):
        for idx in range(len(self.__list)):
            if self.__list[idx].name == inName:
                return idx
        return None

    def get_part_by_name(self, inName):
        idx = self.name_index(inName)
        if idx == None:
            return None
        return(self.__list[idx])

    def compose(self, *others):
        # """union (with the summation  of the same-name parts) lists of entering MixedNumbers"""
        outLists = []
        outLists.append(self.__list)
        for el in others:
            outLists.append(el.list)
        return(Measure(*outLists))


class Elem:
    """the elementary part of a mixed number: a fraction having a measure"""
    def __init__(self, rational, measure = None):
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
        self.__measure = measure

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
    def __init__(self, *inLists):
        self.__list = []
        for lst in inLists:
            for el in lst:
                if not isinstance(el, Elem):
                    raise ValueError("incorrect element of mixed number")
                idx = self.measure_index(el.measure)
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

    def measure_index(self, inMeasure):
        for idx in range(len(self.__list)):
            if self.__list[idx].measure == inMeasure:
                return idx
        return None

    #INCORRECT
    def names(self):
        """all measure names of the number"""
        outList = []
        for el in self.__list:
            outList.append(el.name)
        return outList

    #INCORRECT
    def get_elem_by_name(self, inName):
        for el in self.__list:
            if el.name == inName:
                return el
        return None
	
    def compose(self, *others):
        """union (with the summation  of the same-name parts) lists of entering MixedNumbers"""

        # по факту, и конструирование числа из элементов
        # и суммирование двух чисел - 
        # сводятся к операции компоновки,
        # то есть, объединению списков суммированию одноименных элементов.
        # compose фактически явлется алиасом для конструктора класса:
        # в конструктор передаются списки,
        # сюда - непосредственно MixedNum

        outLists = []
        outLists.append(self.__list)
        for mxNum in others:
            outLists.append(mxNum.list)
        return(MixedNum(*outLists))

    def reciprocal(self):
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
        outList = []
        for oEl in other.__list:
            for sEl in self.__list:
                outList.append(
                    Elem(
                        oEl.rational.mul(sEl.rational)
                        ,oEl.measure.compose(sEl.measure)
                    )
                )
        return(MixedNum(outList))

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


        # подготавливаем общий сет всех единиц 
        measureSet = set()
        for mSt in converter.measures:
            measureSet = measureSet.union(mSt)

        # преобразуем делимое и делитель к наименьшим единицам в существующих сетах единиц
        lwSelf  = converter.convert_to_lowest(self, measureSet).pack()
        lwOther = converter.convert_to_lowest(other, measureSet).pack()
        if len(lwOther.__list) == 0:
            raise ZeroDivisionError('division by zero')

        # вычисляем минимальное (по модулю) частное среди пар операндов с совпадающими единицами
        minQuotient = None
        exsDirection = None
        for measure in lwOther.names():
            if measure in lwSelf.names():
                elSelf  = lwSelf.get_elem_by_name(measure)
                elOther = lwOther.get_elem_by_name(measure)
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
        remainder = converter.convert(remainder, self.names())

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

        # подготавливаем общий сет всех единиц 
        measureSet = set()
        for mSt in converter.measures:
            measureSet = measureSet.union(mSt)

        # преобразуем делимое и делитель к наименьшим единицам в существующих сетах единиц
        lwSelf  = converter.convert_to_lowest(self, measureSet).pack()
        lwOther = converter.convert_to_lowest(other, measureSet).pack()


        result = 0 # по умолчанию числа равны
        # перебираем "левое соединение" единиц other с с единицами self
        for measure in lwOther.names():
            if measure in lwSelf.names():
                elSelf  = lwSelf.get_elem_by_name(measure)
                elOther = lwOther.get_elem_by_name(measure)
                side = elSelf.rational.intComp(elOther.rational)
            else:
                # сравнение элемента с ничем полностью определяется знаком элемента
                # (нулевые элементы, которые имеют неотрицательный знак, - исключены благодаря pack())
                elOther =   lwOther.get_elem_by_name(measure)
                side    = - elOther.rational.intSign() # здесь минус: знак инвертирован, 
                                                       # потому что элементы сравниваются в обратном порядке)

            if side == 0:
                continue
            if result != 0 and result != side:
                # разошлись стороны относительно нуля
                return None
            result = side

        # соединяем единицы наборот, 
        # в поисках единиц, присутствующих 
        # проверяем знак на совпадение
        for measure in lwSelf.names():
            if measure not in lwOther.names():
                elSelf  = lwSelf.get_elem_by_name(measure)
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
    # measures - список множеств, отдельное множество - это перечень единиц, относящихся к одному контексту
    # (то есть таких, которые могут быть взаимно выражены друг через друга)
    # ranged - список всех единиц, общий (не разделенный по сетам), 
    # который перед конвертацией должен быть отсортирован в восходящем порядке
    # (в итоге для каждого сета будет известен упорядоченный список единиц)
    # isRanged - соответственно, признак отсортированности, 
    # который сбрасывается при любом изменении курсов 
    
    def __init__(self) -> None:
        self.__rates    = {}    # list of dictionaries, contains rates to convert one measure to another
        self.__measures = []    # list of sets, every set contains "line" (unordered) of measures of one context
        self.__ranged   = []    # ranged (sorted from "minimal" to "maximal") list of measures (all-in-one)
        self.__isRanged = False # True, if ranged was really sorted. When rate are modifyed, sets to False

    @property
    def rates(self):
        return(self.__rates)

    @property
    def measures(self):
        return(self.__measures)

    def sort_ranged(self):

        """sort ranged if not yet"""

        if not self.__isRanged:
            # bubble sort (ascending)
            done = False
            while not done:
                done = True
                for idx in range(1,len(self.__ranged)):
                    if (self.__ranged[idx].rational.intComp(self.__ranged[idx-1].rational) < 0):
                        self.__ranged[idx], self.__ranged[idx-1] = self.__ranged[idx-1], self.__ranged[idx]
                        done = False
            self.__isRanged = True

    @property
    def ranged(self):
        self.sort_ranged()
        return(self.__ranged)

    def get_measureSet(self, inMeasure):

        """return set where the inMeasure is"""

        for el in self.__measures:
            if inMeasure in el:
                return el
        return None

    def get_measureList(self, inMeasure):

        """return (ordered) list of inMeasure's set"""

        mSet = self.get_measureSet(inMeasure)
        if mSet == None:
            return None

        self.sort_ranged()
        outList = []
        for el in self.ranged:
            if el.name in mSet:
                outList.append(el.name)
        return (outList)

    def add_rate(self, source, target, multiplicity, rate):
        """add main and dependent (cross and reverse) rates"""

        #inner auxiliary functions
        def update_measures(*inMeasures):
            """add a measure to the corresponding set"""

            outList = []
            crSet = {*inMeasures}
            for mSt in self.__measures:
                found = False
                for measure in inMeasures:
                    if measure in mSt:
                        found = True
                        crSet = crSet.union(mSt)
                        break
                if not found:
                    outList.append(mSt)
            outList.append(crSet)
            self.__measures = outList
            return self.__measures[-1]

        def add_cross_rate(base, cross, measureSet, depth = False):
            """cross-rates"""
            
            for msreFound in measureSet:
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
                    msreFound, cross, measureSet
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
                    add_cross_rate(cross, msreFound, measureSet, True)
                

        def add_record(source, target, measureSet, multiplicity, rate):
            """elementary entry of rate table"""

            # таблица устроена как словарь, 
            # где ключом является кортеж (исходная + целевая единица),
            # данными - словарь {кратность, курс}

            self.__rates[(source, target)] = {
                                                'multiplicity': multiplicity
                                                ,'rate':        rate
                                            }

            # update ranged
            msrSource = Measure((MsrPart(source),))
            frac = Frac.shorter(rate, multiplicity)
            # костылек - создаем объект, чтобы воспользоваться его методом :(
            idx = MixedNum(self.__ranged).measure_index(msrSource)
            if idx == None:
                self.__ranged.append(Elem(frac,msrSource))
            else:
                if (self.__ranged[idx].rational.intComp(frac) > 0):
                    # replace by lesser
                    self.__ranged[idx] = Elem(frac, msrSource)

            # reverse record
            if not (target, source) in self.__rates:
                add_record(target, source, measureSet, rate, multiplicity)
            
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

        measureSet = update_measures(source, target)

        self.__isRanged = False # сбрасываем признак сортировки 
        add_record(source, target, measureSet, multiplicity, rate)
        add_cross_rate(source, target, measureSet)
        add_cross_rate(target, source, measureSet)

        return True


    def convert_to_lowest(self, mixedNum, measureSet):
        """preliminary calculation for .convert() and .times()"""

        # приводим элементы MixedNum к наименьшей еинице внутри каждого сета

        # сортируем ranged, если еще не сортирован
        self.sort_ranged()

        lowest      = []
        unConverted = []
        for el in mixedNum.list:
            found = False

            # ищем единицу каждого элемента числа в запрошенном сете единиц
            if el.name in measureSet:
                for base in self.__ranged:
                # перебираем упорядоченный набор единиц
                # (начиная с наименьшей)
                    if el.name == base.name:
                        # ту же самую единицу добавляем в результат как есть
                        found = True
                        lowest.append(Elem(el.rational, base.name))
                        break

                    rate = (el.name, base.name)
                    if rate in self.__rates.keys():
                        # добавляем конвертацию единицы числа в первую же найденную единицу (наименьшую),
                        # если курс перевода существует
                        found = True
                        lowest.append(
                            Elem(
                                el.rational.mul(
                                    Frac.shorter(
                                        numerator = self.__rates[rate]['rate']
                                        ,denominator = self.__rates[rate]['multiplicity']
                                    )
                                )
                                ,base.name
                            )
                        )
                        break
            if not found:
                # если единица не найдена 
                # (неизвестна, либо ни одна из единиц ее сета не запрошена для конвертации)
                # - добавим ее как есть в конец результирующего числа
                unConverted.append(el)
        return(MixedNum(lowest, unConverted))


    def convert(self, mixedNum, inMeasures):
        """heart of whole class"""
        
        # normalize
        measures = []
        for measure in inMeasures:
            measures.append(measure.strip())

        lowest = self.convert_to_lowest(mixedNum, set(measures))

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

        for measure in measures:
            # для каждой запрошенной единицы
            for idx in range(len(remainders)):
                # определяем делитель
                if measure == remainders[idx].name:
                    divisor = Frac(1)
                else:
                    rate = (remainders[idx].name, measure)
                    if not rate in self.__rates.keys():
                        # курс не найден - списки не изменились
                        continue
                    divisor = Frac.shorter(
                            numerator = self.__rates[rate]['multiplicity']
                            ,denominator = self.__rates[rate]['rate']
                        )
                # получаем очередное частное
                quotient = remainders[idx].rational.div(divisor)
                # выделяем целую часть (на случай, если далее встретятся более мелкие единицы)
                intQuotient = Frac(quotient.mixed().intPart)
                outList.append(Elem(intQuotient, measure))
                # остаток уменьшаяется, его единица перезаписывается
                remainders[idx] = Elem(remainders[idx].rational.sub(intQuotient.mul(divisor)), remainders[idx].name)
                # сырое частное перезаписывается
                # в конце концов необработанные ошметки сырых частных добавятся к результату
                quotients[idx]  = Elem(quotient.sub(intQuotient), measure)

        return(MixedNum(outList, quotients).pack())
