# -*- coding: utf-8 -*-
"""

"""

import mraa
import RoboMUX as mux

# Translation between normal ADC inexes and the ones that mraa uses
idx2mraa = {0:1, 1:2, 2:3, 3:4, 4:5, 5:6, 6:7}

# Translation between string IDs and normal ADC indexes (to be translated to MRAA)
str2idx = {'P9_39':0, 'P9_40':1, 'P9_37':2, 'P9_38':3, 
            'P9_33':4, 'P9_36':5, 'P9_35':6}


class RoboADC:
    def __init__(self):
        self._pin_objects = []
        self._mux_object = mux.RoboMUX()
        for pin in self.SCAN_PINS:
            scan_idx, mraa_idx = self.validate_pin(pin)
            if scan_idx is -1 or mraa_idx is -1:
                raise ValueError("Init Error: pin scan list is incorrect!")
            x = mraa.Aio(mraa_idx)
            
            self._pin_objects.append(x)
            if self.SCAN_PINS_MUX[scan_idx] is not None:
                self._mux_object.add_mux_slot('ADC', pin, self.SCAN_PINS_MUX[scan_idx][:3], self.SCAN_PINS_MUX[scan_idx][-1])
            self.all_devices.append({'chn':pin, 'val':0, 'cnt':0, 'actv':False, 'sublist':[]})
            
    
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
            ret.append(self._mux_object.get_muxed_values(pin, self.get_mv, pin))
        return ret
    
    def _update_channel(self, chn, val):
        """ Updates a specific channel with a milivolt value. If the milivolt value is a list,
            as would be the case for a MUX, the subchannels are updated accordingly.
            Returns a message list of the type: {'chn', 'subchn', 'event':'disc'/'conn'/'none', 'mux':'disc'/'conn'/'none'}"""
        chn_idx = next((index for (index, d) in enumerate(self.all_devices) if d["chn"] == chn))
        c_dict = self.all_devices[chn_idx]
        ret_list = []
        if isinstance(val, list):
            c_dict['val'] = -1     # Since val is a list -> update the dict 
            c_dict['actv'] = False # Reset the 'actv' value
            mux_con_flag = False
            for val_idx, val_mv in enumerate(val):
                try:    # Try and get the dictionary of the MUXed value index
                    sbchn_idx = next((index for (index, d) in enumerate(c_dict['sublist']) if d["subchn"] == val_idx))
                    sbchn_dict = c_dict['sublist'][sbchn_idx] # Get the subchannel dictionanry
                    sbchn_dict['val'] = val_mv
                    if val_mv <= 0.005 and sbchn_dict['cnt'] > 0:
                        sbchn_dict['cnt'] -= 1          # Decrease counter value
                        if sbchn_dict['cnt'] == 0 and sbchn_dict['actv']:
                            sbchn_dict['actv'] = False  # Disable channel if the counter reached 0
                            ret_list.append({'chn':chn, 'subchn':sbchn_idx, 'event':'disc', 'mux':'none'})
                    elif val_mv >= 0.005 and sbchn_dict['cnt'] < self.timeout_ticks:
                        sbchn_dict['cnt'] += 1          # Increment counter value
                        if sbchn_dict['cnt'] == self.timeout_ticks and sbchn_dict['actv'] == False:
                            sbchn_dict['actv'] = True  # Enable channel if the counter reached the threshold
                            ret_list.append({'chn':chn, 'subchn':sbchn_idx, 'event':'conn', 'mux':'none'})
                    if sbchn_dict['actv'] == True:      # For any active subchannel, the channel is active
                        c_dict['actv'] = True
                except: # We don't have a dictionary for the MUXed value yet
                    c_dict['sublist'].append({'chn':chn, 'subchn':val_idx, 'val':val_mv, 'cnt':1, 'actv':False})
                    mux_con_flag = True
            if mux_con_flag:    # Return MUX connected event
                ret_list.append({'chn':chn, 'subchn':-1, 'event':'none', 'mux':'conn'})
        else:
            if len(c_dict['sublist']) > 0: # Return MUX disconnected event
                ret_list.append({'chn':chn, 'subchn':-1, 'event':'none', 'mux':'disc'})
            c_dict['sublist'] = []  # Since no MUX connected -> we have no sublist
            c_dict['val'] = val     # Since val is a value -> update it
            
            if val <= 0.005 and c_dict['cnt'] > 0:     # Reading of 0 on an existing channel with cnt > 0
                c_dict['cnt'] -= 1          # Decrease counter value
                if c_dict['cnt'] == 0 and c_dict['actv']:
                    c_dict['actv'] = False  # Disable channel if the counter reached 0
                    ret_list.append({'chn':chn, 'subchn':-1, 'event':'disc', 'mux':'none'})
            elif val >= 0.005 and c_dict['cnt'] < self.timeout_ticks:
                c_dict['cnt'] += 1          # Increment counter value
                if c_dict['cnt'] == self.timeout_ticks and c_dict['actv'] == False:
                    c_dict['actv'] = True  # Enable channel if the counter reached the threshold
                    ret_list.append({'chn':chn, 'subchn':-1, 'event':'conn', 'mux':'none'})
        return ret_list
                    
    
    def update_devices(self):
        """ Updates the connected devices dictionary list. Returns a new list of 
        dictionaries on the form of {'chn', 'subchn', 'event':'disc'/'conn'/'none', 'mux':'disc'/'conn'/'none'}"""
        ret_list = []
        milivolts = self.get_all_mv()        
        for scan_idx, mv_val in enumerate(milivolts):   # Go through all scan channels and update them
            chn = self.SCAN_PINS[scan_idx]              # Get the pin channel from the scan index
            new_elems = self._update_channel(chn, mv_val)
            ret_list += new_elems
            
        self.connected_devices = []     # Update connected devices - start by clearing previous results
        for elem in self.all_devices:
            if elem['actv']:
                if len(elem['sublist']) > 0:
                    for sub_elem in elem['sublist']:
                        if sub_elem['actv']:
                            self.connected_devices.append({'chn':sub_elem['chn'], 'subchn':sub_elem['subchn'], 'val':sub_elem['val'], 'cnt':sub_elem['cnt'], 'actv':True})
                else:
                    self.connected_devices.append({'chn':elem['chn'], 'subchn':-1, 'val':elem['val'], 'cnt':elem['cnt'], 'actv':True})
        
        return ret_list
        
        
    """ List of scan pins to be initialized. SHOULD BE CONSTAT THROUGHT EXECUTION """
    SCAN_PINS = [0, 1, 2]
    
    """ Set here the MUX pins for each scan pin. Mux pins are(in order): A, B, C, detect """
    SCAN_PINS_MUX = [None, ["P8_41", "P8_42", "P8_43", "P8_44"], None]
    
    """ The MUX object for the ADC. """
    _mux_object = None
    
    """ List of all initialized pin objects. Created from the list of scan pins. """
    _pin_objects = []
    
    """ List of connected devices dictionary. Contains: {chn, subchn, val, cnt, actv}.
        Subchannel is -1 in case no MUX is connected. """
    connected_devices = []
    
    """ List of all devices dictionary. Contains: {chn, val, cnt, actv, sublist}. Val is -1 for MUXed channels.
        Sublist is a list of dictionaries for all MUXed values: {subchn, val, cnt, actv}"""
    all_devices = []
    
    """ Number of ticks for a timeout. If the output is 0 for more ticks than 
        this value, the devices is considered disconnected. """
    timeout_ticks = 5
