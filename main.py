import util
import os

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

if __name__ == '__main__':
    answer_sheet: util.ScorePaper = util.getScorePaper("testcases/answer_sheet.png")
    test_cases = os.listdir("testcases")
    test_cases = list(filter(lambda x: x.startswith("testcase_"), test_cases))
    with open("score.csv", "w") as f:
        for testcase in test_cases:
            (id, score, cancled) = write_score(answer_sheet, f"testcases/{testcase}")
            print(f"{id}: {score} {'(cancled)' if cancled else ''}")
            f.write(f"{id},{score}{',CANCLED' if cancled else ''}\n")
