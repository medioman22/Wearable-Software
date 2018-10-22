# SoftWEAR firmware

This firmware is supposed to be runing on a BeagleBone Green wireless. Its perpose is to help you to connect and see sensors connected to the board through a simple interface for now.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

For the firmeware to run you will need:
* Beaglebone Green wireless
* PC or Mac with Python 3 installed
* USB micro to A cable
* Micro SD card with a way to write it on the PC
* Sensors that you want to have on the board

### Installing and setup of the BBGW

Download and falsh the "debian 8.10" image from the [Beaglebone image repo](https://beagleboard.org/latest-images). To flash it onto the board.

We the flash is done, plug your beaglebone to a PC with the power USB cable and access it with SSH 
```
ssh debian@192.168.7.2
```

Connect the board to a accessible network (with only a password and not a username/password combo. E.g. a wifi hotsport on you smartphone) by following the "ConnectWifi.pdf" guide in "Manual"

Then make sure to do an update
```
sudo apt-get update
```

You will now need to clone this repository into your beaglebone in order to install everything.
```
git clone https://github.com/medioman22/Wearable-Software.git
```

#### Installing all the packages in you BBGW from the repo

In order for the code on the beaglebone to run properly. It will need to have some packages installed.
To do so you can use the provided script in the repository that you just download.
To run it use

```
install_package.sh  (not yet implemented in the repo)
```

#### Installing all the packages in you BBGW manually

Or you can manually install the packages

List of packages used
* [Adafruit_Python_GPIO](https://github.com/adafruit/Adafruit_Python_GPIO)
* [Serial](https://pypi.org/project/serial/)

To install the [Adafruit_Python_GPIO](https://github.com/adafruit/Adafruit_Python_GPIO) one, click on the name to follow the instruction in ther github page.
To install the other package, use

```
sudo pip install serial
```

You will also need to have the `Firmware/src` folrder of the firmware to by copied to you beaglebone. 
In order to do so you can clone the repository as explain before or use a FTP connection.[Filezilla](https://filezilla-project.org/) could be usefull.
To connect with a FTP client, use the SSH port `192.168.7.2` the username `debian` the password `temppwd` (if not changed from the default beaglebone image one) and port `22`.

### Installing and setup of the PC

On the PC, you will need to have Python 3.5 or above installed as well as some pakages

```
pip install pyqt5
pip install pyqtgraph
```


## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Known issue

* The BNO055 sensor is not able to run on the `NDOF` mode from the interface. To do so you need to change the initial mode of initialization of the sensor in the `Firmware/src/drivers/I2C_BNO055.py` from `0` to `11` in the init function.
