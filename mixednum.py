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

    @staticmethod
    def name_in_list(name, list):
        found = False
        for idx in range(len(list)):
            if list[idx].name == name:
                return idx
        return None

class MixedNum:

    def __init__(self, *inLists):
        self.__list = []
        for inList in inLists:
            for item in inList:
                idx = Elem.name_in_list(item.name, self.__list)
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
        lowestSelf  = converter.convert(self, converter.lowest)
        lowestOther = converter.convert(other, converter.lowest)
        if (len(lowestSelf.list) != 1) or (len(lowestOther.list) != 1):
            raise ValueError('incompatible measures')
        return(lowestSelf.list[0].rational.div(lowestOther.list[0].rational))

class Converter:
    
    __rates    = {}
    __measures = []
    __lowest     = ''
    __lowestMul  = 0
    __lowestRate = 0
    __ranged = []
    __isRanged = False

    @property
    def rates(self):
        return(self.__rates)

    @property
    def measures(self):
        return(self.__measures)

    @property
    def lowest(self):
        return(self.__lowest)

    @property
    def ranged(self):
        return(self.__ranged)

    def add_rate(self, source, target, multiplicity, rate):


        #inner functions
        def add_cross_rate(base, cross):

            if not base in self.__measures:
                self.__measures.append(base)
            
            for found in self.__measures:
                if found == cross:
                    continue

                if (found,cross) in self.__rates:
                    continue

                rateBase  = self.__rates[(base, cross)]
                rateFound = self.__rates[(base, found)]

                multiplicity = rateFound['rate']         * rateBase['multiplicity']
                rate         = rateFound['multiplicity'] * rateBase['rate']
                gcd_ = Frac.gcd(multiplicity, rate)
                add_record(
                    found,cross
                        ,multiplicity // gcd_
                        ,rate         // gcd_
                    )

            if not cross in self.__measures:
                self.__measures.append(cross)


        def add_record(source, target, multiplicity, rate):

            self.__rates[(source, target)] = {
                                                'multiplicity': multiplicity
                                                ,'rate':        rate
                                            }

            add_cross_rate(source, target)

            if (
                self.__lowest == ''
                or (
                        self.__lowestMul      <= multiplicity
                        and self.__lowestRate >= rate
                    )
                ):
                    self.__lowest     = source
                    self.__lowestMul  = multiplicity
                    self.__lowestRate = rate

            frac = Frac(0,rate, multiplicity)
            idx = Elem.name_in_list(source, self.__ranged)
            if idx == None:
                self.__ranged.append(Elem(frac, source))
            else:
                if (self.__ranged[idx].rational.sub(frac).intSign() > 0):
                    self.__ranged[idx] = Elem(frac, source)

            #inverted
            if not (target, source) in self.__rates:
                add_record(target, source, rate, multiplicity)
            
            self.__isRanged = False
            return True

        #main body
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

        return (add_record(source, target, multiplicity, rate))

    def convert(self, mixedNum, *measures):

        if not self.__isRanged:
            done = False
            while not done:
                done = True
                for idx in range(1,len(self.__ranged)):
                    if (self.__ranged[idx].rational.sub(self.__ranged[idx-1].rational).intSign() < 0):
                        self.__ranged[idx], self.__ranged[idx-1] = self.__ranged[idx-1], self.__ranged[idx]
                        done = False
            self.__isRanged = True

        lowestNum = Frac() # representing lowest measure
        unConverted = []
        for elem in mixedNum.list:
            if elem.name == self.__lowest:
                lowestNum = lowestNum.add(
                    elem.rational
                ).reduce()
                continue

            rate = (elem.name, self.__lowest)
            if rate in self.__rates.keys():
                lowestNum = lowestNum.add(
                    elem.rational.mul(
                        Frac(
                            numerator = self.__rates[rate]['rate']
                            ,denominator = self.__rates[rate]['multiplicity']
                        )
                    )
                ).reduce()
            else:
                unConverted.append(elem)

        outList = []
        idxLast = len(measures) - 1
        for idx in range(idxLast + 1):
            measure = measures[idx]
            if measure == self.__lowest:
                divider = Frac(1)
            else:
                rate = (self.__lowest, measure)
                if not rate in self.__rates.keys():
                    raise ValueError('incorrect measures')
                divider = Frac(
                        numerator = self.__rates[rate]['multiplicity']
                        ,denominator = self.__rates[rate]['rate']
                    )
            frac = lowestNum.div(divider)
            if idx < idxLast:
                intFrac = Frac(frac.mixed().intPart)
                outList.append(Elem(intFrac, measure))
                lowestNum = lowestNum.sub(intFrac.mul(divider))
            else:
                outList.append(Elem(frac, measure))

        return(MixedNum(outList, unConverted))