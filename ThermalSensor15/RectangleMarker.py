# mark rectangles and save them to pickle file
# Run the program thermalCamxx.py and press S to take a snapshot.
# Then run this program to mark rectangular masking regions.
# Then run thermalCamxx again.
 
from matplotlib import pyplot as plt
from time import sleep
import numpy as np
import pickle
import math
import cv2
 
frame = cv2.imread('snapshot.png')
print ("Frame size: ", end='')
print (frame.shape)  # (height,width,depth)

boxes = []
terminate = False
while not terminate:
    print ('Press any key [Esc to exit]..')
    k = cv2.waitKey(0) & 0xFF
    if (k == 27):  # Esc is pressed
        break   
    bbox = cv2.selectROI('Marker', frame, fromCenter=False, showCrosshair=False)
    print ('[x,y,width,height]: ', end='')
    print (bbox)               
    if (bbox[2] > 0 and bbox[3] > 0):
        boxes.append(bbox)
 
        
print ('Selected areas:')
print(boxes)        
pickle.dump(boxes , open("mask_out.p", "wb"))
print ("Masking regions saved as 'mask_out.p'")

print ("Reading cut out masks..")
cut_out_masks = pickle.load(open( "mask_out.p", "rb"))
print (cut_out_masks)