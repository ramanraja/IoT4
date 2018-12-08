# MLX90640 library wrapper

# for original python library:
# pip install MLX90640
# https://github.com/pimoroni/mlx90640-library/tree/master/python

from __future__ import print_function 
import MLX90640  as mlx
from time import sleep
import numpy as np
import threading

FRAME_LENGTH = 768        # 24x32 pixels
MAX_WAIT_CYCLES = 20      # Rx data timeout, in units of 100 mSec

class I2CReceiver (threading.Thread):
       
    def open(self, fps):
        mlx.setup(fps)
        self.terminate = False
        self.data_ready = False
        self.acquire_mode = True
        self.empty_array = np.array([])
        self.primary_buffer = np.zeros(FRAME_LENGTH, dtype=float)    
        self.secondary_buffer = np.zeros(FRAME_LENGTH, dtype=float)      
        return True
    
    
    def close(self):
        self.terminate = True
        mlx.cleanup()
        print ("MLX sensor closed.")   
        
                
    def requestData(self):
        self.acquire_mode = True  # just for safety; this is best placed in getData()
        
    
    def getData(self):    
        attempts = 0;
        while (not self.data_ready):
            sleep(0.1)
            attempts += 1
            if (attempts > MAX_WAIT_CYCLES):
                return (self.empty_array)   
                
        self.secondary_buffer = self.primary_buffer.copy()
        self.data_ready = False  
        self.acquire_mode = True
        return (self.secondary_buffer)
    
     
    def run(self): 
        while not self.terminate:
            try:
                if (not self.acquire_mode):
                    sleep(0)
                    continue
                self.primary_buffer = mlx.get_frame()
                self.acquire_mode = False                
                self.data_ready = True
            except Exception as e:
                print(e)    
                