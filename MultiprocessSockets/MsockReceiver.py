# https://stackoverflow.com/questions/6920858/interprocess-communication-in-python
# high level messaging wrapper for sockets for multiprocessing situation : server

from multiprocessing.connection import Listener
from time import sleep
import threading

DEFAULT_PORT = 6000

class MsockReceiver (threading.Thread):

    def open (self, port=DEFAULT_PORT):
        self.terminate = False
        self.port = port
        self.message = "place holder"
        print ("Opening MSocket Receiver..")  
        return True        
        
        
    def close(self):
        print  ("Closing MSocket Receiver..")  
        self.terminate = True
         
         
    def run(self): 
        print ('MSocket receiver thread starts...')
        try:
            address = ('localhost', self.port)     # family is deduced to be 'AF_INET'
            listener = Listener(address, authkey = b'your_password')        
            print ("Listening on port {}..".format(self.port))
            conn = listener.accept()  # blocking
            print ('Connection accepted from {}'.format (listener.last_accepted))            
        except Exception as e:
            print("MSocket error. Quitting :")
            print (e)    
            return
        while not self.terminate:
            try:
                self.message = conn.recv()  # blocking
                print (self.message)
                if self.message == 'exit': break
            except Exception as e:
                print(e)   
        print ('closing connection..')                
        conn.close()
        listener.close()
        print ('MSocket  receiver thread exits.')    
        
#----------------------------------------------------------------------------- 
# MAIN
#----------------------------------------------------------------------------- 

def main():
    sock = MsockReceiver()
    sock.open()
    sock.start()
    
    print ("Press CTRL+C to quit...")
    
    while True:
        try :
            sleep (2)
        except KeyboardInterrupt:
            print ("CTRL+C pressed.")
            break
        except Exception as e:
            print(e)            
    
    sock.close()
    sleep (2.0)
    print("Main thread exits.") 

if __name__ == "__main__":
    main()        
        
              