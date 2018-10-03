# -*- coding: utf-8 -*-

import datetime
import math

class Utils():
    """The utils of the application."""

    def timeDifSeconds(self, start, end):
        """Start and end are datetime instances."""
        diff = end - start
        millis = diff.days * 24 * 60 * 60
        millis += diff.seconds
        millis += diff.microseconds / 1000000
        return millis

    def functionForLabel(self, function):
        """Return function with label."""
        if (function == '~'):
            return self.noFunction
        elif (function == 'f(t) = a'):
            return self.constantFunction
        elif (function == 'f(t) = a * t + b'):
            return self.linearFunction
        elif (function == 'f(t) = rect((t - b) / a)'):
            return self.rectFunction
        elif (function == 'f(t) = tri((t - b) / a)'):
            return self.triFunction
        elif (function == 'f(t) = b * (exp(- a * t) - 1)'):
            return self.expFunction
        elif (function == 'f(t) = sin((2pi * t)/a + b)'):
            return self.sinFunction
        else:
            return self.noFunction


    def noFunction(self, p, time):
        """Return always 'None'."""
        return None

    def constantFunction(self, p, time):
        """Return a constant value."""
        return p['a']

    def linearFunction(self, p, time):
        """Return a linear function with bounds."""
        delta = self.timeDifSeconds(time, datetime.datetime.now())
        ft = p['a'] * delta + p['b']
        while (ft > p['upper']):
            ft -= p['upper'] - p['lower']
        while (ft < p['lower']):
            ft += -p['lower'] + p['upper']
        return ft

    def rectFunction(self, p, time):
        """Return a rect function."""
        delta = self.timeDifSeconds(time, datetime.datetime.now())
        deltaCalc = 1
        if (p['a'] != 0):
            deltaCalc = (delta - p['b']) / p['a']
        fr = math.floor((deltaCalc + p['a'] / 2) % 2)

        ft = p['lower']
        if (fr == 0):
            ft = p['upper']
        return ft

    def triFunction(self, p, time):
        """Return a tri function."""
        delta = self.timeDifSeconds(time, datetime.datetime.now())
        deltaCalc = 1
        if (p['a'] != 0):
            deltaCalc = (delta - p['b']) / (p['a'] / 2)
        fr = math.floor(deltaCalc % 2)

        ft = 0
        if (p['a'] != 0):
            ft = - math.floor(deltaCalc) + deltaCalc
            if (fr == 1):
                ft = math.floor(deltaCalc) + 1 - deltaCalc

        ft = p['lower'] + ft * (p['upper'] - p['lower'])
        return ft

    def expFunction(self, p, time):
        """Return an exp function."""
        delta = self.timeDifSeconds(time, datetime.datetime.now())
        ft = p['lower'] - p['b'] * math.expm1(-p['a'] * delta) * (p['upper'] - p['lower'])
        if (p['b'] < 0):
            ft = p['upper'] - p['b'] * math.expm1(-p['a'] * delta) * (p['upper'] - p['lower'])
        return ft

    def sinFunction(self, p, time):
        """Return an sin function."""
        delta = self.timeDifSeconds(time, datetime.datetime.now())
        ft = (p['upper'] - p['lower']) / 2
        if (p['a'] != 0):
            ft = (p['upper'] - p['lower']) / 2 + math.sin(2 * math.pi  * delta / p['a'] + p['b']) * (p['upper'] - p['lower']) / 2
        return ft
