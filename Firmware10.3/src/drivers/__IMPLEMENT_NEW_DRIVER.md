# Implement new driver for a Device

## Analog In, Digital In/Out and PWM Out Devices

Those devices have default drivers implements which usually do not need to changed. But one can always have a look at them to implement special behaviour.

## I2C Devices

There are already a few I2C devices implemented and a template file is provided.

* Open the `Firmware/src/drivers/__I2C_DRIVER_TEMPLATE.py` and fill in the necessary functionality marked with
```
<…>
```
or
```
###########################
# …
# …
###########################
```
* Import and register the new driver in the `/Firmware/src/I2CModule.py` module. The file has a list called `DRIVERS` which holds all registered drivers.

* Register the used addresses in the `/Firmware/src/Config.py` module. Add the used addresses to the `ADDRESS` list.

* Restart the Firmware

## SPI Devices

* Not yet implemented

## UART Devices

* Not yet implemented

## MUX Drivers

* There are MUX drivers which generally should not get changed. But you can have a look at those files if you need to extend them.

* Just keep in mind that there exists 2 different MUX types:
 1. Basic MUX which handles **1** channel
 2. I2C MUX which handles an **SCL/SDA** channel pair configured via I2C
