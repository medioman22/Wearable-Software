# -*- coding: utf-8 -*-
# Author: Cyrill Lippuner
# Date: October 2018

# Standard color set for plots
standardColorSet = [
    (0,     200,    0),
    (200,   0,      0),
    (0,     0,      200),
    (200,   200,    100),
    (200,   0,      100),
    (200,   100,    0),
    (0,     200,    100),
    (100,   0,      100),
    (200,   100,    200),
    (100,   100,    0),
    (100,   100,    200),
    (50,    50,     200),
    (50,    0,       200),
    (50,    150,    0),
    (100,   150,    50),
    (100,   50,     0),
    (50,    150,    50),
    (150,   0,      150),
    (200,   200,    200)
]

class Utils():
    """The utils of the application."""

    def timeDifSeconds(self, start, end):
        """Start and end are datetime instances."""
        diff = end - start
        millis = diff.days * 24 * 60 * 60
        millis += diff.seconds
        millis += diff.microseconds / 1000000
        return millis
