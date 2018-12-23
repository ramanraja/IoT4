# streams MLX90640 data to HTTP clients

#from __future__ import print_function
from numpy import percentile
import I2CReceiver as i2cr
from flask import Flask
from time import sleep
import numpy as np
import pickle
import math
import time
import sys
 
ROWS = 24
COLS = 32
FPS = 2
MAX_ERRORS = 10 
data_ptr = None
quartiles = np.ones(5)
prev_quartiles = np.zeros(5)
error_counter = 0
freeze_check = True
     
sensor = i2cr.I2CReceiver()
if (not sensor.open(FPS)):
     print ('------- ERROR: I2C sensor cannot start --------')
     #sys.exit(1)
sensor.start()
sleep(0.2)
print ('Press CTRL+C to exit...')
          
# the application object
app = Flask("MLX_Streamer")

#---------------------------------------------------------------------------------------------

@app.route('/hello')
def hello():
    return ('<h2>This is MLX sensor streamer</h2>')


@app.route('/stop')
def stop():
    sensor.close()
    #os.system('sudo kill -9 `sudo lsof -t -i:5000`')
    print ('sudo kill -9 `sudo lsof -t -i:5000`')
    return ('dummy stop method')


@app.route('/reboot')
def reboot():
    #os.system('sudo reboot')
    print ('sudo reboot')
    return ('dummy reboot method')
      
      
@app.route('/resetsensor')
def resetsensor():
    global sensor, error_counter
    print("Resetting sensor..")
    try:
        sensor.close()
        time.sleep(3)  # let the sensor thread exit
        sensor = i2cr.I2CReceiver()
        if (not sensor.open(FPS)):
            print ('------- ERROR: I2C sensor cannot start --------')
            return ("Sensor could not be initialized.")
        sensor.start()
        sleep(0.2)    
        error_counter = 0
        return ("Sensor reset successfully.")
    except Exception as e:
        print (e)
        return("Failed to reset sensor.")
	      
      
@app.route('/summary')
def summary():
    global data_ptr
    data_ptr = sensor.getData()
    quartiles = percentile(data_ptr, [0, 25, 50, 75, 100])
    data_str = '<br/>'.join (str(x) for x in quartiles)
    return(data_str)
	
	      
@app.route('/')
def index():
    global data_ptr, error_counter, quartiles, prev_quartiles 
    try:
        data_ptr = sensor.getData()
        #print (len(data_ptr))
        if (len(data_ptr) == 0):
            print ('--- No data from sensor ---')
            return ("")   # the float parser needs an empty string
        #print (data_ptr[1:10])
        
        if (freeze_check):
            quartiles = percentile(data_ptr, [0, 25, 50, 75, 100])
            print(quartiles)    
            # check if the sensor has frozen
            sum_all = np.sum(np.isclose(prev_quartiles, quartiles))
            if (sum_all > 2):  # data has not changed much
                error_counter += 1
                if(error_counter > MAX_ERRORS):
                    print("Frozon frame ! Quitting..")
                    '''sensor.close()
                    time.sleep(2)
                    sensor.open()
                    sensor.start()'''
                    #os.system("sudo kill -9 `sudo lsof -t -i:5000`")
                    print ("sudo kill -9 `sudo lsof -t -i:5000`")
                    error_counter = 0 
                    return("")  # the float parser needs an empty string
                else:
                    error_counter = 0
            prev_quartiles = quartiles		     
            # end of freeze check
            
        # send data to HTTP client    
        # Note: no delimiters are used since HTTP will take care of it
        data_str = ' '.join (str(x) for x in data_ptr)
        return (data_str)
    except Exception as e:
        print (e)
        return("")    # for the float parser
#---------------------------------------------------------------------------------------------

app.run(host='0.0.0.0', port=5000, use_reloader=False, debug=True)  #, threaded=True)

# if use_reloader = True, multiple worker threads are created for sensor and
# they all fail to read the sensor   
