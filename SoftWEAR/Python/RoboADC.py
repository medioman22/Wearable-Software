# -*- coding: utf-8 -*-
"""

"""

import mraa

# Translation between normal ADC inexes and the ones that mraa uses
idx2mraa = {0:1, 1:2, 2:3, 3:4, 4:5, 5:6, 6:7}

# Translation between string IDs and normal ADC indexes (to be translated to MRAA)
str2idx = {'P9_39':0, 'P9_40':1, 'P9_37':2, 'P9_38':3, 
            'P9_33':4, 'P9_36':5, 'P9_35':6}


class RoboADC:
    def __init__(self):
        self._pin_objects = []
        for pin in self.SCAN_PINS:
            scan_idx, mraa_idx = self.validate_pin(pin)
            if scan_idx is -1 or mraa_idx is -1:
                raise ValueError("Init Error: pin scan list is incorrect!")
            x = mraa.Aio(mraa_idx)
            self._pin_objects.append(x)
    
    def validate_pin(self, pin):
        """ Returns scan_idx, mraa_idx if succesful, -1, -1 if not"""
        idx = None
        try:    # Parse the input parameter
            if isinstance(pin, str):
                idx = str2idx[pin]      # Pin is in string format -> use dict
        except KeyError:       
            return -1, -1
        
        if not idx and isinstance(pin, int):
            idx = pin                   # If pin is already a number, save it
        
        if idx is None:     # If we don't have a index by now -> error
            return -1, -1
            
        try:
            mraa_idx = idx2mraa[idx]    # Convert index to mraa index
        except KeyError:
            return -1, -1
        
        try:            # Get the scan index from the 
            scan_idx = self.SCAN_PINS.index(idx)            
        except ValueError:
            return -1, mraa_idx
        
        return scan_idx, mraa_idx
    
    def get_mv(self, pin):
        scan_idx, mraa_idx = self.validate_pin(pin)
        
        if mraa_idx is -1:
            raise ValueError("Parameter error: pin should either be a number 0-6 or a string(e.g. P9_39)")
        if scan_idx is -1:
            raise ValueError("Parameter error: pin is correct but is not on the list of initialized pins")
        
        return 1.8 * self._pin_objects[scan_idx].readFloat()
    
    def get_all_mv(self):
        ret = []
        for pin in self.SCAN_PINS:
            ret.append(self.get_mv(pin))
        return ret
    
    def update_connected_devices(self):
        """ Updates the connected devices dictionary list. Returns the connect /
            disconnect message along with a new list of dictionaries on the form 
            of {'chn', 'event':'disc'/'conn'}"""
        milivolts = self.get_all_mv()
        ret_message = ""
        ret_list = []
        to_delete = []
        to_add = []
        to_confirm = []
        for scan_idx, mv_val in enumerate(milivolts):   # Go through all scan channels
            c_chn = self.SCAN_PINS[scan_idx]
            try:    # Try and get existing connected device index
                conn_idx = next((index for (index, d) in enumerate(self.connected_devices) if d["chn"] == c_chn))
                if mv_val <= 0.005:     # Reading of 0 on an existing channel
                    self.connected_devices[conn_idx]['cnt'] -= 1        # Decrease counter value
                    if self.connected_devices[conn_idx]['cnt'] == 0:    # If 0 -> delete element
                        to_delete.append(self.connected_devices[conn_idx])
                elif self.connected_devices[conn_idx]['actv'] is True:  # If != 0 on an active chn -> reset ticks
                    self.connected_devices[conn_idx]['cnt'] = self.timeout_ticks
                    self.connected_devices[conn_idx]['val'] = mv_val
                elif self.connected_devices[conn_idx]['actv'] is False:
                    self.connected_devices[conn_idx]['cnt'] += 1        # If != 0 on an unconfirmed chn -> incr. ticks
                    self.connected_devices[conn_idx]['val'] = mv_val
                    if self.connected_devices[conn_idx]['cnt'] == self.timeout_ticks:
                        to_confirm.append(self.connected_devices[conn_idx])
                        self.connected_devices[conn_idx]['actv'] = True # Set chn to active, add to confirm list
            except: # Fail -> we don't have an existing channel -> add it!
                to_add.append({'chn':c_chn, 'val':mv_val, 'cnt':1, 'actv':False})
                
        for elem in to_delete:
            if elem['actv'] is True:
                ret_message += "Disconnected ADC on channel " + str(elem['chn']) + "\n"
                ret_list.append({'chn':elem['chn'], 'event':'disc'})
            conn_idx = next((index for (index, d) in enumerate(self.connected_devices) if d["chn"] == elem['chn']))
            del self.connected_devices[conn_idx]    # Delete element
            
        for elem in to_add:
            self.connected_devices.append(elem)            
            
        for elem in to_confirm:
            ret_message += "Connected new ADC on channel " + str(elem['chn']) + "\n"
            ret_list.append({'chn':elem['chn'], 'event':'conn'})
        return ret_message, ret_list
        
        
    """ List of scan pins to be initialized. SHOULD BE CONSTAT THROUGHT EXECUTION """
    SCAN_PINS = [0, 1, 2]
    
    """ List of all initialized pin objects. Created from the list of scan pins. """
    _pin_objects = []
    
    """ List of connected devices dictionary. Contains: {chn, val, cnt, actv} """
    connected_devices = []
    
    """ Number of ticks for a timeout. If the output is 0 for more ticks than 
        this value, the devices is considered disconnected. """
    timeout_ticks = 5
