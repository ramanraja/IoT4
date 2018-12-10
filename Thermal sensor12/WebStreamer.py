# streams MLX90640 data to HTTP clients

#from __future__ import print_function
from flask import Flask
from time import sleep
import numpy as np
import pickle
import math
import time
import sys
import I2CReceiver as i2cr
     
ROWS = 24
COLS = 32
FPS = 2
MAX_ERRORS = 5 

data_ptr = None
     
sensor = i2cr.I2CReceiver()
if (not sensor.open(FPS)):
     print ('I2C sensor error')
     sys.exit(1)
sensor.start()
sleep(0.2)
print ('Press CTRL+C to exit...')
          
app = Flask("MLX_Streamer")

@app.route('/')
def index():
     data_ptr = sensor.getData()
     #print (type(data_ptr))
     print (len(data_ptr))
     if (len(data_ptr) == 0):
        return ("")
     print (data_ptr[1:10])
     # Note no delimiters are used since HTTP will take care of it
     data_str = ' '.join (str(x) for x in data_ptr)
     return (data_str)

app.run(debug=True)    