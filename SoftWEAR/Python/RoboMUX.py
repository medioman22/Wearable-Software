# -*- coding: utf-8 -*-
"""
"""
import mraa
import RoboUtil as util

class RoboMUX:
    class MUX:
        def __init__(self, peripheral, channel, select_pins, detect_pin):
            """ The select pins are from LSB to MSB [A, B, C]  """           
            
            self.peripheral = peripheral
            self.chn = channel
            if len(select_pins) is not 3:
                raise ValueError("Parameter error: the MUX need exactly 3 select pins")
            
            """ Init first select pin as output, and put it to 0 """
            self._pin_a = mraa.Gpio(util.gpio2mraa[select_pins[0]])
            self._pin_a.dir(mraa.DIR_OUT)
            self._pin_a.write(0)
            
            """ Init second select pin as output, and put it to 0 """
            self._pin_b = mraa.Gpio(util.gpio2mraa[select_pins[1]])
            self._pin_b.dir(mraa.DIR_OUT)
            self._pin_b.write(0)
            
            """ Init third select pin as output, and put it to 0 """
            self._pin_c = mraa.Gpio(util.gpio2mraa[select_pins[2]])
            self._pin_c.dir(mraa.DIR_OUT)
            self._pin_c.write(0)
            
            """ Init the detect pin and set it as input """
            self._pin_detect = mraa.Gpio(util.gpio2mraa[detect_pin])
            self._pin_detect.dir(mraa.DIR_IN)
        
        def __del__(self):
            pass
        
        def select(self, mux_chn):
            if mux_chn < 0 or mux_chn > 7:
                raise ValueError("Parameter error: the MUX has only 8 channels (0-7)")
            if mux_chn & 4 == 4:
                self._pin_c.write(1)
            else:
                self._pin_c.write(0)
                
            if mux_chn & 2 == 2:
                self._pin_b.write(1)
            else:
                self._pin_b.write(0)
                
            if mux_chn & 1 == 1:
                self._pin_a.write(1)
            else:
                self._pin_a.write(0)
                
        def isMuxConnected(self):
            return self._pin_detect.read()
             
        """ The mraa pin objects used by the MUX. """
        _pin_a = None           # The LSB select pin
        _pin_b = None
        _pin_c = None           # The MSB select pin
        _pin_detect = None      # The detect pin
                
        """ Peripheral type. Can be: ADC, I2C, UART, SPI """
        peripheral = ''
        
        """ Channel of the connected peripheral. """
        chn = '0'
        
    def __init__(self):
        pass
    
    def __del__(self):
        pass
    
    def add_mux_slot(self, peripheral, channel, select_pins, detect_pin):
        if peripheral not in ['ADC', 'I2C', 'UART', 'SPI' ]:
            raise ValueError("Parameter error: peripheral should be ADC, I2C, UART or SPI") 
        for pin in select_pins:
            if pin not in util.gpio2mraa:
                raise ValueError("Parameter error: Pin is not a valid GPIO pin")
            if pin in util.UsedGPIO.pin_list:
                raise ValueError("Parameter error: Pin is already used elsewhere")
        if detect_pin not in util.gpio2mraa:
            raise ValueError("Parameter error: Pin is not a valid GPIO pin")
        if detect_pin in util.UsedGPIO.pin_list:
            raise ValueError("Parameter error: Pin is already used elsewhere")
        
        if self._peripheral == '':
            self._peripheral = peripheral
        elif self._peripheral != peripheral:
            raise RuntimeError("Cannot mix MUX peripherals in the same class!")
        
        new_mux = self.MUX(peripheral, channel, select_pins, detect_pin)
        self._mux_list.append(new_mux)
            
    def get_muxed_values(self, channel, func, *args, **kwargs):
        """ Calls the given function with all the arguments and returns a list
            of all the return values. If no Mux connected, just returns the 
            func result. """
        c_mux = [mux for mux in self._mux_list if mux.chn == channel]
        
        if len(c_mux) > 1:  # If more than 1 MUX -> signal error
            raise RuntimeError("The " + self._peripheral + " channel " + str(channel) + " has too many MUX objects!")
        if len(c_mux) == 0: # If no MUX -> execute and return the function
            return func(*args, **kwargs)
            
        c_mux = c_mux[0]
        
        ret = []
        if not c_mux.isMuxConnected():
            return func(*args, **kwargs)
            
        for idx in range(0,8):
            c_mux.select(idx)
            ret.append(func(*args, **kwargs))
        return ret
                                
    _mux_list = []
    
    _peripheral = ''
