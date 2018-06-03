# -*- coding: utf-8 -*-
"""
SoftWEAR I2C module. Adds MUX features and hardware detection to normal I2C 
capabilities of the underlying mraa library.
"""
import RoboMUX as mux  # SoftWEAR MUX class. 
import I2C_BNO055      # SoftWEAR driver for the BNO055 device
import I2C_MPU6050     # SoftWEAR driver for the MPU6050 device

class RoboI2C:
    def __init__(self):
        """ Class constructor of the SoftWEAR I2C. Initializes the device drivers
            and the MUX object associated with I2C. """
        self._scan_driver_objects = []      # Init the driver collection list 
        self.connected_devices = []         # Init the connected decives list
        self._mux_object = mux.RoboMUX()    # Init the MUX object
        
        for idx, chn in enumerate(self.SCAN_CHNS):
            driver_obj_list = []            # Init the list of driver objects
            
            if self.SCAN_CHNS_MUX[idx] is not None: # Create and add MUX object on the channel
                self._mux_object.add_mux_slot('I2C', chn, self.SCAN_CHNS_MUX[idx][:3], self.SCAN_CHNS_MUX[idx][-1])
            
            """ Create the object for driver of BNO055 """
            bno055 = I2C_BNO055.BNO055(chn, ADR_set=False)  
            driver_obj_list.append(bno055)  # Add the BNO055 device driver to list
            
            mpu6050 = I2C_MPU6050.MPU6050(chn, ADR_set=False)
            driver_obj_list.append(mpu6050) # Add the MPU6050 device driver to list
            
            # TODO: add more driver objects here
            
            # Add the object list to the channel collection
            self._scan_driver_objects.append(driver_obj_list)
            
            # Create the entry for this channel dictionary
            self.all_devices.append({'chn':chn, 'device':'', 'vals':[], 'actv':False, 'sublist':[], 'drv_idx':-1})
    
    def _update_channel(self, chn_dict, subchn_dict):
        """ Updates the device with a given channel dictionary and subchannel dictionary. 
            If subchannel is None, then we don't have any MUX attached. Returns a new list of 
            dictionaries on the form of {'chn', 'subchn', 'event':'disc'/'conn'/'none', 'device':device/'', 'mux':'disc'/'conn'/'none'}"""
        ret_list = []
        chn_idx = next((index for (index, d) in enumerate(self.SCAN_CHNS) if d == chn_dict['chn']))
        
        if subchn_dict is not None:                # See if we have a MUX
            if subchn_dict['actv']:                # Check if device is connected
                drv_obj = self._scan_driver_objects[chn_idx][subchn_dict['drv_idx']]
                if self._mux_object.func_on_mux_chn(chn_dict['chn'], subchn_dict['subchn'], drv_obj.getDeviceConnected):
                    # If still connected, get the updated values and save them
                    subchn_dict['vals'] = self._mux_object.func_on_mux_chn(chn_dict['chn'], subchn_dict['subchn'], drv_obj.getAcceleractionXYZ)
                else:   # If no longer connected -> reflect change
                    subchn_dict['actv'] = False
                    chn_dict['actv'] = False        # Init channel active to False
                    for subdict in chn_dict['sublist']:
                        if subdict['actv'] == True: # If we find an active subchannel
                            chn_dict['actv'] = True # Revert channel active to True
                    subchn_dict['drv_idx'] = -1     # Reset the driver index to -1
                    subchn_dict['vals'] = []        # Reset the values to the empty list
                    subchn_dict['device'] =''       # Reset the device to an empty string
                    ret_list.append({'chn':chn_dict['chn'], 'subchn':subchn_dict['subchn'], 'event':'disc', 'device':chn_dict['device'], 'mux':'none'})
            else:                                   # No MUX connected
                for drv_idx, drv in enumerate(self._scan_driver_objects[chn_idx]):  # Try all available drivers
                    if self._mux_object.func_on_mux_chn(chn_dict['chn'], subchn_dict['subchn'], drv.getDeviceConnected):  # If any driver works
                        drv.ConfigureDevice()       # Configure the device and save driver & vals
                        subchn_dict['vals'] = self._mux_object.func_on_mux_chn(chn_dict['chn'], subchn_dict['subchn'], drv.getAcceleractionXYZ)
                        subchn_dict['device'] = self._mux_object.func_on_mux_chn(chn_dict['chn'], subchn_dict['subchn'], drv.getDevice)
                        subchn_dict['drv_idx'] = drv_idx
                        subchn_dict['actv'] = True
                        chn_dict['actv'] = True
                        ret_list.append({'chn':chn_dict['chn'], 'subchn':subchn_dict['subchn'], 'event':'conn', 'device':chn_dict['device'], 'mux':'none'})
        else:           # Treat channel without MUX
            if chn_dict['actv']:                # Check if device is connected
                drv_obj = self._scan_driver_objects[chn_idx][chn_dict['drv_idx']]
                if drv_obj.getDeviceConnected():
                    # If still connected, get the updated values and save them
                    chn_dict['vals'] = drv_obj.getAcceleractionXYZ()
                else:   # If no longer connected -> reflect change
                    chn_dict['actv'] = False
                    chn_dict['drv_idx'] = -1        # Reset the driver index to -1
                    chn_dict['vals'] = []           # Reset the values to the empty list
                    chn_dict['device'] =''          # Reset the device to an empty string
                    ret_list.append({'chn':chn_dict['chn'], 'subchn':-1, 'event':'disc', 'device':chn_dict['device'], 'mux':'none'})
            else:       # Not connected channel -> check for any new connections
                for drv_idx, drv in enumerate(self._scan_driver_objects[chn_idx]):  # Try all available drivers
                    if drv.getDeviceConnected():            # If any driver works
                        drv.ConfigureDevice()               # Configure the device and save driver & vals
                        chn_dict['vals'] = drv.getAcceleractionXYZ()
                        chn_dict['device'] = drv.getDevice()
                        chn_dict['drv_idx'] = drv_idx
                        chn_dict['actv'] = True
                        ret_list.append({'chn':chn_dict['chn'], 'subchn':-1, 'event':'conn', 'device':chn_dict['device'], 'mux':'none'})
        return ret_list
        
    def update_devices(self):
        """ Updates the connected devices dictionary list. Returns a new list of 
        dictionaries on the form of {'chn', 'subchn', 'event':'disc'/'conn'/'none', 'device':device/'', 'mux':'disc'/'conn'/'none'}"""
        ret_list = []
        for idx, chn in enumerate(self.SCAN_CHNS):
            c_device = self.all_devices[idx]        # Go thtough all I2C channels
            if self._mux_object.get_mux_connected(chn):     # Check if MUX connected
                for sbchn in range(0,8):            # Go through all MUX subchannels
                    try:  # Try and get the dictionary of the MUXed value index
                        sbchn_idx = next((index for (index, d) in enumerate(c_device['sublist']) if d["subchn"] == sbchn))
                        subdevice = c_device['sublist'][sbchn_idx]
                    except: # We don't have a dictionary for the MUXed value yet -> add a default one
                        subdevice = {'subchn':sbchn, 'vals':[], 'actv':False, 'drv_idx':-1, 'device':''}
                        c_device['sublist'].append(subdevice)
                    # Call the update function
                    ret_list += self._update_channel(c_device, subdevice)
            else:
                if len(c_device['sublist']) > 0:    # If first execution after MUX disconnect
                    c_device['actv'] = False        # Mark device as inactive
                    c_device['drv_idx'] = -1
                    c_device['vals'] = []
                    c_device['device'] =''
                c_device['sublist'] = []
                
                # Call the update function
                ret_list += self._update_channel(c_device, None)  
                        
        self.connected_devices = []     # Update connected devices - start by clearing previous results
        for elem in self.all_devices:
            if elem['actv']:
                if len(elem['sublist']) > 0:
                    for sub_elem in elem['sublist']:
                        if sub_elem['actv']: 
                            self.connected_devices.append({'chn':elem['chn'], 'subchn':sub_elem['subchn'],'device':sub_elem['device'], 'vals':sub_elem['vals'], 'drv_idx':sub_elem['drv_idx']})
                else:
                    self.connected_devices.append({'chn':elem['chn'], 'subchn':-1, 'device':elem['device'], 'vals':elem['vals'], 'drv_idx':elem['drv_idx']})
        return ret_list
            
    
    """ List of scan I2C channels where devices will connect to"""
    SCAN_CHNS = [1]
    
    """ Set here the MUX pins for each scan Channel. Mux pins are(in order): A, B, C, detect """
    SCAN_CHNS_MUX = [["P8_29", "P8_30", "P8_31", "P8_32"]]
    
    """ The MUX object for the I2C. """
    _mux_object = None
    
    """ Each channel will have a list of driver objects. These objects will be 
        used to detect & use devices """
    _scan_driver_objects = None
    
    """ List of connected devices dictionary. Contains: {chn, subchn, device, vals, drv_idx}.
        Subchannel is -1 in case no MUX is connected. """
    connected_devices = []
    
    """ List of all 'devices' dictionary. Contains: {chn, device, vals, actv, sublist, drv_idx}
        Sublist is a list of dictionaries for all MUXed values: {subchn, device, vals, actv, drv_idx}"""
    all_devices = []