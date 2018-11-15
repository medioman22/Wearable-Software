# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 17:17:04 2018

@author: Hugo
"""

import csv

my_list = ['N', 'N', 'N', 'N', 'S']
second_list = ['S', 1, 'NS','S','N']




sub = 'shat'
  
 
with open('C:\\Users\\Hugo\\Documents\\GitHub\\Wearable-Software\\Haptic_control\\logs\\' + sub + '_intens_feedback.csv', 'w') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar= '|', quoting=csv.QUOTE_MINIMAL)
    filewriter.writerow(['Given Direction', 'Real Direction'])
    for i in range(0,len(my_list)):
        filewriter.writerow([my_list[i], second_list[i]])
   