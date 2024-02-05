#import libraries
import pickle
import cv2
import cvzone

#define 
circle_width, circle_height = 25,25
pickle_name = 'exam1'
position_path = './pickle/'
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
    if events == cv2.EVENT_LBUTTONDOWN:
        posList.append([(x, y),params])
        with open(position_path+pickle_name, 'wb') as f:
            pickle.dump(posList, f)
    if events == cv2.EVENT_RBUTTONDOWN:
        posList.pop()
        with open(position_path+pickle_name, 'wb') as f:
            pickle.dump(posList, f)
#start running
while True:
    idx = 0
    for pos in posList:
        idx += 1
        cv2.rectangle(img, pos[0], (pos[0][0] + circle_width, pos[0][1] + circle_height), (0, 0, 0), 2)
    cvzone.putTextRect(img, f'Idx:{idx}', (100, 50), scale=3,
                           thickness=2, offset=20, colorR=(0,200,0))
    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouseClick,idx)
    cv2.waitKey(1) 