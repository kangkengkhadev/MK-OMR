import pickle
import numpy as np
import cv2
from cv2.typing import MatLike

class MyPickle:
    def __init__(self, filename):
        self.filename = filename
        ext_name = self.filename.split("_")
        self.rect_range = int(ext_name[4])
        self.size = (int(ext_name[3]), int(ext_name[2]))

    def get_file(self):
        with open(self.filename, "rb") as f:
            posList = pickle.load(f)
        return posList

class ScorePaper:
    def __init__(self):
        self.seat_no = ["X", "X"]
        self.id = ["X", "X", "X", "X", "X", "X", "X", "X"]
        self.cancle = False
        self.answer = [""] * 60

    def set_seat_no(self, index):
        self.seat_no[index // 10] = str(index % 10)

    def set_id(self, index):
        index -= 20
        self.id[index // 10] = str(index % 10)

    def set_cancel(self, flag):
        self.cancle = flag

    def set_answer(self, index):
        if 0 <= index <= 249:
            self.answer[index // 5] += str(index % 5 + 1)
        elif 250 <= index <= 849:
            index -= 250
            self.answer[50 + index // 60] += str(index % 10)

    def get_answer(self):
        return self.answer
    
    def get_id(self):
        return "".join(self.id)

    def get_cancel(self):
        return self.cancle

    def name_section_indexing(self, index):
        if 0 <= index <= 19:
            self.set_seat_no(index)
        elif 20 <= index <= 99:
            self.set_id(index)
        elif index == 100:
            self.set_cancel(True)

    def answer_section_indexing(self, index):
        self.set_answer(index)

    def print(self):
        print("Seat No: ", "".join(self.seat_no))
        print("ID: ", "".join(self.id))
        print("Cancle: ", self.cancle)
        for i in range(60):
            print(f"{i + 1}:\t{self.answer[i]}")

def getPickleIntances() -> tuple[MyPickle, MyPickle]:
    name_section_pickle = "pickle_label/rect2_250_1000_15_15"
    answer_section_pickle = "pickle_label/rect1_1250_1000_15_15"

    name_section_instance = MyPickle(name_section_pickle)
    answer_section_instance = MyPickle(answer_section_pickle)

    return (name_section_instance, answer_section_instance)

def accept(expected: int, actual: int) -> bool:
    return abs(expected - actual) / expected * 100 < 5

def cropImage(test_case: str) -> list[MatLike]:
    expected_height_1 = 224
    expected_height_2 = 981
    min_area = 200000

    og_image = cv2.imread(test_case)
    og_image = cv2.resize(og_image, (1000, 1250), interpolation=cv2.INTER_LINEAR)
    og_image = cv2.cvtColor(og_image, cv2.COLOR_BGR2GRAY)

    cropped_rectangles = []
    adpt_thresh = cv2.adaptiveThreshold(
        og_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 51, 9
    )
    contours, _ = cv2.findContours(
        adpt_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    for contour in contours:
        if cv2.contourArea(contour) > 4000:
            x, y, w, h = cv2.boundingRect(contour)
            cropped_rectangle = cv2.cvtColor(og_image[y : y + h, x : x + w], cv2.COLOR_GRAY2BGR)
            height = cropped_rectangle.shape[0]
            area = cropped_rectangle.shape[0] * cropped_rectangle.shape[1]
            if (accept(expected_height_1, height) or accept(expected_height_2, height)) and area > min_area:
                cropped_rectangles.append(cropped_rectangle)
    cropped_rectangles.sort(key=lambda x: x.shape[0] * x.shape[1])
    cv2.imwrite("mock_images/rectangle_1.png", cropped_rectangles[1])
    cv2.imwrite("mock_images/rectangle_2.png", cropped_rectangles[0])

    return cropped_rectangles

def convertToBinary(test_case: str) -> tuple[MatLike, MatLike]:
    cropped_rectangles = cropImage(test_case)
    if len(cropped_rectangles) != 2:
        print("Error: cropped_rectangles should have length 2")
        return tuple()

    thresh = 200

    name_section, answer_section = cropped_rectangles

    name_section_instance, answer_section_instance = getPickleIntances()

    name_section_bin = cv2.resize(name_section, name_section_instance.size)
    name_section_bin = cv2.threshold(name_section_bin, thresh, 255, cv2.THRESH_BINARY)[1]
    answer_section_bin = cv2.resize(answer_section, answer_section_instance.size)
    answer_section_bin = cv2.threshold(answer_section_bin, thresh, 255, cv2.THRESH_BINARY)[1]

    return (name_section_bin, answer_section_bin)

def getScorePaper(test_case: str) -> ScorePaper:
    name_section_bin, answer_section_bin = convertToBinary(test_case)
    name_section_instance, answer_section_instance = getPickleIntances()
    score_paper = ScorePaper()

    white_max_percentage = 40

    for pos in name_section_instance.get_file():
        x, y = pos[0]
        index = pos[1]
        cropped_section = name_section_bin[y : y + name_section_instance.rect_range, x : x + name_section_instance.rect_range]
        white_pixel = np.sum(cropped_section == 255)
        black_pixel = np.sum(cropped_section == 0)
        percentage = white_pixel / (white_pixel + black_pixel) * 100
        if percentage < white_max_percentage:
            score_paper.name_section_indexing(index)
            cv2.rectangle(name_section_bin, (x, y), (x + name_section_instance.rect_range, y + name_section_instance.rect_range), (0, 255, 0), 2)
        else:
            cv2.rectangle(name_section_bin, (x, y), (x + name_section_instance.rect_range, y + name_section_instance.rect_range), (0, 0, 255), 2)

    for pos in answer_section_instance.get_file():
        x, y = pos[0]
        index = pos[1]
        cropped_section = answer_section_bin[y : y + answer_section_instance.rect_range, x : x + answer_section_instance.rect_range]
        white_pixel = np.sum(cropped_section == 255)
        black_pixel = np.sum(cropped_section == 0)
        percentage = white_pixel / (white_pixel + black_pixel) * 100
        if percentage < white_max_percentage:
            score_paper.answer_section_indexing(index)
            cv2.rectangle(answer_section_bin, (x, y), (x + answer_section_instance.rect_range, y + answer_section_instance.rect_range), (0, 255, 0), 2)
        else:
            cv2.rectangle(answer_section_bin, (x, y), (x + answer_section_instance.rect_range, y + answer_section_instance.rect_range), (0, 0, 255), 2)

    return score_paper
