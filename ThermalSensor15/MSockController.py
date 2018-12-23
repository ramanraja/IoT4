# Multi socket client
# Sends remote commands to thermalSensor to adjust min/max/threshold
# Run this in a separate terminal on the same machine

from multiprocessing.connection import Client
import time

print('Type a command on the console') 
print('Example: m 23 28')
print('m=min-max temperature: 23=minimum; 28=maximum') 
print('Example: t 220 255')
print('t=thresholds: 220=lower; 255=upper')
print('Example: r 1')
print('r=min-max temperature range: 0:23-25 deg; 1:24-26 deg; 2:25-27 deg C')
print("\nType 'quit' to break.")


address = ('localhost', 6000)
print ('Trying to connect to server at port 6000...')

conn = None
try:
    conn = Client(address, authkey = b'your_password')
    print ('Connected to server.')
except Exception as e:
    print (e)
    
print ('CTRL+C to exit..')    
inp = None
while (True):
    try:
        inp = input("Command: ")
        print (inp)
        conn.send(inp)
    except Exception as e:
        print (e)
    if (inp=='quit'):
        break

try:
    # Optional: close the server also
    #print ('Sending exit command..')
    #conn.send('exit')

    print ('Closing connection...')
    conn.close()
except Exception as e:
    print (e)
    
print ('Client exits')
