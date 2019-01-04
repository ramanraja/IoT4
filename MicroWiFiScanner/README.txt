# python -m serial.tools.list_ports
# python -m serial.tools.miniterm  COM13  115200

Install esptool :

$ pip install esptool

Download micropython from
https://micropython.org/download#esp8266

Connect the 8266 through the FTDI board and press the GPIO0 and reset buttons to
issue the following commands:

Erase the 8266 flash:
$ esptool --port COM13  erase_flash

$ esptool --port COM13 --baud 115200 write_flash --flash_size=detect 0 esp8266-20180511-v1.9.4.bin --verify

If successful, run a serial terminal program:
$ python -m serial.tools.miniterm  COM13  115200
Hit Enter a few times to get the micropython REPL prompt:

The default password for the wifi AP is micropythoN (note the uppercase N) 
and its IP address is 192.168.4.1.

Useful REPL commands:
>>> import time
>>> dir(time)                   # list all functions in the time module
>>> import os
>>> os.listdir()
>>> os.mkdir('mydir')
>>> os.remove('file.txt')
>>> time.sleep(1)            
>>> time.sleep_ms(500)       
>>> time.sleep_us(10)        

If you get the exception 'SyntaxError: invalid syntax\r\n' then it is most probably
an indentation problem. Check your tabs and spaces.

Ampy is a helpful tool to run scripts from your PC:
$ pip install adafruit-ampy
$ ampy --help

To run a script directly from a file on your PC:
$ ampy -p COM12 run myfile.py

Or you can upload the file to 8266:
$ ampy -p COM12 put myfile.py
Then from the REPL prompt, just import the .py file. This will exucute the commands in it:
>>> import myfile

You can create two start up scripts:
The boot.py script is executed first (if it exists) and then main.py script is executed. 
