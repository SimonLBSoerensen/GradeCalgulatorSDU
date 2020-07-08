from bs4 import BeautifulSoup
import pyperclip
import numpy as np
from datetime import datetime

debug_mode = False

decimals = 1
bar_length = 50

def cal_GPA(grads, ects, low_grade=2, high_grade=12):
    total_ects = np.sum(ects)
    prodoct_score = np.sum(grads * ects)
    return (prodoct_score/total_ects-low_grade)/(high_grade-low_grade)*10+2

def devide_bachelor_master():
    pass

def number_grade_test(grade):
    number_grade = False
    try:
        grade = int(grade)
    except:
        pass
    else:
        number_grade = True
    return number_grade

bachelor = []
master = []

sdu_mode = input("Are you from SDU? (y/n): ")

if sdu_mode.lower() == "y":
    if debug_mode:
        with open("example.html") as f:
            html = f.read()
    else:
        _ = input("Copi the html of the 'Grade Results' page on 'selvbprod.sdu.dk' to you clipboard and hit enter...")
        html = pyperclip.paste()

    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find(id="resultTableGrup")

    if debug_mode:
        bch_date = datetime.strptime("25-06-2019", "%d-%m-%Y")  #
    else:
        bch_fomat = input("Enter a day there is between the last bachelor grade and (before) the first master grade (dd-mm-yyyy): ")
        bch_date = datetime.strptime(bch_fomat, "%d-%m-%Y")

    for tr in table.find_all("tr")[1:]:
        code, name, judged, registered, grade, letter_grade, ects = [td.get_text().strip() for td in tr.find_all("td")]

        ects = float(ects)
        judged = datetime.strptime(judged, "%d.%m.%Y")
        registered = datetime.strptime(registered, "%d.%m.%Y")

        number_grade = number_grade_test(grade)
        if number_grade:
            grade = int(grade)

        if ects == 0:
            continue

        arr = [code, name, judged, registered, grade, letter_grade, ects, number_grade]

        if judged <= bch_date:
            bachelor.append(arr)
        else:
            master.append(arr)
else:
    for level, arr in zip(["bachelor", "master"], [bachelor, master]):
        while True:
            temp = input("{}: Input a course (or 'x' for end of {} courcses). Enter 'ECTS,grade', grade can be numeric or B for pass: ".format(level.title(), level))
            if temp == "x":
                break

            ects, grade = temp.split(",")

            ects = float(ects)

            number_grade = number_grade_test(grade)
            if number_grade:
                grade = int(grade)

            arr.append([None, None, None, None, grade, None, ects, number_grade])


bachelor = np.array(bachelor)
master = np.array(master)


def print_part_info(part_name, part_data):
    bar_padding = bar_length - len(part_name)
    print(part_name + "-" * bar_padding)

    if len(part_data) == 0:
        return

    codes, names, judgeds, registereds, grades, letter_grades, ects, number_grade = part_data.T

    print("Number of courses:", len(grades))


    print("ECTS sum:", np.round(np.sum(ects), decimals=decimals))

    number_grads_idxs = np.where(number_grade == 1)[0]
    passed_npassed_idx = np.delete(np.arange(len(number_grade)), number_grads_idxs)
    print("Grade stats (mean +- stddev / min / max): {:0.2f} +- {:0.2f} / {:0.2f} / {:0.2f}".format(
                                                                                np.mean(grades[number_grads_idxs]),
                                                                                np.std(grades[number_grads_idxs]),
                                                                                np.min(grades[number_grads_idxs]),
                                                                                np.max(grades[number_grads_idxs])))
    print("Number/passed grade ECTS: {:0.1f}/{:0.1f}".format(np.sum(ects[number_grads_idxs]),
                                                                    np.sum(ects[passed_npassed_idx])))
    print("Percentage of passed/not passed courses (based on ECTS): {:0.2f}%".format(np.sum(ects[passed_npassed_idx])/np.sum(ects)*100))

    number_dict = dict(np.array(np.unique(grades[number_grads_idxs], return_counts=True)).T)
    letter_dict = dict(np.array(np.unique(grades[passed_npassed_idx], return_counts=True)).T)
    print("Grads counts:", {**letter_dict, **number_dict})

    m_gpa = cal_GPA(grades[number_grads_idxs], ects[number_grads_idxs])
    print("GPA:", np.round(m_gpa, decimals=decimals))
    print("")


print_part_info("Bachelor", bachelor)
print_part_info("Master", master)
print_part_info("Overall", np.array(list(bachelor) + list(master)))
input("Exit...")
