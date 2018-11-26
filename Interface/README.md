# Interface

The interface is written to be using the API connection from the Firmware the display and configure the BBGW.

When connecting to the BBGW<br>
*Network Configuration*
```
IP: 192.168.7.2
Port: 12345
```

## Getting Started

These instructions will help you run the Interface.

### Prerequisites

For the Interface to run you will need:
* Beaglebone Green Wireless with running Firmware
* Network for BBGW and PC
* python3 installed

### Run

Start the Interface:
```
python3 main.py
```

## Guide

More information about the Interface and how to use it can be found in the `GUIDE.md`.

## Files & Streaming

More information about file formats and streaming can be found in the `API.md`.

## Documentation

More information about the Interface code and the functionality can be found in the `DOCS.md`.

# SoftWEAR firmware interface
 
This interface as been develop to work along the SoftWEAR firmware. It should be used on a PC connected to a BeagleBone green wireless

## Installing and setup of the PC

On the PC, you will need to have Python 3.5 or above installed as well as some pakages

```
pip install pyqt5
pip install pyqtgraph
```


## Running the tests

Go in the `Interface/src` folder in your PC and run the `main.py` file

```
python3 main.py
```

NOTE: if you PC have only the python 3 installed, it can append that you will need to use the command `python` instead of `python3`

