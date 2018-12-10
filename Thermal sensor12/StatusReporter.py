# helper class to send HTTP POST messages to backends

from threading import Thread
from time import sleep
import requests
import dweepy
import json

# pip install dweepy


class StatusReporter(Thread):

    HELLO_MSG = 0
    RESTARTED_MSG = 5
    SENSOR_ERROR_MSG = 6    
    REGULAR_MSG = 7
    EVENT_MSG = 8

    
    # post status to test URL once in 60 sec, and to prod URL once every 5 messages (5 min)
    def init(self, deviceID=0, frequency=60, prodMultiplier=5):
        self.terminate = False
        self.device_id = deviceID
        self.test_freq = frequency
        self.prod_multiplier = prodMultiplier
        self.message_count = 0
        print ("StatusReporter created for device {}.".format(self.device_id))
        self.payload = {"ID":0, "C":0, "P":0}
        self.payload ['ID'] = self.device_id
        self.payload ['C'] = 0
        self.payload ['P'] = StatusReporter.HELLO_MSG
        self.jheader = {"content-type":"application/json"}
        
        
    def open(self, testURL=None, prodURL=None):
        self.test_url = testURL
        self.prod_url = prodURL
        print ("Test URL: {}".format(self.test_url))
        print ("Prod URL: {}".format(self.prod_url))
        
        
    def close (self):
        self.terminate = True    # terminate the worker thread
        print ('StatusReporter closed.')
                
                
    # set the status for lazy update later            
    def set_status (self, count, param=REGULAR_MSG):
        self.payload ['C'] = count
        self.payload ['P'] = param   


    # send an immediate notification
    def send_message (self, count, param=EVENT_MSG):
        self.payload ['C'] = count
        self.payload ['P'] = param 
        print (self.payload)
        self.post_to_test()
        self.post_to_prod()  # this is an async event, so send to both URLs
        self.payload ['P'] = StatusReporter.REGULAR_MSG
        
        
    def post_to_prod (self):
        try:
            print ("sending to: {}".format(self.prod_url))
            response = requests.post(self.prod_url, json=self.payload, headers=self.jheader)
            print ('Response code: ', response.status_code)
            print (response.text)
            if (response.status_code != 200):
                print ("- HTTP error -")          
        except Exception as e:
            print (e)

    def post_to_test (self):    
        try:
            print ("sending to: {}".format(self.test_url))
            dweepy.dweet_for(self.test_url, self.payload)
        except Exception as e:
            print (e)
        

    def run(self):
        #print ('Status thread starts...')
        while not self.terminate:
            self.post_to_test()
            self.message_count = (self.message_count+1) % self.prod_multiplier
            if (self.message_count == 0):
                self.post_to_prod()        
            for i in range (int(self.test_freq/2)):
                if (self.terminate) : break
                sleep(2)                
        print ('Status therad exits.')   
        
        
#----------------------------------------------------------------------------- 
# MAIN
#----------------------------------------------------------------------------- 

# import StatusReporter as sta

def main():
    device_id = 1
    aws_url = 'http://52.40.239.77:5800/post_thermal_data'   
    dweet_user = 'vz-ind-rmz-ther{}'.format(device_id)
    
    reporter = StatusReporter()
    reporter.init(device_id)
    reporter.open(dweet_user, aws_url)  
    reporter.start()
    reporter.send_message(StatusReporter.RESTARTED_MSG, StatusReporter.EVENT_MSG)  
    
    print ("Press CTRL+C to quit...")
    count = 1
    while True:
        try :
            reporter.set_status(count)   
            count = (count+1)%10
            sleep (30)
        except KeyboardInterrupt:
            print ("CTRL+C pressed.")
            break
        except Exception as e:
            print(e) 
            sleep(4)           
    
 
    reporter.close()
    sleep (1.0)
    print("Main thread exits.") 

if __name__ == "__main__":
    main()           