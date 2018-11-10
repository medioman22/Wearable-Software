import keyboard     #Using module keyboard
import time
import threading
from threading import Thread
t_init = time.time()

def measure_time():
    t_init = time.time()
   
    while True:         #making a loop
        try:            #used try so that if user pressed other than the given key error will not be shown
            if keyboard.is_pressed('a'): #if key 'a' is pressed
                t_fin = time.time()
                print(t_fin-t_init)
                break   #finishing the loop
            else:
                pass
        except:
            break
       
    return t_fin - t_init

def func1():
    time.sleep(1)
    print (time.time()-t_init)
    

def func2():
    time.sleep(1)
    print (time.time()-t_init)

#measure_time()
Thread(target = func1).start()
Thread(target = func2).start()