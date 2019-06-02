# Firmware API

## Disclaimer

If you haven't read the README, please read it before coming back here. To use the **API**, your must have a running Firmware and be able to established TCP/IP connection to a computer.

## Prerequisites

For the Firmware API to interface you will need:
* Beaglebone Green Wireless with running Firmware
* Network for BBGW and PC
* A framework on the computer to create a TCP/IP socket

## Intro

The API to the Firmware allows to receive data from connected sensors, set values for devices and configure the behavior. It is based on simple *JSON* messages which are serialized and sent to a TCP/IP socket. Each message is standalone and the whole process is state-less.

## TL;DR

As a quick overview to start there are three important messages to exchange.

To get the currently connected devices, send following message to the board:
```
>> {"type": "DeviceList"}
```

You will get a bunch of register messages for devices like:
```
<< {"type": "Register",
"name": "<device name>",
"dir": "in|out",
"dim": float<dimensions>,
"about": {<About the device>},
"settings": {<Settings available for the device>},
"mode": "<device mode>",
"flags": "<device flags>",
"frequency": "<device read frequency>",
"dutyFrequency": "<device duty frequency>"}
```

Finally, data messages are sent:
```
>> {"type": "D", "values": [float<timestamp>, [float<data vector>]]}
```
*Careful: Data messages are sent all the time even before a 'DeviceList' request*

## Messages

### >> Receive Message

| Type | Parameters | Description  |        
|:-----|:-----------|:-------------|
| Register | **name** Device name<br>**dir** Data flow direction<br>**dim** Data vector dimension<br>**about** Object with device information<br>**settings** Object providing available settings allowed for device (*null* means *not available*)<br>**mode** Currently active mode or *null*<br>**flags** Currently raised flags or *null*<br>**frequency** Current data read frequency<br>**dutyFrequency** Current duty frequency or *null* | A register message is sent when a new device is detected or requested by a `DeviceList` request message. It provides an identifier and meta information needed to interface the device. |
| Deregister | **name** Device name | A deregister message is sent when a connected devices gets disconnected. |
| D |  **data** List of new data for devices<br>*Data is an object with following parameters:*<br>***name*** Device name<br>***values*** Values since last data message<br>***cycle*** Cycle duration to read the data<br>Format: *[(timestamp, data vector, cycle)]* where timestamp is a float, data vector a list of floats with length *dim* and cycle a float for the duration | A data message is sent every update cycle of the board containing the data read since the last message. In may be *empty* if read frequency is slower than the update cycle of the board. |
| CycleDuration |  **name** Device name<br>**values** Cycle durations for *update* and *scan*<br>Format: Object with fields *update* and *scan* | A cycle message is sent for every update cycle providing the computation time required for the cycles. |
| Ping | - | Pings back when a `Ping` request message is sent |

### << Send Message

| Type | Parameters | Description  |        
|:-----|:-----------|:-------------|
| DeviceList | - | Request a complete list of registered devices. A `Register` message will be sent for each device connected. |
| Set | **name** Device name<br>**dim** Dimension of data vector to set<br>**value** Value to set<br> | Set a *single* value in a data vector for a device. |
| Settings |  **name** Device name<br>**mode** (Optional) New mode for device<br>**frequency** (Optional) New read frequency for device<br>**dutyFrequency** (Optional) New duty frequency for device<br>**flag** (Optional) Flag to raise/clear<br>**value** (Optional) Used for *flag* to raise/clear a flag with *True/False* | Settings message to change device settings provided by the register message. Make sure to only set a specific setting if it is marked as **available** by the register message and use only the values provided in the list. |
| Scan | **value** Bool to enable/disable the scanning | Disabling the scanning can be more performant but it will fail if changes are made on the hardware. |
| Ping | - | Ping the board to get a ping back. |

### Protocol

#### Setup

1. To setup the connection, first create a socket listening to the correct IP and Port.
(You will get `D` and `CycleDuration` messages constantly but you need to ignore them until the setup is finished.)

2. The first message to send is a `DeviceList` message. You will get a bunch of `Register` messages for each connected device with all information and its name. Every future message uses the *name* to identify a device.

#### Runtime

1. During runtime you will constantly getting messages:
  * `D` message with new values for devices
  * `CycleDuration` with the computation time for the last cycles
  * `Register` / `Deregister` messages when new devices are detected or existing devices are disconnected


2. You can send a `Set` message anytime to change a value for a device

3. You can change a setting anytime by sending a `Settings` message with appropriate fields

4. Use the `Ping` message to check the connection and measure connection time

### Example

Look at the example provided in `/Firmware/Example` which uses the **API** to display the incoming messages.


### Embedded Loop

In folder `/src/embedded` is a file `loop.py`, which implements onboard functionality that can be replaced or enhanced. It uses the same api but with a lot less delay due to no need of message transmission between the Firmware and the PC. One can use the script `LoadEmbeddedScript.sh` to copy a `loop.py` file from the PC to the BBGW.

```
bash ./LoadEmbeddedScript.sh "path/to/file" 192.168.7.2
```

The IP is same as used for the login via ssh.

There is also an example in `/Examples` folder using the `api.py` file. This example file can be used as a base for custom implementations and directly copied into the `embedded` folder with the load script.

The file *must* expose a class with a `start` method that takes the api connector object as parameter.
