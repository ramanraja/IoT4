# MLX90640 library multi threaded wrapper
# uses N-fold buffers 

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
NUM_BUF = 5               # number of buffers
MIN_TEMP = 2
MAX_TEMP = 60
MAX_PIXEL_ERRORS = 10
REPAIR_VALUE = 28         # todo: revisit this

class I2CReceiver (threading.Thread):
       
    def open(self, fps):
        mlx.setup(fps)
        self.terminate = False
        self.empty_array = np.array([])
        self.buffers = np.zeros((NUM_BUF, FRAME_LENGTH), dtype=float)    
        self.current_buffer = 0   # where you are filling new data       
        return True
    
    
    def close(self):
        self.terminate = True
        mlx.cleanup()
        print ("MLX sensor closed.")   
        
                
    def getData(self):    
        # (current_buffer-1) mod NUM_BUF has the latest data
        read_buffer = (self.current_buffer + NUM_BUF-1) % NUM_BUF  
        return (self.buffers[read_buffer])
    
    
    def validate(self):
        num_errors = 0
        for (i in range FRAME_LENGTH):
            pix = self.buffers[self.current_buffer, i]
            if (np.isnan(pix) or pix < MIN_TEMP or pix > MAX_TEMP):
                self.buffers[self.current_buffer, i] = REPAIR_VALUE
                num_errors += 1
                if (num_errors > MAX_PIXEL_ERRORS):
                    print("----> Too many pixel errors.")
                    self.buffers[self.current_buffer] = self.empty_array
                    return
                         
                         
    def run(self): 
        while not self.terminate:
            try:
                self.buffers[self.current_buffer] = mlx.get_frame()
                self.validate()
                self.current_buffer = (self.current_buffer+1) % NUM_BUF
            except Exception as e:
                print(e)    
                