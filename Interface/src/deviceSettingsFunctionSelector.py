# -*- coding: utf-8 -*-

import math
import logging
from PyQt5.QtCore import (Qt, pyqtSlot, pyqtSignal)
from PyQt5.QtWidgets import (QWidget, QLabel, QGridLayout, QComboBox, QStackedWidget, QDoubleSpinBox, QGroupBox, QVBoxLayout)


logging.basicConfig(level=logging.DEBUG)

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

    def __init__(self, dim):
        """Initialize the device settings function selection widget."""
        super().__init__()

        # Set dimension
        self._dim = dim

        # Pick default function
        self._function = allowedFunctions[0]
        self._parameters = {'a': 0, 'b': 0, 'lower': 0, 'upper': 100}

        # Initialize the device settings UI
        self.initUI()

        # Emit the default function
        self.functionChanged.emit(self._dim, self._function, self._parameters)

    def initUI(self):
        """Initialize the ui of the device settings function selection widget."""
        # Button for function selector menu
        functionSelectorMenu = QComboBox()
        for function in allowedFunctions:
            functionSelectorMenu.addItem(function)
        functionSelectorMenu.currentTextChanged.connect(self._onFunctionSelection)

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

        # Grid for the device settings layout
        bodyGridLayout = QGridLayout()
        bodyGridLayout.addWidget(functionSelectorMenu,           0, 0, Qt.AlignLeft)
        bodyGridLayout.addWidget(parameterSettingsStack,         1, 0, Qt.AlignLeft | Qt.AlignTop)

        bodyGridLayout.setRowStretch(0, 1)
        bodyGridLayout.setRowStretch(1, 10)

        self.setLayout(bodyGridLayout)


    @pyqtSlot(str)
    def _onFunctionSelection(self, function):
        """Select Function listener."""
        if (function in allowedFunctions):
            i = allowedFunctions.index(function)
            self._parameterSettingsStack.setCurrentWidget(self._parameterSettingsStack.widget(i))
            self._function = function
            self._parameters = {'a': 0, 'b': 0, 'lower': 0, 'upper': 100}
            self.functionChanged.emit(self._dim, self._function, self._parameters.copy())
        else:
            raise ValueError('Function {} is invalid'.format(function))

    @pyqtSlot(float)
    def _onSetParameterA(self, value):
        """Set parameter 'a' listener."""
        print("Set parameter 'a': {}".format(value))
        self._parameters['a'] = value
        self.functionChanged.emit(self._dim, self._function, self._parameters.copy())

    @pyqtSlot(float)
    def _onSetParameterB(self, value):
        """Set parameter 'b' listener."""
        print("Set parameter 'b': {}".format(value))
        self._parameters['b'] = min(max(value, self._parameters['lower']), self._parameters['upper']) # Limit at upper and lower
        self.functionChanged.emit(self._dim, self._function, self._parameters.copy())

    @pyqtSlot(float)
    def _onSetParameterBIgnoreBounds(self, value):
        """Set parameter 'b' listener but ignore bounds."""
        print("Set parameter 'b': {}".format(value))
        self._parameters['b'] = value
        self.functionChanged.emit(self._dim, self._function, self._parameters.copy())

    @pyqtSlot(float)
    def _onSetParameterLower(self, value):
        """Set parameter 'lower' listener."""
        print("Set parameter 'lower': {}".format(value))
        self._parameters['lower'] = min(value, self._parameters['upper']) # Limit at upper
        self.functionChanged.emit(self._dim, self._function, self._parameters.copy())

    @pyqtSlot(float)
    def _onSetParameterUpper(self, value):
        """Set parameter 'upper' listener."""
        print("Set parameter 'upper': {}".format(value))
        self._parameters['upper'] = max(value, self._parameters['lower']) # Limit at lower
        self.functionChanged.emit(self._dim, self._function, self._parameters.copy())

    def function(self):
        """Return the function and its parameters."""
        return self._dim, self._function, self._parameters.copy()
