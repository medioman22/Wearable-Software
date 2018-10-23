# -*- coding: utf-8 -*-
# Author: Cyrill Lippuner
# Date: October 2018

import logging                                                  # Logging package
from PyQt5.QtCore import (  Qt,                                 # Core functionality from Qt
                            QSize,
                            pyqtSignal,
                            pyqtSlot)
from PyQt5.QtWidgets import (   QWidget,                        # Widget objects for GUI from Qt
                                QPushButton,
                                QLabel,
                                QListWidget,
                                QListWidgetItem,
                                QStackedWidget,
                                QGridLayout,
                                QGroupBox)
from PyQt5.QtGui import (QPixmap, QMovie)                       # Media elements from Qt

from deviceSettings import DeviceSettingsWidget                 # Custom device settings widget
from connections.connection import Message                      # Import message

# Logging settings
LOG_LEVEL_PRINT = logging.INFO                                  # Set print level for stout logging
LOG_LEVEL_SAVE = logging.DEBUG                                  # Set print level for .log logging

class InterfaceWidget(QWidget):
    """
    Interface Widget.

        Interface as the central widget of the main window displaying the board informations and connected peripheral devices
    """

    # Signal for connection button clicked
    configureConnectionClicked = pyqtSignal()
    # Signal for connect
    connect = pyqtSignal()
    # Signal for mode change
    sendMessage = pyqtSignal(Message)
    # Signal for update
    update = pyqtSignal()

    # Board label
    _boardLabel = None
    # Board status label
    _boardStatusLabel = None
    # Board ip and port label
    _boardIpPortLabel = None
    # Board cycle durations
    _boardCycleDurations = None
    # Board Device stack
    _deviceStack = None
    # Board Device list
    _deviceList = None
    # Selected device
    _selectedDeviceName = None
    # Logger module
    _logger = None

    def __init__(self):
        """Initialize the interface widget."""
        super().__init__()

        # Configure the logger
        self._logger = logging.getLogger('Interfaces')
        self._logger.setLevel(LOG_LEVEL_PRINT)                  # Only {LOG_LEVEL} level or above will be saved
        # fh = logging.FileHandler('../Logs/Interface.log', 'w')
        # formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        # fh.setFormatter(formatter)
        # fh.setLevel(LOG_LEVEL_SAVE)                             # Only {LOG_LEVEL} level or above will be saved
        # self._logger.addHandler(fh)

        self._logger.info("Interface initializing …")

        # Initialize interface UI
        self.initUI()

        self._logger.info("Interface initialized")

    def initUI(self):
        """Initialize the ui of the interface widget."""
        # Configure button handling
        configureButton = QPushButton("Configure …")
        configureButton.clicked.connect(self.onConfigureConnection)
        connectButton = QPushButton("Connect")
        connectButton.clicked.connect(self.onConnect)
        self._logger.debug("Interface UI buttons created")

        # Image of current board
        boardPixmapLabel = QLabel()
        boardPixmap = QPixmap()
        scaledboardPixmap = boardPixmap.scaledToWidth(240)
        boardPixmapLabel.setPixmap(scaledboardPixmap)
        self._boardPixmapLabel = boardPixmapLabel
        self._logger.debug("Interface UI image created")

        # Label of current board status
        boardConnectionTypeLabel = QLabel('Connection Type: <b></b>')
        boardConnectionTypeLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._boardConnectionTypeLabel = boardConnectionTypeLabel

        # Label of current board status
        boardStatusLabel = QLabel('Status: <b>Offline</b>')
        boardStatusLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._boardStatusLabel = boardStatusLabel

        # Label of current board ip and port
        boardIpPortLabel = QLabel('IP: <b>–</b>')
        boardIpPortLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._boardIpPortLabel = boardIpPortLabel

        # Label of current board ip and port
        boardCycleDurationLabel = QLabel('')
        boardCycleDurationLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._boardCycleDurationLabel = boardCycleDurationLabel

        # Stream label
        streamLabel = QLabel('Stream ()')
        streamLabel.setVisible(False)
        self._streamLabel = streamLabel

        # Stream indicator
        streamGifLabel = QLabel()
        streamGif = QMovie("assets/stream.gif")
        streamGif.setScaledSize(QSize(24,24))
        streamGifLabel.setMovie(streamGif)
        streamGifLabel.setVisible(False)
        streamGif.start()
        self._streamGifLabel = streamGifLabel

        # Scan indicator
        scanLabel = QLabel('Scanning')
        self._scanLabel = scanLabel
        scanGifLabel = QLabel()
        scanGif = QMovie("assets/scan.gif")
        scanGif.setScaledSize(QSize(24,24))
        scanGifLabel.setMovie(scanGif)
        scanGifLabel.setVisible(False)
        scanGif.start()
        self._scanGifLabel = scanGifLabel
        self._logger.debug("Interface UI labels created")


        # List of connected devices
        deviceList = QListWidget()
        deviceList.currentItemChanged.connect(self.onSelectDevice)
        deviceList.setMinimumWidth(240)
        self._deviceList = deviceList
        self._logger.debug("Interface UI device list created")

        # Stack of connected device settings
        deviceStack = QStackedWidget()
        self._deviceStack = deviceStack
        self._logger.debug("Interface UI device stack created")

        # Layout for information box
        informationGridLayout = QGridLayout()
        informationGridLayout.addWidget(boardConnectionTypeLabel,   0, 0, 1, 4, Qt.AlignLeft)
        informationGridLayout.addWidget(boardStatusLabel,           1, 0, Qt.AlignLeft)
        informationGridLayout.addWidget(boardIpPortLabel,           1, 1, Qt.AlignLeft)
        informationGridLayout.addWidget(scanLabel,                  2, 0, Qt.AlignLeft)
        informationGridLayout.addWidget(scanGifLabel,               2, 1, Qt.AlignLeft)
        informationGridLayout.addWidget(boardCycleDurationLabel,    2, 2, Qt.AlignLeft)
        informationGridLayout.addWidget(streamLabel,                2, 3, Qt.AlignLeft)
        informationGridLayout.addWidget(streamGifLabel,             2, 4, Qt.AlignLeft)
        informationGridLayout.addWidget(connectButton,              3, 0, Qt.AlignLeft)
        informationGridLayout.addWidget(configureButton,            3, 1, Qt.AlignLeft)

        # Group informations
        groupLayout = QGroupBox('Information')
        groupLayout.setLayout(informationGridLayout)
        self._groupLayout = groupLayout

        # Grid for the interface layout
        bodyGridLayout = QGridLayout()
        bodyGridLayout.addWidget(boardPixmapLabel,      0, 0, Qt.AlignCenter)
        bodyGridLayout.addWidget(groupLayout,           0, 1, Qt.AlignLeft)
        bodyGridLayout.addWidget(deviceList,            1, 0, Qt.AlignLeft)
        bodyGridLayout.addWidget(deviceStack,           1, 1, Qt.AlignLeft)

        # Define stretching behaviour
        bodyGridLayout.setRowStretch(0, 1)
        bodyGridLayout.setRowStretch(1, 10)
        bodyGridLayout.setColumnStretch(0, 1)
        bodyGridLayout.setColumnStretch(1, 10)

        self.setLayout(bodyGridLayout)
        self._logger.debug("Interface UI layout created")

    def setBoardInformation(self, board):
        """Set board information."""
        # Set name label
        self._groupLayout.setTitle(board.name())

        # Set image label
        boardPixmap = QPixmap('assets/{}.png'.format(board.name()))
        scaledboardPixmap = boardPixmap.scaledToWidth(240)
        self._boardPixmapLabel.setPixmap(scaledboardPixmap)

        # Set connection type
        self._boardConnectionTypeLabel.setText('Connection Type <b>{}</b>'.format(board.connectionType()))
        self._logger.debug("Interface UI information updated")

    def setStatus(self, status):
        """Set states label."""
        self._boardStatusLabel.setText('Status <b>{}</b>'.format(status))
        self._logger.debug("Interface UI status updated")

    def setIpAndPort(self, ip, port):
        """Set ip and port label."""
        self._boardIpPortLabel.setText('IP <b>{}</b> : <b>{}</b>'.format(ip, port))
        self._logger.debug("Interface UI ip/port updated")

    def setStreamLabel(self, stream, toChannel=None):
        """Set stream label and channel."""
        if stream:                                              # Show stream label
            self._streamLabel.setText('Stream <b>{}</b>'.format(toChannel))
            self._streamLabel.setVisible(True)
            self._streamGifLabel.setVisible(True)
        else:                                                   # Hide stream label
            self._streamLabel.setVisible(False)
            self._streamGifLabel.setVisible(False)
        self._logger.debug("Interface UI stream updated")

    def setScanLabel(self, scan):
        """Set scan label and channel."""
        if scan:                                                # Show scan label
            self._scanLabel.setVisible(True)
            self._scanGifLabel.setVisible(True)
        else:                                                   # Hide scan label
            self._scanLabel.setVisible(False)
            self._scanGifLabel.setVisible(False)
        self._logger.debug("Interface UI scan updated")

    def setCycleDurationLabel(self, cycleDurations):
        """Set cycle duration label and channel."""
        self._boardCycleDurations = cycleDurations
        self._boardCycleDurationLabel.setText('Update <b>{:06.2f} ms</b> | Scan <b>{:06.2f} ms</b>'.format(cycleDurations['update'] * 1000, cycleDurations['scan'] * 1000))
        self._logger.debug("Interface UI scan updated")

    def updateDeviceList(self, devices):
        """Update device stack."""
        while self._deviceList.count() > 0:                     # Remove devices from list/stack
            self._deviceList.takeItem(0)
        while self._deviceStack.count() > 0:                    # Remove devices from list/stack
            deviceWidget = self._deviceStack.widget(0)
            self._deviceStack.removeWidget(deviceWidget)
        deviceToSelect = None
        deviceListItemToSelect = None
        deviceWidgetToSelect = None
        for device in devices:                                  # Add devices to list/stack
            deviceListItem = QListWidgetItem(device.name())
            deviceWidget = DeviceSettingsWidget(device)
            deviceWidget.sendMessage.connect(self.onSendMessage)
            deviceWidget.ignore.connect(self.onIgnoreDevice)
            self._deviceList.addItem(deviceListItem)
            self._deviceStack.addWidget(deviceWidget)
            if (device.name() == self._selectedDeviceName):     # Check for previous selection
                deviceToSelect = device
                deviceListItemToSelect = deviceListItem
                deviceWidgetToSelect = deviceWidget
        if (deviceToSelect != None):                            # Reselect device
            self._deviceList.setCurrentItem(deviceListItemToSelect)
            self._deviceStack.setCurrentWidget(deviceWidgetToSelect)
        elif (len(self._deviceList) > 0):
            self._deviceList.setCurrentRow(0)
            self._deviceStack.setCurrentIndex(0)
        self._logger.debug("Interface UI device list updated")


        self._deviceList.sortItems(Qt.AscendingOrder);          # Sort the device list

    def updateData(self):
        """Update all data elements."""
        for i in range(0, self._deviceList.count()):            # Update data for all devices
            self._deviceStack.widget(i).updateData()


    @pyqtSlot()
    def onConfigureConnection(self):
        """Listen to configure connection click event."""
        self.configureConnectionClicked.emit()
    @pyqtSlot()
    def onConnect(self):
        """Listen to configure connection click event."""
        self.connect.emit()
    @pyqtSlot(QListWidgetItem)
    def onSelectDevice(self, listItem):
        """Listen to device selection event."""
        if listItem == None:                                    # Ignore empty selection
            return
        name = listItem.text()
        if (self._deviceList.count() > 0):                      # Check if the list isn't empty
            for i in range(0, self._deviceList.count()):        # Look for widget with name
                deviceWidget = self._deviceStack.widget(i)
                if (deviceWidget.device().name() == name):      # Break on first matching widget found
                    self._deviceStack.setCurrentWidget(deviceWidget)
                    self._selectedDeviceName = name
                    self._logger.info("Device '{}' selected".format(name))
                    break
            else:                                               # Ignore when widget does no longer exist
                pass


    @pyqtSlot(Message)
    def onSendMessage(self, message):
        """Listen to send message event from device widgets and pass them to the main."""
        self.sendMessage.emit(message)

    @pyqtSlot()
    def onIgnoreDevice(self):
        """Listen to ignore flag of a device to pass it to the main."""
        self.update.emit()
