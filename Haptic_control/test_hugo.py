import keyboard     #Using module keyboard
import time
import threading
from threading import Thread
t_init = time.time()


def measure_time():
    t_init = time.time()
    was_pressed = False
    while True:         #making a loop
        try:            #used try so that if user pressed other than the given key error will not be shown
            key_pressed = check_key_pressed()
            if key_pressed : #if direction key is pressed
                if not was_pressed :
                    t_fin = time.time()
                    print('Direction : ', key_pressed, ', Reaction time :', t_fin-t_init)
                    was_pressed = True
                pass   #finishing the loop
            else:
                was_pressed = False
                pass
        except:
            break
        
def check_key_pressed():
    direction_dict = {'q' : 'NW',
           'w' : 'N', 'e': 'NE', 'a': 'W', 'd': 'E', 'y': 'SW', 'x': 'S', 'c': 'SE','space': 'Space','1':1}
    for key in direction_dict.keys():
        if keyboard.is_pressed(key) :
            return direction_dict[key]
            break
        else : pass
    return None


def func1():
    while True:    
        time.sleep(1)
        print (time.time()-t_init)
    

def func2(a=32):
    time.sleep(1)
    print(' ', a)
    print (time.time()-t_init)

measure_time()
Thread(target = func1).start()

Thread(target = measure_time).start()
    