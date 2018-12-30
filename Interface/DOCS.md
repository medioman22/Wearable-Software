# Interface DOCS

This documentation provides a *schematic* overview of the Interface. For a more in-depth view of the individual modules please have a look at the *inline* documentation in the files.

## Content

* `README.md` contains everything needed to run the Interface
* `DOCS.md` and `API.md` contain the documentation of the Interface
* `src` contains the source code of the Firmware
* `Logs` contains a set of files generated at runtime
* `Plots` contains generated files at runtime

## Setup

Look at `README.md` for instructions to run the software.

## Source

`requirements.txt` holds the necessary libraries in order to run the Interface.

* The interface is running on python3
* PyQt5 is used for graphical layout ([more info](https://pypi.org/project/PyQt5/))
* pyqtgraph is used for realtime plotting integrated into PyQt* ([more info](http://www.pyqtgraph.org))

### main.py

The main file is the heart of the Interface and used to start it with:

```
python3 main.py
```

#### Initialization

The initialization imports all necessary modules and opens the main window. The *main* manages several menus and options which lets one:

* Select and configure the board with ip/port
* Enable streaming to UDP or Files
* Disable scanning and configure plotting buffer range

It also handles the data flow from the connection to the board to the visual modules displaying the data as well as the streaming to UDP and Files.

#### Update Thread

The *update* thread is executed every `UPDATE_LOOP`. It has following tasks:

1. Get all messages received via the board connection
2. Update the state of the board and its devices and store new data in the model
3. Refresh the visual modules with the new data
4. If streaming, send the data via UDP or write it to a File (More info about the UPD/File format, have a look at `API.md`)
5. Send new commands for the board via the board connection

### Boards

In the folder `/boards` is an abstract class for a *board*. On top of that one can implement a specific board handling the custom serializing for the associated connection.

Implemented boards:

* `beagleboneGreenWirelessBoard.py`

#### Board

The abstract board class is a model of the real board describing its state like *name*, *ip*, *port*, *etc*. It has methods to `register`/`deregister` devices, `update` with new data for the devices and `configure` settings. It is allowed to manage the devices, even the `_private` fields.

#### Devices

The device class is a model of a real device connected to the board describing its state like *name*, *about*, *settings*, *values*, *etc*. The device instances are created and destroyed by the board only!

### Communication

In the folder `/connections` is an abstract class for a *connection*. On top of that one can implement a connection for a specific board. The implemented communication class then handles all data traffic of the Interface to the board. One is able to send and receive serialized JSON messages. The messages are internally queued and one can use the non-blocking *send* and *get* methods to push and pop messages.

Implemented connections:

* `beagleboneGreenWirelessConnection.py` with a *TCP/IP* socket

### connectionDialog.py

The connection dialog is used to set *IP* and *Port* of the connection.

### interface.py

The interface widget represents the currently connected board (if one, else it shows the controls to connect) and displays an image, the name and the high-level settings and controls for the board. It also has a list of connected devices which can be selected and are managed by the `deviceSettings.py` widget.

When getting a refresh message from the `main.py`, the interface takes care that all the devices get refreshed by calling the `deviceSettings.py` widget.

### deviceSettings.py

The device settings widgets represents a single device currently connected. It displays the configuration, the live values and a live plot as well as (if allowed) input fields for values and settings control.

### udpBroadcast.py

The UDP Broadcast module sets up a UDP socket and a proper thread handling the data stream coming from the `main.py` module. It is non-blocking and can be used along the other functionalities.

When calling the module as a script it will just stream constantly:

```
python3 udpBroadcast.py
```

This is useful to debug the UDP connection without needing to connect any hardware.

### utils.py

The utils module is a collection of globally used constants and functions.

## Logs

All performance and debug logs generated by the interface are stored in the `/Logs` folder.

## Plots

When streaming data to a file, per default to chooses the `/Plot` folder to save the file.

This folder also contains *.m* files to load the files into MATLAB.