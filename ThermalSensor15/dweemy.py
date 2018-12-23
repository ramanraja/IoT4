# dweemy.py
# DIY implementation for dweepy

import requests
import json
import time

def dweet_for (dweet_handle, payload):
    try:
        url = 'https://dweet.io/dweet/for/' + dweet_handle
        response = requests.post(url, json=payload, 
                   headers={"content-type":"application/json"})
        return (response.status_code)
    except Exception as e:
        print (e)    
        return (-1)
 
    
 