# -*- coding: utf-8 -*-
# Author: Cyrill Lippuner
# Date: October 2018

import sys                                                      # System package
import logging                                                  # Logging package
import functools                                                # Functools for extended usage
from PyQt5.QtCore import (  Qt,                                 # Core functionality from Qt
                            QSize,
                            pyqtSignal,
                            pyqtSlot)
from PyQt5.QtWidgets import (   QWidget,                        # Widget objects for GUI from Qt
                                QPushButton,
                                QDoubleSpinBox,
                                QCheckBox,
                                QHBoxLayout,
                                QVBoxLayout,
                                QScrollArea,
                                QLabel,
                                QGridLayout,
                                QGroupBox,
                                QComboBox,
                                QFileDialog,
                                QMessageBox)
from PyQt5.QtGui import (QMovie)                                # Media elements from Qt
import pyqtgraph as pg                                          # Custom graphics package
import numpy as np                                              # Number utility package
from connections.connection import Message                      # Import message

# from deviceSettingsFunctionSelector import DeviceSettingsFunctionSelectorWidget # Custom device settings function selector widget

pg.setConfigOptions(antialias=True)                             # Enable antialiasing for prettier plots

# Logging settings
LOG_LEVEL_PRINT = logging.INFO                                  # Set print level for stout logging
LOG_LEVEL_SAVE = logging.DEBUG                                  # Set print level for .log logging

# Standard color set for plots
standardColorSet = [
    (0,     200,    0),
    (200,   0,      0),
    (0,     0,      200),
    (200,   200,    100),
    (200,   0,      100),
    (200,   100,    0),
    (0,     200,    100),
    (100,   0,      100),
    (200,   100,    200),
    (100,   100,    0),
    (100,   100,    200),
    (50,    50,     200),
    (50,    0,       200),
    (50,    150,    0),
    (100,   150,    50),
    (100,   50,     0),
    (50,    150,    50),
    (150,   0,      150),
    (200,   200,    200)
]

class DeviceSettingsWidget(QWidget):
    """
    Device Settings Widget.

        Default device settings
    """

    # Message signal
    sendMessage = pyqtSignal(Message)
    # Signal for ignore
    ignore = pyqtSignal()

    # Associated device
    _device = None
    # Plots used to display current data
    _plots = None
    # Logger module
    _logger = None
    # Popup with plot
    _popupPlotWidget = None
    # Plots used to display current data for popup
    _popupPlots = None
    # Data widgets for in
    _dataWidgets = None
    # Set widgets for out
    _setWidgets = None
    # Flag whether set options have been initialized with real values
    _setInit = False

    def __init__(self, device):
        """Initialize the device settings widget."""
        super().__init__()

        # Configure the logger
        self._logger = logging.getLogger('DeviceSettings')
        self._logger.setLevel(LOG_LEVEL_PRINT)                  # Only {LOG_LEVEL} level or above will be saved
        # fh = logging.FileHandler('../Logs/DeviceSettings.log', 'w')
        # formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        # fh.setFormatter(formatter)
        # fh.setLevel(LOG_LEVEL_SAVE)                             # Only {LOG_LEVEL} level or above will be saved
        # self._logger.addHandler(fh)
        self._setWidgets = []
        self._dataWidgets = []
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
        infoButton = QPushButton('Info');
        infoButton.clicked.connect(self._onShowInfo)
        informationLayout.addWidget(infoButton)

        # Group informations
        groupInformationWidget = QGroupBox(self._device.name())
        groupInformationWidget.setLayout(informationLayout)
        self._logger.debug("Device settings UI information created")

        # Scroll area for data in/out
        inoutScroll = QScrollArea()
        inoutScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        inoutScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        inoutScroll.setMinimumWidth(200)
        # Widgets for dir=in
        if (self._device.dir() == 'in'):
            # Layout for device data
            dataLayout = QVBoxLayout()
            dataLayout.addWidget(QLabel('Input Data'))
            for dim in range(self._device.dim()):
                dataLabel = QLabel('–')
                dataLabel.setMinimumWidth(180)
                self._dataWidgets.append(dataLabel)
                dataLayout.addWidget(dataLabel)

            # Group data
            dataWidget = QWidget()
            dataWidget.setLayout(dataLayout)
            inoutScroll.setWidget(dataWidget)
        # Widgets for dir=out
        elif (self._device.dir() == 'out'):
            if 'dataType' in self._device.about():
                setLayout = QVBoxLayout()
                setLayout.addWidget(QLabel('Output Control'))
                if self._device.about()['dataType'] == 'On/Off':
                    for dim in range(self._device.dim()):
                        # On/Off button
                        toggleButton = QPushButton('{}: Off'.format(self._device.about()['dimMap'][dim]))
                        toggleButton.setStyleSheet('QPushButton {{color: rgb({},{},{})}}'.format(standardColorSet[dim][0], standardColorSet[dim][1], standardColorSet[dim][2]))
                        toggleButton.setCheckable(True)
                        toggleButton.toggled.connect(functools.partial(self._onToggled, dim))
                        self._setWidgets.append(toggleButton)
                        setLayout.addWidget(toggleButton)
                elif self._device.about()['dataType'] == 'Range':
                    for dim in range(self._device.dim()):
                        # Range field
                        spinBox = QDoubleSpinBox()
                        spinBox.setPrefix(self._device.about()['dimMap'][dim] + ': ')
                        spinBox.setSuffix(' ' + self._device.about()['dimUnit'][dim])
                        spinBox.setStyleSheet('QDoubleSpinBox {{color: rgb({},{},{})}}'.format(standardColorSet[dim][0], standardColorSet[dim][1], standardColorSet[dim][2]))
                        spinBox.setMinimum(self._device.about()['dataRange'][0]);
                        spinBox.setMaximum(self._device.about()['dataRange'][1]);
                        spinBox.valueChanged.connect(functools.partial(self._onSpinBoxChanged, dim))
                        self._setWidgets.append(spinBox)
                        setLayout.addWidget(spinBox)
                setWidget = QWidget()
                setWidget.setLayout(setLayout)
                inoutScroll.setWidget(setWidget)


        # Device status layout
        statusLayout = QVBoxLayout()
        statusLayout.addWidget(groupInformationWidget)
        statusLayout.addWidget(inoutScroll)
        statusLayout.addStretch(1)

        # Grid for the device settings layout
        bodyGridLayout = QGridLayout()
        bodyGridLayout.addLayout(statusLayout,              0, 0, 2, 1, Qt.AlignLeft | Qt.AlignTop)
        self._logger.debug("Device settings UI status created")

        # Widget for plot data
        plotWidget = pg.PlotWidget(title='Live Data Plot')
        plotWidget.showAxis('bottom', False)
        self._plotWidget = plotWidget;

        # Create plots for all dimensions
        self._plots = []
        for i in range(self._device.dim()):
            plot = plotWidget.plot(pen=(standardColorSet[i]), name="Plot {}".format(i))
            self._plots.append(plot)
            bodyGridLayout.addWidget(plotWidget,            1, 1, 3, 1, Qt.AlignLeft | Qt.AlignTop)
        self._logger.debug("Device settings UI plot created")

        # Stream indicator
        streamGifLabel = QLabel()
        streamGif = QMovie("assets/stream.gif")
        streamGif.setScaledSize(QSize(24,24))
        streamGifLabel.setMovie(streamGif)
        streamGifLabel.setVisible(False)
        streamGif.start()
        self._streamGifLabel = streamGifLabel

        # Save button
        saveButton = QPushButton('Save Single Plot')
        saveButton.clicked.connect(self._onSavePlot)
        self._saveButton = saveButton

        # Stop save button
        saveStopButton = QPushButton('Stop Plot')
        saveStopButton.setVisible(False)
        saveStopButton.clicked.connect(self._onSaveStopPlot)
        self._saveStopButton = saveStopButton

        # Ignore flag
        ignoreCheckBox = QCheckBox('Ignore')
        if self._device.ignore():
            ignoreCheckBox.setChecked(True)
        else:
            ignoreCheckBox.setChecked(False)
        ignoreCheckBox.stateChanged.connect(self._onIgnore)
        self._ignoreCheckBox = ignoreCheckBox
        self._logger.debug("Device settings UI buttons created")

        # Show plot in popup
        plotPopup = QPushButton('Show Plot In Popup')
        plotPopup.clicked.connect(self._onShowPlotInPopup)
        self._plotPopup = plotPopup

        # Control options
        controlLayout = QHBoxLayout()
        controlLayout.addWidget(streamGifLabel)
        controlLayout.addWidget(saveButton)
        controlLayout.addWidget(saveStopButton)
        controlLayout.addWidget(plotPopup)
        controlLayout.addWidget(ignoreCheckBox)
        controlLayout.addStretch(1)
        bodyGridLayout.addLayout(controlLayout,             0, 1, 1, 1, Qt.AlignLeft | Qt.AlignTop)
        self._logger.debug("Device settings UI layout created")


        # Settings
        if self._device.settings() != None:
            settingsLayout = QGridLayout()

            # Mode setting
            if ('modes' in self._device.settings()):            # Check if modes are available
                # Button for mode selector menu
                modeSelectorMenu = QComboBox()
                for mode in self._device.settings()['modes']:   # Loop all modes
                    modeSelectorMenu.addItem(mode)
                index = modeSelectorMenu.findText(self._device.mode())
                modeSelectorMenu.setCurrentIndex(index);
                modeSelectorMenu.currentTextChanged.connect(self._onModeSelection)
                settingsLayout.addWidget(QLabel('Mode'), 0, 0, Qt.AlignLeft)
                settingsLayout.addWidget(modeSelectorMenu, 0, 1, Qt.AlignLeft)

            # Frequency setting
            if ('frequencies' in self._device.settings()):      # Check if frequency are available
                # Button for frequency selector menu
                frequencySelectorMenu = QComboBox()
                for frequency in self._device.settings()['frequencies']: # Loop all frequencies
                    frequencySelectorMenu.addItem(frequency)
                index = frequencySelectorMenu.findText(self._device.frequency())
                frequencySelectorMenu.setCurrentIndex(index);
                frequencySelectorMenu.currentTextChanged.connect(self._onFrequencySelection)
                settingsLayout.addWidget(QLabel('Frequency'), 1, 0, Qt.AlignLeft)
                settingsLayout.addWidget(frequencySelectorMenu, 1, 1, Qt.AlignLeft)

            # Duty frequency setting
            if ('dutyFrequencies' in self._device.settings()):  # Check if dutyFrequency are available
                # Button for dutyFrequency selector menu
                dutyFrequencySelectorMenu = QComboBox()
                for dutyFrequency in self._device.settings()['dutyFrequencies']: # Loop all dutyFrequencies
                    dutyFrequencySelectorMenu.addItem(dutyFrequency)
                index = dutyFrequencySelectorMenu.findText(self._device.dutyFrequency())
                dutyFrequencySelectorMenu.setCurrentIndex(index);
                dutyFrequencySelectorMenu.currentTextChanged.connect(self._onDutyFrequencySelection)
                settingsLayout.addWidget(QLabel('Duty Frequency'), 2, 0, Qt.AlignLeft)
                settingsLayout.addWidget(dutyFrequencySelectorMenu, 2, 1, Qt.AlignLeft)

            # Flag setting
            if ('flags' in self._device.settings()):            # Check if flags are available
                # Checkbox for flags
                for flag in self._device.settings()['flags']:   # Loop all flags
                    flagCheckboxWidget = QCheckBox(flag)
                    if flag in self._device.flags():            # Check if flag is raised
                        flagCheckboxWidget.setChecked(True)
                    else:
                        flagCheckboxWidget.setChecked(False)
                    flagCheckboxWidget.stateChanged.connect(functools.partial(self._onFlagChanged, flag))
                    settingsLayout.addWidget(flagCheckboxWidget, 3, 0, Qt.AlignLeft)

            bodyGridLayout.addLayout(settingsLayout,            3, 0, 1, 1, Qt.AlignLeft | Qt.AlignTop)
            self._logger.debug("Device settings created")




        # Define stretching behaviour
        bodyGridLayout.setRowStretch(0, 1)
        bodyGridLayout.setRowStretch(1, 10)
        bodyGridLayout.setRowStretch(2, 1)
        bodyGridLayout.setRowStretch(3, 1)

        self.setLayout(bodyGridLayout)
        self._logger.debug("Device settings UI layout created")


    def updateData(self):
        """Update data of a device."""
        newData = self._device.data()                           # Get data from device
        newTimestamp = self._device.timestamp()                 # Get timestamp from device
        if len(newData) == self._device.dim():                  # Check if data has same length as dim
            for dim in range(self._device.dim()):               # Loop all dim
                if (self._device.activeDim()[dim]):             # Only print active dim
                    if self._device.dir() == 'in':
                        self._dataWidgets[dim].setText('<span style="color: rgb({},{},{})">{}: {:.4f} {}</span>'.format(standardColorSet[dim][0], standardColorSet[dim][1], standardColorSet[dim][2], self._device.about()['dimMap'][dim], newData[dim], self._device.about()['dimUnit'][dim]))
                    if (not self._setInit and                   # Check if output control widgets need to be initialized
                        self._device.dir() == 'out' and
                        'dataType' in self._device.about()):
                                                                # Initialize On/Off buttons
                        if self._device.about()['dataType'] == 'On/Off':
                            if newData[dim] == 1:               # Set to On
                                self._setWidgets[dim].setChecked(True)
                                self._setWidgets[dim].setText('{}: On'.format(self._device.about()['dimMap'][dim]))
                            else:                               # Set to Off
                                self._setWidgets[dim].setChecked(False)
                                self._setWidgets[dim].setText('{}: Off'.format(self._device.about()['dimMap'][dim]))
                        if self._device.about()['dataType'] == 'Range':
                                                                # Set the value
                            self._setWidgets[dim].setValue(newData[dim])
        self._setInit = True                                    # Clear init output flag

        if (self._device.fileName() != None and None not in newData): # Save values
            with open(self._device.fileName(), "a") as fh:      # Open file to append data
                fh.write(','.join(([str(newTimestamp)] + list('{:f}'.format(el) for el in newData))) + '\n') # Write data

        if (len(newData) > 0):                                  # Only update if new data is available
            for i, pastDataI in enumerate(self._device.pastData()): # Update every plot with past data from the device
                self._plots[i].setData(y=np.asarray(pastDataI), x=np.arange(len(pastDataI))) # Plot values
                if self._device.activeDim()[i] == False:        # Check if dimension is active
                    self._plots[i].setPen((0,0,0))              # Set pen to BLACK
                else:
                    self._plots[i].setPen(standardColorSet[i])  # Set pen to default color
                if self._popupPlots != None and len(self._popupPlots) > 0: # Check for open popup
                    self._popupPlots[i].setData(y=np.asarray(pastDataI), x=np.arange(len(pastDataI))) # Plot values for popup


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
    def _onShowInfo(self):
        """Show the info."""
        QMessageBox.information(self, '{}'.format(self._device.name()), self._device.about()['info'], QMessageBox.Close, QMessageBox.Close)
        self._logger.info("Show info")

    @pyqtSlot()
    def _onStartFunction(self):
        """Start the function."""
        self._device.setFunctionRunning(True)                   # Start function
        self._startButton.setVisible(False)
        self._stopButton.setVisible(True)
        self._logger.info("Start function '{}'".format(self._device.function()))

    @pyqtSlot()
    def _onStopFunction(self):
        """Stop the function."""
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
                self._streamGifLabel.setVisible(True)

    @pyqtSlot()
    def _onSaveStopPlot(self):
        """Stop saving the plot."""
        self._device.setFileName(None)
        self._saveStopButton.setVisible(False)
        self._streamGifLabel.setVisible(False)
        self._saveButton.setVisible(True)
        self._logger.info("Data streaming has been stopped")

    @pyqtSlot(int, bool)
    def _onToggled(self, dim, value):
        """Set value for dim."""
        if (value):                                             # Set value to 1 for dim
            self.sendMessage.emit(Message('Set', self._device.name(), {'dim': dim, 'value': 1}))
            self._setWidgets[dim].setText('{}: On'.format(self._device.about()['dimMap'][dim]))
        else:                                                   # Set value to 0 for dim
            self.sendMessage.emit(Message('Set', self._device.name(), {'dim': dim, 'value': 0}))
            self._setWidgets[dim].setText('{}: Off'.format(self._device.about()['dimMap'][dim]))
        self._logger.info("Set to '{}' for dim".format(value))

    @pyqtSlot(int, float)
    def _onSpinBoxChanged(self, dim, value):
        """Set value for dim."""
                                                                # Set new value
        self.sendMessage.emit(Message('Set', self._device.name(), {'dim': dim, 'value': value}))
        self._logger.info("Set to '{}' for dim".format(value))

    @pyqtSlot(int)
    def _onIgnore(self, flag):
        """Set ignore flag."""
        if (flag == Qt.CheckState.Checked):                     # Set ignore flag for the device
            self._device.setIgnore(True)
            self.ignore.emit()
            self._logger.info("Ignore device '{}'".format(self._device.name()))
        else:
            self._device.setIgnore(False)
            self.ignore.emit()
            self._logger.info("Do not ignore device '{}'".format(self._device.name()))

    @pyqtSlot(str)
    def _onModeSelection(self, mode):
        """Select mode listener."""
        if (mode in self._device.settings()['modes']):
            self.sendMessage.emit(Message('Settings', self._device.name(), {'mode': mode}))
            self._logger.info("Mode '{}' selected".format(mode))
        else:
            raise ValueError('Mode {} is invalid'.format(mode))

    @pyqtSlot(str)
    def _onFrequencySelection(self, frequency):
        """Select frequency listener."""
        if (frequency in self._device.settings()['frequencies']):
            self.sendMessage.emit(Message('Settings', self._device.name(), {'frequency': frequency}))
            self._logger.info("Frequency '{}' selected".format(frequency))
        else:
            raise ValueError('Frequency {} is invalid'.format(frequency))

    @pyqtSlot(str)
    def _onDutyFrequencySelection(self, dutyFrequency):
        """Select dutyFrequency listener."""
        if (dutyFrequency in self._device.settings()['dutyFrequencies']):
            self.sendMessage.emit(Message('Settings', self._device.name(), {'dutyFrequency': dutyFrequency}))
            self._logger.info("Duty frequency '{}' selected".format(dutyFrequency))
        else:
            raise ValueError('Duty frequency {} is invalid'.format(dutyFrequency))

    @pyqtSlot(int, int)
    def _onFlagChanged(self, flag, value):
        """Set flag."""
        if (value == Qt.CheckState.Checked):                     # Set flag for the device
            self.sendMessage.emit(Message('Settings', self._device.name(), {'flag': flag, 'value': True}))
            self._logger.info("Flag '{}' enabled".format(flag))
        else:
            self.sendMessage.emit(Message('Settings', self._device.name(), {'flag': flag, 'value': False}))
            self._logger.info("Flag '{}' disabled".format(flag))

    @pyqtSlot()
    def _onShowPlotInPopup(self):
        """Show plot in popup."""
        if (self._popupPlotWidget != None):                           # Bring popup to front
            self._popupPlotWidget.show()
            self._popupPlotWidget.activateWindow()
            self._popupPlotWidget.raise_()
        else:
            # Widget for plot data
            self._popupPlots = []
            self._popupPlotWidget = pg.PlotWidget(title='Live Data Plot')
            self._popupPlotWidget.setWindowTitle(self._device.name())
            self._popupPlotWidget.showAxis('bottom', False)
            for i in range(self._device.dim()):
                plot = self._popupPlotWidget.plot(pen=(standardColorSet[i]), name="Plot {}".format(i))
                self._popupPlots.append(plot)
            self._logger.debug("Popup Plot For {}".format(self._device.name()))
            self._popupPlotWidget.show()
            self._popupPlotWidget.activateWindow()
            self._popupPlotWidget.raise_()



    def device(self):
        """Return the device."""
        return self._device
