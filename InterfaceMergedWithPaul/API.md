# Interface API

## Disclaimer

If you haven't read the README, please read it before coming back here. To use the **API**, your must have a running Interface and be able to connect to a board.

## Prerequisites

For the Interface API to interface you will need:
* Running Interface with connected board
* A framework on the computer to create a UDP socket or read .CSV files

## Intro

The API of the Interface allows to receive a data stream from a connected board. There are 2 different methods to receive the data, in file format or live via UDP.

### Plot Visualisation

The easiest way to get the acquired data is by using the *Single Device Plot* which saves the data in following format:

| Date | Dim[1] | Dim[2] | Dim[3] | …        
|:-----|:-------|:-------|:-------|:---|
| Timestamp [s] | 1234 | 0.1234 | 1.234 |
| Timestamp [s] | 1234 | 0.1234 | 1.234 |
| Timestamp [s] | 1234 | 0.1234 | 1.234 |
| Timestamp [s] | 1234 | 0.1234 | 1.234 |
| Timestamp [s] | 1234 | 0.1234 | 1.234 |
| Timestamp [s] | 1234 | 0.1234 | 1.234 |
| Timestamp [s] | 1234 | 0.1234 | 1.234 |
| … | … | … | … |

The rows are sorted by `timestamp`

### Multi Plot Visualisation

The multiplot visualisation is a lot more complex as the different devices have different dimensions and read frequencies. Therefore the file has following format:

| Device | Dim | Date | Value |
|:-----|:-------|:-------|:-------|
| Device1 | 1 | Timestamp [s] | 123 |
| Device1 | 2 | Timestamp [s] | 345 |
| Device1 | 3 | Timestamp [s] | 567 |
| Device2 | 1 | Timestamp [s] | 1.23 |
| Device3 | 1 | Timestamp [s] | 0.123 |
| Device2 | 1 | Timestamp [s] | 1.23 |
| Device3 | 1 | Timestamp [s] | 0.123 |
| Device2 | 1 | Timestamp [s] | 1.23 |
| Device3 | 1 | Timestamp [s] | 0.123 |
| Device1 | 1 | Timestamp [s] | 123 |
| Device1 | 2 | Timestamp [s] | 345 |
| Device1 | 3 | Timestamp [s] | 567 |
| Device2 | 1 | Timestamp [s] | 1.23 |
| Device3 | 1 | Timestamp [s] | 0.123 |
| Device2 | 1 | Timestamp [s] | 1.23 |
| Device3 | 1 | Timestamp [s] | 0.123 |
| Device2 | 1 | Timestamp [s] | 1.23 |
| Device3 | 1 | Timestamp [s] | 0.123 |
| … | … | … | … |

The rows are sorted by `timestamp > device > dimension`

### UDP Stream

The UDP Stream uses the same format as the *Multi Plot Visualisation* by serializing every row to a message. **CAREFUL**: Usually UDP packets arrive ordered but it cannot be guaranteed.

A sequence of UDP messages could look like this:
```
>> "Device1,1,Timestamp,123"
>> "Device1,2,Timestamp,345"
>> "Device1,3,Timestamp,567"
>> "Device2,1,Timestamp,1.23"
>> "Device3,1,Timestamp,0.123"
>> "Device2,1,Timestamp,1.23"
>> "Device3,1,Timestamp,0.123"
>> "Device2,1,Timestamp,1.23"
>> "Device3,1,Timestamp,0.123"
```

The order of the rows cannot be guaranteed!

### Example

* Look at the example provided in `/Plots/UDPBroadcast.m` which uses the **UDP Stream** to receive the data stream in MATLAB.
* Look at the example provided in `/Plots/[Multi]PlotVisualisation.m` which uses the **CSV File** to load the data in MATLAB.
