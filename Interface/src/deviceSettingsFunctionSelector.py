# -*- coding: utf-8 -*-

import math
import logging
from PyQt5.QtCore import (Qt, pyqtSlot, pyqtSignal)
from PyQt5.QtWidgets import (QWidget, QLabel, QGridLayout, QComboBox, QStackedWidget, QDoubleSpinBox, QGroupBox, QVBoxLayout)


# Logging settings
LOG_LEVEL_PRINT = logging.INFO
LOG_LEVEL_SAVE = logging.DEBUG

# List of allowed functions
allowedFunctions = ['~','f(t) = a', 'f(t) = a * t + b', 'f(t) = rect((t - b) / a)', 'f(t) = tri((t - b) / a)', 'f(t) = b * (exp(- a * t) - 1)', 'f(t) = sin((2pi * t)/a + b)']


class DeviceSettingsFunctionSelectorWidget(QWidget):
    """
    Device Settings Widget Function Selector.

    Select functions to apply to an outgoing device
    """

    # Signal for function changes clicked
    functionChanged = pyqtSignal(int, str, dict)
    # Dimension
    _dim = None
    # Selected function
    _function = None
    # function parameters
    _parameters = None
    # widgets for function parameters
    _parameterWidgets = None
    # Logger module
    _logger = None

    def __init__(self, dim):
        """Initialize the device settings function selection widget."""
        super().__init__()

        # Configure the logger
        self._logger = logging.getLogger('DeviceSettingsFunctionSelector')
        self._logger.setLevel(LOG_LEVEL_PRINT)   # Only {LOG_LEVEL} level or above will be saved
        fh = logging.FileHandler('../Logs/DeviceSettingsFunctionSelector.log', 'w')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fh.setFormatter(formatter)
        fh.setLevel(LOG_LEVEL_SAVE)              # Only {LOG_LEVEL} level or above will be saved
        self._logger.addHandler(fh)

        self._logger.info("Device settings function selector initializing …")


        # Set dimension
        self._dim = dim

        # Pick default function
        self._function = allowedFunctions[0]
        self._parameters = {'a': 0, 'b': 0, 'lower': 0, 'upper': 100}

        # Initialize the device settings UI
        self.initUI()

        self._logger.info("Device settings function selector initialized")

        # Emit the default function
        self.functionChanged.emit(self._dim, self._function, self._parameters)

    def initUI(self):
        """Initialize the ui of the device settings function selection widget."""
        # Button for function selector menu
        functionSelectorMenu = QComboBox()
        for function in allowedFunctions:
            functionSelectorMenu.addItem(function)
        functionSelectorMenu.currentTextChanged.connect(self._onFunctionSelection)
        self._logger.debug("Device settings function selector UI selector created")

        # Stack of parameter settings
        parameterSettingsStack = QStackedWidget()
        self._parameterSettingsStack = parameterSettingsStack

        # Parameter settings (ordered by list of allowed functions)
        self._parameterWidgets = []
        # ~
        parameterSettingsLabel = QLabel('')
        parameterSettingsStack.addWidget(parameterSettingsLabel)
        self._parameterWidgets.append([])
        # f(t) = a
        parameterGroup = QGroupBox('Constant value')
        parameterGroupLayout = QVBoxLayout()
        parameterGroupLayout.addWidget(QLabel('a'))
        parameterABox = QDoubleSpinBox();
        parameterABox.setRange(-10000,10000)
        parameterABox.setSingleStep(0.01);
        parameterABox.setValue(0);
        parameterABox.valueChanged.connect(self._onSetParameterA)
        parameterGroupLayout.addWidget(parameterABox)
        parameterGroupLayout.addStretch(1)
        parameterGroup.setLayout(parameterGroupLayout)
        parameterSettingsStack.addWidget(parameterGroup)
        self._parameterWidgets.append([parameterGroup])
        # f(t) = a * t + b
        parameterGroup = QGroupBox('Linear bounded function')
        parameterGroupLayout = QVBoxLayout()
        parameterGroupLayout.addWidget(QLabel('a'))
        parameterABox = QDoubleSpinBox();
        parameterABox.setRange(-10000,10000)
        parameterABox.setSingleStep(0.01);
        parameterABox.setValue(0);
        parameterABox.valueChanged.connect(self._onSetParameterA)
        parameterGroupLayout.addWidget(parameterABox)
        parameterGroupLayout.addWidget(QLabel('b'))
        parameterBBox = QDoubleSpinBox();
        parameterBBox.setRange(-10000,10000)
        parameterBBox.setSingleStep(0.01);
        parameterBBox.setValue(0);
        parameterBBox.valueChanged.connect(self._onSetParameterB)
        parameterGroupLayout.addWidget(parameterBBox)
        parameterGroupLayout.addWidget(QLabel('upper'))
        parameterUpperBox = QDoubleSpinBox();
        parameterUpperBox.setRange(-10000,10000)
        parameterUpperBox.setSingleStep(0.01);
        parameterUpperBox.setValue(100);
        parameterUpperBox.valueChanged.connect(self._onSetParameterUpper)
        parameterGroupLayout.addWidget(parameterUpperBox)
        parameterGroupLayout.addWidget(QLabel('lower'))
        parameterLowerBox = QDoubleSpinBox();
        parameterLowerBox.setRange(-10000,10000)
        parameterLowerBox.setSingleStep(0.01);
        parameterLowerBox.setValue(0);
        parameterLowerBox.valueChanged.connect(self._onSetParameterLower)
        parameterGroupLayout.addWidget(parameterLowerBox)
        parameterGroupLayout.addStretch(1)
        parameterGroup.setLayout(parameterGroupLayout)
        parameterSettingsStack.addWidget(parameterGroup)
        self._parameterWidgets.append([parameterGroup])
        # f(t) = rect((t - b) / a)
        parameterGroup = QGroupBox('Rect function')
        parameterGroupLayout = QVBoxLayout()
        parameterGroupLayout.addWidget(QLabel('a'))
        parameterABox = QDoubleSpinBox();
        parameterABox.setRange(-10000,10000)
        parameterABox.setSingleStep(0.01);
        parameterABox.setValue(0);
        parameterABox.valueChanged.connect(self._onSetParameterA)
        parameterGroupLayout.addWidget(parameterABox)
        parameterGroupLayout.addWidget(QLabel('b'))
        parameterBBox = QDoubleSpinBox();
        parameterBBox.setRange(-10000,10000)
        parameterBBox.setSingleStep(0.01);
        parameterBBox.setValue(0);
        parameterBBox.valueChanged.connect(self._onSetParameterB)
        parameterGroupLayout.addWidget(parameterBBox)
        parameterGroupLayout.addWidget(QLabel('upper'))
        parameterUpperBox = QDoubleSpinBox();
        parameterUpperBox.setRange(-10000,10000)
        parameterUpperBox.setSingleStep(0.01);
        parameterUpperBox.setValue(100);
        parameterUpperBox.valueChanged.connect(self._onSetParameterUpper)
        parameterGroupLayout.addWidget(parameterUpperBox)
        parameterGroupLayout.addWidget(QLabel('lower'))
        parameterLowerBox = QDoubleSpinBox();
        parameterLowerBox.setRange(-10000,10000)
        parameterLowerBox.setSingleStep(0.01);
        parameterLowerBox.setValue(0);
        parameterLowerBox.valueChanged.connect(self._onSetParameterLower)
        parameterGroupLayout.addWidget(parameterLowerBox)
        parameterGroupLayout.addStretch(1)
        parameterGroup.setLayout(parameterGroupLayout)
        parameterSettingsStack.addWidget(parameterGroup)
        self._parameterWidgets.append([parameterGroup])
        # f(t) = tri((t - b) / a)
        parameterGroup = QGroupBox('Tri function')
        parameterGroupLayout = QVBoxLayout()
        parameterGroupLayout.addWidget(QLabel('a'))
        parameterABox = QDoubleSpinBox();
        parameterABox.setRange(-10000,10000)
        parameterABox.setSingleStep(0.01);
        parameterABox.setValue(0);
        parameterABox.valueChanged.connect(self._onSetParameterA)
        parameterGroupLayout.addWidget(parameterABox)
        parameterGroupLayout.addWidget(QLabel('b'))
        parameterBBox = QDoubleSpinBox();
        parameterBBox.setRange(-10000,10000)
        parameterBBox.setSingleStep(0.01);
        parameterBBox.setValue(0);
        parameterBBox.valueChanged.connect(self._onSetParameterB)
        parameterGroupLayout.addWidget(parameterBBox)
        parameterGroupLayout.addWidget(QLabel('upper'))
        parameterUpperBox = QDoubleSpinBox();
        parameterUpperBox.setRange(-10000,10000)
        parameterUpperBox.setSingleStep(0.01);
        parameterUpperBox.setValue(100);
        parameterUpperBox.valueChanged.connect(self._onSetParameterUpper)
        parameterGroupLayout.addWidget(parameterUpperBox)
        parameterGroupLayout.addWidget(QLabel('lower'))
        parameterLowerBox = QDoubleSpinBox();
        parameterLowerBox.setRange(-10000,10000)
        parameterLowerBox.setSingleStep(0.01);
        parameterLowerBox.setValue(0);
        parameterLowerBox.valueChanged.connect(self._onSetParameterLower)
        parameterGroupLayout.addWidget(parameterLowerBox)
        parameterGroupLayout.addStretch(1)
        parameterGroup.setLayout(parameterGroupLayout)
        parameterSettingsStack.addWidget(parameterGroup)
        self._parameterWidgets.append([parameterGroup])
        # f(t) = b * (exp(- a * t) - 1)
        parameterGroup = QGroupBox('Exponential function')
        parameterGroupLayout = QVBoxLayout()
        parameterGroupLayout.addWidget(QLabel('a'))
        parameterABox = QDoubleSpinBox();
        parameterABox.setRange(-10000,10000)
        parameterABox.setSingleStep(0.01);
        parameterABox.setValue(0);
        parameterABox.valueChanged.connect(self._onSetParameterA)
        parameterGroupLayout.addWidget(parameterABox)
        parameterGroupLayout.addWidget(QLabel('b'))
        parameterBBox = QDoubleSpinBox();
        parameterBBox.setRange(-1,1)
        parameterBBox.setSingleStep(0.01);
        parameterBBox.setValue(0);
        parameterBBox.valueChanged.connect(self._onSetParameterBIgnoreBounds)
        parameterGroupLayout.addWidget(parameterBBox)
        parameterGroupLayout.addWidget(QLabel('upper'))
        parameterUpperBox = QDoubleSpinBox();
        parameterUpperBox.setRange(-10000,10000)
        parameterUpperBox.setSingleStep(0.01);
        parameterUpperBox.setValue(100);
        parameterUpperBox.valueChanged.connect(self._onSetParameterUpper)
        parameterGroupLayout.addWidget(parameterUpperBox)
        parameterGroupLayout.addWidget(QLabel('lower'))
        parameterLowerBox = QDoubleSpinBox();
        parameterLowerBox.setRange(-10000,10000)
        parameterLowerBox.setSingleStep(0.01);
        parameterLowerBox.setValue(0);
        parameterLowerBox.valueChanged.connect(self._onSetParameterLower)
        parameterGroupLayout.addWidget(parameterLowerBox)
        parameterGroupLayout.addStretch(1)
        parameterGroup.setLayout(parameterGroupLayout)
        parameterSettingsStack.addWidget(parameterGroup)
        self._parameterWidgets.append([parameterGroup])
        # f(t) = sin((2pi * t)/a + b)
        parameterGroup = QGroupBox('Sinus function')
        parameterGroupLayout = QVBoxLayout()
        parameterGroupLayout.addWidget(QLabel('a'))
        parameterABox = QDoubleSpinBox();
        parameterABox.setRange(-10000,10000)
        parameterABox.setSingleStep(0.01);
        parameterABox.setValue(0);
        parameterABox.valueChanged.connect(self._onSetParameterA)
        parameterGroupLayout.addWidget(parameterABox)
        parameterGroupLayout.addWidget(QLabel('b'))
        parameterBBox = QDoubleSpinBox();
        parameterBBox.setRange(-2 * math.pi, 2 * math.pi)
        parameterBBox.setSingleStep(0.01);
        parameterBBox.setValue(0);
        parameterBBox.valueChanged.connect(self._onSetParameterBIgnoreBounds)
        parameterGroupLayout.addWidget(parameterBBox)
        parameterGroupLayout.addWidget(QLabel('upper'))
        parameterUpperBox = QDoubleSpinBox();
        parameterUpperBox.setRange(-10000,10000)
        parameterUpperBox.setSingleStep(0.01);
        parameterUpperBox.setValue(100);
        parameterUpperBox.valueChanged.connect(self._onSetParameterUpper)
        parameterGroupLayout.addWidget(parameterUpperBox)
        parameterGroupLayout.addWidget(QLabel('lower'))
        parameterLowerBox = QDoubleSpinBox();
        parameterLowerBox.setRange(-10000,10000)
        parameterLowerBox.setSingleStep(0.01);
        parameterLowerBox.setValue(0);
        parameterLowerBox.valueChanged.connect(self._onSetParameterLower)
        parameterGroupLayout.addWidget(parameterLowerBox)
        parameterGroupLayout.addStretch(1)
        parameterGroup.setLayout(parameterGroupLayout)
        parameterSettingsStack.addWidget(parameterGroup)
        self._parameterWidgets.append([parameterGroup])

        parameterSettingsStack.setCurrentWidget(parameterSettingsStack.widget(0))
        self._logger.debug("Device settings function selector UI stacked parameters created")

        # Grid for the device settings layout
        bodyGridLayout = QGridLayout()
        bodyGridLayout.addWidget(functionSelectorMenu,           0, 0, Qt.AlignLeft)
        bodyGridLayout.addWidget(parameterSettingsStack,         1, 0, Qt.AlignLeft | Qt.AlignTop)

        bodyGridLayout.setRowStretch(0, 1)
        bodyGridLayout.setRowStretch(1, 10)

        self.setLayout(bodyGridLayout)
        self._logger.debug("Device settings function selector UI layout created")


    @pyqtSlot(str)
    def _onFunctionSelection(self, function):
        """Select Function listener."""
        if (function in allowedFunctions):
            i = allowedFunctions.index(function)
            self._parameterSettingsStack.setCurrentWidget(self._parameterSettingsStack.widget(i))
            self._function = function
            self._parameters = {'a': 0, 'b': 0, 'lower': 0, 'upper': 100}
            self.functionChanged.emit(self._dim, self._function, self._parameters.copy())
            self._logger.info("Function '{}' selected with parameters: {}".format(self._function, str(self._parameters)))
        else:
            raise ValueError('Function {} is invalid'.format(function))

    @pyqtSlot(float)
    def _onSetParameterA(self, value):
        """Set parameter 'a' listener."""
        self._parameters['a'] = value
        self._logger.info("Parameter 'a' of function '{}' changed to {}".format(self._function, value))
        self.functionChanged.emit(self._dim, self._function, self._parameters.copy())

    @pyqtSlot(float)
    def _onSetParameterB(self, value):
        """Set parameter 'b' listener."""
        self._parameters['b'] = min(max(value, self._parameters['lower']), self._parameters['upper']) # Limit at upper and lower
        self._logger.info("Parameter ba' of function '{}' changed to {}".format(self._function, value))
        self.functionChanged.emit(self._dim, self._function, self._parameters.copy())

    @pyqtSlot(float)
    def _onSetParameterBIgnoreBounds(self, value):
        """Set parameter 'b' listener but ignore bounds."""
        self._parameters['b'] = value
        self._logger.info("Parameter 'b' of function '{}' changed to {}".format(self._function, value))
        self.functionChanged.emit(self._dim, self._function, self._parameters.copy())

    @pyqtSlot(float)
    def _onSetParameterLower(self, value):
        """Set parameter 'lower' listener."""
        self._parameters['lower'] = min(value, self._parameters['upper']) # Limit at upper
        self._logger.info("Parameter 'lower' of function '{}' changed to {}".format(self._function, value))
        self.functionChanged.emit(self._dim, self._function, self._parameters.copy())

    @pyqtSlot(float)
    def _onSetParameterUpper(self, value):
        """Set parameter 'upper' listener."""
        self._parameters['upper'] = max(value, self._parameters['lower']) # Limit at lower
        self._logger.info("Parameter 'upper' of function '{}' changed to {}".format(self._function, value))
        self.functionChanged.emit(self._dim, self._function, self._parameters.copy())

    def function(self):
        """Return the function and its parameters."""
        return self._dim, self._function, self._parameters.copy()
