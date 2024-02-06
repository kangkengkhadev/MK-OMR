#import libraries
import pickle
import cv2
import cvzone
import numpy as np

#define 
circle_width, circle_height = 25,25
pickle_name = 'exam1'
position_path = './pickle/'
global img
img = cv2.imread('Ideal.JPEG', 0)
img = cv2.resize(img, (1700, 2250), interpolation = cv2.INTER_LINEAR)

#debug
try:
    with open(position_path+pickle_name, 'rb') as f:
        posList = pickle.load(f)
except:
    posList = []


#function click
def mouseClick(events, x, y, flags, params):
    global img 
    if events == cv2.EVENT_LBUTTONDOWN:
        if y > 60 and y < 120 and x > 90 and x < 250:   
            posList.pop()
            img = cv2.imread('Ideal.JPEG', 0)
            img = cv2.resize(img, (1700, 2250), interpolation = cv2.INTER_LINEAR)
            idx = 0
            for pos in posList:
                idx+=1
                cv2.rectangle(img, pos[0], (pos[0][0] + circle_width, pos[0][1] + circle_height), (0, 0, 0), 2)
            cvzone.putTextRect(img, f'Idx:{idx}', (100, 50), scale=3,
                           thickness=2, offset=20, colorR=(0,200,0))
            cv2.putText(img, 'Undo',(140,120),cv2.FONT_HERSHEY_PLAIN, 2,(0),3)
        else: 
            posList.append([(x, y),params])
        with open(position_path+pickle_name, 'wb') as f:
            pickle.dump(posList, f)

#start running

while True:
    idx = 0
    for pos in posList:
                cv2.rectangle(img, pos[0], (pos[0][0] + circle_width, pos[0][1] + circle_height), (0, 0, 0), 2)
                idx += 1
    cvzone.putTextRect(img, f'Idx:{idx}', (100, 50), scale=3,
                           thickness=2, offset=20, colorR=(0,200,0))
    cv2.putText(img, 'Undo',(140,120),cv2.FONT_HERSHEY_PLAIN, 2,(0),3)
    k=cv2.waitKey(1) & 0xFF
    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouseClick,idx)
    cv2.waitKey(1) 