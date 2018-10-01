# -*- coding: utf-8 -*-

import sys
import logging
import time
from PyQt5.QtCore import (Qt, pyqtSlot)
from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QLabel, QGridLayout, QGroupBox, QFileDialog)
import pyqtgraph as pg
import numpy as np

from deviceSettingsFunctionSelector import DeviceSettingsFunctionSelectorWidget

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

logging.basicConfig(level=logging.DEBUG)

# Standard color set for plots
standardColorSet = [
    (0,200,0),
    (200,0,100),
    (0,0,200),
    (200,200,100),
    (200,0,0),
    (200,200,200),
    (200,200,200),
    (200,200,200),
    (200,200,200),
    (200,200,200),
    (200,200,200),
    (200,200,200)
]

class DeviceSettingsWidget(QWidget):
    """
    Device Settings Widget.

    Default device settings
    """

    # Associated device
    _device = None

    # Plots used to display current data
    _plots = None

    def __init__(self, device):
        """Initialize the device settings widget."""
        super().__init__()

        if (device == None):
            raise ValueError('device is invalid')
        else:
            self._device = device;

        # Initialize the device settings UI
        self.initUI()


    def initUI(self):
        """Initialize the ui of the device settings widget."""
        # Layout for information of device
        informationLayout = QHBoxLayout()
        informationLayout.addWidget(QLabel('Direction: <i>{}</i>'.format(self._device.dir())))
        informationLayout.addWidget(QLabel('Dimension: <i>{}</i>'.format(self._device.dim())))

        # Group informations
        groupInformationWidget = QGroupBox(self._device.name())
        groupInformationWidget.setLayout(informationLayout)

        # Label for device data
        dataLabel = QLabel('Data')
        self._dataLabel = dataLabel

        # Layout for device data
        dataLayout = QHBoxLayout()
        dataLayout.addWidget(dataLabel)

        # Group data
        groupDataWidget = QGroupBox("Data [{}]".format(self._device.dim()))
        groupDataWidget.setLayout(dataLayout)

        # Device status layout
        statusLayout = QHBoxLayout()
        statusLayout.addWidget(groupInformationWidget)
        statusLayout.addWidget(groupDataWidget)
        statusLayout.addStretch(1)

        # Grid for the device settings layout
        bodyGridLayout = QGridLayout()
        bodyGridLayout.addLayout(statusLayout,                  0, 0, Qt.AlignLeft)

        # Widgets for dir=in
        if (self._device.dir() == 'in'):
            # Widget for plot data
            plotWidget = pg.PlotWidget(title='Live Data Plot')
            plotWidget.showAxis('bottom', False)
            self._plotWidget = plotWidget;

            # Create plots for all dimensions
            self._plots = []
            for i in range(self._device.dim()):
                plot = plotWidget.plot(pen=(standardColorSet[i]), name="Plot {}".format(i))
                self._plots.append(plot)
                bodyGridLayout.addWidget(plotWidget,            2, 0, Qt.AlignLeft | Qt.AlignTop)

            # Save button
            saveButton = QPushButton('Save Plot')
            saveButton.clicked.connect(self._onSavePlot)
            self._saveButton = saveButton

            # Save button
            saveStopButton = QPushButton('Stop Plot')
            saveStopButton.setVisible(False)
            saveStopButton.clicked.connect(self._onSaveStopPlot)
            self._saveStopButton = saveStopButton

            # Control options
            controlLayout = QHBoxLayout()
            controlLayout.addWidget(saveButton)
            controlLayout.addWidget(saveStopButton)
            controlLayout.addStretch(1)
            bodyGridLayout.addLayout(controlLayout,             1, 0, Qt.AlignLeft | Qt.AlignTop)

        # Widgets for dir=out
        else:

            # Start button
            startButton = QPushButton('Start Function')
            startButton.clicked.connect(self._onStartFunction)
            self._startButton = startButton

            # Stop button
            stopButton = QPushButton('Stop Function')
            stopButton.setVisible(False)
            stopButton.clicked.connect(self._onStopFunction)
            self._stopButton = stopButton

            # Control options
            controlLayout = QHBoxLayout()
            controlLayout.addWidget(startButton)
            controlLayout.addWidget(stopButton)
            controlLayout.addStretch(1)
            bodyGridLayout.addLayout(controlLayout,             1, 0, Qt.AlignLeft | Qt.AlignTop)

            # List of function selectors
            functionSelectionLayout = QHBoxLayout()

            # Function selector widgets
            self._functionSelectors = []
            for i in range(self._device.dim()):
                functionSelector = DeviceSettingsFunctionSelectorWidget(i)
                functionSelector.functionChanged.connect(self.updateFunction)
                functionSelectionLayout.addWidget(functionSelector)
                self._functionSelectors.append(functionSelector)
            bodyGridLayout.addLayout(functionSelectionLayout,   2, 0, Qt.AlignLeft | Qt.AlignTop)



        # Define stretching behaviour
        bodyGridLayout.setRowStretch(0, 1)
        bodyGridLayout.setRowStretch(1, 1)
        bodyGridLayout.setRowStretch(2, 10)

        self.setLayout(bodyGridLayout)


    def updateData(self):
        """Update data of a device."""
        newData = self._device.data()
        self._dataLabel.setText("<b>{}</b>".format("<br>".join('{:.4f}'.format(el) for el in newData if el != None)))

        # Save values
        if (self._device.fileName() != None and None not in newData):
            with open(self._device.fileName(), "a") as fh:
                fh.write(','.join(([str(time.time())] + list('{:f}'.format(el) for el in newData))) + '\n')

        # Widgets for dir=in
        if (self._device.dir() == 'in'):
            # Only update if new data is available
            if (len(newData) > 0):

                # Update every plot with past data from the device
                for i, pastDataI in enumerate(self._device.pastData()):
                    # Plot values
                    self._plots[i].setData(y=np.asarray(pastDataI), x=np.arange(len(pastDataI)))

        # Widgets for dir=out
        else:
            pass

    def saveFileDialog(self):
        """Dialog to select location to save file."""
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Device Plot For {}".format(self._device.name()),"{}/../../Plots/{}-plot.csv".format(sys.path[0], self._device.name()),"Text Files (*.csv)", options=options)
        if fileName:
            print('Save plot to file: {}'.format(fileName))
        return fileName

    @pyqtSlot(int, str, dict)
    def updateFunction(self, dim, function, parameters):
        """Update function of a device."""
        print('Update Function')
        self._device.setFunctionRunning(False)
        self._stopButton.setVisible(False)
        self._startButton.setVisible(True)
        self._device.setFunction(dim, function, parameters)


    @pyqtSlot()
    def _onStartFunction(self):
        """Start the funtion."""
        print('Start Function')
        self._device.setFunctionRunning(True)
        self._startButton.setVisible(False)
        self._stopButton.setVisible(True)

    @pyqtSlot()
    def _onStopFunction(self):
        """Stop the funtion."""
        print('Stop Function')
        self._device.setFunctionRunning(False)
        self._stopButton.setVisible(False)
        self._startButton.setVisible(True)

    @pyqtSlot()
    def _onSavePlot(self):
        """Save the plot."""
        fileName = self.saveFileDialog()
        # Prepare file
        if (fileName != None):
            with open(fileName, "w") as fh:
                fh.write(','.join((['Date'] + list('{:d}'.format(el) for el in range(self._device.dim())))) + '\n')
                self._device.setFileName(fileName)
                self._saveButton.setVisible(False)
                self._saveStopButton.setVisible(True)

    @pyqtSlot()
    def _onSaveStopPlot(self):
        """Stop saving the plot."""
        self._device.setFileName(None)
        self._saveStopButton.setVisible(False)
        self._saveButton.setVisible(True)

    def device(self):
        """Return the device."""
        return self._device
