import cv2
import pickle

#define 
circle_width, circle_height = 15,15
size = (1000, 1250) # (1000, 250) or (1000, 1250)
position_path = './pickle_label/'
image_name = "mock_images/rectangle_1.png"
startname = "rect1_"

global img
img = cv2.imread(image_name, 0)
img = cv2.imread(image_name, cv2.IMREAD_GRAYSCALE)
img = cv2.resize(img,size, interpolation = cv2.INTER_LINEAR) 
pickle_name = startname+ str(img.shape[0]) + "_" + str(img.shape[1]) + "_" + str(circle_width) + "_" + str(circle_height)

with open(position_path+pickle_name, 'rb') as f:
    posList = pickle.load(f)
    for i in range(850-60*5, 850-60*4):
        posList[i][0] = (posList[i][0][0], posList[i][0][1] +1)

with open(position_path+pickle_name, 'wb') as f:
    pickle.dump(posList, f)
    print("done")
for pos in posList:
    cv2.rectangle(img, pos[0], (pos[0][0] + circle_width, pos[0][1] + circle_height), (0, 0, 0), 2)
cv2.imshow("image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
