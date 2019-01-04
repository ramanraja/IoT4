import gc
import wifi_connect
import scan_hotspots

if (wifi_connect.connect()):
    scan_hotspots.scan_and_send()
    
gc.collect()
# TODO: go to deep sleep
