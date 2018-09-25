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

    # Configure connection button clicked
    configureConnectionClicked = pyqtSignal()
    # Connect button clocked
    connect = pyqtSignal()

    # Board label
    _boardLabel = None
    # Board status label
    _boardStatusLabel = None
    # Board Ip label
    _boardIpLabel = None
    # Board Device stack
    _deviceStack = None
    # Board Device list
    _deviceList = None

    def __init__(self, name='––', ip='0.0.0.0', status='Initializing'):
        """Initialize the interface widget."""
        super().__init__()

        self.initUI()
        self.setName(name)
        self.setIp(ip)
        self.setStatus(ip)


    def initUI(self):
        """Initialize the ui of the interface widget."""
        configureButton = QPushButton("Configure …")
        configureButton.clicked.connect(self.onConfigureConnection)
        connectButton = QPushButton("Connect")
        connectButton.clicked.connect(self.onConnect)

        # Image of current board
        boardPixmapLabel = QLabel()
        boardPixmap = QPixmap('assets/bbb-image.jpg')
        scaledboardPixmap = boardPixmap.scaledToWidth(164)
        boardPixmapLabel.setPixmap(scaledboardPixmap)

        # Label of current board
        boardLabel = QLabel('Beaglebone Black Wireless')
        boardLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._boardLabel = boardLabel

        # Label of current board status
        boardStatusLabel = QLabel('Status: <b>Offline</b>')
        boardStatusLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._boardStatusLabel = boardStatusLabel

        # Label of current board ip
        boardIpLabel = QLabel('IP: <b>–</b>')
        boardIpLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._boardIpLabel = boardIpLabel

        # List of connected devices
        deviceList = QListWidget()
        self._deviceList = deviceList

        # Stack of connected device settings
        deviceStack = QStackedWidget()
        self._deviceStack = deviceStack

        # Layout for information box
        informationGridLayout = QGridLayout()
        informationGridLayout.addWidget(boardLabel,        0, 0, 1, 2, Qt.AlignLeft)
        informationGridLayout.addWidget(boardStatusLabel,  1, 0, Qt.AlignLeft)
        informationGridLayout.addWidget(boardIpLabel,      1, 1, Qt.AlignLeft)
        informationGridLayout.addWidget(connectButton,     2, 0, Qt.AlignLeft)
        informationGridLayout.addWidget(configureButton,   2, 1, Qt.AlignLeft)

        # Group informations
        groupLayout = QGroupBox('Information')
        groupLayout.setLayout(informationGridLayout)

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
        self._boardLabel.setText(name)

    def setIp(self, ip):
        """Set ip label."""
        self._boardIpLabel.setText('IP: <b>{}</b>'.format(ip))

    def setStatus(self, status):
        """Set states label."""
        self._boardStatusLabel.setText('Status: <b>{}</b>'.format(status))

    def updateDeviceList(self, devices):
        """Update device stack."""
        print('update',devices)
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
