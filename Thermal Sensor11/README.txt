
thermalCam39.py:
derived from thermalCam38.py
Reads any thermal sensor through any communication channel
Can do HSV or gray scale detection
sending periodic data to Dweet and AWS, and instant notification when the count changes
outliers removed from people count before averaging.
    MLX90640_Udp4.ino/MLX90640_Udp3.ino  
    OR  MLX90640_Serial5.ino 
    OR  the RPi library MLX90640