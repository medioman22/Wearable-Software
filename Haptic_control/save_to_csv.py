# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 17:17:04 2018

@author: Hugo
"""

import numpy as np

my_list = [3, 4, 5, 2, 1]

arr = np.array(my_list)

sub = 'matteo'

np.savetxt(sub + '_intens_feedback.csv', arr, delimiter = ',')