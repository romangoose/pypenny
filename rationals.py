# Any copyright is dedicated to the Public Domain.
# https://creativecommons.org/publicdomain/zero/1.0/
# ===================== OR =========================
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Версия 2023-01-23

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

    def __str__(self):
        return(str(self.dict()))

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
        """fraction with integer part extracted"""
        return Rational(
            self.numerator  // self.denominator + self.intPart # intPart
            ,self.numerator %  self.denominator                # numerator
            ,self.denominator                                  # denominator
            ,self.isNegative                                   # isNegative
        )

    def simple(self):
        """proper notation of the fraction (without integer part)"""
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
        """reverses the sign of a fraction"""
        return Rational(
            self.intPart         # intPart
            ,self.numerator      # numerator
            ,self.denominator    # denominator
            ,not self.isNegative # isNegative
        )

    def abs(self):
        """absolute value"""
        return Rational(
            self.intPart         # intPart
            ,self.numerator      # numerator
            ,self.denominator    # denominator
            ,False                # isNegative
        )

    def add(self, other):
        """addition"""
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
        """substract"""
        return self.add(other.opposite())


    def intComp(self, other):
        """comparison result as a number -1/0/1 (is self less than, equal to, greater than other)"""
        if self.isNegative != other.isNegative:
            # if signs are not equal, 
            # operands are not equal too,
            # and self is lesser if negative
            return -1 if self.isNegative else 1

        if self.denominator == other.denominator:
            num = (
                      (self.intPart  * self.denominator  + self.numerator)
                    - (other.intPart * other.denominator + other.numerator)
            )
            if num == 0: return 0
            return self.intSign() if num > 0 else -self.intSign()
        else:
            frac = self.sub(other)
            if frac.isZero(): return 0
            return frac.intSign()

    def reciprocal(self):
        """1/self"""
        if self.isZero():
            raise ZeroDivisionError('Reciprocal causes division by zero')

        return Rational(
            0                                                 # intPart
            ,self.denominator                                 # numerator
            ,self.intPart * self.denominator + self.numerator # denominator
            ,self.isNegative                                  # isNegative
        )

    def mul(self, other):
        """multiplication"""
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
        """division"""
        if other.isZero():
            raise ZeroDivisionError('Division by zero')
        return self.mul(other.reciprocal())


    @staticmethod
    def gcd(a: int, b: int) -> int:
        """greatest common divisor"""
        a, b = abs(a), abs(b)
        if min(a,b) == 0:
            return max(a,b,1)

        while b > 0:
            a,b = b, a%b

        return a

    @staticmethod
    def lcm(a: int, b: int) -> int:
        """less common multiplier"""
        a, b = abs(a), abs(b)
        return (a//Rational.gcd(a,b))*b
