import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO
import time

GPIO.setup("P9_14", GPIO.OUT)
print(Adafruit_BBIO)

while True:
    GPIO.output("P9_14", GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output("P9_14", GPIO.LOW)
    time.sleep(0.5)
