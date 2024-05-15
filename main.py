import util
import os
import argparse
import pickle
import cv2
import numpy as np
from functools import cmp_to_key

def write_score(answer_sheet: util.ScorePaper, test_case: str):
    score_paper: util.ScorePaper = util.getScorePaper(test_case)
    n = len(answer_sheet.get_answer())
    score = 0

    for i in range(n):
        if 1 <= i + 1 <= 50:
            if answer_sheet.get_answer()[i] == score_paper.get_answer()[i]:
                score += 1.5
        elif 51 <= i + 1 <= 60:
            if answer_sheet.get_answer()[i] == score_paper.get_answer()[i]:
                score += 2.5
    return (score_paper.get_id(), score, score_paper.get_cancel())

def run():
    answer_sheet: util.ScorePaper = util.getScorePaper("testcases/answer_sheet.png")
    test_cases = os.listdir("testcases/b2")
    test_cases = list(filter(lambda x: x.startswith("b2_"), test_cases))
    with open("score.csv", "w") as f:
        for testcase in test_cases:
            (id, score, cancled) = write_score(answer_sheet, f"testcases/b2/{testcase}")
            print(f"{id}: {score} {'(cancled)' if cancled else ''}")
            f.write(f"{id},{score}{',CANCLED' if cancled else ''}\n")

def test(file_name: str):
    util.checkDetectedCircles(file_name)
    paper: util.ScorePaper = util.getScorePaper(file_name)
    paper.print()

def comparator_y_x(a, b):
    x1, y1, r1 = a
    x2, y2, r2 = b
    if abs(y1 - y2) < r1 / 2:
        return x1 - x2
    return y1 - y2

def generate_testcases():
    marked = set()

    img = cv2.imread("clear.png", cv2.IMREAD_COLOR)
    gray_scale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_blurred = cv2.blur(gray_scale, (3, 3))
    detected_circles = cv2.HoughCircles(gray_blurred, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=10, maxRadius=30)
    if detected_circles is not None:
        colors = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        detected_circles = np.uint16(np.around(detected_circles))
        circles = []
        for pt in detected_circles[0, :]:
            a, b, r = pt[0], pt[1], pt[2]
            if 2339*0.2 > b and a > 1654*0.8:
                circles.append([int(a), int(b), int(r)])

        circles.sort(key=cmp_to_key(comparator_y_x))

        i = 0
        for x, y, r in circles:
            # draw solid circle
            cv2.circle(img, (x, y), r, (0, 0, 0), -1)
            i += 1

    cv2.imshow("image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("args", type=str, nargs="*")
    cmd = parser.parse_args().args[0]
    if (cmd == "run"):
        run()
    elif (cmd == "test"):
        file_name = parser.parse_args().args[1]
        test("testcases/"+file_name)
    elif (cmd == "generate"):
        generate_testcases()
    else:
        print("Invalid command")
