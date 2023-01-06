# Версия 2022-12-17
# Лицензия CC0 https://creativecommons.org/publicdomain/zero/1.0/deed.ru
import numbers
import operator


"""Rational numbers (fractions)"""

class Rational:

    """Rational number as [intPart]+fraction(numerator/denominator),[-]"""

    def __init__(self, intPart: int = 0, numerator: int = 0, denominator: int = 1, isNegative: bool = False):
        def isCorrect(intPart, numerator, denominator,isNegative):
            return (
                type(intPart)         is int
                and type(numerator)   is int
                and type(denominator) is int
                and type(isNegative)  is bool
                and (intPart     >= 0)
                and (numerator   >= 0)
                and (denominator >= 1)
            )

        if isCorrect(intPart, numerator, denominator,isNegative):
            self.__intPart     = intPart
            self.__numerator   = numerator
            self.__denominator = denominator
            self.__isNegative  = isNegative
        else:
            raise ValueError("incorrect part(s) of rational")


    @property
    def intPart(self):
        return(self.__intPart)

    @property
    def numerator(self):
        return(self.__numerator)

    @property
    def denominator(self):
        return(self.__denominator)

    @property
    def isNegative(self):
        return(self.__isNegative)

    def tuple(self):
        return (self.intPart, self.numerator, self.denominator, self.isNegative)

    def dict(self):
        return {
                'intPart'      : self.intPart
                ,'numerator'   : self.numerator
                ,'denominator' : self.denominator
                ,'isNegative'  : self.isNegative
                }

    def intSign(self) -> int:
        """sign as +/-1 (for evaluation)"""
        return -1 if self.isNegative else 1

    def isZero(self) -> bool:
        return (self.intPart == 0 and self.numerator == 0)

    def decimal(self) -> float:
        """float (approximate) value for further (human) math"""
        return (self.intPart + self.numerator/self.denominator)*self.intSign()


    def mixed(self):
        return Rational(
            self.numerator  // self.denominator + self.intPart # intPart
            ,self.numerator %  self.denominator                # numerator
            ,self.denominator                                  # denominator
            ,self.isNegative                                   # isNegative
        )

    def simple(self):
        return Rational(
            0                                                 # intPart
            ,self.intPart * self.denominator + self.numerator # numerator
            ,self.denominator                                 # denominator
            ,self.isNegative                                  # isNegative
        )
   
    def reduce(self):
        if self.numerator == 0:
            # simlest case: set denominator to 1
            return Rational(self.intPart,0,1,self.isNegative) 

        gcd_ = Rational.gcd(self.numerator, self.denominator)
        return Rational(
                self.intPart               # intPart
                ,self.numerator   // gcd_  # numerator
                ,self.denominator // gcd_  # denominator
                ,self.isNegative           # isNegative
        )


    def opposite(self):
        return Rational(
            self.intPart         # intPart
            ,self.numerator      # numerator
            ,self.denominator    # denominator
            ,not self.isNegative # isNegative
        )

    def add(self, other):
        lcm_ =  Rational.lcm(self.denominator,other.denominator)

        num = (
             (  self.intPart    * lcm_
              + self.numerator  * lcm_ // self.denominator)  * self.intSign()
           + (  other.intPart   * lcm_
              + other.numerator * lcm_ // other.denominator) * other.intSign()
        )

        return Rational(
            0           # intPart
            ,abs(num)   # numerator
            ,lcm_       # denominator
            ,(num < 0)  # isNegative
        )

    def sub(self, other):
        return self.add(other.opposite())


    def reciprocal(self):
        if self.isZero():
            raise ZeroDivisionError('Reciprocal causes division by zero')

        return Rational(
            0                                                 # intPart
            ,self.denominator                                 # numerator
            ,self.intPart * self.denominator + self.numerator # denominator
            ,self.isNegative                                  # isNegative
        )

    def mul(self, other):
        return Rational(
            0                                                           # intPart
            ,(
                  (self.intPart  * self.denominator  + self.numerator)
                * (other.intPart * other.denominator + other.numerator) 
            )                                                           # numerator
            ,self.denominator * other.denominator                       # denominator
            ,(self.isNegative ^ other.isNegative)                       # isNegative
        )

    def div(self, other):
        if other.isZero():
            raise ZeroDivisionError('Division by zero')
        return self.mul(other.reciprocal())


    #greatest common divisor
    @staticmethod
    def gcd(a: int, b: int) -> int:
        a, b = abs(a), abs(b)
        if min(a,b) == 0:
            return max(a,b,1)

        while b > 0:
            a,b = b, a%b

        return a

    #less common multiplier
    @staticmethod
    def lcm(a: int, b: int) -> int:
        a, b = abs(a), abs(b)
        return (a//Rational.gcd(a,b))*b
