# Save your thermal camera settings into a pickle file.
# This can weork with serial/UDP/I2C port version of the program
# python settings_90640.py

import pickle

cv_settings = { 
    "sensor_type" : "MLX-90621",     # 8x8/4x16/24x32 thermal camera
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


'''---------------------------------------------------------------------
# Keeping a backup copy for reference: do not modify the entries below:
------------------------------------------------------------------------
cv_settings = { 
    "sensor_type" : "MLX-90640",     # 24x32 thermal camera
    "rows" :  24, 
    "cols" :  32,
    "sleep_time" : 50,               # mSec between packet requests    
    "comm_type" : 2,                 # 1=UDP, 2=serial, 3=I2C
    
    "serial_port" : "COM12",
    "udp_ip" : "192.168.0.123",
    "udp_port" : 12345,
    "server_timeout" : 2.0,          # I2C frames per second 
    "fps" : 2,
    
    "interpolation": 2,              # 0=none, 2=bicubic
    "palette" :  1,                  # 10=gray scale, 1=bwr
    "min_temp" : 28, 
    "max_temp" : 34, 
    "use_gray_scale" : 0,            # 0=use HSV, 1=use grayscale

    "min_red" : [0, 70, 70], 
    "max_red" : [10, 255, 255],              
    "blur_size" : 23,                
    "neighbourhood" : 19,            # must be odd
    "cparam" : 3,
    
    "running_buffer_length" : 5,     # moving average buffer
    "num_erode_dilate" : 7,          # number of iterations
    "lower_threshold" : 220,         # gray scale thresholds
    "upper_threshold" : 255,
    "alpha" : 1.2,                   # contrast multiplier
    "beta" : 0.2                     # brightness adjustment
    }
----------------------------------------------------------------------'''    