#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Wearable Software Interface

This application provides an interface to the firmware loaded on the BBB

Author: Cyrill Lippuner
Last edited: September 2018
"""

import sys
import logging
from PyQt5.QtCore import (pyqtSlot)
from PyQt5.QtWidgets import (QMainWindow, QMenu, QToolTip, QMessageBox, QAction, QDesktopWidget, QApplication)
from PyQt5.QtGui import (QFont, QIcon)

from interface import InterfaceWidget
from connectionDialog import ConnectionDialog
from board import Board
from mockedBoard import MockedBoard

logging.basicConfig(level=logging.DEBUG)
logging.warning('Initialize …')


# Global variables
availableBoards = [MockedBoard(), Board('Beaglebone Black Wireless')]

class MainWindow(QMainWindow):
    """The main window of the application."""

    # The selected board
    _board = None

    # The connection ip
    _ip = None

    # The connection port
    _port = None


    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        # Setup UI
        self.initUI()

        # Create connection settings dialog
        self.connectionDialog = ConnectionDialog()
        self.connectionDialog.settingsChanged.connect(self._connectionSettingsChangedListener)

        # Load default board
        self.loadBoard(availableBoards[0].name())


    def initUI(self):
        """Initialize the ui of the main window."""
        # Initialize the window
        self.setWindowTitle('Wearable Software Interface')
        self.setWindowIcon(QIcon('assets/Face.png'))
        self.resize(600, 480)
        self.center()

        # Configure the menus
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        boardMenu = menubar.addMenu('&Board')

        # Configure the board selection menu
        selectMenu = QMenu('Select Board', self)
        for availableBoard in availableBoards:
            selectMenu.addAction(QAction(availableBoard.name(), self))
        selectMenu.triggered.connect(self._selectBoardListener)
        boardMenu.addMenu(selectMenu)

        # Configure the connection menu
        connectionAct = QAction('&Connect', self)
        connectionAct.setStatusTip('Connect')
        connectionAct.triggered.connect(self._connectListener)
        boardMenu.addAction(connectionAct)
        configureConnectionAct = QAction('&Configure Connection …', self)
        configureConnectionAct.setStatusTip('Configure connection settings')
        configureConnectionAct.triggered.connect(self._showConnectionDialogListener)
        boardMenu.addAction(configureConnectionAct)


        # Configure the exit menu option
        exitAct = QAction(QIcon('assets/Delete.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)
        boardMenu.addAction(exitAct)

        # Configure the status bar
        self.statusBar()

        # Set default font size for tooltips
        QToolTip.setFont(QFont('SansSerif', 10))

        # Configure the interface widget
        interface = InterfaceWidget()
        interface.configureConnectionClicked.connect(self._showConnectionDialogListener)
        interface.connect.connect(self._connectListener)
        self._interface = interface
        self.setCentralWidget(interface)


        # Show ready message when ui is loaded
        self.statusBar().showMessage('UI Ready')
        self.show()


    def loadBoard(self, name):
        """Load a board."""
        self._board = next((x for x in availableBoards if x.name() == name), None)

        # Throw for no board
        if (self._board == None):
            raise ValueError('board definition not found')

        # Update values from board configuration
        self._ip = self._board.defaultIp()
        self._port = self._board.defaultPort()
        self.updateUI()

        print('{} loaded'.format(name))






    def center(self):
        """Center the main window."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())




    def updateUI(self):
        """Update all ui elements."""
        self.updateStatusValues()
        self.updateDeviceList()

    def updateStatusValues(self):
        """Update all status values."""
        self._interface.setName(self._board.name())
        self._interface.setImage(self._board.name())
        self._interface.setIpAndPort(self._ip, self._port)
        if (self._board.connected()):
            self._interface.setStatus('Online')
        else:
            self._interface.setStatus('Offline')

    def updateDeviceList(self):
        """Update device lists."""
        self._interface.updateDeviceList(self._board.deviceList())







    def closeEvent(self, event):
        """Confirm closing application."""
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()










    @pyqtSlot()
    def _showConnectionDialogListener(self):
        """Show connection dialog."""
        self.connectionDialog.setValues(self._ip, self._port)
        self.connectionDialog.show()


    @pyqtSlot(str, str)
    def _connectionSettingsChangedListener(self, ip, port):
        """Update connection settings."""
        self._ip = ip
        self._port = port
        self.updateStatusValues()


    @pyqtSlot()
    def _connectListener(self):
        """Try to connect (fails at the moment per default)."""
        print("Abort connection trial")


    @pyqtSlot(QAction)
    def _selectBoardListener(self, action):
        """Select a board."""
        if (self._board.connected()):
            print('Deconnect the board') # TODO: Implement proper deconnection

        # Load selected board configuration
        self.loadBoard(action.text())











# Run main app
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
