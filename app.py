from typing import Any
import cv2
import numpy as np
from matplotlib import pyplot as plt
from os import walk
import pickle

path = "template/"
pickle_name = 'exam2'
position_path = './pickle/'
circle_width, circle_height = 25,25
img = cv2.imread('test.jpg', cv2.IMREAD_GRAYSCALE)
im_gray = cv2.resize(img, (1700, 2250), interpolation = cv2.INTER_LINEAR)
(thresh, im_bw) = cv2.threshold(im_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
thresh = 200
img = cv2.threshold(im_gray, thresh, 255, cv2.THRESH_BINARY)[1]
sens = 200

class UserAns:
    def __init__(self):
        self.id = [None]*8
        self.answer = {1:{k:None for k in range(1, 51)}, 2:{k:[None for i in range(6)] for k in range(1, 11)}}

    def getId(self):
        return self.id

    def getAnswer(self):
        return self.answer

def formatToUserAns(arr):
    arr.append(9999999)
    user = UserAns()
    
    #read user.id
    currentIdx = 0
    while arr[currentIdx] <= 79:
        user.getId()[arr[currentIdx]//10] = arr[currentIdx]%10
        currentIdx += 1
    
    prev = -1

    #read part1 (multiple choice)
    while arr[currentIdx] <= 329:
        current = (arr[currentIdx] - 80)//5+1
        if prev >= current:
            user.getAnswer()[1][current] = "INVALID"
        else:
            user.getAnswer()[1][current] = (arr[currentIdx] - 80)%5 + 1
        prev = current
        currentIdx += 1

    offset = 330

    while arr[currentIdx] <= 929:
        current = (arr[currentIdx] - offset)//60+1
        limit = 60*current
        # user.getAnswer()[2][current] = [None]*6
        errorFlag = False
        while arr[currentIdx] - offset < limit:
            field = ((arr[currentIdx] - offset)//10)%6
            if user.getAnswer()[2][current][field] != None:
                errorFlag = True
            user.getAnswer()[2][current][field] = (arr[currentIdx] - offset)%10
            currentIdx += 1
        if errorFlag:
            user.getAnswer()[2][current] = "INVALID"

    return user

def get_file(position_path):
    with open(position_path, 'rb') as f:
        posList = pickle.load(f)
    return posList

arr = []

posList = get_file(position_path+pickle_name)
for pos in posList:
    x,y = pos[0]
    imgCrop = img[y:y + circle_height, x:x + circle_width]
    count = cv2.countNonZero(imgCrop)
    print(count)
    if(count < sens):
        arr.append(pos[1])  

print(arr)
# user = formatToUserAns(arr)
# #user_id
# print(user.getId())
# #multiple choice
# for key, value in formatToUserAns(arr).getAnswer()[1].items():
#     print("{}: {}".format(key, value))
# #filled
# for key, values in formatToUserAns(arr).getAnswer()[2].items():
#     print("{}: {}".format(key, values))