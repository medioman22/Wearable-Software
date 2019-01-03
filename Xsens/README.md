# Xsens data sending softwear

This program is writen in C++ and is based on the Xsens SDK examples.
It uses the [QT library](https://www.qt.io/) to display an interface for easy connection with an Xsens sensor.

## Developing 

The code was compile for a Windows 10 machine. It was done through visual studio with the QT tool plugin to handle all the depandancies and compilation makefile.

To run it, you need to recompile it in debug mode unfortunatly. I didn't manage to have it run without visual studio 2017 setup correctly with the right QT version `5.11.2`.


## Getting started

For know, the UPD IP and port are hard coded in the `UDP.h` file. They are localhost and `12347` for the port.

You begin the streaming by clicking on the `Start measurement`` button on the interface.