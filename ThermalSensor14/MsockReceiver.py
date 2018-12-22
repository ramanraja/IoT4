# high level messaging wrapper for sockets: multiprocessing server

from multiprocessing.connection import Listener
from time import sleep
import threading

DEFAULT_PORT = 6000

class MsockReceiver (threading.Thread):

    def open (self, port=DEFAULT_PORT):
        self.setDaemon(True)
        self.terminate = False
        self.port = port
        self.data_ready = False
        self.message = "# place holder"
        print ("Opening MSocket Receiver..")  
        return True        
        
        
    def close(self):
        print  ("Closing MSocket Receiver..")  
        self.terminate = True
         
         
    def getData(self):  
        if (not self.data_ready):
            return ("")
        self.data_ready = False
        return self.message
        
        
    def dataAvailable(self):
        return self.data_ready
            
             
    def run(self): 
        print ('MSocket receiver thread starts...')
        while not self.terminate:
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
                    self.data_ready = True                
                    print (self.message)                        
                    if self.message == 'exit':   # quit inner loop
                        break
                except Exception as e:
                    print(e)   
                    break
            print ('closing client connection..')                
            conn.close()
            listener.close()
            if self.message == 'exit':   # quit outer loop 
                break
        print ('shutting down Msock server..')                
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
            if (sock.dataAvailable()):
                cmd = sock.getData()            
                print ('Rx command: {}'.format(cmd))
                if (cmd=='exit'):
                    break
            sleep (1)
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
        
              