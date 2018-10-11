# -*- coding: utf-8 -*-

import sys                                                      # System package
import time                                                     # Time package
import logging                                                  # Logging package
from PyQt5.QtCore import (  Qt,                                 # Core functionality from Qt
                            pyqtSlot)
from PyQt5.QtWidgets import (   QWidget,                        # Widget objects for GUI from Qt
                                QPushButton,
                                QCheckBox,
                                QHBoxLayout,
                                QLabel,
                                QGridLayout,
                                QGroupBox,
                                QFileDialog)
import pyqtgraph as pg                                          # Custom graphics package
import numpy as np                                              # Number utility package

from deviceSettingsFunctionSelector import DeviceSettingsFunctionSelectorWidget # Custom device settings function selector widget

pg.setConfigOptions(antialias=True)                             # Enable antialiasing for prettier plots

# Logging settings
LOG_LEVEL_PRINT = logging.INFO                                  # Set print level for stout logging
LOG_LEVEL_SAVE = logging.DEBUG                                  # Set print level for .log logging

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
    # Logger module
    _logger = None

    def __init__(self, device):
        """Initialize the device settings widget."""
        super().__init__()

        # Configure the logger
        self._logger = logging.getLogger('DeviceSettings')
        self._logger.setLevel(LOG_LEVEL_PRINT)                  # Only {LOG_LEVEL} level or above will be saved
        fh = logging.FileHandler('../Logs/DeviceSettings.log', 'w')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fh.setFormatter(formatter)
        fh.setLevel(LOG_LEVEL_SAVE)                             # Only {LOG_LEVEL} level or above will be saved
        self._logger.addHandler(fh)

        self._logger.info("Device settings initializing …")


        if (device == None):
            raise ValueError('device is invalid')
        else:
            self._device = device;

        # Initialize the device settings UI
        self.initUI()
        self._logger.info("Device settings initialized")


    def initUI(self):
        """Initialize the ui of the device settings widget."""
        # Layout for information of device
        informationLayout = QHBoxLayout()
        informationLayout.addWidget(QLabel('Direction: <i>{}</i>'.format(self._device.dir())))
        informationLayout.addWidget(QLabel('Dimension: <i>{}</i>'.format(self._device.dim())))

        # Group informations
        groupInformationWidget = QGroupBox(self._device.name())
        groupInformationWidget.setLayout(informationLayout)
        self._logger.debug("Device settings UI information created")

        # Label for device data
        dataLabel = QLabel('Data')
        self._dataLabel = dataLabel

        # Layout for device data
        dataLayout = QHBoxLayout()
        dataLayout.addWidget(dataLabel)

        # Group data
        groupDataWidget = QGroupBox("Data [{}]".format(self._device.dim()))
        groupDataWidget.setLayout(dataLayout)
        self._logger.debug("Device settings UI data created")

        # Device status layout
        statusLayout = QHBoxLayout()
        statusLayout.addWidget(groupInformationWidget)
        statusLayout.addWidget(groupDataWidget)
        statusLayout.addStretch(1)

        # Grid for the device settings layout
        bodyGridLayout = QGridLayout()
        bodyGridLayout.addLayout(statusLayout,                  0, 0, Qt.AlignLeft)
        self._logger.debug("Device settings UI status created")

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
            self._logger.debug("Device settings UI plot created")

            # Save button
            saveButton = QPushButton('Save Single Plot')
            saveButton.clicked.connect(self._onSavePlot)
            self._saveButton = saveButton

            # Save button
            saveStopButton = QPushButton('Stop Plot')
            saveStopButton.setVisible(False)
            saveStopButton.clicked.connect(self._onSaveStopPlot)
            self._saveStopButton = saveStopButton

            # Ignore flag
            ignoreCheckBox = QCheckBox('Ignore device in data plots and streams')
            if self._device.ignore():
                ignoreCheckBox.setChecked(True)
            else:
                ignoreCheckBox.setChecked(False)
            ignoreCheckBox.stateChanged.connect(self._onIgnore)
            self._ignoreCheckBox = ignoreCheckBox
            self._logger.debug("Device settings UI buttons created")


            # Control options
            controlLayout = QHBoxLayout()
            controlLayout.addWidget(saveButton)
            controlLayout.addWidget(saveStopButton)
            controlLayout.addWidget(ignoreCheckBox)
            controlLayout.addStretch(1)
            bodyGridLayout.addLayout(controlLayout,             1, 0, Qt.AlignLeft | Qt.AlignTop)
            self._logger.debug("Device settings UI layout created")

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
            self._logger.debug("Device settings UI buttons created")

            # Control options
            controlLayout = QHBoxLayout()
            controlLayout.addWidget(startButton)
            controlLayout.addWidget(stopButton)
            controlLayout.addStretch(1)
            bodyGridLayout.addLayout(controlLayout,             1, 0, Qt.AlignLeft | Qt.AlignTop)
            self._logger.debug("Device settings UI control created")

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
            self._logger.debug("Device settings UI function selector created")



        # Define stretching behaviour
        bodyGridLayout.setRowStretch(0, 1)
        bodyGridLayout.setRowStretch(1, 1)
        bodyGridLayout.setRowStretch(2, 10)

        self.setLayout(bodyGridLayout)
        self._logger.debug("Device settings UI layout created")


    def updateData(self):
        """Update data of a device."""
        newData = self._device.data()
        self._dataLabel.setText("<b>{}</b>".format("<br>".join('{:.4f}'.format(el) for el in newData if el != None)))

        if (self._device.fileName() != None and None not in newData): # Save values
            with open(self._device.fileName(), "a") as fh:      # Open file to append data
                fh.write(','.join(([str(time.time())] + list('{:f}'.format(el) for el in newData))) + '\n') # Write data

        if (self._device.dir() == 'in'):                        # Widgets for dir=in
            if (len(newData) > 0):                              # Only update if new data is available
                for i, pastDataI in enumerate(self._device.pastData()): # Update every plot with past data from the device
                    self._plots[i].setData(y=np.asarray(pastDataI), x=np.arange(len(pastDataI))) # Plot values

        else:                                                   # Widgets for dir=out
            pass

    def saveFileDialog(self):
        """Dialog to select location to save file."""
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog             # Can be uncommented if there is a problem with the default menu on OSX
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Device Plot For {}".format(self._device.name()),"{}/../../Plots/{} Plot.csv".format(sys.path[0], self._device.name()),"Text Files (*.csv)", options=options)
        if not fileName:
            self._logger.info('No file selected')
            return
        else:
            self._logger.info("Stream data to file '{}'".format(fileName))
            return fileName

    @pyqtSlot(int, str, dict)
    def updateFunction(self, dim, function, parameters):
        """Update function of a device."""
        self._device.setFunctionRunning(False)                  # Stop function
        self._stopButton.setVisible(False)
        self._startButton.setVisible(True)
        self._device.setFunction(dim, function, parameters)     # Set function parameter
        self._logger.debug("Function '{}' updated".format(function))


    @pyqtSlot()
    def _onStartFunction(self):
        """Start the funtion."""
        self._device.setFunctionRunning(True)                   # Start function
        self._startButton.setVisible(False)
        self._stopButton.setVisible(True)
        self._logger.info("Start function '{}'".format(self._device.function()))

    @pyqtSlot()
    def _onStopFunction(self):
        """Stop the funtion."""
        self._device.setFunctionRunning(False)                  # Stop function
        self._stopButton.setVisible(False)
        self._startButton.setVisible(True)
        self._logger.info("Stop function '{}'".format(self._device.function()))

    @pyqtSlot()
    def _onSavePlot(self):
        """Save the plot."""
        fileName = self.saveFileDialog()                        # Get file location
        if (fileName != None):                                  # Prepare file if one is selected
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
        self._logger.info("Data streaming has been stopped")

    @pyqtSlot(int)
    def _onIgnore(self, flag):
        """Set ignore flag."""
        if (flag == Qt.CheckState.Checked):                     # Set ignore flag for the device
            self._device.setIgnore(True)
            self._logger.info("Ignore device '{}' for streaming services".format(self._device.name()))
        else:
            self._device.setIgnore(False)
            self._logger.info("Do not ignore device '{}' for streaming services".format(self._device.name()))


    def device(self):
        """Return the device."""
        return self._device
