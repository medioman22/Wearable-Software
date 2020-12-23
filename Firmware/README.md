# Firmware

The Firmware is written to run on a BeagleBone Green wireless. Its purpose is to help you to connect and interface sensors connected to the board. The following guidlines are written on the work done by Cyrill Lippuner. The firmware version is updated to Debian 10.3 and code is prepared for python3. 

*Network Configuration*
```
IP: 192.168.7.2 Cable
IP: 192.168.8.1 Wifi
Port: 12345
```

## Getting Started

These instructions will help you installing the Firmware on the BBGW. See deployment for notes on how to deploy the Firmware on a live system.

### Prerequisites

For the Firmware to run you will need:
* Beaglebone Green Wireless
* USB micro to A cable
* Micro SD card and a tool to flash it with a bootable image
* Basic Wifi Network for the BBGW
* Sensors that you want to have on the board

### Setup of the BBGW Firmware

#### Installing the drivers

##### *OSX*

* Connect BBG via USB cable - wait for reboot
* Volume should show up in finder (Do not use README.htm and START.htm as they are outdated. Look for online version)
**CAREFUL**: Drivers provided by the board itself are outdated. Go to the webpage itself to download most recent drivers or use tested drivers from the rep with following configuration.
* Go to [Online README](http://beagleboard.org/static/beaglebone/latest/README.htm) where you should see a list of the most recent drivers.
In folder `/Firmware/Drivers` is a set of drivers used in *summer 2018*.
* (TESTED: MacOSX High Sierra: Go to `/Firmware/Drivers/MacOSX/` and install all drivers)

When drivers are installed, you should see the board in `settings > network` to show up

##### *Windows*

* Connect BBG via USB cable - wait for reboot
* Volume should show up in explorer or prompt
(Do not use README.htm and START.htm as they are outdated. Look for online version)
**CAREFUL**: Drivers provided by the board itself are outdated. Go to the webpage itself to download most recent drivers or use tested drivers from the rep with following configuration.
*(Install the one for your operating system. Note that on Windows it may fail due to lack of signature. Search the web how to disable signature requirement for Windows.)*
* Go to http://beagleboard.org/static/beaglebone/latest/README.htm You should see a list of the most recent drivers.
In folder `/Firmware/Drivers` is a set of drivers used in *summer 2018*.

#### Flashing the Image

Download the "debian 10.3" image from the [Beaglebone image repo](https://beagleboard.org/latest-images) and flash it onto the board.

* Follow instructions `/Firmware/Manuals/LoadImage.pdf` to burn the correct image on the SD card.
[BBGW Getting Started](http://beagleboard.org/getting-started#step1)
* Flashing eMMC can take up to *~15min*

**(Come back here when you are able to login)** To set up the standalone microSD image to automatically flash the eMMC on powerup. Login and edit `/boot/uEnv.txt` with nano `sudo nano /boot/uEnv.txt`, vim or your preferred console editor.

In `/boot/uEnv.txt`:
```
##enable BBB: eMMC Flasher:
#cmdline=init=/opt/scripts/tools/eMMC/init-eMMC-flasher-v3.sh
Change to:

##enable BBB: eMMC Flasher:
cmdline=init=/opt/scripts/tools/eMMC/init-eMMC-flasher-v3.sh
Optional, update Flasher Scripts:
```

Type:
```
cd /opt/scripts/
git pull
```

and reboot the system, it'll flash the eMMC on the next bootup. (make sure to remove the microSD after flashing is complete, otherwise it'll just keep on re-flashing the eMMC)
[BBGW Getting Started](http://elinux.org/Beagleboard:BeagleBoneBlack_Debian#Flashing_eMMC)

#### Imaging on SD card

It is also possible to burn the image on the SD card. For every firmware, there is two options, one is refered with SD and the other with Flash as shown bellow:

Flash Version name:
```
AM3358 Debian 10.3 2020-04-06 4GB eMMC IoT Flasher
```

SD Version name:
```
AM3358 Debian 10.3 2020-04-06 4GB SD IoT
```

It is enough to burn the image to SD card and attach it to the board and turn it on.


#### Connecting to the BBGW

We the flash is done, plug your BBGW to a PC with the power USB cable and access it with SSH:
```
ssh debian@192.168.7.2
```
*(Use Terminal on OSX or PuTTY on Windows)*

Once connected, you should be asked to enter a password:
```
> Debian GNU/Linux 10

> BeagleBoard.org Debian Buster IoT Image 2020-04-06

> Support: http://elinux.org/Beagleboard:BeagleBoneBlack_Debian

> default username:password is [debian:temppwd]

> debian@192.168.7.2's password:
```
Type `temppwd` to continue.
You should get a welcome message like this:
```
> The programs included with the Debian GNU/Linux system are free software;
> the exact distribution terms for each program are described in the individual files in /usr/share/doc/*/copyright.

> Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent permitted by applicable law.
```

#### First things first

Make sure to do an update:
```
sudo apt-get update
```
*(In case you are asked for a root password: `temppwd`)*

#### Connecting the BBGW to the Wifi Network

Connect the board to an accessible wifi network (with a simple password. E.g. a wifi hotspot on you smartphone) by following the `Firmware/Manuals/ConnectWifi.pdf` guide:

Check the internet connection with:
```
ping epfl.ch
```

*(Should you ran into the problem that your pings are blocked, follow the `Firmware/Manuals/ICMPEchoIssues.pdf` guide to solve that problem.)*

#### Get the repo from github

You will now need to clone this repository into your home folder in order to proceed.
```
cd ~
git clone https://github.com/medioman22/Wearable-Software.git
```

Switch to a branch if necessary:
```
cd Wearable-Software
git checkout <branch>
```

*Alternatively*:
You can also clone the github repo on your machine and use a FTP connection. [Filezilla](https://filezilla-project.org/) could be useful.
To connect with a FTP client, use the SSH port `192.168.7.2` the username `debian` the password `temppwd` (if not changed from the default beaglebone image) and port `22`.

#### Installing all the packages in you BBGW from the repo

In order for the firmware to run on the beaglebone you will need to have some packages installed.
To do so you can use the provided script in the repository that you just download.
Run following commands:
```
cd ~
sudo bash ~/Wearable-Software/Firmware/Scripts/Install_PythonPackages.sh
```

#### Alternatively: Installing all the packages in you BBGW manually

Or you can manually install the packages:

List of packages used
* Python Packages (listed in the Wearable-Software/Firmware/src/requirements.txt)
```
sudo pip3 install -r requirements.txt
```
* [Adafruit_Python_GPIO](https://github.com/adafruit/Adafruit_Python_GPIO)
To install the Adafruit_Python_GPIO, follow the instruction on the README.


### Launch the Firmware

To launch the Firmware from the console, type:
```
cd ~
sudo python3 Wearable-Software/Firmware/src/Main.py [ldmepf]
```

*Options:*

| Flag | Description  |        
|:-----|:-------------|
| l    | Provide a live console output of the current state of the Firmware |
| d    | Log the diagnosis of the different device drivers |
| m    | Log the data exchange of the Firmware on the TCP/IP socket |
| e    | Log the event exchange of the Firmware on the TCP/IP socket |
| p    | Log the system profiling for the Firmware (can be printed with `Wearable-Software/Firmware/src/_PrintStats.py`) |
| f    | Use the local embedded loop file |

*Those flags can be combined, but may have a negative impact on the performance*

#### Stop the Firmware

In order to stop the Firmware you need to break manually with `Ctrl-C`.

#### Start up launch

The Firmware can be configured to launch at start up with following command:
```
sudo bash Wearable-Software/Firmware/Scripts/EnableAutoLaunch.sh [ldmepf]
```

And to disable it:

```
sudo bash Wearable-Software/Firmware/Scripts/DisableAutoLaunch.sh
```

## API

More information about the api connection protocol can be found in the `API.md`.

## Documentation

More information about the Firmware code and the functionality can be found in the `DOCS.md`.

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

[This system is not yet deployable and only used to prototype!]

## Known Issues

* The BNO055 sensor is not able to run on the `NDOF` mode from the interface. To do so you need to change the initial mode of initialization of the sensor in the `Firmware/src/drivers/I2C_BNO055.py` from `0` to `11` in the init function.
