from decimal import DivisionByZero
from rationals import Rational as Frac

class Elem:

    def __init__(self, rational, name=''):
        self.__rational = rational
        self.__name = name.strip()

    @property
    def name(self):
        return(self.__name)

    @property
    def rational(self):
        return(self.__rational)


class MixedNum:

    def __init__(self, *inLists):
        self.__list = []
        for inList in inLists:
            for item in inList:
                idx = MixedNum.name_in_list(item.name, self.__list)
                if idx == None:
                    self.__list.append(Elem(item.rational, item.name))
                else:
                    self.__list[idx] = Elem(self.__list[idx].rational.add(item.rational), item.name)

    @property
    def list(self):
        return(self.__list)

    def rationals(self):
        outList = []
        for elem in self.__list:
            outList.append(elem.rational)
        return outList

    def names(self):
        outList = []
        for elem in self.__list:
            outList.append(elem.name)
        return outList

    def get_elem_by_name(self, inName):
        for elem in self.__list:
            if elem.name == inName:
                return elem
        return None
	
    def compose(self, *others):
        outLists = []
        outLists.append(self.__list)
        for mNum in others:
            outLists.append(mNum.list)
        return(MixedNum(*outLists))

    def pack(self):
        outList = []
        for item in self.list:
            if not item.rational.isZero():
                outList.append(Elem(item.rational, item.name))
        return(MixedNum(outList))

    def with_rationals(self, func, pars=None):
        outList = []
        for item in self.list:
            if pars == None:
                outList.append(Elem(func(item.rational), item.name))
            else:
                outList.append(Elem(func(item.rational,pars), item.name))
        return(MixedNum(outList))

    def times(self, other, converter):
        measureSet = set()
        for set_ in converter.measures:
            measureSet = measureSet.union(set_)

        lowestSelf  = converter.convert_to_lowest(self, measureSet).pack()
        lowestOther = converter.convert_to_lowest(other, measureSet).pack()
        if len(lowestOther.__list) == 0:
            raise DivisionByZero('division by zero')

        minimalDividend = None
        for name_ in lowestOther.names():
            if name_ in lowestSelf.names():
                elemSelf  = lowestSelf.get_elem_by_name(name_)
                elemOther = lowestOther.get_elem_by_name(name_)
                dividend = elemSelf.rational.div(elemOther.rational).reduce()
                if (minimalDividend == None) or (dividend.intComp(minimalDividend) < 0):
                    minimalDividend = Frac(**dividend.dict())
            else:
                minimalDividend = Frac()
                break
        #вычитаем из делимого делитель, умноженный на рассчитанный минимальный делитель
        remainder = self.compose(other.with_rationals(Frac.mul, minimalDividend).with_rationals(Frac.opposite))

        return(minimalDividend, remainder)

        #if (len(lowestSelf.list) != 1) or (len(lowestOther.list) != 1):
        #    raise ValueError('incompatible measures')
        #return(lowestSelf.list[0].rational.div(lowestOther.list[0].rational))

    @staticmethod
    def name_in_list(name, list):
        for idx in range(len(list)):
            if list[idx].name == name:
                return idx
        return None


class Converter:
    
    __rates    = {}
    __measures_old = []
    __measures = []
    __lowest     = ''
    __lowestMul  = 0
    __lowestRate = 0
    __ranged = []
    __isRanged = False

    @property
    def rates(self):
        return(self.__rates)

    #@property
    #def measures_old(self):
    #    return(self.__measures_old)

    @property
    def measures(self):
        return(self.__measures)

    #@property
    #def lowest(self):
    #    return(self.__lowest)

    @property
    def ranged(self):
        return(self.__ranged)

    def get_measureSet(self, inMeasure):
        for elem in self.__measures:
            if inMeasure in elem:
                return elem
        return None

    def add_rate(self, source, target, multiplicity, rate):

        #inner functions
        def add_measures(*inMeasures):
            outList = []
            currSet = {*inMeasures}
            for elem in self.__measures:
                found = False
                for inMeasure in inMeasures:
                    if inMeasure in elem:
                        found = True
                        currSet = currSet.union(elem)
                        break
                if not found:
                    outList.append(elem)
            outList.append(currSet)
            self.__measures = outList
            return self.__measures[-1]

        def add_cross_rate(base, cross, measureSet):

            #if not base in self.__measures_old:
            #    self.__measures_old.append(base)
            measureSet = add_measures(base, cross)
            
            #for found in self.__measures_old:
            for found in measureSet:
                if found == cross:
                    continue

                if (found,cross) in self.__rates:
                    continue
                
                #HERE возможно, оптимизировать поиск? (каждый раз получаем keys для проверки, а таблица растет)
                #if not (base, found) in self.__rates.keys():
                #    continue

                rateBase  = self.__rates[(base, cross)]
                rateFound = self.__rates[(base, found)]

                multiplicity = rateFound['rate']         * rateBase['multiplicity']
                rate         = rateFound['multiplicity'] * rateBase['rate']
                gcd_ = Frac.gcd(multiplicity, rate)
                add_record(
                    found, cross, measureSet
                        ,multiplicity // gcd_
                        ,rate         // gcd_
                    )

            #if not cross in self.__measures_old:
            #    self.__measures_old.append(cross)


        def add_record(source, target, measureSet, multiplicity, rate):

            self.__rates[(source, target)] = {
                                                'multiplicity': multiplicity
                                                ,'rate':        rate
                                            }

            add_cross_rate(source, target, measureSet)

            #if (
            #    self.__lowest == ''
            #    or (
            #            self.__lowestMul      <= multiplicity
            #            and self.__lowestRate >= rate
            #        )
            #    ):
            #        self.__lowest     = source
            #        self.__lowestMul  = multiplicity
            #        self.__lowestRate = rate

            frac = Frac(0,rate, multiplicity)
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
        commonMultiplicator = Frac(multiplicity.denominator * rate.denominator)
        
        multiplicity = multiplicity.mul(commonMultiplicator).simple()
        multiplicity = multiplicity.numerator // multiplicity.denominator
        
        rate = rate.mul(commonMultiplicator).simple()
        rate = rate.numerator // rate.denominator

        measureSet = add_measures(source, target)
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
        for elem in mixedNum.list:
            rateFound = False

            if elem.name in measureSet:
                for base in self.__ranged:
                    #we begins from lowest measure
                    if elem.name == base.name:
                        #the same measure
                        rateFound = True
                        lowest.append(Elem(elem.rational, base.name))
                        break

                    rate = (elem.name, base.name)
                    if rate in self.__rates.keys():
                        rateFound = True
                        lowest.append(
                            Elem(
                                elem.rational.mul(
                                    Frac(
                                        numerator = self.__rates[rate]['rate']
                                        ,denominator = self.__rates[rate]['multiplicity']
                                    )
                                )
                                ,base.name
                            )
                        )
                        break
            if not rateFound:
                unConverted.append(elem)
        return(MixedNum(lowest, unConverted))

    def convert(self, mixedNum, *measures):

        measureSet = set()
        for measure in measures:
            set_ = self.get_measureSet(measure)
            if set_ != None:
                measureSet = measureSet.union(set_)

        lowest = self.convert_to_lowest(mixedNum, measureSet) #(lowest, unConverted)

        outList = []
        for elem in lowest.list:
            measuresEOF = len(measures) - 1
            lowestNum = Frac(**elem.rational.dict())
            found = False
            for idx in range(measuresEOF + 1):
                measure = measures[idx]
                if measure == elem.name:
                    divider = Frac(1)
                    found = True
                else:
                    rate = (elem.name, measure)
                    if not rate in self.__rates.keys():
                        continue #raise ValueError('incorrect measures')
                    divider = Frac(
                            numerator = self.__rates[rate]['multiplicity']
                            ,denominator = self.__rates[rate]['rate']
                        )
                    found = True
                frac = lowestNum.div(divider)
                if idx < measuresEOF:
                    intFrac = Frac(frac.mixed().intPart)
                    outList.append(Elem(intFrac, measure))
                    lowestNum = lowestNum.sub(intFrac.mul(divider))
                else:
                    outList.append(Elem(frac, measure))
            if not found:
                outList.append(Elem(elem.rational, elem.name + '_unc'))
        return(MixedNum(outList))
        
        #OLD
        #lowestNum = Frac() # representing lowest measure
        #unConverted = []
        #for elem in mixedNum.list:
        #    if elem.name == self.__lowest:
        #        lowestNum = lowestNum.add(
        #            elem.rational
        #        ).reduce()
        #        continue

        #    rate = (elem.name, self.__lowest)
        #    if rate in self.__rates.keys():
        #        lowestNum = lowestNum.add(
        #            elem.rational.mul(
        #                Frac(
        #                    numerator = self.__rates[rate]['rate']
        #                    ,denominator = self.__rates[rate]['multiplicity']
        #                )
        #            )
        #        ).reduce()
        #    else:
        #        unConverted.append(elem)

        #outList = []
        #idxLast = len(measures) - 1
        #for idx in range(idxLast + 1):
        #    measure = measures[idx]
        #    if measure == self.__lowest:
        #        divider = Frac(1)
        #    else:
        #        rate = (self.__lowest, measure)
        #        if not rate in self.__rates.keys():
        #            raise ValueError('incorrect measures')
        #        divider = Frac(
        #                numerator = self.__rates[rate]['multiplicity']
        #                ,denominator = self.__rates[rate]['rate']
        #            )
        #    frac = lowestNum.div(divider)
        #    if idx < idxLast:
        #        intFrac = Frac(frac.mixed().intPart)
        #        outList.append(Elem(intFrac, measure))
        #        lowestNum = lowestNum.sub(intFrac.mul(divider))
        #    else:
        #        outList.append(Elem(frac, measure))

        #return(MixedNum(outList, unConverted))