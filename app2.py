import cv2
import cv2.mat_wrapper
import numpy as np
import os
import pickle

name = "mark.jpg"
main_sec_pickle = "pickle_label/rect1_1250_1000_15_15"
name_sec_pickle = "pickle_label/rect2_250_1000_15_15"
default_rect_space = 200000

# transform imahe for rectangle
org_image = cv2.imread(name)
org_image = cv2.resize(org_image, (1000, 1250), interpolation = cv2.INTER_LINEAR)
gray = cv2.cvtColor(org_image , cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blurred, 20, 150)
contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cropped_rectangles = []

# tansform for omr
img_for_detect = cv2.imread(name, cv2.IMREAD_GRAYSCALE)
img_for_detect_gray = cv2.resize(img_for_detect, (1000, 1250), interpolation = cv2.INTER_LINEAR)
(thresh, im_bw) = cv2.threshold(img_for_detect_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
thresh = 200
img_for_detect = cv2.threshold(img_for_detect_gray, thresh, 255, cv2.THRESH_BINARY)[1]
sens = 50

# find rectangles
for contour in contours:
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.03 * peri, True)
    if len(approx) == 4:
        x, y, w, h = cv2.boundingRect(approx)
        cropped_rectangle = org_image[y:y+h, x:x+w]
        if cropped_rectangle.shape[0] * cropped_rectangle.shape[1] < default_rect_space:
            continue
        cropped_rectangles.append(cropped_rectangle)


class MyPickle:
    def __init__(self, filename):
        self.filename = filename
        ext_name = self.filename.split('_')
        self.width = int(ext_name[2])
        self.height = int(ext_name[3])
        self.rect_range = int(ext_name[4])
        self.wh = (self.height,self.width)

    def get_file(self):
        with open(self.filename, 'rb') as f:
            posList = pickle.load(f)
        return posList
    
# for i, rectangle in enumerate(cropped_rectangles):
#     cv2.imshow(f"Cropped Rectangle {i+1}", rectangle)

# print(len(cropped_rectangles))

# cv2.waitKey(0)
# cv2.destroyAllWindows()

if(len(cropped_rectangles) != 2):
    print(len(cropped_rectangles))
    cv2.imshow("Cropped Rectangle",cropped_rectangles[0])
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print("Error while cropping please try again or evaluate by yourself")
else:
    # set name and main
    idx_max = 0
    space = 0
    cand1 = cropped_rectangles[0]
    cand2 = cropped_rectangles[1] 
    if(cand1.shape[0]*cand1.shape[1] > cand2.shape[0]*cand2.shape[1]):
        main_sec_image = cand1
        name_sec_image = cand2 
    else:
        main_sec_image = cand2
        name_sec_image = cand1

    # new objects
    main_sec_obj = MyPickle(main_sec_pickle)
    name_sec_obj = MyPickle(name_sec_pickle)

    # convert main rect to binary
    main_sec_image = cv2.resize(main_sec_image,main_sec_obj.wh)
    img_for_detect = cv2.cvtColor(main_sec_image, cv2.COLOR_BGR2GRAY)
    img_for_detect_gray = cv2.resize(img_for_detect, (main_sec_obj.height, main_sec_obj.width), interpolation = cv2.INTER_LINEAR)
    (thresh, im_bw) = cv2.threshold(img_for_detect_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    thresh = 200
    main_sec_image = cv2.threshold(img_for_detect_gray, thresh, 255, cv2.THRESH_BINARY)[1]
    
    # convert name rect to binary 
    name_sec_image = cv2.resize(name_sec_image,name_sec_obj.wh)
    img_for_detect = cv2.cvtColor(name_sec_image, cv2.COLOR_BGR2GRAY)
    img_for_detect_gray = cv2.resize(img_for_detect, (name_sec_obj.height, name_sec_obj.width), interpolation = cv2.INTER_LINEAR)
    (thresh, im_bw) = cv2.threshold(img_for_detect_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    thresh = 200
    name_sec_image = cv2.threshold(img_for_detect_gray, thresh, 255, cv2.THRESH_BINARY)[1]

    # omr for main
    main_sec_detect = []
    for pos in  main_sec_obj.get_file():
        x,y = pos[0]
        imgCrop = main_sec_image[y:y + main_sec_obj.rect_range, x:x + main_sec_obj.rect_range]
        count = cv2.countNonZero(imgCrop)
        cv2.rectangle(main_sec_image, (x, y), (x + main_sec_obj.rect_range, y + main_sec_obj.rect_range), (0, 255, 0), 2)
        if(count < sens):
            main_sec_detect.append(pos[1]) 

    # omr for name
    name_sec_detect = []
    for pos in  name_sec_obj.get_file():
        x,y = pos[0]
        imgCrop = name_sec_image[y:y + name_sec_obj.rect_range, x:x + name_sec_obj.rect_range]
        count = cv2.countNonZero(imgCrop)
        cv2.rectangle(name_sec_image, (x, y), (x + name_sec_obj.rect_range, y + name_sec_obj.rect_range), (0, 255, 0), 2)
        if(count < sens):
            name_sec_detect.append(pos[1]) 
    
    
    cv2.imshow("Main Section Image", main_sec_image)
    cv2.imshow("Name Section Image", name_sec_image)
    print(main_sec_detect,name_sec_detect)
    cv2.waitKey(0)
    cv2.destroyAllWindows()