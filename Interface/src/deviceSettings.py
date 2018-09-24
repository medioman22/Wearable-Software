#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from PyQt5.QtCore import (Qt, pyqtSignal, pyqtSlot)
from PyQt5.QtWidgets import (QWidget, QMessageBox, QPushButton, QAction, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QSplitter, QStackedWidget)
from PyQt5.QtGui import (QPixmap)

logging.basicConfig(level=logging.DEBUG)

class DeviceSettingsWidget(QWidget):
    """
    Device Settings Widget.

    Default device settings
    """

    # Associated device
    _device = None

    def __init__(self, device):
        """Initialize the device settings widget."""
        super().__init__()

        self._device = device;
        self.initUI()


    def initUI(self):
        """Initialize the ui of the device settings widget."""
        bodyLayout = QVBoxLayout()
        bodyLayout.addWidget(QLabel('Device Settings'))

        self.setLayout(bodyLayout)


    def device(self):
        """Return the device."""
        return self._device
