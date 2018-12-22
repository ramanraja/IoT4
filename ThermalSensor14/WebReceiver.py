# Receives MLX90640 data packet from web server
# It works through a ON-OFF flow control system: receives a packet in the 
# background, and waits for the next rquest from UI client. 
# To speed up, it uses double buffering

#from __future__ import print_function 
from time import sleep
import numpy as np
import threading
import requests

ERROR_RECOVERY_PERIOD = 1.0   # sleep after a failed attempt to fetch data
FRAME_LENGTH = 768            # 24x32 pixels
NUM_BUF = 3

DEFAULT_URL = 'http://127.0.0.1:5000/'

class WebReceiver (threading.Thread):
       
    def open(self, sensorURL = DEFAULT_URL):
        self.setDaemon(True)
        self.terminate = False
        self.in_waiting = False
        self.sensor_url = sensorURL
        self.datastr = "place holder"
        self.empty_array = np.array([])
        self.buffers = np.zeros((NUM_BUF, FRAME_LENGTH), dtype=float)    
        self.write_buffer = 0   # where you are filling new data     
        self.read_buffer = (self.write_buffer + NUM_BUF-1) % NUM_BUF
        print ("Web Receiver opened.")  
        return True
    
    
    def close(self):
        self.terminate = True
        print ("Web Receiver closed.")   
        
                
    def getData(self):    
        self.in_waiting = True    #  ask for the next packet
        return (self.buffers[self.read_buffer])
    
    
    def validate_and_store(self):
        temp_data = [float(n) for n in self.datastr.split()]
        if (len(temp_data) != FRAME_LENGTH):
            print ('--- Data length error ---')
            self.buffers[self.write_buffer] = self.empty_array
            return               
        self.buffers[self.write_buffer, : ] = temp_data    # copy

                         
    def run(self): 
        print ('Web receiver thread starts...')
        while not self.terminate:
            try:
                if (not self.in_waiting): # not expecting any data at the moment
                    sleep(0)  # equivalent to yielding CPU time
                    continue            
                response = requests.get(self.sensor_url)  
                if (response.status_code >= 200 and response.status_code < 300):
                    self.datastr = response.text
                    self.validate_and_store()
                    self.write_buffer = (self.write_buffer+1) % NUM_BUF
                    self.read_buffer =  (self.write_buffer + NUM_BUF-1) % NUM_BUF 
                    self.in_waiting = False
                else:
                    print ("HTTP error: {}".format(response.status_code))
                    self.buffers[self.read_buffer] = self.empty_array
                    slep(ERROR_RECOVERY_PERIOD)  # do not flood the server
            except Exception as e:
                print(e)   
        print ('Web receiver thread exits.') 
              
       
#----------------------------------------------------------------------------- 
# MAIN
#----------------------------------------------------------------------------- 

def main():
    # address of the HTTP server with the sensor
    senurl = 'http://127.0.0.1:5000/'  
    FRAME_DELAY = 3.0
    
    web = WebReceiver()
    web.open(senurl)
    web.start()
    
    print ("Press CTRL+C to quit...")
    
    while True:
        try :
            dat = web.getData()
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
    
    web.close()
    sleep (1.0)
    print("Main thread exits.") 

if __name__ == "__main__":
    main()  
                