import cv2
import cv2.mat_wrapper
import numpy as np
import os
import pickle

name = "Test_page-0002.jpg"
main_sec_pickle = "pickle_label/rect1_1250_1000_15_15"
name_sec_pickle = "pickle_label/rect2_250_1000_15_15"
default_rect_space = 200000

# transform imahe for rectangle
org_image = cv2.imread(name)
org_image = cv2.resize(org_image, (1000, 1250), interpolation = cv2.INTER_LINEAR)
result = org_image.copy()
gray = cv2.cvtColor(org_image , cv2.COLOR_BGR2GRAY)
thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,51,9)
cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
for c in cnts:
    cv2.drawContours(thresh, [c], -1, (255,255,255), -1)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,9))
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=4)
# blurred = cv2.GaussianBlur(gray, (3, 3), 0)
# edges = cv2.Canny(blurred, 120, 255, 1)
# contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cropped_rectangles = []

# tansform for omr
img_for_detect = cv2.imread(name, cv2.IMREAD_GRAYSCALE)
img_for_detect_gray = cv2.resize(img_for_detect, (1000, 1250), interpolation = cv2.INTER_LINEAR)
(thresh, im_bw) = cv2.threshold(img_for_detect_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
thresh = 0
img_for_detect = cv2.threshold(img_for_detect_gray, thresh, 255, cv2.THRESH_BINARY)[1]
sens = 40

# # find rectangles
# for contour in contours:
#     peri = cv2.arcLength(contour, True)
#     approx = cv2.approxPolyDP(contour, 0.03 * peri, True)
#     if len(approx) == 4:
#         x, y, w, h = cv2.boundingRect(approx)
#         cropped_rectangle = org_image[y:y+h, x:x+w]
#         if cropped_rectangle.shape[0] * cropped_rectangle.shape[1] < default_rect_space:
#             continue
#         cropped_rectangles.append(cropped_rectangle)

cnts = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
area_treshold = 4000
for c in cnts:
    if cv2.contourArea(c) > area_treshold :
        x,y,w,h = cv2.boundingRect(c)
        cropped_rectangle = org_image[y:y+h, x:x+w]
        if cropped_rectangle.shape[0] * cropped_rectangle.shape[1] < default_rect_space:
            continue
        cv2.imwrite(str(c.shape)+".png",cropped_rectangle)
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

class ScorePaper:
    def __init__(self):
        self.seat_no = ['X', 'X']
        self.id = ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']
        self.cancle = False
        self.choice = [""] * 60

    def get_seat_no(self):
        return self.seat_no

    def set_seat_no(self, index):
        self.seat_no[index // 10] = str(index % 10)

    def get_id(self):
        return self.id

    def set_id(self, index):
        index -= 20;
        self.id[index // 10] = str(index % 10)

    def get_cancle(self):
        return self.cancle

    def set_cancel(self, flag):
        self.cancle = flag;

    def get_choice(self):
        return self.choice

    def set_choice(self, index):
        if 0 <= index <= 249:
            self.choice[index // 5] += str(index % 5 + 1)
        elif 250 <= index <= 849:
            self.choice[index // 60] += str(index % 10)

def student_info_index(score_paper: ScorePaper, index: int):
    if 0 <= index <= 19:
        score_paper.set_seat_no(index)
    elif 20 <= index <= 99:
        score_paper.set_id(index)
    elif index == 100:
        score_paper.set_cancel(True)

def score_info_index(score_paper: ScorePaper, index: int):
        score_paper.set_choice(index)

if(len(cropped_rectangles) != 2):
    print(len(cropped_rectangles))
    print("Error while cropping please try again or evaluate by yourself")
    main_sec_obj = MyPickle(main_sec_pickle)
    main_sec_image = cropped_rectangles[0] 
    main_sec_image = cv2.resize(main_sec_image,main_sec_obj.wh)
    img_for_detect = cv2.cvtColor(main_sec_image, cv2.COLOR_BGR2GRAY)
    img_for_detect_gray = cv2.resize(img_for_detect, (main_sec_obj.height, main_sec_obj.width), interpolation = cv2.INTER_LINEAR)
    (thresh, im_bw) = cv2.threshold(img_for_detect_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    thresh = 200
    main_sec_image = cv2.threshold(img_for_detect_gray, thresh, 255, cv2.THRESH_BINARY)[1]
    score_paper = ScorePaper()
    # omr for main
    main_sec_detect = []
    for pos in  main_sec_obj.get_file():
        x,y = pos[0]
        imgCrop = main_sec_image[y:y + main_sec_obj.rect_range, x:x + main_sec_obj.rect_range]
        count = cv2.countNonZero(imgCrop)
        cv2.rectangle(main_sec_image, (x, y), (x + main_sec_obj.rect_range, y + main_sec_obj.rect_range), (0, 255, 0), 2)
        if(count < sens):
            score_info_index(score_paper, pos[1])
            main_sec_detect.append(pos[1]) 
    print(main_sec_detect)
    # cv2.imshow("Main Section Image", main_sec_image)
    cv2.imshow("Cropped Rectangle",cropped_rectangles[0])
    cv2.waitKey(0)
    cv2.destroyAllWindows()
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

    score_paper = ScorePaper()

    # omr for main
    main_sec_detect = []
    for pos in  main_sec_obj.get_file():
        x,y = pos[0]
        imgCrop = main_sec_image[y:y + main_sec_obj.rect_range, x:x + main_sec_obj.rect_range]
        count = cv2.countNonZero(imgCrop)
        cv2.rectangle(main_sec_image, (x, y), (x + main_sec_obj.rect_range, y + main_sec_obj.rect_range), (0, 255, 0), 2)
        if(count < sens):
            score_info_index(score_paper, pos[1])
            main_sec_detect.append(pos[1]) 

    # omr for name
    name_sec_detect = []
    for pos in  name_sec_obj.get_file():
        x,y = pos[0]
        imgCrop = name_sec_image[y:y + name_sec_obj.rect_range, x:x + name_sec_obj.rect_range]
        count = cv2.countNonZero(imgCrop)
        cv2.rectangle(name_sec_image, (x, y), (x + name_sec_obj.rect_range, y + name_sec_obj.rect_range), (0, 255, 0), 2)
        if(count < sens):
            student_info_index(score_paper, pos[1])
            name_sec_detect.append(pos[1]) 
    
    
    cv2.imshow("Main Section Image", main_sec_image)
    cv2.imshow("Name Section Image", name_sec_image)
    print(main_sec_detect,name_sec_detect)
    print("====== Student Info ======")
    print("Seat No.:", "".join(score_paper.get_seat_no()))
    print("ID:", "".join(score_paper.get_id()))
    print("Cancle this paper:", score_paper.get_cancle())
    print("====== Student Choice ======")
    print("Choice:")
    for i in range(0, len(score_paper.get_choice())):
        print("Q", i+1, ":", score_paper.get_choice()[i])
    cv2.waitKey(0)
    cv2.destroyAllWindows()
