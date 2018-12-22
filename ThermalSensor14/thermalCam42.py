
# converted sliders to socket based remote tool
# Done: just stream the sensor data from RPi Zero. 
# Done: post status to dweet and AWS
# Done: moving average with outlier removal.

# Read MLX90640 thermal sensor (24x32) through UDP/serial/I2C on RPi
# Detect humans by gray scale thresholding OR HSV based separation.
# use it with the Arduino program  MLX90640_Udp3.ino or  
# MLX90640_Udp4.ino/  MLX90640_Serial5.ino or the RPi library MLX90640
# manual recalibration of min and max temperatures when you press 'c' or space bar.
# running average of people count to suppress noise
# https://www.pyimagesearch.com/2015/09/21/opencv-track-object-movement/
# https://www.learnopencv.com/color-spaces-in-opencv-cpp-python/

from MsockReceiver import MsockReceiver
from matplotlib import pyplot as plt
import StatusReporter as starep
from time import sleep
import numpy as np
import datetime
import pickle
import math
import time
import sys
import cv2
import os
import io

BASE_TEMP = 23.0       # min
INCREMENT_TEMP = 2.0   # max = min+INCREMENT_TEMP

# slider control callback method 
def check_calibration():
    global MIN_TEMP, MAX_TEMP, LOWER_THRESHOLD, UPPER_THRESHOLD
    if (not msock.dataAvailable()):
        return False
    try:        
        cmd = msock.getData()            
        print ('Received command: {}'.format(cmd))
        if (cmd[0]=='m' or cmd[0]=='M'):
            cmd = cmd[1:]
            minmax = [float(n) for n in cmd.split()]
            MIN_TEMP = minmax[0]
            MAX_TEMP = minmax[1]
        elif (cmd[0]=='r' or cmd[0]=='R'):
            cmd = cmd[1:]
            minmax = float(cmd)
            MIN_TEMP = minmax + BASE_TEMP
            MAX_TEMP = MIN_TEMP + INCREMENT_TEMP
        elif (cmd[0]=='t' or cmd[0]=='T'):
            cmd = cmd[1:]
            thresh = [float(n) for n in cmd.split()]
            LOWER_THRESHOLD = thresh[0]
            UPPER_THRESHOLD = thresh[1]
        else:
            print ('Bad configuration command !')
            return False
        print ("MIN TEMP = {},  MAX TEMP = {}".format(MIN_TEMP, MAX_TEMP))            
        print ("THRESHOLDS = {} and {}".format(LOWER_THRESHOLD, UPPER_THRESHOLD))    
        return True
    except Exception as e:
        print (e)
        return False

    
# -------------------------------------------------------------------------
# constants  
# -------------------------------------------------------------------------
COMM_UDP = 1
COMM_SERIAL = 2
COMM_I2C = 3
COMM_WEB = 4

# https://matplotlib.org/gallery/images_contours_and_fields/interpolation_methods.html

interpolation_strings = ['none', 'bilinear', 'bicubic', 'quadric', 'gaussian' ,
    'spline16', 'spline36', 'hanning', 'hamming', 'hermite', 
    'kaiser', 'catrom', 'bessel', 'mitchell', 'sinc', 
    'lanczos', 'nearest']

# https://matplotlib.org/users/colormaps.html

palette_strings = ['flag', 'bwr', 'coolwarm', 'RdYlGn', 'seismic', 
    'BrBG', 'RdGy', 'winter', 'YlOrRd', 'YlOrBr',
    'Greys', 'Greens', 'Oranges', 'Reds', 'bone', 
    'RdYlBu', 'cool', 'gnuplot']

# -------------------------------------------------------------------------
# configure
# -------------------------------------------------------------------------

print ('\nUsage: python ThermalCam.py [min_temperature] [max_tempeature]')
print()

cv_settings = pickle.load(open( "settings_90640.p", "rb"))
print (cv_settings)
print() 

DEVICE_ID = cv_settings['device_id'] 
sensor_url = cv_settings['sensor_server_url'] 
AWS_URL = cv_settings['aws_url']  
DWEET_HANDLE = cv_settings['dweet_handle'] + str(DEVICE_ID)
print (DWEET_HANDLE)

COMM_TYPE = cv_settings['comm_type']
FPS = cv_settings['fps']
SERIAL_PORT = cv_settings['serial_port']
REMOTE_UDP_IP_ADDRESS = cv_settings['udp_ip']
REMOTE_UDP_PORT = cv_settings['udp_port']
SERVER_TIMEOUT = cv_settings['server_timeout']
SHOW_WINDOW = cv_settings['show_window']

sensor_type = cv_settings['sensor_type']
ROWS = cv_settings['rows']
COLS = cv_settings['cols']
MIN_TEMP = cv_settings['min_temp']
MAX_TEMP = cv_settings['max_temp']

USE_GRAY_SCALE = cv_settings['use_gray_scale']
INTERPOLATION = cv_settings['interpolation']
PALETTE = cv_settings['palette']
MIN_RED = np.array (cv_settings['min_hue'], dtype = "uint8")
MAX_RED = np.array (cv_settings['max_hue'], dtype = "uint8")

BLUR_SIZE = cv_settings['blur_size']
NEIGHBOURHOOD = cv_settings['neighbourhood']   # must be odd
CPARAM = cv_settings['cparam']
ED_CYCLES =  cv_settings['num_erode_dilate']
LOWER_THRESHOLD = cv_settings['lower_threshold']
UPPER_THRESHOLD = cv_settings['upper_threshold']
ALPHA = cv_settings['alpha']
BETA = cv_settings['beta']
MAX_ERRORS = cv_settings['max_errors']
N = cv_settings['running_buffer_length']
SLEEP_TIME = cv_settings['sleep_time']

# Now override with command line arguments
if (len(sys.argv) > 1):
    MIN_TEMP = int(sys.argv[1])
print ("Minimum temperature : {}".format (MIN_TEMP))
if (len(sys.argv) > 2):
    MAX_TEMP = int(sys.argv[2])
print ("Maximum temperature : {}".format (MAX_TEMP))
if (MIN_TEMP < 6 or MAX_TEMP > 60):
    print ("Temperature range must be between 6 and 60 degree C");
    sys.exit(1)
if (N < 5):
    print ("Length of running buffer should be at least 5");
    sys.exit(1)    
# -------------------------------------------------------------------------   
# main  
# -------------------------------------------------------------------------


sensor = None
reporter = None
calib_changed = True

if (COMM_TYPE == COMM_UDP):
    import UdpReceiver as udp   
    sensor = udp.UdpReceiver()
    if (not sensor.open(REMOTE_UDP_IP_ADDRESS, REMOTE_UDP_PORT, SERVER_TIMEOUT)):
         print ('UDP Socket error')
         sys.exit(1)
     
elif (COMM_TYPE == COMM_SERIAL):
    import SerialReceiver as seri   
    sensor = seri.SerialReceiver()
    # NOTE: sensor.open() has 3 parameters, so if you skip the middle one(baud), then
    # the third param has to be explicitly named *
    if (not sensor.open(SERIAL_PORT, timeout=SERVER_TIMEOUT)): 
         print ('Serial port error')
         sys.exit(1)
    print ('Serial port is open')
    
elif (COMM_TYPE == COMM_WEB):
    import WebReceiver as webr
    sensor = webr.WebReceiver()
    if (not sensor.open(sensor_url)): 
         print ('Web server error')
         sys.exit(1)
    print ('Web server is reachable.')
    
else: 
    import I2CReceiver as i2cr
    sensor = i2cr.I2CReceiver()
    if (not sensor.open(FPS)):
         print ('I2C sensor error')
         sys.exit(1)
                              
print ('about to start sensor..')          
sensor.start()
sleep(0.2)

print ('about to create Status reporter..')
reporter = starep.StatusReporter()
print ('Status reporter created')
reporter.init(DEVICE_ID)
reporter.open(DWEET_HANDLE, AWS_URL)  
reporter.start()
sleep(2.0)  # not to exceed Dweet rate limit
reporter.send_message(0,starep.StatusReporter.RESTARTED_MSG) 

print ('about to create calibration multiSocket..')          
msock = MsockReceiver()
msock.open()
msock.start()

# running average of people count:
people_count = np.zeros(N)
previous_count = 0
index = 0 
min_temp = MIN_TEMP
max_temp = MAX_TEMP

'''
if SHOW_WINDOW:
    cv2.namedWindow('controller')
    cv2.resizeWindow('controller', width=600,height=85)
    cv2.createTrackbar('MIN','controller',50,220, calibrator)   # min=20, max=42 C 
    cv2.createTrackbar('MAX','controller',90,220, calibrator)   # min=20, max=42 C
'''

black_img = np.zeros ((ROWS,COLS), dtype=float)
plt.figure()
plt.axis("off")
img = plt.imshow(black_img, 
        cmap=palette_strings[PALETTE], 
        interpolation=interpolation_strings[INTERPOLATION],
        vmin = MIN_TEMP, vmax = MAX_TEMP)  

print ('Press CTRL+C to exit...')
data_ptr = None 
type1_error_count = 0
type2_error_count = 0
type3_error_count = 0

while True:
    try:
        if (check_calibration()) :
            img = plt.imshow(black_img, 
                    cmap=palette_strings[PALETTE], 
                    interpolation=interpolation_strings[INTERPOLATION],
                    vmin = MIN_TEMP, vmax = MAX_TEMP)     
                    
        #start_time = datetime.datetime.now()
        data_ptr = sensor.getData()
        if (len(data_ptr) == 0):
            print(" --->>> MLX sensor timed out.")
            type1_error_count += 1
            if (type1_error_count > MAX_ERRORS):
                print ('---> EXIT: type 1 error count exceeded limit !')
                sys.exit(1)
            continue
        type1_error_count = 0
            
        # now the data is in the sensor's internal buffer, referenced by data_ptr
        # *** This works because this is a request-response protocol ***
        #print (len(data_ptr))
        if (len(data_ptr) != ROWS*COLS):
            print ('--- Packet error: length mismatch ---')
            print (len(data_ptr))
            type2_error_count += 1
            if (type2_error_count > MAX_ERRORS):
                print ('---> EXIT: type 2 error count exceeded limit !')
                sys.exit(2)            
            continue
        type2_error_count = 0       
                     
        data_ptr = np.array (data_ptr)
        min_temp = np.min(data_ptr)    # do NOT use min() and max() in basic python library:
        max_temp =  np.max(data_ptr)   # they ignore nan values
        if (np.isnan(min_temp) or np.isnan(max_temp)):
            print ('--- Packet error: nan values present ---')
            type3_error_count += 1
            if (type3_error_count > MAX_ERRORS):
                print ('---> EXIT: type 3 error count exceeded limit !')
                sys.exit(3)
        type3_error_count = 0
        
        print ("min : {} , max : {}".format (min_temp, max_temp))
        data_ptr = data_ptr.reshape(ROWS, COLS)
        img.set_array(data_ptr) 
        
        #------------------------------------------ 
        # this also works:
        #plt.savefig('frame.png', bbox_inches='tight')
        #frame = cv2.imread('frame.png')
        #-------------------------------------------
        
        # transfer to cv2 using in-memory file:
        buf = io.BytesIO()
        plt.savefig (buf, format='png')
        buf.seek(0)
        frame = np.asarray (bytearray(buf.read()), dtype=np.uint8)
        if (USE_GRAY_SCALE):
            frame = cv2.imdecode (frame, cv2.IMREAD_GRAYSCALE)  # for grayscale
        else:
            frame = cv2.imdecode (frame, cv2.IMREAD_COLOR)      # for HSV separation  
        buf.close()
        
        #-------- preprocessing ----------------
        # increase contrast, adjust brightness
        frame = cv2.convertScaleAbs(frame, alpha=ALPHA, beta=BETA) 
        # first blur, and then threshold        
        blurred = cv2.GaussianBlur(frame, (BLUR_SIZE, BLUR_SIZE), 0)
        blurred = cv2.erode(blurred , None, iterations =ED_CYCLES)
        blurred = cv2.dilate(blurred , None, iterations =ED_CYCLES)
        
        #-------- thresholding ----------------
        the_mask = None
        if (USE_GRAY_SCALE):
            # For contour finding, the foreground should be white against black background         
            #T,the_mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_OTSU+cv2.THRESH_BINARY_INV) 
            #print ("Otsu's threshold: %d" % (T))
            
            #the_mask = cv2.adaptiveThreshold (blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            #           cv2.THRESH_BINARY_INV, NEIGHBOURHOOD, CPARAM) 
            
            # For contour finding the foreground should be white against black background 
            retval,the_mask = cv2.threshold (blurred, LOWER_THRESHOLD,UPPER_THRESHOLD, cv2.THRESH_BINARY_INV) 
    
            #NOTE : the third argument MUST be explicitly named as 'mask'
            #masked = cv2.bitwise_and(frame, frame, mask=the_mask)   
        else:
            hsv_frame = cv2.cvtColor (frame, cv2.COLOR_BGR2HSV)       
            the_mask = cv2.inRange (hsv_frame, MIN_RED, MAX_RED)     
                 
        #----------- contour detection ----------
        # finding contours destroys the original image, so make a copy if you need it later
        (junk_img, contours, hierarchy) = cv2.findContours (the_mask,   # the_mask.copy(), 
                                          #cv2.RETR_TREE,   
                                          cv2.RETR_EXTERNAL, 
                                          cv2.CHAIN_APPROX_SIMPLE)
        ccount = len(contours)
        #print ("{} contour(s) found.".format(ccount))
        people_count[index] = ccount
        index = (index+1) % N
        sorted_counts = np.sort(people_count)
        # ignore the two end values as outliers
        ave_count = int(np.round(np.mean(sorted_counts[1:-1])))
        
        reporter.set_status(ave_count)
        print ("PEOPLE COUNT: {}".format(ave_count))
        if (ave_count != previous_count):
            # too much noise -> too many status messages to Dweet
            #####reporter.send_message(ave_count,starep.StatusReporter.EVENT_MSG) 
            print('--- People count CHANGED, but NOT sending status ----')
        previous_count = ave_count
        
        if SHOW_WINDOW:
            if (ccount > 0):
                cntrs = sorted(contours, key = cv2.contourArea, reverse = True)
                cv2.drawContours(frame, cntrs, -1, (0, 255, 0), 1)
                #rect = np.int32(cv2.BoxPoints(cv2.minAreaRect(cntrs)))
                #cv2.drawContours(frame, [rect], -1, (0, 255, 0), 2)
                i = 0
                for c in cntrs:
                    (x,y,w,h) = cv2.boundingRect(c)
                    #cv2.rectangle(frame, (x,y),(x+w,y+h), (0, 255, 0), 1)
                    cv2.putText(frame, str(i+1), (x,y), cv2.FONT_HERSHEY_SIMPLEX, 
                                0.7, (0,0,0), 1, cv2.LINE_AA)  
                    i += 1
            cv2.putText(frame, str(ave_count), (20,70), cv2.FONT_HERSHEY_SIMPLEX, 
                        3.0, (0,0,0), 5, cv2.LINE_AA)       
            cv2.imshow("Thermal Camera", frame)
            #cv2.imshow("The Mask", the_mask)
        
        #end_time = datetime.datetime.now()        
        #delta = end_time - start_time
        #print("Time taken for one frame: {} seconds".format(delta))
        
        key = cv2.waitKey(SLEEP_TIME) & 0xFF  # TODO: revisit the delay
        if (key==27): 
            break     
        if (key==ord('c') or key==ord(' ')): 
            print("----->>> Calibrating...")    
            min_t = math.floor(min_temp)
            max_t = math.ceil(max_temp)
            img = plt.imshow(data_ptr, 
                    cmap=palette_strings[PALETTE], 
                    interpolation=interpolation_strings[INTERPOLATION],
                    vmin = min_t, vmax = max_t)
            print ("min_t : {} , max_t : {}".format (min_t, max_t)) 
    except KeyboardInterrupt:
        break
    except Exception as e:        
        print (e)

sensor.close()
msock.close()
reporter.close()
cv2.destroyAllWindows()
sleep (2.0)
print("Main thread exits.")

#-----------------------------------------------------------------------------------------------
# Configuration program: run it once before starting the main program
'''--------------------------------------------------------------------------------------------
import pickle
cv_settings = { 
    "sensor_type" : "MLX-90640",     # 8x8/4x16/24x32 thermal camera
    "rows" :  24, 
    "cols" :  32,
    "device_id" : 1,
    "sensor_server_url" : "http://127.0.0.1:5000/",
    "aws_url" : "http://52.40.239.77:5800/post_thermal_data",
    "dweet_handle" : "vz-ind-rmz-ther",
    "max_errors" : 5,
    "show_window" : 1,
    
    "sleep_time" : 50,               # mSec between packet requests    
    "comm_type" : 4,                 # 1=UDP, 2=serial, 3=I2C, 4=HTTP
    
    "serial_port" : "COM12",
    "udp_ip" : "192.168.0.109",
    "udp_port" : 12345,
    "server_timeout" : 2.0,          # I2C frames per second 
    "fps" : 2,
    
    "interpolation": 2,              # 0=none, 2=bicubic 
    "palette" :  10,                  # 10=gray scale, 1=bwr
    "min_temp" : 28, 
    "max_temp" : 34, 
    "use_gray_scale" : 1,            # 0=use HSV, 1=use grayscale

    "min_hue" : [0, 70, 70], 
    "max_hue" : [10, 255, 255],              
    "blur_size" : 23,                
    "neighbourhood" : 19,            # must be odd
    "cparam" : 3,
    
    "running_buffer_length" : 9,     # moving average buffer
    "num_erode_dilate" : 7,          # number of iterations
    "lower_threshold" : 220,         # gray scale thresholds
    "upper_threshold" : 255,
    "alpha" : 1.2,                   # contrast multiplier
    "beta" : 0.2                     # brightness adjustment
    }
    

pickle.dump(cv_settings , open("settings_90640.p", "wb"))
print ("Config saved as 'settings_90640.p'")    
---------------------------------------------------------------------------------------------'''



              