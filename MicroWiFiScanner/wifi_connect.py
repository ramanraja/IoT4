# connect to Wifi network

WIFI_SSID = 'RajaSSID'
WIFI_PASSWD = 'rajaPasswd'

def connect():
    import network
    from time import sleep
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASSWD)
        count = 0
        while not wlan.isconnected():
            sleep(0.2)
            count += 1
            if (count > 50):
                print ('Wifi timed out.')
                break
    if wlan.isconnected():
        print('WiFi connected:\n', wlan.ifconfig())
        return True
    else:
        print('No WiFi connection')
        return False
    
       
if __name__ == "__main__":
    connect()    
    