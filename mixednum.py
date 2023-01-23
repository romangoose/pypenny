from rationals import Rational as Frac

class Elem:
    """the elementary part of a mixed number: a fraction having a measure name"""
    def __init__(self, rational, name=''):
        self.__rational = rational
        self.__name = name.strip()

    def __str__(self):
        return(str({'rational':str(self.__rational), 'name':str(self.__name)}))

    @property
    def name(self):
        return(self.__name)

    @property
    def rational(self):
        return(self.__rational)


class MixedNum:
    """list of named fractions"""
    def __init__(self, *inLists):
        self.__list = []
        for lst in inLists:
            for el in lst:
                idx = MixedNum.name_in_list(el.name, self.__list)
                if idx == None:
                    self.__list.append(Elem(el.rational, el.name))
                else:
                    self.__list[idx] = Elem(self.__list[idx].rational.add(el.rational), el.name)

    def __str__(self):
        return(str(self.__list))

    @property
    def list(self):
        return(self.__list)

    def rationals(self):
        """all fractions of the number"""
        outList = []
        for el in self.__list:
            outList.append(el.rational)
        return outList

    def names(self):
        """all measure names of the number"""
        outList = []
        for el in self.__list:
            outList.append(el.name)
        return outList

    def get_elem_by_name(self, inName):
        for el in self.__list:
            if el.name == inName:
                return el
        return None
	
    def compose(self, *others):
        """union (with the summation  of the same-name parts) lists of entering MixedNumbers"""

        """
        In fact, both:
            - assembling a number from elements
            - and summation of several numbers 
            are reduced to the compose operation.

        """

        outLists = []
        outLists.append(self.__list)
        for mxNum in others:
            outLists.append(mxNum.list)
        return(MixedNum(*outLists))

    def pack(self):
        """remove zero-elements"""
        outList = []
        for el in self.list:
            if not el.rational.isZero():
                outList.append(Elem(el.rational, el.name))
        return(MixedNum(outList))

    def with_rationals(self, func, pars=None):
        """apply a function to the rational part of the MixedNumber elements"""

        """in this way it is possible, for example, to multiply (by a measureless number), reduce, etc."""
        outList = []
        for el in self.list:
            if pars == None:
                outList.append(Elem(func(el.rational), el.name))
            else:
                outList.append(Elem(func(el.rational,pars), el.name))
        return(MixedNum(outList))

    def times(self, other, converter):

        """Mx/Mx division with remainder"""
	# calculate how many times the divisor occurs in the dividend

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


        measureSet = set()
        for mSt in converter.measures:
            measureSet = measureSet.union(mSt)

        lwSelf  = converter.convert_to_lowest(self, measureSet).pack()
        lwOther = converter.convert_to_lowest(other, measureSet).pack()
        if len(lwOther.__list) == 0:
            raise ZeroDivisionError('division by zero')

        # вычисляем минимальное частное среди пар операндов с совпадающими единицами
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
                # если в смешанном делителе есть единица, не входящая в состав делимого
                # то делитель содержится в делимом ноль раз, по определению "исчерпания"
                minQuotient = Frac()
                break
        # вычитаем из делимого делитель, умноженный на найденное минимальное частное
        remainder = self.compose(other.with_rationals(Frac.mul, minQuotient).with_rationals(Frac.opposite))

        # конвертируем остаток в исходные единицы
        # (в делителе может присутствовать единица, отсутствующая в делимом, что может привести к неудобной форме результата)
        remainder = converter.convert(remainder, self.names())

        return(minQuotient, remainder)

    @staticmethod
    def name_in_list(inName, inList):
        for idx in range(len(inList)):
            if inList[idx].name == inName:
                return idx
        return None


class Converter:
    """converts one measure to another if there is a corresponding exchange rate"""
    
    __rates    = {}    # list of dictionaries, contains rates to convert one measure to another
    __measures = []    # list of sets, every set contains "line" (unordered) of measures of one context
    __ranged   = []    # ranged (sorted from "minimal" to "maximal") list of measures (all-in-one)
    __isRanged = False # True, if ranged was really sorted. When rate are modifyed, sets to False

    @property
    def rates(self):
        return(self.__rates)

    @property
    def measures(self):
        return(self.__measures)

    @property
    def ranged(self):
        return(self.__ranged)

    def get_measureSet(self, inMeasure):
        for el in self.__measures:
            if inMeasure in el:
                return el
        return None

    @staticmethod
    def simple_frac(numerator, denominator):
        absN = abs(numerator)
        absD = abs(denominator)
        return Frac(
            intPart = 0
            ,numerator = absN
            ,denominator = absD
            ,isNegative = ((absN != numerator) != (absD != denominator))
        )

    def add_rate(self, source, target, multiplicity, rate):

        #inner functions
        def update_measures(*inMeasures):
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

        def add_cross_rate(base, cross, measureSet):
            #measureSet = update_measures(base, cross)
            
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

        def add_record(source, target, measureSet, multiplicity, rate):

            self.__rates[(source, target)] = {
                                                'multiplicity': multiplicity
                                                ,'rate':        rate
                                            }

            add_cross_rate(source, target, measureSet)

            frac = self.simple_frac(rate, multiplicity)
            idx = MixedNum.name_in_list(source, self.__ranged)
            if idx == None:
                self.__ranged.append(Elem(frac, source))
            else:
                if (self.__ranged[idx].rational.intComp(frac) > 0):
                    # replace by lesser
                    self.__ranged[idx] = Elem(frac, source)

            # inverted
            if not (target, source) in self.__rates:
                add_record(target, source, measureSet, rate, multiplicity)
            
            self.__isRanged = False
            return True

        # main body
        if source == target:
            return False

        if multiplicity.isZero() or rate.isZero():
            return False

        if (source,target) in self.__rates:
            return False

        # multiplicity and rate may be a fractions
        # but we must reduce they to integer
        commonMult = Frac(multiplicity.denominator * rate.denominator)
        
        multiplicity = multiplicity.mul(commonMult).simple()
        multiplicity = (multiplicity.numerator // multiplicity.denominator)*multiplicity.intSign()
        
        rate = rate.mul(commonMult).simple()
        rate = (rate.numerator // rate.denominator)*rate.intSign()

        measureSet = update_measures(source, target)
        return (add_record(source, target, measureSet, multiplicity, rate))

    def convert_to_lowest(self, mixedNum, measureSet):
        if not self.__isRanged:
            #bubble sort (DESC)
            done = False
            while not done:
                done = True
                for idx in range(1,len(self.__ranged)):
                    if (self.__ranged[idx].rational.intComp(self.__ranged[idx-1].rational) < 0):
                        self.__ranged[idx], self.__ranged[idx-1] = self.__ranged[idx-1], self.__ranged[idx]
                        done = False
            self.__isRanged = True

        lowest      = []
        unConverted = []
        for el in mixedNum.list:
            found = False

            if el.name in measureSet:
                for base in self.__ranged:
                    #we begins from lowest measure
                    if el.name == base.name:
                        #the same measure
                        found = True
                        lowest.append(Elem(el.rational, base.name))
                        break

                    rate = (el.name, base.name)
                    if rate in self.__rates.keys():
                        found = True
                        lowest.append(
                            Elem(
                                el.rational.mul(
                                    self.simple_frac(
                                        numerator = self.__rates[rate]['rate']
                                        ,denominator = self.__rates[rate]['multiplicity']
                                    )
                                )
                                ,base.name
                            )
                        )
                        break
            if not found:
                unConverted.append(el)
        return(MixedNum(lowest, unConverted))


    def convert(self, mixedNum, inMeasures):

        measures = []
        for measure in inMeasures:
            measures.append(measure.strip())

        lowest = self.convert_to_lowest(mixedNum, set(measures))

        outList = []
        remainders = []
        quotients  = []
        for el in lowest.list:
            remainders.append(el)
            quotients.append(el)

        for measure in measures:
            for idx in range(len(remainders)):
                if measure == remainders[idx].name:
                    divisor = Frac(1)
                else:
                    rate = (remainders[idx].name, measure)
                    if not rate in self.__rates.keys():
                        continue
                    divisor = self.simple_frac(
                            numerator = self.__rates[rate]['multiplicity']
                            ,denominator = self.__rates[rate]['rate']
                        )
                quotient = remainders[idx].rational.div(divisor)
                intQuotient = Frac(quotient.mixed().intPart)
                outList.append(Elem(intQuotient, measure))
                remainders[idx] = Elem(remainders[idx].rational.sub(intQuotient.mul(divisor)), remainders[idx].name)
                quotients[idx]  = Elem(quotient.sub(intQuotient), measure)

        return(MixedNum(outList, quotients).pack())
