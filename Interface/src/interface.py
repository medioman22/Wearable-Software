#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from PyQt5.QtCore import (Qt, pyqtSignal, pyqtSlot)
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QListWidget, QStackedWidget, QGridLayout, QGroupBox)
from PyQt5.QtGui import (QPixmap)

from deviceSettings import DeviceSettingsWidget

logging.basicConfig(level=logging.DEBUG)

class InterfaceWidget(QWidget):
    """
    Interface Widget.

    Interface as the central widget of the main window displaying the board informations and connected peripheral devices
    """

    # Signal for connection button clicked
    configureConnectionClicked = pyqtSignal()
    # Signal for connect
    connect = pyqtSignal()

    # Board label
    _boardLabel = None
    # Board status label
    _boardStatusLabel = None
    # Board ip and port label
    _boardIpPortLabel = None
    # Board Device stack
    _deviceStack = None
    # Board Device list
    _deviceList = None

    def __init__(self, name='––', ip='0.0.0.0', port='', status='Initializing'):
        """Initialize the interface widget."""
        super().__init__()

        # Initialize interface UI
        self.initUI()
        self.setName(name)
        self.setIpAndPort(ip, port)
        self.setStatus(status)


    def initUI(self):
        """Initialize the ui of the interface widget."""
        # Configure button handling
        configureButton = QPushButton("Configure …")
        configureButton.clicked.connect(self.onConfigureConnection)
        connectButton = QPushButton("Connect")
        connectButton.clicked.connect(self.onConnect)

        # Image of current board
        boardPixmapLabel = QLabel()
        boardPixmap = QPixmap()
        scaledboardPixmap = boardPixmap.scaledToWidth(164)
        boardPixmapLabel.setPixmap(scaledboardPixmap)
        self._boardPixmapLabel = boardPixmapLabel

        # Label of current board status
        boardStatusLabel = QLabel('Status: <b>Offline</b>')
        boardStatusLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._boardStatusLabel = boardStatusLabel

        # Label of current board ip and port
        boardIpPortLabel = QLabel('IP: <b>–</b>')
        boardIpPortLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._boardIpPortLabel = boardIpPortLabel

        # List of connected devices
        deviceList = QListWidget()
        deviceList.currentTextChanged.connect(self.onSelectDevice)
        self._deviceList = deviceList

        # Stack of connected device settings
        deviceStack = QStackedWidget()
        self._deviceStack = deviceStack

        # Layout for information box
        informationGridLayout = QGridLayout()
        informationGridLayout.addWidget(boardStatusLabel,  0, 0, Qt.AlignLeft)
        informationGridLayout.addWidget(boardIpPortLabel,  0, 1, Qt.AlignLeft)
        informationGridLayout.addWidget(connectButton,     1, 0, Qt.AlignLeft)
        informationGridLayout.addWidget(configureButton,   1, 1, Qt.AlignLeft)

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

    def setName(self, name):
        """Set name label."""
        self._groupLayout.setTitle(name)

    def setImage(self, name):
        """Set image label."""
        boardPixmap = QPixmap('assets/{}.jpg'.format(name))
        scaledboardPixmap = boardPixmap.scaledToWidth(164)
        self._boardPixmapLabel.setPixmap(scaledboardPixmap)

    def setIpAndPort(self, ip, port):
        """Set ip and port label."""
        self._boardIpPortLabel.setText('IP <b>{}</b> : <b>{}</b>'.format(ip, port))

    def setStatus(self, status):
        """Set states label."""
        self._boardStatusLabel.setText('Status <b>{}</b>'.format(status))

    def updateDeviceList(self, devices):
        """Update device stack."""
        # Remove devices from list/stack
        while self._deviceList.count() > 0:
            self._deviceList.takeItem(0)
        while self._deviceStack.count() > 0:
            deviceWidget = self._deviceStack.widget(0)
            self._deviceStack.removeWidget(deviceWidget)
        # Add devices to list/stack
        for device in devices:
            self._deviceList.addItem(device.name())
            self._deviceStack.addWidget(DeviceSettingsWidget(device))


        # Sort the device list
        self._deviceList.sortItems(Qt.AscendingOrder);


    @pyqtSlot()
    def onConfigureConnection(self):
        """Listen to configure connection click event."""
        self.configureConnectionClicked.emit()
    @pyqtSlot()
    def onConnect(self):
        """Listen to configure connection click event."""
        self.connect.emit()
    @pyqtSlot(str)
    def onSelectDevice(self, name):
        """Listen to device selection event."""
        # Check if the list isn't empty
        if (self._deviceList.count() > 0):
            # Look for widget with name
            for i in range(0, self._deviceList.count()):
                deviceWidget = self._deviceStack.widget(i)
                # Break on first matching widget found
                if (deviceWidget.device().name() == name):
                    self._deviceStack.setCurrentWidget(deviceWidget)
                    break
            # Raise an error if no widget has been found
            else:
                raise ValueError('device not found')
