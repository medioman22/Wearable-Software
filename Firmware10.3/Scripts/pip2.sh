#!/bin/bash

apt-get update
apt-get install build-essential python-pip python-dev python-smbus git
git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
cd Adafruit_Python_GPIO
python setup.py install
pip install -r Wearable-Software/Firmware/src/requirements.txt

