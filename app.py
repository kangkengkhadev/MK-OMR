import cv2
import numpy as np
from matplotlib import pyplot as plt
from os import walk
import pickle

path = "template/"
pickle_name = 'exam1'
position_path = './pickle/'
circle_width, circle_height = 25,25
img = cv2.imread('Ideal.JPEG', 0)
img = cv2.resize(img, (1700, 2250), interpolation = cv2.INTER_LINEAR)
sens = 500

# structure = [
#     ["part0", [8,10,0]], # 0-79 
#     ["part1", [50,5,1]], # 80 - 129
#     ["part2", [10,6,0]], # 
# ]

# def to_ans(structure,ans):
#     for i in structure:
#         if(ans > (i[1][0]*i[1][1])-1):
#             ans = ans - (i[1][0]*i[1][1] )
#             print("has con")
#             continue
            
#         else:
#             for j in range(1,i[1][0]): # 1-8
#                 for k in range(i[1][2],i[1][1]):
#                     if ((j-1)*i[1][1])+k == ans+i[1][2]:
#                         return [i[0],j,k]
#             print("not found")

# print(to_ans(structure,78))

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
    if(count < sens):
        arr.append(pos[1])  
        
print(arr)

