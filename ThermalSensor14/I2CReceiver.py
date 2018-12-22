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
        self.setDaemon(True)
        self.terminate = False  
        
        mlx.setup(fps)   # initialize the sensor

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
        for i in range (FRAME_LENGTH):
            pix = self.buffers[self.current_buffer, i]
            if (np.isnan(pix) or pix < MIN_TEMP or pix > MAX_TEMP):
                self.buffers[self.current_buffer, i] = REPAIR_VALUE
                num_errors += 1
                if (num_errors > MAX_PIXEL_ERRORS):
                    print("----> Too many pixel errors.")
                    self.buffers[self.current_buffer] = self.empty_array
                    return
                         
                         
    def run(self): 
        print("I2C receiver thread starts.")
        while not self.terminate:
            try:
                self.buffers[self.current_buffer] = mlx.get_frame()
                self.validate()
                self.current_buffer = (self.current_buffer+1) % NUM_BUF
            except Exception as e:
                print(e)    
        print("I2C receiver thread exits.")
                
                
#----------------------------------------------------------------------------- 
# MAIN
#----------------------------------------------------------------------------- 

def main():
    FPS = 2
    FRAME_DELAY = 5.0
    ERROR_RECOVERY_PERIOD = 5.0
    
    i2c = I2CReceiver()
    i2c.open(FPS)
    i2c.start()
    
    print ("Press CTRL+C to quit...")
    
    while True:
        try :
            dat = i2c.getData()
            if (len(dat) == 0):
                print(" --->>> could not contact sensor")
                sleep(ERROR_RECOVERY_PERIOD)
            else:
                print (dat[1:10])    
            sleep (FRAME_DELAY)
        except KeyboardInterrupt:
            print ("CTRL+C pressed.")
            break
        except Exception as e:
            print(e)            
    
    i2c.close()
    sleep (1.0)
    print("Main thread exits.") 

if __name__ == "__main__":
    main()  
                            