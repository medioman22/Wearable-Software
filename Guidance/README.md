# Cloning Firmware from a working BBGW

The working debian 8.10 flasher is no longer avaialble in BeagleBone image database. For making sure the systems are flashed with the right image, it is required to clone the working image from the BBGW. 

## Solution

The solution is pretty straightforward. Steps are explained below:

1. Make Sure the device is off.
2. Remove micro-sd.
3. Boot the Board.
4. When booted completely, insert the micro-sd.
5. Then enter the following command on the dash: sudo /opt/scripts/tools/eMMC/beaglebone-black-make-microSD-flasher-from-eMMC.sh
6. When the LEDs stop and the script terminates, remove the SD card.
7. Then use the micro-sd as image and follow the procedure for flashing the new devices.

## Source

The procedure is obtained from the following link:

https://stackoverflow.com/questions/17834561/duplicating-identical-beaglebone-black-setups

In the case of failure with solution provided here, you can follow other instructions provided in the link above.



