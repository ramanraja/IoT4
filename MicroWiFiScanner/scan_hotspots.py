# scan for available APs using a Generator and send it to a server in chunks

DEVICE_ID = 1
CHUNK_LEN = 10
SERVER_URL = "http://192.168.0.100:5000/ultra"
    
def scan():
    try:
        import network
        nic = network.WLAN(network.STA_IF)
        nic.active(True)
        aplist = nic.scan()
        #print(aplist)
        for ap in aplist:
            #print (ap)
            jap = {}
            jap["M"]= ":".join(hex(m)[2:] for m in ap[1])
            jap["S"]= ap[0].decode('utf-8')
            jap["R"]= ap[3]
            yield(jap)
    except Exception as e:
        print (e)
        return None        


def send_chunk(payload):        
    try:
        import urequests as requests
    except ImportError:
        import requests
    r = None
    try :
        r = requests.post(url=SERVER_URL, json=payload)
        #print(r.text)      # as string
        print(r.json())     # if applicable
    except Exception as e:
        print (e)
    if r is not None:
        r.close()  # to avoid memory leakage !!!
    
    
def scan_and_send ():
    jpayload = {}
    chunk_count = 0  
    first_chunk = True
    last_chunk = False
    
    for apdata in scan():   
        last_chunk = False
        if (chunk_count==0): 
            if (first_chunk):
                first_chunk = False
            else:
                print('Sending chunk..')
                send_chunk(jpayload)
            jpayload = {}
            jpayload["DEVICE"] = DEVICE_ID    
            jpayload["DATA"] = []   
        print (apdata)
        jpayload["DATA"].append(apdata)
        chunk_count = (chunk_count+1) % CHUNK_LEN
        last_chunk = True
    
    if (last_chunk):
        print('Sending last chunk..')
        send_chunk(jpayload)

 
if __name__ == "__main__":
    try:
        scan_and_send()
    except Exception as e:
        print (e)
        
        

