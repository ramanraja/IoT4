# Multi socket client
# Sends remote commands to thermalSensor to adjust min/max/threshold
# Run this in a separate terminal on the same machine

from multiprocessing.connection import Client
import time

address = ('localhost', 6000)
print ('Trying to connect to server at port 6000...')
conn = Client(address, authkey = b'your_password')
print ('Connected to server')

print('Type a command on the console. For eg: r 23 28')
print('r=range; 23=minimum temperature; 28=maximum temperature') 
print("\nType 'exit' to break.")

while (True):
    inp = input("Command: ")
    print (inp)
    conn.send(inp)
    if (inp=='quit'):
        break

#print ('Sending exit command..')
#conn.send('exit')

print ('Closing connection...')
conn.close()

print ('Client exits')
